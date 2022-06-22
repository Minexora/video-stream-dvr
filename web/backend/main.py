import os
import json
import logging
import traceback
from flask_cors import CORS
from engineio.payload import Payload
from flask_socketio import SocketIO, emit, send
from flask import Flask, Response, render_template, request, jsonify

# aynı anda birden fazla işlem için kullanılmaktadır.
Payload.max_decode_packets = 5000

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
app.config['SECRET_KEY'] = 'secret!'

# socket flask ile birleştirme
sio = SocketIO(app)

# çalışılan konumu almak için
basedir = os.path.dirname(os.path.realpath(__file__))

# log yapılandırması
logging.basicConfig(
    handlers=[
        logging.FileHandler(filename=os.path.join(basedir, "server.log"), encoding="UTF-8"),
    ],
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# cors hatası vermemesi için
CORS(app)


# global değişkenler
buffer = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/videos')
def video():
    return render_template('record.html')


# @app.route('/video_feed', methods=['GET'])
# def video_feed():
#     args = request.args
#     return Response(
#         get_video_stream(stream=args['stream']),
#         mimetype='multipart/x-mixed-replace; boundary=frame'
#     )


# def get_video_stream(stream):
#     while True:
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpg\r\n\r\n' + buffer[stream][:-1] + b'\r\n\r\n')


#  soket server
class SocketServer:
    manager = None
    ui = None

    def __init__(self) -> None:
        sio.on_event("connect", self.on_connect, namespace='/')
        sio.on_event("add_manager", self.on_add_manager, namespace='/')
        sio.on_event("add_ui", self.add_ui, namespace='/')
        sio.on_event("add_video_stream", self.on_add_video_stream, namespace='/')
        sio.on_event("add_camera", self.ui_add_camera, namespace='/')
        sio.on_event("video_stream", self.on_video_stream, namespace='/')
        sio.on_event("on_error", self.error_handler, namespace='/')
        sio.on_event("disconnect", self.on_disconnect, namespace='/')

    def on_connect(self):
        emit('add_camera', {'data': f'{request.sid} Connected.'})
        logging.info(f"{request.sid} numaralı id bağlandı.")

    def on_add_manager(self):
        self.manager = request.sid
        logging.info(f"Manager bağlantı sağladı. ID: ")

    def add_ui(self):
        global buffer
        self.add_ui = request.sid
        for stream in buffer.keys():
            if buffer[stream]:
                emit('on_add_camera_result', {"status": True, "data": {"camera_name": stream, "img": "data:image/png;base64,"+buffer[stream][-1]}})

    def on_add_video_stream(self, data):
        global buffer
        buffer[data["camera_name"]] = []
        logging.info(f"Stream bağlantı kurdu. ID: {request.sid}")

    def ui_add_camera(self, data):
        try:
            logging.info("Kamera ekleniyor.")
            if (self.manager):
                emit('on_add_camera', data, to=self.manager)
                emit('on_add_camera_result', {"status": True, "data": data})
                logging.info("Kamera eklendi.")
            else:
                emit('on_add_camera_result', {"status": False, "msg": "Manager bağlı değil."})
                logging.info("Manager bağlı değil.")
        except Exception:
            logging.error(traceback.format_exc())

    def on_video_stream(self, data):
        global buffer
        buffer[data["camera_name"]].append(data['buffer'])
        emit('on_video_picture', {"data": {"camera_name": data["camera_name"], "img": "data:image/png;base64," + buffer[data["camera_name"]][-1]}}, to=self.add_ui)

    def error_handler(self, e):
        logging.error(f'ERROR: {str(e)}')

    def on_disconnect(self):
        logging.info(f'{request.sid} client bağlantısı koptu.')


if __name__ == "__main__":
    SocketServer()
    sio.run(app, host="0.0.0.0", port=8080)

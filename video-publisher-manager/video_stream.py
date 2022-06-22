import os
import cv2
import json
import base64
import logging
import socketio
from threading import Thread


basedir = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(
    filename=os.path.join(basedir, "video-publisher-manager.log"),
    format="%(asctime)s - %(levelname)s - %(message)s ",
    level=logging.INFO,
)


class VideoStream(Thread):

    def __init__(self, camera_name, camera_url) -> None:
        Thread.__init__(self)
        self.camera_name = camera_name
        self.camera_url = camera_url

    def run(self):
        def on_connect():
            logging.info("Server bağlantısı kuruldu.")
            self.sio.emit('add_video_stream', {"camera_name": self.camera_name})
            logging.info("Video stream kaydı yapıldı.")

            logging.info(f"{self.camera_url} adresine bağlantı kuruluyor.")
            video = cv2.VideoCapture(self.camera_url)

            if(video.isOpened()):
                logging.info(f"{self.camera_url} adresine bağlanıldı.Video paylaşılıyor.")

            while(video.isOpened()):
                success, frame = video.read()
                if not success:
                    logging.error(f"{ self.camera_name } adlı stream için video okunamadı.Çıkılıyor.")
                    break
                ret, buffer = cv2.imencode('.jpg', frame)
                buff = base64.b64encode(buffer)
                self.sio.emit('video_stream', {"camera_name": self.camera_name, "buffer": buff.decode('utf-8') })
            
            video.release()
            logging.info(f'{ self.camera_name } adlı stream için video paylaşma işlemi bitirildi.')

        def error_handler(e):
            logging.error(f'ERROR: {str(e)}')

        def on_disconnect():
            logging.info('Client disconnected')

        self.sio = socketio.Client()
        self.sio.on("connect", on_connect, namespace='/')
        self.sio.on("on_error", error_handler, namespace='/')
        self.sio.on("disconnect", on_disconnect, namespace='/')
        self.sio.connect('http://127.0.0.1:8080', wait_timeout=10)
        self.sio.wait()

import os
import logging
import socketio
from video_stream import VideoStream

basedir = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(
    filename=os.path.join(basedir, "video-publisher-manager.log"),
    format="%(asctime)s - %(levelname)s - %(message)s ",
    level=logging.INFO,
)

sio = socketio.Client()


#  soket server
class VideoPublisherManager:
    threads = {}

    def __init__(self) -> None:
        sio.on("connect", self.on_connect, namespace='/')
        sio.on("on_add_camera", self.on_add_camera, namespace='/')
        sio.on("on_error", self.error_handler, namespace='/')
        sio.on("disconnect", self.on_disconnect, namespace='/')

    def on_connect(self):
        logging.info("Server bağlantısı kuruldu.")
        sio.emit('add_manager')
        logging.info("Server manager kaydı yapıldı.")

    def on_add_camera(self, data):       
        video_thread = VideoStream(camera_name=data['camera_name'], camera_url=data['camera_url'])
        video_thread.daemon = True
        video_thread.start()
        self.threads[data["camera_name"]] = video_thread

    def error_handler(self, e):
        logging.error(f'ERROR: {str(e)}')

    def on_disconnect(self):
        logging.info('Client disconnected')


if __name__ == '__main__':
    VideoPublisherManager()
    sio.connect('http://127.0.0.1:8080', wait_timeout=10)
    sio.wait()

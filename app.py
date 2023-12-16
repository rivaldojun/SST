from flask import Flask,render_template,jsonify,redirect,url_for,request,session,flash,Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_,or_
from flask_socketio import SocketIO, emit, send,join_room
from flask_cors import CORS
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

class VideoCamera(object):
    cv2.setUseOptimized(True)
    cv2.setNumThreads(4)  # Nombre de threads (à ajuster)
    cv2.ocl.setUseOpenCL(True)  # Utiliser OpenCL si disponible

    def __init__(self, video_path):
        self.video = cv2.VideoCapture(video_path)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            success, image = self.video.read()

            # Recolor image to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
          
            # Make detection
            results = pose.process(image)
        
            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                     )

            _, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


app=Flask(__name__)

#BASE DE DONNE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

app.secret_key = '123'
socketio = SocketIO(app)
CORS(app)
socketio.init_app(app, cors_allowed_origins="*")


@app.route('/')
def visiteur() :
    return render_template('visiteur.html',INSCRIPTION='SIGN UP',CONNEXION='LOG IN')

@app.route('/rula')
def rula() :
    return render_template('rula.html')

@app.route('/start')
def start() :
    return render_template('start.html')

@app.route('/video_feed_1')
def video_feed_1():
    return Response(gen(VideoCamera(0)), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__=="__main__":
    socketio.run(app,debug=True)

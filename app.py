from flask import Flask,render_template,jsonify,redirect,url_for,request,session,flash,Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_,or_
from flask_socketio import SocketIO, emit, send,join_room
from flask_cors import CORS
import cv2
import numpy as np
import threading
import time
import mediapipe as mp
from Rula import score_final_from_table_c
import datetime

messages = {}
messages['score'] = ''
messages['score_inst'] = ''


app=Flask(__name__)

#BASE DE DONNE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

app.secret_key = '123'
socketio = SocketIO(app)
CORS(app)
socketio.init_app(app, cors_allowed_origins="*")

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numbers = db.Column(db.String, nullable=False)
    nom=db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

with app.app_context():
        db.create_all()

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle


s=[5,8,1]

class VideoCamera():
    cv2.setUseOptimized(True)
    cv2.setNumThreads(4)  # Nombre de threads (à ajuster)
    cv2.ocl.setUseOpenCL(True)  # Utiliser OpenCL si disponible

    def __init__(self, video_path):
        self.video = cv2.VideoCapture(video_path)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        params = {
    'shoulder_angle': 0,
    'elbow_angle': 0,
    'wrist_angle': 0,
    'trunck_angle': 0,
    'neck_angle': 0,
    'static_time': 0,
    'charge': 5,
    'mid_range_twist': True,
    'is_raised': False,
    'is_abducted': True,
    'shoulder_is_supported': False,
    'shoulder_in_extension': False,
    'is_out_to_side': False,
    'is_bent_from_midline': True,
    'neck_is_twisted': False,
    'neck_is_bending': True,
    'neck_in_extension': False,
    'trunk_is_twisted': False,
    'trunk_is_bending': False,
    'leg_is_supported': False,   
    'intermitence': False,
    'static_posture': False,
    'repetead': True,
    'complete_twist': False
}
        
        # Curl counter variables
        counter = 0 
        stage = None
        score_rula = 0
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
            
            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates
                shoulder_left = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow_left = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist_left = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                hip_left = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                pinky_left = [landmarks[mp_pose.PoseLandmark.LEFT_PINKY.value].x,landmarks[mp_pose.PoseLandmark.LEFT_PINKY.value].y]
                knee_left = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]



                shoulder_right = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow_right = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist_right = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                
                
                
                # Calculate angle
                angle_elbow_left = calculate_angle(shoulder_left, elbow_left, wrist_left)

                angle_elbow_right = calculate_angle(shoulder_right, elbow_right, wrist_right)

                angle_shoulder_left = calculate_angle(shoulder_left, elbow_left, hip_left)

                angle_wrist_left = calculate_angle(wrist_left, elbow_left, pinky_left)

                angle_trunk_left = calculate_angle(knee_left, hip_left,shoulder_left)


                params['elbow_angle'] = angle_elbow_left

                params['shoulder_angle'] = angle_shoulder_left
                params['wrist_angle'] = angle_wrist_left
                params['trunck_angle'] = angle_trunk_left
                score_rula = score_final_from_table_c(params)
                cv2.putText(image, str(angle_elbow_left), 
                           tuple(np.multiply(elbow_left, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
                cv2.putText(image, str(angle_elbow_right), 
                            tuple(np.multiply(elbow_right, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                cv2.putText(image, str(angle_shoulder_left), 
                            tuple(np.multiply(shoulder_left, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                cv2.putText(image, str(angle_wrist_left), 
                            tuple(np.multiply(wrist_left, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                cv2.putText(image, str(angle_trunk_left), 
                            tuple(np.multiply(knee_left, [640, 480]).astype(int)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                    )
                cv2.putText(image, f"Score rula: {score_rula}",(10,10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA)
            except:
                pass
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                    )
                                     

            _, jpeg = cv2.imencode('.jpg', image)
            # new_score = Score(value=score_rula)
            # db.session.add(new_score)
            # db.session.commit()
            return jpeg.tobytes(),score_rula


@app.route('/')
def visiteur() :
    return render_template('visiteur.html',INSCRIPTION='SIGN UP',CONNEXION='LOG IN')

@app.route('/submit', methods=['POST','GET'])
def submit():
    if request.method=='POST':
        name = request.form['name']
        session['nom']=name
        return redirect(url_for('rula'))
    return render_template('nom.html')

@app.route('/activite')
def activite():
    nom_utilisateur = session.get('nom')
    activites=Score.query.filter_by(nom=nom_utilisateur).all()
    return render_template('activite.html', activites=activites)


@app.route('/activite_plus/<id>')
def activite_plus(id):
    activite=Score.query.filter_by(id=id).first()
    numbers_list = [int(n) for n in activite.numbers.split(',')]
    return render_template('graph_activite.html', numbers_list=numbers_list)


@app.route('/enregistrer/<str_score>')
def enregistrer(str_score):
    # Ici, vous devez également obtenir le nom de l'utilisateur ou un identifiant unique
    # Pour cet exemple, je vais utiliser un nom statique
    nom_utilisateur = session.get('nom')

    # Créer une nouvelle instance de Score
    new_score = Score(numbers=str_score, nom=nom_utilisateur)

    # Ajouter l'instance à la base de données
    db.session.add(new_score)
    db.session.commit()

    return redirect(url_for('visiteur'))

@app.route('/rula')
def rula() :
    return render_template('rula.html')

@app.route('/how')
def how() :
    return render_template('how.html')

@app.route('/start/<int:id>')
def start(id) :
    return render_template('start.html',id=id,s=s)

def gen(camera):
    while True:
        frame,score= camera.get_frame()
        messages['score']=str(score)
        messages['score_inst'] =str(score)

        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        

@socketio.on('request_data')
def request_data():
    # Fetch or compute the latest data
    data = {
        'score': messages['score'],
        'score_inst': messages['score_inst']
    }
    socketio.emit('data_response', data)

@app.route('/video_feed_1/<int:id>')
def video_feed_1(id):
    return Response(gen(VideoCamera(id)), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__=="__main__":
    socketio.run(app,debug=True)

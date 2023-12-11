from flask import Flask,render_template,jsonify,redirect,url_for,request,session,flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_,or_
from flask_socketio import SocketIO, emit, send,join_room
from flask_cors import CORS

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












if __name__=="__main__":
    socketio.run(app,debug=True)

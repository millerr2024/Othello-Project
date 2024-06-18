#Some code borrowed from https://pypi.org/project/Flask-Login/ 
from app import app
import flask
from flask import render_template, request
import flask_login
from flask_login import LoginManager
import psycopg2
import os
from dotenv import load_dotenv
import json
from datetime import datetime
# import pytz


load_dotenv()

app.secret_key = os.getenv('SECRET_KEY', 'for dev')

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    conn = psycopg2.connect(database="login", user="webapp", 
                        password="dbPass", host="database", port="5432") 
  
    # create a cursor 
    cur = conn.cursor() 
  
    query = "SELECT username FROM userInfo WHERE username='%s'" % (username)

    cur.execute(query)

    # Fetch the data 
    data = cur.fetchall() 

    # close the cursor and connection 
    cur.close() 
    conn.close() 

    #check if no matching username
    if len(data) == 0:
        return

    user = User()
    user.id = username
    return user

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login/<username>/<password>')
def login(username, password):
    dict_to_return = {}

    conn = psycopg2.connect(database="login", user="webapp", 
                        password="dbPass", host="database", port="5432") 
  
    # create a cursor 
    cur = conn.cursor() 
  
    query = "SELECT pass FROM userInfo WHERE username='%s'" % (username)

    cur.execute(query)

    # Fetch the data 
    data = cur.fetchall() 

    # close the cursor and connection 
    cur.close() 
    conn.close() 

    #check if no stored password for this username or if stored password doesn't match user inputted pass
    if len(data) != 0 and str(data[0][0]) == password:
        user = User()
        user.id = username
        flask_login.login_user(user)
        dict_to_return['status'] = "success"
        return json.dumps(dict_to_return)

    dict_to_return['status'] = "error"
    return json.dumps(dict_to_return)


@app.route('/board')
@flask_login.login_required
def board():
    return render_template("board.html")

@app.route('/logout')
def logout():
    flask_login.logout_user()
    dict_to_return = {}
    dict_to_return['status'] = "success"
    return json.dumps(dict_to_return)

@login_manager.unauthorized_handler
def unauthorized_handler():
    dict_to_return = {}
    dict_to_return['status'] = "error"
    return json.dumps(dict_to_return)

@app.route('/newUser/<username>/<password>')
def newUser(username, password):
    dict_to_return = {}

    conn = psycopg2.connect(database="login", user="webapp", 
                        password="dbPass", host="database", port="5432") 
  
    # create a cursor 
    cur = conn.cursor() 
  
    query = "SELECT username FROM userInfo WHERE username='%s'" % (username)

    cur.execute(query)

    # Fetch the data 
    data = cur.fetchall() 

    #check if username already in use
    if len(data) != 0:
        dict_to_return['status'] = "error"
        return json.dumps(dict_to_return)
    
    #get today's date for profile info
    current_date = datetime.now()
    # converted_datetime = current_date.astimezone("America/Chicago")
    # formatted_date = converted_datetime
    formatted_date = current_date.strftime('%d %b %Y')

    #insert into table
    cur.execute('''INSERT INTO userInfo (username, pass, date_joined) VALUES (%s, %s, %s)''', (username, password, formatted_date))
  
    conn.commit()

    # close the cursor and connection 
    cur.close() 
    conn.close() 

    user = User()
    user.id = username
    flask_login.login_user(user)
    dict_to_return['status'] = "success"
    return json.dumps(dict_to_return)

@app.route('/newUserPage')
def newUserPage():
    return render_template("newUser.html")

@app.route('/stats')
@flask_login.login_required
def stats():
    dict_to_return = {}

    username = request.args.get('username', None)

    conn = psycopg2.connect(database="login", user="webapp", 
                        password="dbPass", host="database", port="5432") 
  
    # create a cursor 
    cur = conn.cursor() 
  
    query = "SELECT date_joined FROM userInfo WHERE username='%s';" % (username)

    cur.execute(query)

    # Fetch the data 
    data = cur.fetchall() 

    return render_template("stats.html", data=data)
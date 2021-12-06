#-----imports-----
#Web Server Modules
from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for

#Sql Server Modules
import pandas as pd
import pymysql
import logging
import sshtunnel
from sshtunnel import SSHTunnelForwarder

#-----------------

#-----Variables-----(Variables are predefined for readability and better debugging)
username = ""
password = ""

ssh_host = '192.168.1.64'
ssh_username = 'pi'
ssh_password = 'gm13112001'
database_username = 'remoteUser'
database_password = 'gm13112001'
database_name = 'test'
localhost = '127.0.0.1'
global tunnel
global connection


#-------------------

app = Flask(__name__)
#-----Url Routing-----
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods = ['POST'])
def login():
    username = request.form["username"]
    password = request.form["password"]
    #do database interaction and user verification
    open_ssh_tunnel()
    mysql_connect()
    
    run_query("USE test")
    #SQL INJECTION VUNERABLE!!
    data = run_query("SELECT passwd FROM users WHERE username = " + "\"" + username + "\"")
    #temporary
    if(len(data) >= 1):
        if(data[0][0] == password):
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    return "placeholder"

#---------------------

#sql
#opening an ssh tunnel to connect to the database
def open_ssh_tunnel(verbose=False):
    if verbose:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG

    global tunnel
    tunnel = SSHTunnelForwarder(
        (ssh_host, 22),
        ssh_username = ssh_username,
        ssh_password = ssh_password,
        remote_bind_address = ('127.0.0.1', 3306)
    )
    tunnel.start()

#Connecting to database via ssh tunnel
def mysql_connect():
    global connection
    connection = pymysql.connect(
        host='127.0.0.1',
        user=database_username,
        passwd=database_password,
        db=database_name,
        port=tunnel.local_bind_port
    )

def run_query(sql):    
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    return cursor.fetchall()

def mysql_disconnect():
    connection.close()

def close_ssh_tunnel():    
    tunnel.close
#Runtime
if __name__ == "__main__":
    app.run(debug=True)
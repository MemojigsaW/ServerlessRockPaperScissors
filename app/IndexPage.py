from app import webapp
from flask import render_template, request, jsonify, redirect, session, flash, url_for
from util import awsapis as aws
import base64
import io
import PIL.Image as Image
from functools import wraps
import gc

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print(session)
        if 'loggedin' in session:
            return f(*args, **kwargs)
        else:
            flash("Need to login", "error")
            return redirect(url_for('loadIndexPage'))
    return wrap

@webapp.route("/", methods=['POST', 'GET'])
def loadIndexPage():
    history = None
    if 'loggedin' in session:
        response = aws.get_dynamo_response()
        if 'Item' in response:
            history = response['Item']
    return render_template('index.html', session=session, history=history)

@webapp.route('/sign_in')
def sign_in():
    return redirect(webapp.aws_auth.get_sign_in_url())

@webapp.route('/aws_cognito_redirect')
def aws_cognito_redirect():
    try:
        access_token = webapp.aws_auth.get_access_token(request.args)
        webapp.aws_auth.token_service.verify(access_token)
        print(webapp.aws_auth.token_service.claims)
        session['username'] = webapp.aws_auth.token_service.claims['username']
        session['access_token'] = access_token
        session['loggedin'] = True
        session.permanent = True
    except:
        print("Authentication failed")
    
    return redirect(url_for('loadIndexPage'))

@webapp.route("/sign_out", methods=['POST', 'GET'])
def sign_out():
    print("sign out called")
    session.clear()
    gc.collect()
    return redirect(url_for('loadIndexPage'))

@webapp.route("/add_dummy_dynamo_entry")
@login_required
def add_dummy_dynamo_entry():
    aws.add_dynamo_history('lose', 'rock')
    
    return redirect(url_for('loadIndexPage'))

@webapp.route("/delete_history")
@login_required
def deleteHistory():
    aws.clear_dynamo_history()
    try:
        session["Computer_Score"] = 0
        session["Player_Score"] = 0
    except Exception as e:
        print(e)
    return redirect(url_for('loadIndexPage'))

@webapp.route("/api/get_model_status", methods=['GET'])
def getmodelstatus():
    response = aws.get_model_info()
    return response


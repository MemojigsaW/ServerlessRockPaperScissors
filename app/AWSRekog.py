import boto3
import config as cfg
from flask import render_template, url_for, redirect, flash, session, request, jsonify
from app import webapp
import random
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
from util import awsapis as aws
from app.IndexPage import login_required

cscore = 0
pscore = 0


@webapp.route("/AWSManage", methods=['GET'])
@login_required
def loadManagerPage():
    print("call loadmanagerpage")
    return render_template('RPSResults.html')


@webapp.route('/api/Startmodel', methods=['GET'])
def Start_Model():
    client = boto3.client('rekognition')

    project_arn = cfg.PROJECT_ARN
    model_arn = cfg.MODEL_ARN
    min_inference_units = 1
    version_name = cfg.VERSION_NAME

    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response = client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])

        # Get the running status
        describe_response = client.describe_project_versions(ProjectArn=project_arn,
                                                             VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage'])
        output = jsonify({
            'succeed': True
        })
    except Exception as e:
        output = jsonify({
            'succeed': False
        })
    finally:
        return output


@webapp.route('/api/Stopmodel', methods=['GET'])
def Stop_Model():
    client = boto3.client('rekognition')
    model_arn = cfg.MODEL_ARN

    print('Stopping model:' + model_arn)

    # Stop the model
    try:
        response = client.stop_project_version(ProjectVersionArn=model_arn)
        status = response['Status']
        print('Status: ' + status)
        output = jsonify({
            'succeed': True
        })
    except Exception as e:
        output = jsonify({
            'succeed': False
        })
    finally:
        return output

@webapp.route('/api/analyze_s3', methods=['POST'])
def analyze_s3():
    s3path = request.form["S3_Image"]
    response = None;
    try:
        client = boto3.client('rekognition')

        bucket = cfg.BUCKET_NAME
        photo = s3path
        min_confidence = cfg.MIN_CONFIDENCE
        model = cfg.MODEL_ARN

        # Call DetectCustomLabels
        response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                               MinConfidence=min_confidence,
                                               ProjectVersionArn=model)

        # calculate and display bounding boxes for each detected custom label
        print('Detected custom labels for ' + photo)
        print('Label ' + str(response['CustomLabels'][0]['Name']))
        print('Confidence ' + str(response['CustomLabels'][0]['Confidence']))
        response = jsonify({
            'succeed': True,
            'Label': str(response['CustomLabels'][0]['Name']),
            'Confidence': str(response['CustomLabels'][0]['Confidence'])
        })
    except Exception as e:
        response = jsonify({
            'succeed': False
        })
    finally:
        return response


@webapp.route('/redirect_GamePage', methods=['GET', 'POST'])
def preloadGamePage():
    if request.method == 'GET':
        return render_template('GamePage.html')

    player_label = request.form['Label']
    s3path = request.form['s3path']

    player_value = player_hand(player_label)

    # generate computer play
    value = (random.randint(1, 3))
    print(value)
    if value == 1:
        play = "Rock"
        url = 'https://john-bucket43634.s3.amazonaws.com/Rock_Img2.png'
    elif value == 2:
        play = "Scissors"
        url = 'https://john-bucket43634.s3.amazonaws.com/Scissors_Img2.png'
    else:
        play = "Paper"
        url = 'https://john-bucket43634.s3.amazonaws.com/Paper_Img2.png'

    # obtain screenshot
    s3 = boto3.client('s3')
    url1 = s3.generate_presigned_url('get_object',
                                     Params={
                                         'Bucket': cfg.BUCKET_NAME,
                                         'Key': s3path,
                                     },
                                     ExpiresIn=3600)

    # todo globals do not work the way they are suppose to in flask
    # also the score is not up to date with dynamo, maybe dynamocall
    game_results, state, pscore, cscore = winner(player_value, value)

    # remove if once cognito is ready for us all
    if 'loggedin' in session:
        aws.add_dynamo_history(state, player_label.lower())

    session["url1"] = url1
    session["url"] = url
    session["Computer"] = play
    session["Player"] = player_label
    session["game_results"] = game_results

    if not session.get('Computer_Score'):
        session['Computer_Score'] = 0
    if not session.get('Player_Score'):
        session['Player_Score'] = 0

    if "win" in game_results:
        session['Player_Score'] = session['Player_Score']+1
    elif "lose" in game_results:
        session['Computer_Score'] = session['Computer_Score']+1

    # session["Computer_Score"] = cscore
    # session["Player_Score"] = pscore

    return redirect(url_for('loadGamePage'))


@webapp.route('/GamePage', methods=['GET', 'POST'])
def loadGamePage():
    try:
        url1 = session["url1"]
        url = session["url"]
        play = session["Computer"]
        player_label = session["Player"]
        game_results = session["game_results"]
        _cscore = session["Computer_Score"]
        _pscore = session["Player_Score"]
        return render_template('GamePage.html', url1=url1, url=url, Computer=play, Player=player_label,
                               game_results=game_results, Computer_Score=_cscore, Player_Score=_pscore)
    except Exception as e:
        return redirect(url_for('loadManagerPage'))


# @webapp.route('/api/Analyze', methods=['GET'])
# def Analyze_Picture():
#     print("Call analyze picture")
#
#     try:
#         client = boto3.client('rekognition')
#
#         bucket = cfg.BUCKET_NAME
#         photo = cfg.PHOTO
#         min_confidence = cfg.MIN_CONFIDENCE
#         model = cfg.MODEL_ARN
#
#         # Call DetectCustomLabels
#         response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
#                                                MinConfidence=min_confidence,
#                                                ProjectVersionArn=model)
#
#         # calculate and display bounding boxes for each detected custom label
#         print('Detected custom labels for ' + photo)
#         print('Label ' + str(response['CustomLabels'][0]['Name']))
#         print('Confidence ' + str(response['CustomLabels'][0]['Confidence']))
#
#         player_value = player_hand(str(response['CustomLabels'][0]['Name']))
#
#         play2 = str(response['CustomLabels'][0]['Name'])
#
#         # generate computer play
#         value = (random.randint(1, 3))
#         print(value)
#         if value == 1:
#             play = "Rock"
#             url = 'https://john-bucket43634.s3.amazonaws.com/Rock_Img2.png'
#         elif value == 2:
#             play = "Scissors"
#             url = 'https://john-bucket43634.s3.amazonaws.com/Scissors_Img2.png'
#         else:
#             play = "Paper"
#             url = 'https://john-bucket43634.s3.amazonaws.com/Paper_Img2.png'
#
#         # obtain screenshot
#         s3 = boto3.client('s3')
#         url1 = s3.generate_presigned_url('get_object',
#                                          Params={
#                                              'Bucket': bucket,
#                                              'Key': 'image.png',
#                                          },
#                                          ExpiresIn=3600)
#
#         game_results, state, pscore, cscore = winner(player_value, value)
#
#         # remove if once cognito is ready for us all
#         if 'loggedin' in session:
#             aws.add_dynamo_history(state, play2.lower())
#
#         return render_template('GamePage.html', url1=url1, url=url, Computer=play, Player=play2,
#                                game_results=game_results, Computer_Score=cscore, Player_Score=pscore)
#     except Exception as e:
#         return str(e)


@webapp.route('/testimage')
def Test_Image():
    print("call testimage")

    value = (random.randint(1, 3))
    print(value)
    if value == 1:
        play = "Rock"
        url = 'https://john-bucket43634.s3.amazonaws.com/Rock_Img2.png'
    elif value == 2:
        play = "Scissors"
        url = 'https://john-bucket43634.s3.amazonaws.com/Scissors_Img2.png'
    else:
        play = "Paper"
        url = 'https://john-bucket43634.s3.amazonaws.com/Paper_Img2.png'
    play2 = "Rock"
    s3 = boto3.client('s3')
    url1 = s3.generate_presigned_url('get_object',
                                     Params={
                                         'Bucket': 'john-bucket43634',
                                         'Key': 'image.png',
                                     },
                                     ExpiresIn=3600)

    player_value = 1
    game_results, state, pscore, cscore = winner(player_value, value)

    # remove if once cognito is ready for us all
    if 'loggedin' in session:
        aws.add_dynamo_history(state, play2.lower())

    return render_template('GamePage.html', url1=url1, url=url, Computer=play, Player=play2,
                           game_results=game_results, Computer_Score=cscore, Player_Score=pscore)


def winner(user_action, computer_action):
    global cscore
    global pscore

    if user_action == computer_action:
        results = "It's a tie!"
        state = 'tie'
    elif user_action == 1:
        if computer_action == 2:
            results = "Rock smashes scissors! You win!"
            pscore += 1
            state = 'win'
        else:
            results = "Paper covers rock! You lose."
            cscore += 1
            state = 'lose'
    elif user_action == 2:
        if computer_action == 3:
            results = "Scissors cuts paper! You win!"
            pscore += 1
            state = 'win'
        else:
            results = "Rock smashes scissors! You lose."
            cscore += 1
            state = 'lose'
    elif user_action == 3:
        if computer_action == 1:
            results = "Paper covers rock! You win!"
            pscore += 1
            state = 'win'
        else:
            results = "Scissors cuts paper! You lose."
            cscore += 1
            state = 'lose'
    return results, state, pscore, cscore


def player_hand(hand_shape):
    if hand_shape.lower() == "rock":
        value = 1
    elif hand_shape.lower() == "scissors":
        value = 2
    else:
        value = 3
    return value

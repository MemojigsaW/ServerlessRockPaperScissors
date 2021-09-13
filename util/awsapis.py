import boto3
import config as cfg
from flask import session, jsonify
from boto3.dynamodb.conditions import Key, Attr


def uploadFile(file, key, _format) -> bool:
    s3client = boto3.client('s3')
    success = False
    try:
        response = s3client.put_object(
            Body=file,
            Bucket=cfg.BUCKET_NAME,
            Key=key + "." + _format,
            ContentType='image/png',
            ACL='public-read'
        )
        success = True
    except Exception as e:
        print(e)
    return success


def get_dynamo_response():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('users')
    response = table.get_item(
        Key={
            'username': session['username']
        }
    )
    return response


def add_dynamo_history(state, action):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('users')
    response = get_dynamo_response()

    if ('Item' in response):
        item = response['Item']
        numWins = item['numWins']
        numLoses = item['numLoses']
        numTies = item['numTies']
        games = (item['games']) + [{'state': state, 'action': action}]
        if (state == 'win'):
            numWins += 1
        elif (state == 'lose'):
            numLoses += 1
        else:
            numTies += 1

        table.update_item(
            Key={
                'username': session['username']
            },
            UpdateExpression="set numWins = :nw, numLoses = :nl, numTies= :nt, games = :a",
            ExpressionAttributeValues={
                ':nw': numWins,
                ':nl': numLoses,
                ':nt': numTies,
                ':a': games
            }
        )

    else:
        table.put_item(
            Item={
                'username': session['username'],
                'numWins': 0,
                'numLoses': 0,
                'numTies': 0,
                'games': []
            }
        )
        add_dynamo_history(state, action)


def clear_dynamo_history():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('users')
    table.update_item(
        Key={
            'username': session['username']
        },
        UpdateExpression="set games = :a",
        ExpressionAttributeValues={
            ':a': []
        }
    )


def get_model_info():

    client = boto3.client("rekognition")
    try:
        response = client.describe_project_versions(
            ProjectArn=cfg.PROJECT_ARN,
            VersionNames=[
                cfg.VERSION_NAME,
            ],
        )
        output = jsonify({
            'succeed': True,
            'status': response['ProjectVersionDescriptions'][0]['Status']
        })
    except Exception as e:
        output = jsonify({
            'succeed': False
        })
    finally:
        return output
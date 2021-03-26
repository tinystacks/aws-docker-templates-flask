from flask import Flask
from flask import request
import boto3
import os
import datetime
import uuid
from boto3.dynamodb.conditions import Key

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME'))
idp_client = boto3.client('cognito-idp')


@app.route('/ping', methods=['GET'])
def ping():
    return ""

@app.route('/item', methods=['PUT'])
def put():
    request_data = request.get_json()
    table.put_item(
        Item={
            'userId': "SYSTEM",
            'itemId': str(uuid.uuid4()),
            'title': request_data['title'],
            'content': request_data['content']
        }
    )
    return ""
    
@app.route('/item', methods=['GET'])
def get():
    return str(table.scan()['Items'])

@app.route('/authenticated-item', methods=['PUT'])
def put_authenticated():
    request_data = request.get_json()
    user = idp_client.get_user(AccessToken=request.headers['authorization'].split(' ')[1])
    table.put_item(
        Item={
            'userId': user['Username'],
            'itemId': str(uuid.uuid4()),
            'title': request_data['title'],
            'content': request_data['content']
        }
    )
    return ""

@app.route('/authenticated-item', methods=['GET'])
def get_authenticated():
    user = idp_client.get_user(AccessToken=request.headers['authorization'].split(' ')[1])
    results = table.query(
        KeyConditionExpression=Key('userId').eq(user['Username'])
    )
    return str(results["Items"])

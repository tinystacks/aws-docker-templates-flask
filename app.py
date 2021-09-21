from flask import Flask
from flask import request
from flask import Response
import boto3
import os
import datetime
import uuid
import json
from boto3.dynamodb.conditions import Key

app = Flask(__name__)
dynamodb_client = None
table = None

def dynamodb_table():
  global dynamodb_client
  global table
  if (dynamodb_client == None):
    dynamodb_client = boto3.resource('dynamodb')
    table = dynamodb_client.Table(os.environ.get('TABLE_NAME', 'TableNameEnvVarNotSet'))
  return table

def cognito_client():
  if (cognito == none):
    cognito = boto3.client('cognito-idp')
  return cognito

local_items = []

@app.route('/ping', methods=['GET'])
def ping():
    return ""

@app.route('/item', methods=['PUT'])
def put():
    request_data = request.get_json()
    print(request_data['title'])
    item = {'title': request_data['title'], 'content': request_data['content']}
    local_items.append(item)
    return make_response("")
    
@app.route('/item', methods=['GET'])
def get():
    return make_response(json.dumps(local_items))

@app.route('/db-item', methods=['PUT'])
def put_db_item():
    request_data = request.get_json()
    dynamodb_table().put_item(
        Item={
            'userId': "SYSTEM",
            'itemId': str(uuid.uuid4()),
            'title': request_data['title'],
            'content': request_data['content']
        }
    )
    return make_response("")
    
@app.route('/db-item', methods=['GET'])
def get_db_items():
    # return boto3.client('dynamodb').list_tables()
    return make_response(str(dynamodb_table().scan()['Items']))

@app.route('/db-item', methods=['DELETE'])
def delete_db_item():
    request_data = request.get_json()
    dynamodb_table().delete_item(
        Key={
            'userId': "SYSTEM",
            'itemId': str(uuid.uuid4()),
        }
    )
    return make_response("")

@app.route('/authenticated-item', methods=['PUT'])
def put_authenticated():
    request_data = request.get_json()
    user = cognito_client.get_user(AccessToken=request.headers['authorization'].split(' ')[1])
    dynamodb_table().put_item(
        Item={
            'userId': user['Username'],
            'itemId': str(uuid.uuid4()),
            'title': request_data['title'],
            'content': request_data['content']
        }
    )
    return make_response("")

@app.route('/authenticated-item', methods=['GET'])
def get_authenticated():
    user = cognito_client.get_user(AccessToken=request.headers['authorization'].split(' ')[1])
    results = dynamodb_table().query(
        KeyConditionExpression=Key('userId').eq(user['Username'])
    )
    return make_response(str(results["Items"]))

def make_response(rv):
    resp = Response(rv)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

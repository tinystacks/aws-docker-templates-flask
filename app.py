from flask import Flask, request, Response, jsonify
import boto3
import os
import datetime
import uuid
import json
from boto3.dynamodb.conditions import Key
from flask_sqlalchemy import SQLAlchemy

# App Initialization
app = Flask(__name__)

app.config.from_pyfile('./config/appconfig.cfg')
CONF = f"postgresql://{app.config['PG_USER']}:{app.config['PG_PASSWORD']}@{app.config['PG_HOST']}:{app.config['PG_PORT']}/{app.config ['PG_DATABASE']}"
app.config['SQLALCHEMY_DATABASE_URI'] = CONF

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'
db = SQLAlchemy(app)

# Model Class for Postgres integration
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.String(200), nullable=False)

    def __init__(self, title, content):
        self.title = title
        self.content = content

# DynamoDB
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

@app.route('/', methods=['GET'])
def get():
    return ""

@app.route('/ping', methods=['GET'])
def ping():
    return ""

@app.route('/postgres-item', methods=['GET'])
def itemget():
    query = '''CREATE TABLE if not exists item(id serial PRIMARY KEY, title VARCHAR (200) UNIQUE NOT NULL, content VARCHAR (200) NOT NULL);'''
    db.engine.execute(query)

    items = []
    for item in db.session.query(Item).all():
        del item.__dict__['_sa_instance_state']
        items.append(item.__dict__)

    return jsonify(items)

@app.route('/postgres-item', methods=['POST'])
def itemadd():
    query = '''CREATE TABLE if not exists item(id serial PRIMARY KEY, title VARCHAR (200) UNIQUE NOT NULL, content VARCHAR (200) NOT NULL);'''
    db.engine.execute(query)
    
    request_data = request.get_json()
    title = request_data["title"]
    content = request_data["content"]
    
    entry = Item(title, content)
    db.session.add(entry)
    db.session.commit()
    
    return jsonify("item created")

@app.route('/postgres-item', methods=['PUT'])
def update_item():
    return "update_item"

@app.route('/postgres-item', methods=['DELETE'])
def delete_item():
    return "delete_item"

@app.route('/item', methods=['PUT'])
def put_item():
    request_data = request.get_json()
    print(request_data['title'])
    item = {'title': request_data['title'], 'content': request_data['content']}
    local_items.append(item)
    return make_response("")
    
@app.route('/item', methods=['GET'])
def get_item():
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

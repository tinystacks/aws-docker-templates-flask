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

# app.config.from_pyfile('./config/appconfig.cfg')

pg_user = os.environ.get("PG_USERNAME")
pg_password = os.environ.get("PG_PASSWORD")
pg_host = os.environ.get("PG_HOST")
pg_port = os.environ.get("PG_PORT")
pg_database = os.environ.get("PG_DATABASE")

CONF = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
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
    return "hello world!"

@app.route('/ping', methods=['GET'])
def ping():
    return "pong"

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

# Get All items
@app.route('/local-item', methods=['GET'])
def get_item():
    return make_response(json.dumps(local_items))

# Create a new item
@app.route('/local-item', methods=['POST'])
def put_item():
    request_data = request.get_json()
    print(request_data['title'])
    item = {'title': request_data['title'], 'content': request_data['content']}
    local_items.append(item)
    return make_response("")
    
@app.route('/dynamodb-item', methods=['PUT'])
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
    
@app.route('/dynamodb-item', methods=['GET'])
def get_db_items():
    return make_response(str(dynamodb_table().scan()['Items']))

@app.route('/dynamodb-item', methods=['DELETE'])
def delete_db_item():
    request_data = request.get_json()
    dynamodb_table().delete_item(
        Key={
            'userId': "SYSTEM",
            'itemId': str(uuid.uuid4()),
        }
    )
    return make_response("")

def make_response(rv):
    resp = Response(rv)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp

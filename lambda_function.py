#!/usr/bin/env python3

# External Imports
import io
import os
import urllib3
import json
import zlib
from base64 import b64decode, b64encode
import boto3
import hashlib
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patcher, xray_recorder
patcher.patch(('requests',))
# Configure the X-Ray recorder to generate segments with our service name
xray_recorder.configure(service='Stinkbait Core')

# Set boto3 clients for various services the lambda function will utilize
ssm = boto3.client('ssm')
s3 = boto3.client('s3')
s3resource = boto3.resource('s3')
ddb = boto3.client('dynamodb')

# Import Flask
from flask import Flask, request, jsonify, render_template, send_file, flash, redirect, url_for, session, logging, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user, decode_cookie
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature, base64_decode
from flask.sessions import TaggedJSONSerializer

app = Flask('stinkbait')
app.secret_key = 'f89j2hf2h09fjf84hf0ehf8h9834fh02hf83fh20fh2r2rjfoiwejfnqcn398hf9u3r'
#app.config['SESSION_COOKIE_NAME'] = 'stinkbait'
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = None
XRayMiddleware(app, xray_recorder)

# Initialize the AWS Lambda Powertools
tracer = Tracer(service="Stinkbait Core")
logger = Logger(service="Stinkbait Core", correlation_id_path=correlation_paths.API_GATEWAY_REST)

# Initialize the Flask Login Manager
login_manager = LoginManager(app)
login_manager.init_app(app)


ddb = boto3.resource('dynamodb')
dynamo = boto3.client('dynamodb')
tables = dynamo.list_tables()

# TODO: This is a hack to get the users table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
for table_name in tables['TableNames']:
    if table_name.endswith('users'):
        users_table = ddb.Table(table_name)
        break
#logger.info(users_table)

# TODO: This is a hack to get the target-orgs table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
for table_name in tables['TableNames']:
    if table_name.endswith('target-orgs'):
        target_orgs_table = ddb.Table(table_name)
        break
#logger.info(target_orgs_table)

# TODO: This is a hack to get the target-subjects table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
for table_name in tables['TableNames']:
    if table_name.endswith('target-subjects'):
        target_subjects_table = ddb.Table(table_name)
        break
#logger.info(target_subjects_table)

# TODO: This is a hack to get the campaigns table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
for table_name in tables['TableNames']:
    if table_name.endswith('campaigns'):
        campaigns_table = ddb.Table(table_name)
        break
#logger.info(campaigns_table)

# TODO: This is a hack to get the implants table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function which means my code outside the handler can't use the stage from the event.
for table_name in tables['TableNames']:
    if table_name.endswith('implants'):
        implants_table = ddb.Table(table_name)
        break
#logger.info(implants_table)

for table_name in tables['TableNames']:
    if table_name.endswith('reports'):
        reports_table = ddb.Table(table_name)
        break
#logger.info(reports_table)

# Define User Class for Flask Login
class User():
    def __init__(self, user_id, username, password_hash, role, **kwargs):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.is_authenticated = False
        self.is_active = False
        self.is_anonymous = True
        self.__dict__.update(kwargs)
        logger.info(f'User Object: {self.__dict__}')

        if self.id is not None:
            logger.info(f'User Object: {self.__dict__}')
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False
            logger.info(f'User Object: {self.__dict__}')

    def __repr__(self):
        logger.info(f'User Object: {self.__dict__}')
        return '<User {}>'.format(self.username)


    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id):
        logger.info(f'User ID: {user_id}')
        try:
            response = users_table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={
                    ':uid': user_id
                }
            )
            logger.info(f'Retrieved User by User ID: {response}')
        except Exception as e:
            logger.error(e)
        if 'Items' not in response:
            logger.info("No user found with that ID")
            return None
        else:
            item = response['Items'][0]
            logger.info(f'User Object Per DynamoDB: {item}')
            return item


def get_user_id():
    if 'user_id' in session:
        logger.info("[User ID found in session]"+session['user_id'])
        return session['user_id']
    else:
        user_cookie = request.cookies.get('session')
        if user_cookie != None:
            logger.info("[User cookie found in request]"+user_cookie)
            try:
                compressed = False
                payload = user_cookie
                if payload.startswith('.'):
                    compressed = True
                    payload = payload[1:]
                data = payload.split(".")[0]
                data = base64_decode(data)
                if compressed:
                    data = zlib.decompress(data)
                final_data = data.decode("utf-8")
                decoded_cookie = json.loads(final_data)
                user_id = decoded_cookie['_user_id']
                return user_id
            except Exception as e:
                logger.info("[Decoding error: are you sure this was a Flask session cookie? {}]".format(e))
                return None
        else:
            logger.info("[No session cookie present in request]")
            return None

# Flask-Login user request loader - checks if the user is logged in on every page load by checking the session cookie and loading the user object from DynamoDB
@login_manager.request_loader
def load_user_from_request(request):
    # Load the user ID from the session cookie if it's present, else retrieve the session cookie from the request and decode it to get the user ID
    user_id = get_user_id()
    logger.info(f'User ID: {user_id}')
    if user_id is None:
        return User(user_id=None, username=None, password_hash=None, role=None, is_authenticated=False, is_active=False, is_anonymous=True)
    else:
        # Retrieve User Object from Database (DynamoDB)
        session_user = User.get(user_id)
        try:
            logger.info(f'User ID: {session_user}')
            return User(user_id=session_user['user_id'], username=session_user['username'], password_hash=session_user['password'], role=session_user['role'], email=session_user['user_email'], address=session_user['address'], city=session_user['city'], state=session_user['state'], zip_code=session_user['zip_code'],country=session_user['country'], organization=session_user['organization'], phone=session_user['phone'], is_authenticated=True, is_active=True, is_anonymous=False)
        except Exception as e:
            logger.error(f'WHY WONT YOU WORK {e}')
            return None

# Internal Imports
from allow import allow
from routes import app, User

#Enter main function
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler()
def lambda_handler(event, context):
    logger.set_correlation_id(context.aws_request_id)
    # Analyze incoming HTTP Request, including path of requested resource.
    http_path = event['path']
    http_query_string_parameters = event['queryStringParameters']
    http_method = event['httpMethod']
    http_headers = event['headers']
    http_body = event['body']
    base_url = '/' + event['requestContext']['stage']

    # Check if the request is coming from an allowed IP address and user agent
    allow_check = allow(event, context)
    #logger.info(allow_check[1])

    # # If the request is not coming from an allowed IP address and user agent, return a 403 Forbidden response
    # if allow_check[0] == True:
    #     pass
    # elif allow_check[0] == False:
    #     return {
    #         'statusCode': 403,
    #         'body': 'Forbidden'
    #     }
    try:
        with app.app_context():
            if http_path == '/':
                http_path = '/index'
            else:
                pass
            # Create a Flask Request Context
            ctx = app.test_request_context(
                base_url="https:"+base_url, 
                path=http_path, 
                method=http_method, 
                headers=http_headers, 
                data=http_body)
            # Push the Flask Request Context
            ctx.push()
            if request.url_rule != None:
                pass
            else:
                raise Exception("The route does not exist.")
            rv = app.preprocess_request()
            if rv != None:
                response = app.make_response(rv)
            else:
                # do the main dispatch
                rv = app.full_dispatch_request()
                rv.direct_passthrough = False
                response = app.make_response(rv)
            # do the teardown, starting with the response headers
            headers = dict(response.headers)
            content_type = headers.get('Content-Type', '')
            # Check headers for content type and if it is an image, encode it as base64
            if content_type.startswith('image/'):
                data = b64encode(response.data)
                return {
                    'headers': { "Content-Type": "image/png" },
                    'statusCode': response.status_code,
                    'body': data.decode('utf-8'),
                    'isBase64Encoded': True
                }
            else:
                return {
                    "statusCode": response.status_code,
                    "body": response.data,
                    "headers": headers
                }
    except Exception as e:
        logger.error("Exception: {}".format(e))
        with app.app_context():
            if http_path == '/':
                http_path = '/index'
            else:
                pass
            ctx = app.test_request_context(base_url=base_url, path=http_path, method=http_method, headers=http_headers, data=http_body)
            ctx.push()
            app.preprocess_request()
            html = render_template('404.html')
        return {
            "statusCode": 404,
            "body": html,
            "headers": {
                'Content-Type': 'text/html',
            }
        }
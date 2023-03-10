#!/usr/bin/env python3

# External Imports
import io
import os
import urllib3
import json
import base64
import boto3
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
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app = Flask('stinkbait')
app.secret_key = 'f89j2hf2h09fjf84hf0ehf8h9834fh02hf83fh20fh2r2rjfoiwejfnqcn398hf9u3r'
app.config['SESSION_COOKIE_NAME'] = 'stinkbait'
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = None
XRayMiddleware(app, xray_recorder)

# Initialize the AWS Lambda Powertools
tracer = Tracer(service="Stinkbait Core")
logger = Logger(service="Stinkbait Core", correlation_id_path=correlation_paths.API_GATEWAY_REST)

# Initialize the Flask Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    logger.info("Loading user: {}".format(user_id))
    return User.get(user_id)

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

# TODO: This is a hack to get the implants table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
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

class User(UserMixin):
    def __init__(self, user_id, username, password_hash, role):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @staticmethod
    def get(user_id):
        response = users_table.get_item(Key={'username': user_id})
        if 'Item' not in response:
            return None
        item = response['Item']
        return User(item['user_id'], item['username'], item['password_hash'], item['role'])

# Internal Imports
from allow import allow
from routes import app, User


# Initialize the serializer with the app's secret key
serializer = URLSafeTimedSerializer(app.secret_key)

#Enter main function
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler()
def lambda_handler(event, context):
    logger.set_correlation_id(context.aws_request_id)
    cookie = event['headers']['Cookie']
    if cookie:
        cookie_value = cookie.split("=", 1)[1]
        # Decode the cookie
        logger.info('Cookie: {}'.format(cookie_value))
        try:
            data = serializer.loads(cookie_value)
            # The data should contain the user ID
            logger.info('Serialized Cookie Data: {}'.format(data))
            user_id = data.get('user_id')
            # Load the user based on the user ID
            logger.info('User ID from "Serializer Load": {}'.format(user_id))
            user = load_user(user_id)
            logger.info('User from "Load User": {}'.format(user))
            # Set the user as the current user
            login_user(user)
            # You can now access the current user with current_user
            logger.info('User is logged in: {}'.format(current_user.username))
        except SignatureExpired:
            # Invalid cookie
            logger.info('Signature valid but expired')
        except BadSignature:
            # Invalid cookie
            logger.info('Invalid cookie signature')
        except Exception as e:
            logger.info('Error: {}'.format(e))
    else:
        # No cookie provided
        logger.info('No cookie provided')
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
            ctx = app.test_request_context(base_url="https:"+base_url, path=http_path, method=http_method, headers=http_headers, data=http_body)
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
            headers = dict(response.headers)
            content_type = headers.get('Content-Type', '')
            # Check headers for content type and if it is an image, encode it as base64
            if content_type.startswith('image/'):
                data = base64.b64encode(response.data)
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
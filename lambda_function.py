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
xray_recorder.configure(service='Stinkbait App')

# Internal Imports
from allow import allow

# Set boto3 clients for various services the lambda function will utilize
ssm = boto3.client('ssm')
s3 = boto3.client('s3')
s3resource = boto3.resource('s3')
ddb = boto3.client('dynamodb')

# Import Flask
from flask import Flask, request, jsonify, render_template, send_file, flash, redirect, url_for, session, logging, send_from_directory
app = Flask('stinkbait', template_folder='templates', static_folder='static')
XRayMiddleware(app, xray_recorder)


# Initialize the AWS Lambda Powertools
tracer = Tracer(service="Stinkbait App")
logger = Logger(service="Stinkbait App", correlation_id_path=correlation_paths.API_GATEWAY_REST)

from routes import app

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
    logger.info(allow_check[1])

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
                    'statusCode': 200,
                    'body': data.decode('utf-8'),
                    'isBase64Encoded': True
                }
            else:
                return {
                    "statusCode": 200,
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
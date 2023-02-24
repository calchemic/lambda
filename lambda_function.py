#!/usr/bin/env python3
import urllib3
import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext


from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patcher, xray_recorder
patcher.patch(('requests',))
# Configure the X-Ray recorder to generate segments with our service name
xray_recorder.configure(service='My First Serverless App')
# Instrument the Flask application


#trigger = APIGatewayRestResolver()


# Import Flask
from flask import Flask, request, jsonify, render_template
app = Flask(__name__)
XRayMiddleware(app, xray_recorder)

# Initialize the AWS Lambda Powertools
tracer = Tracer()
logger = Logger()

# Define Flask routes
@tracer.capture_method
@app.route('/about')
def about():
    tracer.put_annotation(key="about", value="about-page")
    return render_template('about.html')

@tracer.capture_method
@app.route('/index')
def index():
    return render_template('index.html')

@tracer.capture_method
@app.route('/login')
def login():
    return render_template('login.html')

@tracer.capture_method
@app.route('/register')
def register():
    return render_template('register.html')

@tracer.capture_method
@app.route('/404')
def error404():
    return render_template('404.html')

#Uncomment the line below if you want to use the Lambda Powertools Logger or Tracer
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler()
def lambda_handler(event, context):

    # Analyze incoming HTTP Request, including path of requested resource.
    http_path = event['path']
    http_query_string_parameters = event['queryStringParameters']
    http_method = event['httpMethod']
    http_headers = event['headers']
    http_body = event['body']
    base_url = '/' + event['requestContext']['stage']

    # # parse event data for source IP and user agent
    # event_source_ip = event['requestContext']['identity']['sourceIp']
    # event_user_agent = event['requestContext']['identity']['userAgent']

    # # IP Allow List
    # if event_source_ip not in ['71.78.212.171']:
    #     return {
    #         "statusCode": 403,
    #         "body": "Forbidden",
    #         "headers": {
    #             'Content-Type': 'text/html',
    #         }
    #     }
    # else:
    #     pass

    # if event_user_agent not in ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36']:
    #     return {
    #         "statusCode": 403,
    #         "body": "Forbidden",
    #         "headers": {
    #             'Content-Type': 'text/html',
    #         }
    #     }
    
    # Render the requested page
    try:
        logger.info(app.name)
        with app.app_context():
            if http_path == '/':
                http_path = '/index'
            else:
                pass
            ctx = app.test_request_context(base_url=base_url, path=http_path, method=http_method, headers=http_headers, data=http_body)
            ctx.push()
            app.preprocess_request()
            logger.info("Request Context: {}".format(ctx.request.base_url))
            html = render_template(http_path[1:] + '.html')
        return {
            "statusCode": 200,
            "body": html,
            "headers": {
                'Content-Type': 'text/html',
            }
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

if __name__ == "__main__":
    lambda_handler(event, context)
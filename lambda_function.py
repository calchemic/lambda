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
@app.route('/campaigns')
def campaigns():
    tracer.put_annotation(key="campaigns", value="campaigns-page")
    return render_template('campaigns.html')

potential_targets = [
    {
        "id": "240722b44c974973aef89654ff647d5b",
        "name": "John Doe",
        "company": "Acme Inc.",
        "email": "john.doe@acme.com",
        "phone": "+1 (555) 123-4567",
        "ip_address": "127.0.0.1",
        "device_type": "Windows 10 build 1809",
        "mobile_device_type": "Android 10"
    },
    {
        "id": "5ce3b427779c43c59f1610a084c1a55a",
        "name": "Jane Smith",
        "company": "XYZ Corporation",
        "email": "jane.smith@xyzcorp.com",
        "phone": "+1 (555) 234-5678",
        "ip_address": "10.10.10.10",
        "device_type": "MacOS 13.1",
        "mobile_device_type": "iOS 16.1"
    }
]

@tracer.capture_method
@app.route('/targets')
def targets():
    tracer.put_annotation(key="targets", value="targets-page")
    return render_template('targets.html', potential_targets=potential_targets)

potential_implants = [
    {
        "id": 1,
        "target": "John Doe",
        "implant_version": "1.0",
        "os_version": "Windows 10",
        "current_user": "jdoe",
        "av_edr": "Windows Defender",
        "lifetime": "24 hours"
    },
    {
        "id": 2,
        "target": "Jane Smith",
        "implant_version": "1.1",
        "os_version": "macOS Big Sur",
        "current_user": "jsmith",
        "av_edr": "Sophos",
        "lifetime": "48 hours"
    }
]

@tracer.capture_method
@app.route('/implants')
def implants():
    tracer.put_annotation(key="implants", value="implants-page")
    logger.info("Implants Page")
    logger.info(implants)
    return render_template('implants.html', potential_implants=potential_implants)

@tracer.capture_method
@app.route('/index')
def index():
    logger.info("Index Page")
    return render_template('index.html')

@tracer.capture_method
@app.route('/login', methods = ['POST', 'GET'])
def login():
    logger.info("Login Page")
    if request.method == 'POST':
        logger.info(request.form)
        return render_template('404.html')
    elif request.method == 'GET':
        logger.info("GET")
        return render_template('login.html')
    else:
        pass

@tracer.capture_method
@app.route('/register')
def register():
    logger.info("Register Page")
    return render_template('register.html')

@tracer.capture_method
@app.route('/404')
@app.errorhandler(404)
def error404(error):
    logger.info("404 Page")
    return render_template('404.html')

#Uncomment the line below if you want to use the Lambda Powertools Logger or Tracer
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
        with app.app_context():
            if http_path == '/':
                http_path = '/index'
            else:
                pass
            ctx = app.test_request_context(base_url="https:"+base_url, path=http_path, method=http_method, headers=http_headers, data=http_body)
            ctx.push()
            logger.info("Request Context: {}".format(ctx))
            if request.url_rule != None:
                pass
            else:
                raise Exception("The route does not exist.")
            rv = app.preprocess_request()
            if rv != None:
                response = app.make_response(rv)
            else:
                # do the main dispatch
                rv = app.dispatch_request()
                response = app.make_response(rv)

        return {
            "statusCode": 200,
            "body": response.data,
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
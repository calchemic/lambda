#!/usr/bin/env python3
import urllib3
import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

# Initialize the AWS Lambda Powertools
tracer = Tracer()
logger = Logger()
#app = APIGatewayRestResolver()


# Import Flask
from flask import Flask, request, jsonify, render_template
app = Flask(__name__)


# Define Flask routes
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/a')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')


#Uncomment the line below if you want to use the Lambda Powertools Logger
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):

    # Analyze incoming HTTP Request, including path of requested resource.
    http_path = event['path']
    http_query_string_parameters = event['queryStringParameters']
    http_method = event['httpMethod']
    http_headers = event['headers']
    http_body = event['body']

    # Set up the Flask request context

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
        if http_method == 'GET' :
            with app.app_context():
                if http_path == '/':
                    http_path = '/index'
                else:
                    pass
                ctx = app.test_request_context(path=http_path, method=http_method, headers=http_headers, data=http_body)
                ctx.push()
                app.preprocess_request()
                logger.info("Request Context: {}".format(ctx))
                html = render_template(http_path[1:] + '.html')
            return {
                "statusCode": 200,
                "body": html,
                "headers": {
                    'Content-Type': 'text/html',
                }
            }
        else:
            return {
                "statusCode": 404,
                "body": "Not Found",
                "headers": {
                    'Content-Type': 'text/html',
                }
            }
    except Exception as e:
        logger.error("Exception: {}".format(e))
        return {
            "statusCode": 404,
            "body": "Not Found",
            "headers": {
                'Content-Type': 'text/html',
            }
        }

if __name__ == "__main__":
    lambda_handler(event, context)
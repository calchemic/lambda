#!/usr/bin/env python3
import urllib3
import bs4
import json
from bs4 import BeautifulSoup
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

# Import Flask
from flask import Flask, request, jsonify, render_template
app = Flask(__name__)

@app.route('/about')
def about():
    return render_template('about.html')

# Disable the "Not Secure" warning when using HTTPS:
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Dummy event and context for local mocking
# event = {'queryStringParameters':'', 'pathParameters':'', 'headers':'', 'body':'', 'requestContext':{'identity':{'sourceIp':'', 'userAgent':''}}}
# context = {}

# Initialize the AWS Lambda Powertools
tracer = Tracer()
logger = Logger()
#app = APIGatewayRestResolver()

#Uncomment the line below if you want to use the Lambda Powertools Logger
@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    # parse event data for query string parameters, path parameters, headers, body, source IP and user agent
    event_data = event['queryStringParameters']
    path = event['path']
    event_headers = event['headers']
    event_body = event['body']
    event_source_ip = event['requestContext']['identity']['sourceIp']
    event_user_agent = event['requestContext']['identity']['userAgent']
    # log the event data
    logger.info(event_data)
    http_method = event['httpMethod']
    if http_method == 'GET' and path == '/about':
        with app.app_context():
            html = render_template('about.html')
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
    # # create a connection pool
    # http = urllib3.PoolManager()
    # # make a GET request to Google
    # r = http.request('GET', 'https://google.com')
    # # render the response HTML into user browser via API Gateway
    # response = {
    #     "statusCode": 200,
    #     "body": r.data.decode('utf-8'),
    #     "headers": {
    #         'Content-Type': 'text/html',
    #     }
    # }
    
    
    # return response

if __name__ == "__main__":
    lambda_handler(event, context)
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
app = Flask(__name__, static_url_path='/static')
XRayMiddleware(app, xray_recorder)


# Initialize the AWS Lambda Powertools
tracer = Tracer()
logger = Logger()


@app.route('/campaigns/email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        to = request.form['to']
        subject = request.form['subject']
        body = request.form['body']
        attachments = request.files.getlist('attachment')
        # Code to send email goes here
        # ...
        message = 'Template Uploaded!'
        return render_template('campaigns/email_template.html', message=message)
    else:
        return render_template('campaigns/email_template.html')

# Static image file route
@app.route('/static/img/<path:path>')
def send_static(path):
    full_path = os.path.join('static', 'img', path)
    logger.info('Image Path: ' + full_path)
    return send_file(full_path)


# Browser tracking route
@app.route('/browser-info', methods=['POST'])
def handle_browser_info():
    data = request.get_json()
    browser = data.get('browser')
    device = data.get('device')
    canvasHash = data.get('canvasHash')
    nav = data.get('nav')
    # logger.info(browser)
    # logger.info(device)
    # logger.info(canvasHash)
    # logger.info(nav)
    # Process browser and device information here...
    return 'OK'

# Admin Dashboard route
@app.route('/admin/dashboard')
def admin_dashboard():
    #TODO: Return Dashboard of various Administrator configuration options
    # Should include things like managing api keys for non-aws services, registering/managing domains, certificates, and email servers (SMTP)
    pass

# API Key Management Admin Dashboard route
@app.route('/admin/dashboard/api-keys')
def api_key_management():
    #TODO implement methods to add/update and delete API Keys using SSM Parameter store Secure String option to store the keys.
    pass

# ######### POTENTIAL CODE FOR API KEY ROUTES - UNTESTED, BUT ROUGHLY CORRECT ##########
# ######### Define the route for updating the OpenAI API key ###########################
# @app.route('/update_openai_key', methods=['POST'])
# def update_openai_key():
#     # Get the new API key value from the form
#     openai_key = request.form['openai_key']

#     # Store the new API key value in SSM Parameter Store
#     ssm.put_parameter(Name='/api_keys/openai', Value=openai_key, Type='SecureString', Overwrite=True)

#     # Return a message indicating success
#     message = 'OpenAI API key updated successfully.'
#     return render_template('api_keys.html', message=message)

# # Define the route for deleting the OpenAI API key
# @app.route('/delete_openai_key', methods=['GET'])
# def delete_openai_key():
#     # Delete the OpenAI API key from SSM Parameter Store
#     ssm.delete_parameter(Name='/api_keys/openai')

#     # Return a message indicating success
#     message = 'OpenAI API key deleted successfully.'
#     return render_template('api_keys.html', message=message)

# # Define the route for adding the OpenAI API key
# @app.route('/add_openai_key', methods=['POST'])
# def add_openai_key():
#     # Get the new API key value from the form
#     openai_key = request.form['openai_key']

#     # Store the new API key value in SSM Parameter Store
#     ssm.put_parameter(Name='/api_keys/openai', Value=openai_key, Type='SecureString')

#     # Return a message indicating success
#     message = 'OpenAI API key added successfully.'
#     return render_template('api_keys.html', message=message)

# # Define the route for updating the Github API key
# @app.route('/update_github_key', methods=['POST'])
# def update_github_key():
#     # Get the new API key value from the form
#     github_key = request.form['github_key']

#     # Store the new API key value in SSM Parameter Store
#     ssm.put_parameter(Name='/api_keys/github', Value=github_key, Type='SecureString', Overwrite=True)

#     # Return a message indicating success
#     message = 'Github API key updated successfully.'
#     return render_template('api_keys.html', message=message)

# # Define the route for deleting the Github API key
# @app.route('/delete_github_key', methods=['GET'])
# def delete_github_key():
#     # Delete the Github API key from SSM Parameter Store
#     ssm.delete_parameter(Name='/api_keys/github')

#     # Return a message indicating success
#     message = 'Github API key deleted successfully.'
#     return render_template('api_keys.html', message=message)

# # Define the route for adding the Github API key
# @app.route('/add_github_key', methods=['POST'])
# def add_github_key():
#     # Get the new API key value from the form
#     github_key = request.form['github_key']

#     # Store the new API key value in SSM Parameter Store
#     ssm.put_parameter(Name='/api_keys/github', Value=github_key, Type='SecureString')

#     # Return a message indicating success
#     message = 'Github API key added successfully.'
#     return render_template('api_keys.html', message=message)

# # Define the route for displaying the API keys
# @app.route('/api_keys', methods=['GET'])
# def api_keys():
#     # Check whether the OpenAI API key exists in SSM Parameter Store
#     openai_key_exists = False
#     try
# ##################### END UNTESTED CODE FOR API KEY ROUTES #######################
# ##################################################################################
class User:
    def __init__(self, image, name, email, phone, address, city, state, zip_code, country, organizations, campaigns, targets, implants, total_organizations, total_campaigns, total_targets, total_implants):
        self.image = image
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country
        self.organizations = organizations
        self.campaigns = campaigns
        self.targets = targets
        self.implants = implants
        self.total_organizations = total_organizations
        self.total_campaigns = total_campaigns
        self.total_targets = total_targets
        self.total_implants = total_implants

class Organization:
    def __init__(self, name):
        self.name = name

class Campaign:
    def __init__(self, name):
        self.name = name

class Target:
    def __init__(self, name):
        self.name = name

class Implant:
    def __init__(self, name):
        self.name = name

organizations = [
    Organization('ABC Inc.'),
    Organization('XYZ Corp.')
]

campaigns = [
    Campaign('Campaign 1'),
    Campaign('Campaign 2'),
    Campaign('Campaign 3')
]

targets = [
    Target('Target 1'),
    Target('Target 2'),
    Target('Target 3'),
    Target('Target 4')
]

implants = [
    Implant('Implant 1'),
    Implant('Implant 2'),
    Implant('Implant 3')
]

user = User(
    'profile.png',
    'John Doe',
    'john.doe@example.com',
    '123-456-7890',
    '123 Main St.',
    'Anytown',
    'TX',
    '12345',
    'USA',
    organizations,
    campaigns,
    targets,
    implants,
    len(organizations),
    len(campaigns),
    len(targets),
    len(implants)
)

# Stinkbait User Profile Page
@app.route('/profile')
def profile():
    return render_template('/profile/profile.html', user=user)

# Stinkbait User Password Reset Page
@app.route('/profile/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        # Get the email, new password, and confirm new password from the form data
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Verify that the new password and confirm password fields match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('reset_password'))

        # TODO: Perform password reset logic here

        flash('Your password has been reset!', 'success')
        return redirect(url_for('login'))
    elif request.method == 'GET':
        # If the request method is GET, render the password reset form template
        return render_template('profile/password_reset.html')

# Org profile page, needs to be moved under targets
@app.route('/org-profile/<org_id>')
def org_profile(org_id):
    # Retrieve the organization's data from your database using the org_id parameter
    # org_data = get_org_data(org_id)

    # Pass the organization's data to the org-profile.html template
    return render_template('/profile/org-profile.html') #, **org_data)

# Campaign profile page
@tracer.capture_method
@app.route('/campaigns')
def campaigns():
    tracer.put_annotation(key="campaigns", value="campaigns-page")
    return render_template('campaigns.html')

potential_reports = [
    {
        'id': 1,
        'organization': 'ABC Inc.',
        'start_date': '2022-01-01',
        'end_date': '2022-03-31',
        'campaigns': 10,
        'targets': 100,
        'implants': 500,
        'grade': 'A'
    },
    {
        'id': 2,
        'organization': 'XYZ Corp.',
        'start_date': '2022-04-01',
        'end_date': '2022-06-30',
        'campaigns': 5,
        'targets': 50,
        'implants': 250,
        'grade': 'B'
    }
]

# Reports page
@tracer.capture_method
@app.route('/reports')
def reports():
    tracer.put_annotation(key="reports", value="reports-page")
    return render_template('reports.html', potential_reports=potential_reports)

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

# Targets page
@tracer.capture_method
@app.route('/targets')
def targets():
    tracer.put_annotation(key="targets", value="targets-page")
    return render_template('targets.html', potential_targets=potential_targets)

target = {
    'id': 1,
    'name': 'John Smith',
    'company': 'Acme Inc.',
    'email': 'john.smith@acme.com',
    'phone': '555-1234',
    'ip_address': '192.168.0.1',
    'ip_address_2': '127.0.0.1',
    'device_type': 'Windows 10 build 1809',
    'browser_type': 'Chrome 88.0.4324.150',
    'browser_screen_resolution': '1920x1080',
    'browser_language': 'en-US',
    'browser_timezone': 'UTC-8',
    'browser_cookies_enabled': True,
    'browser_local_storage_enabled': True,
    'browser_session_storage_enabled': True,
    'browser_plugins': ['Adobe Acrobat', 'Java', 'Silverlight'],
    'browser_fonts': ['Arial', 'Times New Roman', 'Verdana'],
    'mobile_device_type': 'iOS 14.4 / Safari',
    'mobile_device_browser': 'Safari',
    'mobile_browser_screen_resolution': '1334x750',
    'mobile_browser_language': 'en-US',
    'mobile_browser_timezone': 'UTC-7',
    'mobile_browser_cookies_enabled': True,
    'mobile_browser_local_storage_enabled': True,
    'mobile_browser_session_storage_enabled': True,
    'mobile_browser_plugins': ['Adobe Acrobat', 'Java'],
    'mobile_browser_fonts': ['Helvetica', 'Arial']
}

# Target profile page
@app.route('/targets/<int:id>')
def target_profile(id):
    # Look up the target data from the database based on the ID
    # Render the target profile template with the target data
    return render_template('targets/profile.html', target=target)


potential_implants = [
    {
        "id": 1,
        "target": "John Doe",
        "implant_version": "1.0",
        "os_version": "Windows 10",
        "current_user": "jdoe",
        "av_edr": "Windows Defender",
        "lifetime": "24 hours",
        "first_callback":"2021-10-01 12:00:00",
        "last_seen":"2021-10-01 12:00:00",
        "load_payloads":"none",
        "command_history": "none"
    },
    {
        "id": 2,
        "target": "Jane Smith",
        "implant_version": "1.1",
        "os_version": "macOS Big Sur",
        "current_user": "jsmith",
        "av_edr": "Sophos",
        "lifetime": "48 hours",
        "first_callback":"2021-10-01 12:00:00",
        "last_seen":"2021-10-01 12:00:00",
        "load_payloads":"none",
        "command_history": "none"
    }
]

# Implants Dashboard page
@tracer.capture_method
@app.route('/implants')
def implants():
    tracer.put_annotation(key="implants", value="implants-page")
    logger.info("Implants Page")
    logger.info(implants)
    return render_template('implants.html', potential_implants=potential_implants)

# Index page
@tracer.capture_method
@app.route('/index')
def index():
    logger.info("Index Page")
    return render_template('index.html')

# Downloads page
@tracer.capture_method
@app.route('/downloads')
def downloads():
    logger.info("Downloads Page")
    return render_template('downloads.html')

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
    allow_check = allow(event, context)
    logger.info(allow_check[1])

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
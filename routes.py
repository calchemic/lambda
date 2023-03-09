import os
import uuid
import boto3
import json
import base64
import subprocess
from shlex import quote
from lambda_function import logger, tracer, app
from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session, jsonify
from urllib.parse import unquote
import datetime

#########################################################################################
#################################  User Routes  #########################################
#########################################################################################
ddb = boto3.resource('dynamodb')
dynamo = boto3.client('dynamodb')
tables = dynamo.list_tables()

# TODO: This is a hack to get the users table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
for table_name in tables['TableNames']:
    if table_name.endswith('users'):
        users_table = ddb.Table(table_name)
        break
logger.info(users_table)

# TODO: This is a hack to get the target-orgs table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
for table_name in tables['TableNames']:
    if table_name.endswith('target-orgs'):
        target_orgs_table = ddb.Table(table_name)
        break
logger.info(target_orgs_table)

# TODO: This is a hack to get the target-subjects table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
for table_name in tables['TableNames']:
    if table_name.endswith('target-subjects'):
        target_subjects_table = ddb.Table(table_name)
        break
logger.info(target_subjects_table)

# TODO: This is a hack to get the campaigns table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
for table_name in tables['TableNames']:
    if table_name.endswith('campaigns'):
        campaigns_table = ddb.Table(table_name)
        break
logger.info(campaigns_table)

# TODO: This is a hack to get the implants table name.  Need to find a better way to do this. Maybe use a tag? Needs to be dynamic based on the environment stage - but have to pass that from the lambda handler function.
for table_name in tables['TableNames']:
    if table_name.endswith('implants'):
        implants_table = ddb.Table(table_name)
        break
logger.info(implants_table)

for table_name in tables['TableNames']:
    if table_name.endswith('reports'):
        reports_table = ddb.Table(table_name)
        break
logger.info(reports_table)

# Stinkbait User Profile Page
@app.route('/profile')
def profile():
    return render_template('/profile/profile.html') #, user=user)

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

@app.route('/allow-list', methods=['GET', 'POST'])
def allow_list():
    if request.method == 'POST':
        # # If the form was submitted, retrieve the IP address and User Agent from the form data
        # ip_address = request.form['ip_address']
        # user_agent = request.form['user_agent']

        # # Add the IP address and User Agent to the allowed list
        # allowed.append((ip_address, user_agent))
        pass
    # Render the template with the list of allowed IP addresses and User Agents, and the form
    return render_template('profile/allow_list.html') #, allowed=allowed)

@tracer.capture_method
@app.route('/register', methods = ['POST', 'GET'])
def register():
    logger.info("Register Page")
    if request.method == 'POST':
        # Request form returned as immutablemultidict - convert to regular dictionary using to_dict()
        data = request.form.to_dict()
        # Get the first key in the dictionary, which is the form response body
        b64message = list(data.keys())[0]
        # Decode the base64 encoded message
        try:
            # Try decoding the message with standard padding
            message = unquote(base64.b64decode(b64message + '==').decode('utf-8'))
        except Exception as e:
            # If standard padding doesn't work, try decoding the message with no padding
            logger.info(e)
            message = unquote(base64.b64decode(b64message.replace('-', '+').replace('_', '/') + '==').decode('utf-8'))
        logger.info(message)
        message_dict = {}
        for item in message.split('&'):
            key, value = item.split('=')
            message_dict[key] = value.replace('+', ' ')
        try:
            response = users_table.put_item(
                Item={
                    'username': message_dict['username'],
                    'user_email': message_dict['email'],
                    'first_name': message_dict['first_name'],
                    'last_name': message_dict['last_name'],
                    'password': message_dict['password'],
                    'confirm_password': message_dict['confirm_password'],
                    'organization': message_dict['organization'],
                    'phone': message_dict['phone'],
                    'address': message_dict['address'],
                    'city': message_dict['city'],
                    'state': message_dict['state'],
                    'zip_code': message_dict['zip_code'],
                    'country': message_dict['country'],
                    'role': message_dict['role']
                }
            )
            logger.info(response)
            return render_template('login.html')
        except Exception as e:
            logger.info(e)
            return render_template('404.html')
    elif request.method == 'GET':
        return render_template('register.html')


@tracer.capture_method
@app.route('/login', methods = ['POST', 'GET'])
def login():
    logger.info("Login Page")
    if request.method == 'POST':
        return render_template('404.html')
    elif request.method == 'GET':
        logger.info("GET")
        return render_template('login.html')
    else:
        pass

#########################################################################################
#################################  End User Routes  #####################################
#########################################################################################

#########################################################################################
###################################  Targets Routes  ####################################
#########################################################################################

# Create a new organization
@app.route('/targets/orgs/new', methods=['GET', 'POST'])
def target_org_new():
    if request.method == 'POST':
        # If the form was submitted, retrieve the organization name from the form data
        # Request form returned as immutablemultidict - convert to regular dictionary using to_dict()
        data = request.form.to_dict()
        # Get the first key in the dictionary, which is the form response body
        b64message = list(data.keys())[0]
        # Decode the base64 encoded message
        try:
    # Try decoding the message with standard padding
            message = unquote(base64.b64decode(b64message + '==').decode('utf-8'))
        except Exception as e:
            # If standard padding doesn't work, try decoding the message with no padding
            logger.info(e)
            message = unquote(base64.b64decode(b64message.replace('-', '+').replace('_', '/')).decode('utf-8'))
        logger.info(message)
        message_dict = {}
        for item in message.split('&'):
            key, value = item.split('=')
            message_dict[key] = value.replace('+', ' ')
        logger.info(message_dict)
        try:
            response = target_orgs_table.put_item(
                Item={
                    'org_id': str(uuid.uuid4().hex),
                    'org_name': message_dict['org_name'],
                    'org_logo': message_dict['org_logo'],
                    'email_pattern': message_dict['email_pattern'],
                    'hq_address': message_dict['hq_address'],
                    'city': message_dict['city'],
                    'state': message_dict['state'],
                    'zip_code': message_dict['zip'],
                    'country': message_dict['country'],
                    'subsidiaries': message_dict['subsidiaries'],
                    'domains': message_dict['domains'],
                    'targets': message_dict['targets'],
                    'campaigns': message_dict['campaigns'],
                    'implants': message_dict['implants'],
                    'created_datetime': str(datetime.datetime.utcnow())
                }
            )
            logger.info(response)
            return redirect(url_for('target_orgs_dashboard'), code=302)
        except Exception as e:
            logger.info(e)
            return render_template('404.html')
    else:
        return render_template('targets/new_org.html')

# Target Organizations Dashboard
@app.route('/targets/orgs')
def target_orgs_dashboard():
    response = target_orgs_table.scan()
    logger.info(response)
    orgs = []
    for item in response['Items']:
        org = {}
        org['org_id'] = item.get('org_id', 'Unknown')
        org['org_name'] = unquote(item.get('org_name', 'Unknown'))
        org['domains'] = unquote(item.get('domains', 'Unknown'))
        org['email_pattern'] = unquote(item.get('email_pattern', 'Unknown'))
        org['hq_address'] = unquote(item.get('hq_address', 'Unknown'))
        org['city'] = unquote(item.get('city', 'Unknown'))
        org['state'] = unquote(item.get('state', 'Unknown'))
        org['zip'] = unquote(item.get('zip_code', 'Unknown'))
        org['country'] = unquote(item.get('country', 'Unknown'))
        org['phone'] = unquote(item.get('phone_number', 'Unknown'))
        org['subsidiaries'] = unquote(item.get('subsidiaries', 'Unknown'))
        org['targets'] = unquote(item.get('targets', 'Unknown'))
        org['campaigns'] = unquote(item.get('campaigns', 'Unknown'))
        org['implants'] = unquote(item.get('implants', 'Unknown'))
        org['public_co'] = unquote(item.get('public_company', 'Unknown'))
        orgs.append(org)
    return render_template('targets/orgs_dashboard.html', orgs=orgs)

# Org Profile page for a specific organization
@app.route('/targets/orgs/<org_id>')
def org_profile(org_id):
    # Retrieve the organization's data from your database using the org_id parameter
    # org_data = get_org_data(org_id)

    # Pass the organization's data to the org-profile.html template
    return render_template('/targets/org-profile.html') #, **org_data)


# New target page
@app.route('/targets/subjects/new', methods=['GET', 'POST'])
def target_subject_new():
    if request.method == 'POST':
        # If the form was submitted, retrieve the subject name from the form data
        # Request form returned as immutablemultidict - convert to regular dictionary using to_dict()
        data = request.form.to_dict()
        # Get the first key in the dictionary, which is the form response body
        b64message = list(data.keys())[0]
        # Decode the base64 encoded message
        try:
    # Try decoding the message with standard padding
            message = unquote(base64.b64decode(b64message + '==').decode('utf-8'))
        except Exception as e:
            # If standard padding doesn't work, try decoding the message with no padding
            logger.info(e)
            message = unquote(base64.b64decode(b64message.replace('-', '+').replace('_', '/')).decode('utf-8'))
        logger.info(message)
        message_dict = {}
        for item in message.split('&'):
            key, value = item.split('=')
            message_dict[key] = value.replace('+', ' ')
        logger.info(message_dict)
        try:
            response = target_subjects_table.put_item(
                Item={
                    'id': str(uuid.uuid4().hex),
                    'name': message_dict['name'],
                    'target_email': message_dict['email'],
                    'organization': message_dict['organization'],
                    'title': message_dict['title'],
                    'department': message_dict['department'],
                    'phone': message_dict['phone'],
                    'created_datetime': str(datetime.datetime.utcnow())
                }
            )
            logger.info(response)
            return redirect(url_for('target_subjects_dashboard'), code=302)
        except Exception as e:
            logger.info(e)
            return render_template('404.html')
    else:
        return render_template('targets/new_subject.html')


# Targets page
@tracer.capture_method
@app.route('/targets/subjects/dashboard')
def target_subjects_dashboard():
    tracer.put_annotation(key="targets", value="targets-page")
    response = target_subjects_table.scan()
    logger.info(response)
    subjects = []
    for item in response['Items']:
        subject = {}
        subject['id'] = item.get('id', 'Unknown')
        subject['name'] = unquote(item.get('name', 'Unknown'))
        subject['organization'] = unquote(item.get('organization', 'Unknown'))
        subject['email'] = unquote(item.get('email', 'Unknown'))
        subject['phone'] = unquote(item.get('phone', 'Unknown'))
        subject['ip_address'] = unquote(item.get('ip_address', 'Unknown'))
        subject['device_type'] = unquote(item.get('device_type', 'Unknown'))
        subject['mobile_device_type'] = unquote(item.get('mobile_device_type', 'Unknown'))
        subjects.append(subject)
    return render_template('targets/subject_dashboard.html', subjects=subjects)

# Target profile page
@app.route('/targets/subjects/<int:id>')
def target_profile(id):
    # Look up the target data from the database based on the ID
    # Render the target profile template with the target data
    return render_template('targets/subject_profile.html') #, target=target)


#########################################################################################
###############################  End Targets Routes  ####################################
#########################################################################################


#########################################################################################
###################################  Admin Routes  ######################################
#########################################################################################
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


#########################################################################################
###############################  End Admin Routes  ######################################
#########################################################################################


#########################################################################################
#################################  Campaigns Routes  ####################################
#########################################################################################



# Campaign profile page
@tracer.capture_method
@app.route('/campaigns')
def campaigns():
    tracer.put_annotation(key="campaigns", value="campaigns-page")
    return render_template('campaigns.html')

@app.route('/campaigns/email/template', methods=['GET', 'POST'])
def email_template():
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
    
@app.route('/campaigns/email/preview', methods=['GET', 'POST'])
def preview_email():
    #TODO: Implement preview email functionality
    pass

@app.route('/campaigns/email/send', methods=['GET', 'POST'])
def send_email():
    pass

@app.route('/targets/dns-cert-manager', methods=['GET', 'POST'])
def dns_cert_manager():
    # if request.method == 'POST':
    #     if 'register_dns' in request.form:
    #         dns_domain = request.form['dns_domain']
    #         dns_domains.add(dns_domain)
    #         message = f'DNS domain "{dns_domain}" registered successfully!'
    #     elif 'import_dns' in request.form:
    #         dns_domains.update(request.form['dns_domains'].split())
    #         message = 'DNS domains imported successfully!'
    #     elif 'create_certificate' in request.form:
    #         domains = request.form['domains'].split()
    #         certificate_name = request.form['certificate_name']
    #         certificates[certificate_name] = domains
    #         message = f'TLS certificate "{certificate_name}" created successfully!'
    #     elif 'delete_certificate' in request.form:
    #         certificate_name = request.form['certificate_name']
    #         del certificates[certificate_name]
    #         message = f'TLS certificate "{certificate_name}" deleted successfully!'
    # else:
    #     message = None
    return render_template('targets/dns_cert_manager.html') #, dns_domains=dns_domains, certificates=certificates, message=message)

#########################################################################################
###############################  End Campaigns Routes  ##################################
#########################################################################################

#########################################################################################
#################################  Implants Routes  #####################################
#########################################################################################
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

# Implant Shell Routes
@app.route('/implants/shell-session')
def shell_session():
    return render_template('implants/shell_session.html')

# Implant Shell Send Command Route
# TODO: Currently - the JS in shell_session.html is sending the command and data to this route; but something isn't correct. Needs troubleshooting.
@app.route('/implants/shell-session/send-command', methods=['GET', 'POST'])
def send_command():
    try:
        # Set predefined commands here, only commands in this list can be executed
        if (request.form['command'] == "dmesg"):
            stdout, stderr  = subprocess.Popen(["dmesg"], stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
        elif (request.form['command'] == "ls"):
            stdout, stderr  = subprocess.Popen(["ls", "-la", quote(request.form['data']) if request.form['data'] else './' ], stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
        else:
            stdout, stderr = (b"command not found", b"")
        data = {}
        data['command'] = request.form['command']
        data['data'] = request.form['data']
        data['result'] = stdout.decode('utf-8') + "\n" + stderr.decode('utf-8')
        return (json.dumps(data))
    except Exception as e: print(e)
#########################################################################################
################################  End Implants Routes  ##################################
#########################################################################################


#########################################################################################
###############################  Back Office Routes  ####################################
#########################################################################################
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
@app.route('/backoffice/reports')
def backoffice_reports():
    tracer.put_annotation(key="reports", value="reports-page")
    return render_template('backoffice/reports.html', potential_reports=potential_reports)

@app.route('/backoffice/documentation')
def backoffice_documentation():
    return render_template('backoffice/documentation.html')

#########################################################################################
#############################  End Back Office Routes  ##################################
#########################################################################################



#########################################################################################
###############################  General App Routes  ####################################
#########################################################################################
# Browser tracking route
@app.route('/browser-info', methods=['POST'])
def browser_info():
    data = request.get_json()
    browser = data.get('browser')
    device = data.get('device')
    canvasHash = data.get('canvasHash')
    nav = data.get('nav')
    # logger.info(browser)
    # logger.info(device)
    # logger.info(canvasHash)
    # logger.info(nav)
    # # Process browser and device information here...
    return 'OK'

# Static image file route
@app.route('/static/img/<path:path>')
def send_static(path):
    full_path = os.path.join('static', 'img', path)
    return send_file(full_path)

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
@app.route('/404')
@app.errorhandler(404)
def error404(error):
    logger.info("404 Page")
    return render_template('404.html')
#########################################################################################
#############################  End General App Routes  ##################################
#########################################################################################
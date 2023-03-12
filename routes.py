import os
import boto3
import json
import base64
import subprocess
import datetime
import hashlib
from ksuid import ksuid
from shlex import quote
from lambda_function import logger, tracer, app, login_manager, UserMixin, User, login_user, login_required, logout_user, current_user, ddb, dynamo, ses, users_table, target_orgs_table, target_subjects_table, campaigns_table, implants_table, reports_table
from flask import render_template, request, send_file, redirect, url_for, flash, session, jsonify, send_from_directory
from urllib.parse import unquote



#########################################################################################
#################################  User Routes  #########################################
#########################################################################################
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(app.root_path, 'static'),'img/favicon.ico', mimetype='image/vnd.microsoft.icon')

# Stinkbait User Profile Page
@app.route('/profile')
@login_required
def profile():
    logger.info("Profile Page")
    # Get the user's username from the session
    try:
        logger.info(current_user)
        return render_template('profile/profile.html', user=current_user)
    except Exception as e:
        logger.info(e)
        return render_template('404.html')

# Stinkbait User Password Reset Page
@app.route('/profile/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        # Get the email, new password, and confirm new password from the form data
        username = request.form['username']
        current_password = request.form['current_password']
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

@app.route('/register', methods=['POST', 'GET'])
def register():
    logger.info("Register Page")
    if request.method == 'POST':
        try:
            # Request form returned as immutablemultidict - convert to regular dictionary using to_dict()
            data = request.form.to_dict()
            # Get the first key in the dictionary, which is the form response body
            b64message = list(data.keys())[0]
        except Exception as e:
            logger.info(f'Error retrieving form response:{e}')
            return render_template('404.html')
            # Decode the base64 encoded message
        try:
            message = unquote(base64.b64decode(b64message + '==').decode('utf-8'))
        except Exception as e:
            # If standard padding doesn't work, try decoding the message with no padding
            logger.info(e)
            message = unquote(base64.b64decode(b64message.replace('-', '+').replace('_', '/') + '==').decode('utf-8'))
        message_dict = {}
        for item in message.split('&'):
            key, value = item.split('=')
            message_dict[key] = value.replace('+', ' ')
        try:
            # Hash the password
            password = message_dict['password']
            hash_object = hashlib.sha256(password.encode())
            password_hash = hash_object.hexdigest()
            item = {
                'user_id': str(ksuid()),
                'username': message_dict['username'],
                'email': message_dict['email'],
                'first_name': message_dict['first_name'],
                'last_name': message_dict['last_name'],
                'password': password_hash,
                'created_at': str(datetime.datetime.now()),
                'status': 'active'
            }
            if message_dict.get('organization'):
                item['organization'] = message_dict['organization']
            if message_dict.get('phone'):
                item['phone'] = message_dict['phone']
            if message_dict.get('address'):
                item['address'] = message_dict['address']
            if message_dict.get('city'):
                item['city'] = message_dict['city']
            if message_dict.get('state'):
                item['state'] = message_dict['state']
            if message_dict.get('zip_code'):
                item['zip_code'] = message_dict['zip_code']
            if message_dict.get('country'):
                item['country'] = message_dict['country']
            if message_dict.get('role'):
                item['role'] = message_dict['role']
            else:
                item['role'] = 'user'
            response = users_table.put_item(Item=item)
            logger.info(response)
            return redirect(url_for('login'))
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
        data = request.form.to_dict()
        b64message = list(data.keys())[0]
        try:
            message = unquote(base64.b64decode(b64message + '==').decode('utf-8'))
        except Exception as e:
            logger.info(e)
            message = unquote(base64.b64decode(b64message.replace('-', '+').replace('_', '/')).decode('utf-8'))
        message_dict = {}
        for item in message.split('&'):
            key, value = item.split('=')
            message_dict[key] = value.replace('+', ' ')

        username = message_dict['username']
        password = message_dict['password']
        # Get the user from the database based on provided username
        response = users_table.query(
            IndexName='UsernameIndex',
            KeyConditionExpression='username = :uname',
            ExpressionAttributeValues={
                ':uname': username
            }
        )
        user_data = response.get('Items', None)
        if not user_data:
            return render_template('login.html', message="Invalid username or password")
        try:
            hash_object = hashlib.sha256(password.encode())
            password_hash = hash_object.hexdigest()
            user_item = user_data[0]
            pw_hash = user_item['password']
        except Exception as e:
            logger.exception(e)
            return render_template('404.html')
        if password_hash != pw_hash:
            return render_template('login.html', message="Invalid username or password")
        session_user = user_data[0]
        logger.info(f'Logging in User: {session_user}')
        try:
            session_user = User(user_id=session_user['user_id'], username=session_user['username'], password_hash=session_user['password'], role=session_user['role'], email=session_user['email'], address=session_user['address'], city=session_user['city'], state=session_user['state'], zip_code=session_user['zip_code'],country=session_user['country'], organization=session_user['organization'], phone=session_user['phone'], is_authenticated=True, is_active=True, is_anonymous=False)
        except Exception as e:
            logger.exception(e)
            return render_template('404.html')
        logger.info(f'User: {session_user}')
        try:
            logged_in = login_user(user=session_user)
        except Exception as e:
            logger.exception(e)
            return render_template('404.html')
        logger.info(f'Logged in: {logged_in}')
        next = request.args.get('next')
        return redirect(next or url_for('profile'))
    elif request.method == 'GET':
        logger.info('You made a GET request to the Login page')
        try:
            if current_user.id != None:
                logger.info(f'Current User')
                #return redirect(url_for('profile'))
                return redirect(url_for('profile'))
        except Exception as e:
            logger.info(e)
            return redirect(url_for('profile'))
        else:
            logger.info("GET")
            return render_template('login.html')
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
        data = request.form.to_dict()
        b64message = list(data.keys())[0]
        try:
            message = unquote(base64.b64decode(b64message + '==').decode('utf-8'))
        except Exception as e:
            logger.info(e)
            message = unquote(base64.b64decode(b64message.replace('-', '+').replace('_', '/')).decode('utf-8'))
        message_dict = {}
        for item in message.split('&'):
            key, value = item.split('=')
            message_dict[key] = value.replace('+', ' ')
        try:
            item = {
                'org_id': str(ksuid()),
                'created_datetime': str(datetime.datetime.utcnow())
            }
            if message_dict.get('org_name'):
                item['org_name'] = message_dict['org_name']
            if message_dict.get('org_logo'):
                item['org_logo'] = message_dict['org_logo']
            if message_dict.get('email_pattern'):
                item['email_pattern'] = message_dict['email_pattern']
            if message_dict.get('hq_address'):
                item['hq_address'] = message_dict['hq_address']
            if message_dict.get('city'):
                item['city'] = message_dict['city']
            if message_dict.get('state'):
                item['state'] = message_dict['state']
            if message_dict.get('zip'):
                item['zip_code'] = message_dict['zip']
            if message_dict.get('country'):
                item['country'] = message_dict['country']
            if message_dict.get('subsidiaries'):
                item['subsidiaries'] = message_dict['subsidiaries']
            if message_dict.get('domain0'):
                item['domain0'] = message_dict['domain0']
            if message_dict.get('domain1'):
                item['domain1'] = message_dict['domain1']
            if message_dict.get('targets'):
                item['targets'] = message_dict['targets']
            if message_dict.get('campaigns'):
                item['campaigns'] = message_dict['campaigns']
            if message_dict.get('implants'):
                item['implants'] = message_dict['implants']
            response = target_orgs_table.put_item(Item=item)
            return redirect(url_for('target_orgs_dashboard'))
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
        org['domain0'] = unquote(item.get('domain0', 'Unknown'))
        org['domain1'] = unquote(item.get('domain1', 'Unknown'))
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
        data = request.form.to_dict()
        b64message = list(data.keys())[0]
        try:
            message = unquote(base64.b64decode(b64message + '==').decode('utf-8'))
        except Exception as e:
            logger.info(e)
            message = unquote(base64.b64decode(b64message.replace('-', '+').replace('_', '/')).decode('utf-8'))
        message_dict = {}
        for item in message.split('&'):
            key, value = item.split('=')
            message_dict[key] = value.replace('+', ' ')
        try:
            item = {
                'id': str(ksuid()),
                'created_datetime': str(datetime.datetime.utcnow())
            }
            if message_dict.get('first_name'):
                item['first_name'] = message_dict['first_name']
            if message_dict.get('last_name'):
                item['last_name'] = message_dict['last_name']
            if message_dict.get('email'):
                item['target_email'] = message_dict['email']
            if message_dict.get('organization'):
                item['organization'] = message_dict['organization']
            if message_dict.get('title'):
                item['title'] = message_dict['title']
            if message_dict.get('department'):
                item['department'] = message_dict['department']
            if message_dict.get('phone'):
                item['phone'] = message_dict['phone']
            response = target_subjects_table.put_item(Item=item)
            return redirect(url_for('target_subjects_dashboard'))
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
        subject['first_name'] = unquote(item.get('first_name', 'Unknown'))
        subject['last_name'] = unquote(item.get('last_name', 'Unknown'))
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

# New Campaign route
@app.route('/campaigns/new-campaign', methods=['GET', 'POST'])
def campaign_new_campaign():
    if request.method == 'POST':
        data = request.form.to_dict()
        b64message = list(data.keys())[0]
        try:
            message = unquote(base64.b64decode(b64message + '==').decode('utf-8'))
        except Exception as e:
            logger.info(e)
            message = unquote(base64.b64decode(b64message.replace('-', '+').replace('_', '/')).decode('utf-8'))
        message_dict = {}
        for item in message.split('&'):
            key, value = item.split('=')
            message_dict[key] = value.replace('+', ' ')
        try:
            item = {
                'campaign_id': str(ksuid()),
                'created_datetime': str(datetime.datetime.utcnow())
            }
            if message_dict.get('campaign_name'):
                item['campaign_name'] = message_dict['campaign_name']
            if message_dict.get('org_name'):
                item['org_name'] = message_dict['org_name']
            if message_dict.get('targets'):
                item['targets'] = message_dict['targets']
            if message_dict.get('subject'):
                item['subject'] = message_dict['subject']
            if message_dict.get('email_template'):
                item['message'] = message_dict['message']
            if message_dict.get('landing_page_url'):
                item['landing_page_url'] = message_dict['landing_page_url']
            if message_dict.get('landing_page_hosting_provider'):
                item['landing_page_hosting_provider'] = message_dict['landing_page_hosting_provider']
            response = campaigns_table.put_item(Item=item)
            return redirect(url_for('campaigns_dashboard'), code=302)
        except Exception as e:
            logger.info(e)
            return render_template('404.html')
    else:
        return render_template('campaigns/new_campaign.html')
    
# Campaign Dashboard route
@app.route('/campaigns/dashboard')
def campaign_campaigns_dashboard():
    response = campaigns_table.scan()
    campaigns = []
    for item in response['Items']:
        campaign = {}
        campaign['campaign_id'] = item.get('campaign_id', 'Unknown')
        campaign['campaign_name'] = item.get('campaign_name', 'Unknown')
        campaign['org_name'] = item.get('org_name', 'Unknown')
        campaign['targets'] = item.get('targets', 'Unknown')
        campaign['subject'] = item.get('subject', 'Unknown')
        campaign['message'] = item.get('message', 'Unknown')
        campaign['landing_page_url'] = item.get('landing_page_url', 'N/A')
        campaign['landing_page_hosting_provider'] = item.get('landing_page_hosting_provider', 'N/A')
        campaign['created_datetime'] = item.get('created_datetime', 'Unknown')
        campaigns.append(campaign)
    return render_template('campaigns/campaigns_dashboard.html', campaigns=campaigns)


@app.route('/campaigns/email/new_email_template', methods=['GET', 'POST'])
def campaign_email_new_email_template():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        text = request.form['text']
        html = request.form['html']
        # Create the email template using the ses client
        try:
            template = {
                'TemplateName': name,
                'SubjectPart': subject,
                'TextPart': text,
                'HtmlPart': html
            }
            ses.create_template(Template=template)
            # Redirect to a success page or display a success message
            return 'Template created successfully!'
        except Exception as e:
            # Handle any errors that occur during template creation
            logger.info(e)
            return 'Failed to create template'
    else:
        return render_template('campaigns/email/new_email_template.html')
    
@app.route('/campaigns/email/preview', methods=['GET', 'POST'])
def campaign_email_preview_email():
    #TODO: Implement preview email functionality
    pass

@app.route('/campaigns/email/send', methods=['GET', 'POST'])
def campaign_email_send_email():
    pass

@app.route('/targets/dns-cert-manager', methods=['GET', 'POST'])
def campaign_dns_cert_manager():
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
@login_required
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

# Set the CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
#########################################################################################
#############################  End General App Routes  ##################################
#########################################################################################
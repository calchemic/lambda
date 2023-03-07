import os
from lambda_function import logger, tracer, app
from flask import Flask, render_template, request, send_file

#########################################################################################
###################################  Targets Routes  ####################################
#########################################################################################
# Org Profile page for a specific organization
@app.route('/targets/orgs/<org_id>')
def org_profile(org_id):
    # Retrieve the organization's data from your database using the org_id parameter
    # org_data = get_org_data(org_id)

    # Pass the organization's data to the org-profile.html template
    return render_template('/targets/org-profile.html') #, **org_data)

# Create a new organization
@app.route('/targets/orgs/new', methods=['GET', 'POST'])
def new_org_profile():
    if request.method == 'POST':
        pass
    #     db = client['your_database_name']
    #     org_id = uuid.uuid4().hex
    #     org_name = request.form['org_name']
    #     org_logo = request.form.get('org_logo', '')
    #     domains = request.form.getlist('domains')
    #     email_pattern = request.form.get('email_pattern', '')
    #     hq_address = request.form.get('hq_address', '')
    #     city = request.form.get('city', '')
    #     state = request.form.get('state', '')
    #     zip_code = request.form.get('zip', '')
    #     country = request.form.get('country', '')
    #     phone = request.form.get('phone', '')
    #     subsidiaries = request.form.getlist('subsidiaries')
    #     targets = request.form.getlist('targets')
    #     campaigns = request.form.getlist('campaigns')
    #     implants = request.form.getlist('implants')
    #     public_co = request.form.get('public_co', 'false')
    #     organization = {
    #         'org_id': org_id,
    #         'org_name': org_name,
    #         'org_logo': org_logo,
    #         'domains': domains,
    #         'email_pattern': email_pattern,
    #         'hq_address': hq_address,
    #         'city': city,
    #         'state': state,
    #         'zip': zip_code,
    #         'country': country,
    #         'phone': phone,
    #         'subsidiaries': subsidiaries,
    #         'targets': targets,
    #         'campaigns': campaigns,
    #         'implants': implants,
    #         'public_co': public_co
    #     }
    #     db['your_collection_name'].insert_one(organization)
    #     return redirect(url_for('index'))
    else:
        return render_template('targets/org_profile_new.html')

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
@app.route('/targets/subjects/dashboard')
def target_subjects_dashboard():
    tracer.put_annotation(key="targets", value="targets-page")
    return render_template('targets/subject_dashboard.html', potential_targets=potential_targets)

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
@app.route('/targets/subjects/<int:id>')
def target_profile(id):
    # Look up the target data from the database based on the ID
    # Render the target profile template with the target data
    return render_template('targets/subject_profile.html', target=target)

#########################################################################################
###############################  End Targets Routes  ####################################
#########################################################################################

#########################################################################################
#################################  User Routes  #########################################
#########################################################################################

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

#########################################################################################
#################################  End User Routes  #####################################
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

@app.route('/campaigns/dns-cert-manager', methods=['GET', 'POST'])
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
    return render_template('campaigns/dns_cert_manager.html') #, dns_domains=dns_domains, certificates=certificates, message=message)

#########################################################################################
###############################  End Campaigns Routes  ##################################
#########################################################################################

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


#########################################################################################
###############################  General App Routes  ####################################
#########################################################################################


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

#########################################################################################
#############################  End General App Routes  ##################################
#########################################################################################
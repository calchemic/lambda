from flask import Flask, request, jsonify, render_template
# See if it works commented out. app = Flask(__name__)

# Define Home Routes
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')

# Define Implant Routes
@app.route('/implants')
def implants():
    return render_template('implants.html')

# Define Campaign Routes
@app.route('/campaigns')
def campaigns():
    return render_template('campaigns.html')

# Define Target Routes
@app.route('/targets')
def targets():
    return render_template('targets.html')

# Define Report Routes
@app.route('/reports')
def reports():
    return render_template('reports.html')

# Define Settings Routes
@app.route('/settings')
def settings():
    return render_template('settings.html')

# Define Admin Routes
@app.route('/admin')
def admin():
    return render_template('admin.html')

# Define API Routes
@app.route('/api')
def api():
    return render_template('api.html')

# Define Documentation Routes
@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

# Define 404 Routes
@app.route('/404')
def error404():
    return render_template('404.html')

#Define other error handlers

# Define Redirection Routes
@app.route('/redirect')
def redirect():
    return render_template('redirect.html')

# Define User Management Routes
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot.html')

@app.route('/reset')
def reset():
    return render_template('reset.html')
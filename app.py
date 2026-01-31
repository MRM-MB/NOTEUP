# Standard library imports.
from dotenv import load_dotenv
import os
import re
import json
import random
import hashlib
import secrets
from datetime import datetime

# Third-party imports.
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
from oauthlib.oauth2 import WebApplicationClient

# Local application/library specific imports.
from company_info.company_logos import company_logos
from company_info.company_banner import company_banner
from company_info.circular_logos import circular_logos
from company_info.company_link import company_link
from company_info.company_categories import company_categories

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files
app.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)  # Create your own secret key and store it in the .env file
if not os.getenv('SECRET_KEY'):
    print("Warning: SECRET_KEY not set. Using a temporary key; sessions will reset on restart.")
app.config['SESSION_TYPE'] = 'filesystem'
bcrypt = Bcrypt(app)

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

# To use the Google Auth feature, you need to create a .env file in your project directory.
# In the .env file, store your Google Client ID and Google Client Secret like this:
# GOOGLE_CLIENT_ID=your-google-client-id
# GOOGLE_CLIENT_SECRET=your-google-client-secret

# Use the variables in your Flask app configuration or elsewhere
app.config['GOOGLE_CLIENT_ID'] = google_client_id
app.config['GOOGLE_CLIENT_SECRET'] = google_client_secret
app.config['GOOGLE_OAUTH_ENABLED'] = bool(google_client_id and google_client_secret)

# Configuration for Google OAuth
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
REDIRECT_URI = "https://noteup-qej0.onrender.com/login/google/callback"

client = WebApplicationClient(google_client_id)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

class NoteUp:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.users_file = 'users.json'
        self.load_users()
        self.current_user = None
    
        # Method to get a random profile picture URL
    def get_random_profile_picture(self):
        profile_picture_urls = [
            "https://c4.wallpaperflare.com/wallpaper/881/28/979/mac-os-x-os-x-big-sur-hd-wallpaper-preview.jpg",
            "https://wallpapers.com/images/hd/4k-vector-snowy-landscape-p7u7m7qyxich2h31.jpg",
            "https://wallpaper.forfun.com/fetch/ad/adff63b34d681e274fb48249cfa8fd7e.jpeg?h=900&r=0.5",
            "https://wallpaper.forfun.com/fetch/f3/f3cfe96584a23cdc40ba8366b80a93c2.jpeg?h=900&r=0.5",
            "https://wallpaper.forfun.com/fetch/dc/dc194c8f1c0c1cb9e7128273d0bb6949.jpeg?h=900&r=0.5",
            "https://c.wallhere.com/photos/6e/77/Hannah_Jones_digital_art_painting_colorful_landscape_lake_trees_women-1575653.jpg!d",
            "https://img.freepik.com/premium-vector/beauty-purple-nature-view-night-wallpaper-artwork-illustration_605379-21267.jpg",
            "https://c4.wallpaperflare.com/wallpaper/160/360/842/drawing-building-landscape-hd-wallpaper-preview.jpg",
            "https://c4.wallpaperflare.com/wallpaper/443/887/746/duelyst-anton-fadeev-concept-art-artwork-wallpaper-preview.jpg",
            "https://c4.wallpaperflare.com/wallpaper/480/496/23/macos-blue-bra-big-sur-hd-wallpaper-preview.jpg",
            "https://static.vecteezy.com/system/resources/previews/006/757/142/original/deep-blue-ocean-background-free-vector.jpg",
            "https://i.pinimg.com/736x/cd/31/03/cd31035c8a07cf6d99ab62472d98f73e.jpg",
            "https://wallpaperaccess.com/full/8658254.jpg",
            "https://www.shutterstock.com/image-vector/enchanting-anime-landscape-mistcovered-mountain-600nw-2301778699.jpg",
            "https://img.freepik.com/premium-vector/project-132_648489-106.jpg"
        ]
        return random.choice(profile_picture_urls)
    
    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as file:
                self.users = json.load(file)
        else:
            self.users = {}

    def save_users(self):
        with open(self.users_file, 'w') as file:
            json.dump(self.users, file, indent=4)

    def encrypt_password(self, password):
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password, hashed):
        return bcrypt.check_password_hash(hashed, password)

    def encrypt_data(self, data):
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, data):
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            return self.cipher.decrypt(data).decode('utf-8')
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return None

    def check_password_strength(self, password):
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if not re.search(r'[A-Z]', password):
            return "Password must contain at least one uppercase letter."
        if not re.search(r'[a-z]', password):
            return "Password must contain at least one lowercase letter."
        if not re.search(r'\d', password):
            return "Password must contain at least one digit."
        if not re.search(r'[@$!%*?&#]', password):
            return "Password must contain at least one special character."
        return True
    
    def register(self, username, password, security_question1, security_answer1):
        if username in self.users:
            return "Username already exists."
        password_strength = self.check_password_strength(password)
        if password_strength is not True:
            return password_strength
        encrypted_password = self.encrypt_password(password)
        encrypted_security_answer1 = self.encrypt_password(security_answer1)

        profile_picture_url = self.get_random_profile_picture()

        self.users[username] = {
            'password': encrypted_password,
            'security_question1': security_question1,
            'security_answer1': encrypted_security_answer1,
            'accounts': [],
            'profile_picture_url': profile_picture_url
        }
        self.save_users()
        return "Registration successful!"

    def login(self, username, password):
        if username in self.users and self.check_password(password, self.users[username]['password']):
            self.current_user = username
            session['username'] = username  # Set session here
            return "Login successful!"
        return "Invalid username or password."
    
    def logout(self):
        self.current_user = None
        session.pop('username', None)  # Clear session here
        return "Logged out successfully."

    def get_current_user(self):
        if 'username' in session:
            self.current_user = session['username']
            return self.current_user
        return None
    
    def timepass(self):
        self.current_user = None
        session.pop('username', None)
        return "Logged out due to inactivity."
    
    def bye_user(self):
        self.current_user = None
        session.pop('username', None)
        return "🫡 Logged out and account deleted"

    def add_account(self, username, account):
        self.users[username]['accounts'].insert(0, account)
        self.save_users()

    def update_account(self, username, account_index, updated_account):
        self.users[username]['accounts'].pop(account_index)
        self.users[username]['accounts'].insert(0, updated_account)
        self.save_users()

    def delete_user_account(self, username):
        if username in self.users:
            del self.users[username]
            self.save_users()
            return "Account deleted successfully."
        else:
            return "Invalid confirmation text."
    
noteup = NoteUp()

def flash_message(message):
    if 'success' in message.lower():
        flash(message, 'success')
    elif 'error' in message.lower() or 'invalid' in message.lower():
        flash(message, 'danger')
    elif 'warning' in message.lower():
        flash(message, 'warning')
    else:
        flash(message, 'info')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scripts/<path:filename>')
def serve_scripts(filename):
    return send_from_directory('scripts', filename)

@app.route('/check_username', methods=['POST'])
def check_username():
    username = request.form['username']
    if username in noteup.users:
        return json.dumps({'available': False})
    else:
        return json.dumps({'available': True})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        security_question1 = request.form['security_question1']
        security_answer1 = request.form['security_answer1']
        message = noteup.register(username, password, security_question1, security_answer1)
        flash_message(message)
        if message == "Registration successful!":
            return redirect(url_for('login'))
    return render_template('register.html', google_oauth_enabled=app.config['GOOGLE_OAUTH_ENABLED'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        message = noteup.login(username, password)
        flash_message(message)
        if message == "Login successful!":
            session['username'] = username  # Ensure session is set here
            return redirect(url_for('dashboard'))
    return render_template('login.html', google_oauth_enabled=app.config['GOOGLE_OAUTH_ENABLED'])
    
@app.route('/logout')
def logout():
    session.clear()
    message = noteup.logout()
    flash_message(message)
    return redirect(url_for('index'))

@app.route('/timepass')
def timepass():
    session.clear()
    message = noteup.timepass()
    flash_message(message)
    return redirect(url_for('index'))

# Deletion confirmation for NoteUp account
@app.route('/bye_user')
def bye_user():
    session.clear()
    message = noteup.bye_user()
    flash_message(message)
    return redirect(url_for('index'))

@app.route("/login/google")
def google_login():
    if not app.config['GOOGLE_OAUTH_ENABLED']:
        flash("Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env.", "warning")
        return redirect(url_for('login'))
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"],
        prompt="select_account" # Parameter to select account
    )
    return redirect(request_uri)

@app.route("/login/google/callback")
def google_callback():
    if not app.config['GOOGLE_OAUTH_ENABLED']:
        flash("Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env.", "warning")
        return redirect(url_for('login'))
    code = request.args.get("code")

    # Handle case where user cancels the verification
    if not code:
        flash("Verification canceled", "danger")
        return redirect(url_for('index'))

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(google_client_id, google_client_secret),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    userinfo = userinfo_response.json()

    if userinfo.get("email_verified"):
        unique_id = userinfo["sub"]
        users_email = userinfo["email"]
        picture = userinfo["picture"]
        users_name = userinfo["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    session['username'] = users_name
    noteup.current_user = users_name

    # Check if the user already exists
    if users_name not in noteup.users:
        # If user does not exist, create a new entry with a random profile picture
        profile_picture_url = noteup.get_random_profile_picture()
        noteup.users[users_name] = {
            'accounts': [],
            'profile_picture_url': profile_picture_url
        }
        noteup.save_users()
    else:
        # Retrieve the stored profile picture URL
        profile_picture_url = noteup.users[users_name].get('profile_picture_url')

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    if username in noteup.users:
        accounts = noteup.users[username]['accounts']
        profile_picture_url = noteup.users[username].get('profile_picture_url')
    else:
        accounts = []
        profile_picture_url = ""

    return render_template('dashboard.html', 
                           accounts=accounts, 
                           company_logos=company_logos,
                           company_categories=company_categories,
                           profile_picture_url=profile_picture_url)

@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        account_name = request.form['account_name']
        account_user = request.form['account_user']
        email = request.form['email']
        account_password = noteup.encrypt_data(request.form['account_password'])
        year_of_creation = request.form['year_of_creation']
        description = request.form['description']
        account = {
            'name': account_name,
            'username': account_user,
            'email': email,
            'password': account_password,
            'year_of_creation': year_of_creation,
            'description': description
        }
        noteup.add_account(session['username'], account)
        flash_message("Account added successfully!")
        return redirect(url_for('dashboard'))
    return render_template('add_account.html')

@app.route('/update_account/<int:account_index>', methods=['GET', 'POST'])
def update_account(account_index):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    accounts = noteup.users[username]['accounts']
    if request.method == 'POST':
        account_name = request.form['account_name']
        account_user = request.form['account_user']
        email = request.form['email']
        account_password = request.form['account_password']
        if account_password:
            account_password = noteup.encrypt_data(account_password)
        else:
            account_password = accounts[account_index]['password']
        year_of_creation = request.form['year_of_creation']
        description = request.form['description']
        updated_account = {
            'name': account_name,
            'username': account_user,
            'email': email,
            'password': account_password,
            'year_of_creation': year_of_creation,
            'description': description
        }
        # Remove the old company account
        old_account = accounts.pop(account_index)
        # Add the updated account to the top of the list
        accounts.insert(0, updated_account)
        noteup.save_users()
        flash_message("Account updated successfully!")
        return redirect(url_for('dashboard'))
    account = accounts[account_index]
    account['password'] = noteup.decrypt_data(account['password'])
    return render_template('update_account.html', account=account, account_index=account_index)

# Custom Jinja2 filter
@app.template_filter('capitalize_full')
def capitalize_full(name):
    # List of company names that should remain fully capitalized
    "HOSTINGER",
    "PROTON",
    "HOSTINGER",
    "NETFLIX",
    "NETFLIX",
    exceptions = ["CNN", "BBC", "BBVA", "ATT", "CNBC", "DELL", "HSBC", "ICICI", "UPS", "KPMG", "TATA", "SDU", "KTH"]
    
    if name.upper() in exceptions:
        return name.upper()
    
    # Split the name into parts
    name_parts = name.split()
    
    # Capitalize each part
    capitalized_parts = [part.capitalize() for part in name_parts]
    
    # Join the parts back into a single string
    capitalized_name = ' '.join(capitalized_parts)
    
    return capitalized_name


@app.template_filter('regex_replace')
def regex_replace(s, find, replace):
    return re.sub(find, replace, s)

@app.route('/user_account')
def user_account():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    num_accounts = len(noteup.users[username]['accounts'])

    # Check if the user has an assigned profile picture URL
    if 'profile_picture_url' in noteup.users[username]:
        profile_picture_url = noteup.users[username]['profile_picture_url']
    else:
        # If no assigned profile picture URL, generate a new random one and assign it
        profile_picture_url = noteup.get_random_profile_picture()
        noteup.users[username]['profile_picture_url'] = profile_picture_url
        noteup.save_users()

    # Function to get the day with the appropriate suffix
    now = datetime.now()
    def long_date(day):
        if 11 <= day <= 13:
            return f"{day}ᵗʰ"
        elif day % 10 == 1:
            return f"{day}ˢᵗ"
        elif day % 10 == 2:
            return f"{day}ⁿᵈ"
        elif day % 10 == 3:
            return f"{day}ʳᵈ"
        else:
            return f"{day}ᵗʰ"
    long_date = now.strftime("%B ") + long_date(now.day) + now.strftime(", %Y")  # Current date long format (Desktop)
    short_date = datetime.now().strftime("%d/%m/%Y")  # Current date short format (Mobile)
    
    return render_template('user_account.html', 
                           num_accounts=num_accounts, 
                           long_date=long_date, 
                           short_date=short_date,
                           profile_picture_url=profile_picture_url)

@app.route('/view_account/<int:account_index>')
def view_account(account_index):
    if 'username' not in session:
        flash("Please log in to view account details.", "danger")
        return redirect(url_for('login'))

    username = session['username']
    user_accounts = noteup.users.get(username, {}).get('accounts', [])
    
    # Check if the account_index is within range
    if not (0 <= account_index < len(user_accounts)):
        flash("Account not found.", "danger")
        return redirect(url_for('dashboard'))

    account = user_accounts[account_index]
    
    # Create a deep copy of the account for display purposes
    account_display = account.copy()

    # Decrypt the password for display
    decrypted_password = noteup.decrypt_data(account['password'])
    account_display['password'] = decrypted_password if decrypted_password else 'None'  # Set "None" for empty password
    default_banner_url = 'https://wallpapercave.com/wp/wp8944358.jpg'
    
    return render_template('view_account.html', 
                           account=account_display, 
                           account_index=account_index, 
                           company_banner=company_banner, 
                           default_banner_url=default_banner_url, 
                           circular_logos=circular_logos, 
                           company_link=company_link)

@app.route('/delete_account/<int:account_index>', methods=['GET', 'POST'])
def delete_account(account_index):
    if 'username' not in session:
        return redirect(url_for('login'))
    del noteup.users[session['username']]['accounts'][account_index]
    noteup.save_users()
    flash_message("Account deleted successfully!")
    return redirect(url_for('dashboard'))

@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        confirmation_text = request.form['confirmation_text']
        if confirmation_text == "Delete my account":
            username = session['username']
            message = noteup.delete_user_account(username)
            flash_message(message)
            if message == "Account deleted successfully.":
                return redirect(url_for('bye_user'))
        else:
            flash_message("Invalid confirmation text.")
    return render_template('delete_user.html')

@app.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        username = request.form['username']
        if username in noteup.users:
            return redirect(url_for('security_questions', username=username))
        flash_message("Username not found.")
    return render_template('recover_password.html')

@app.route('/security_questions', methods=['GET', 'POST'])
def security_questions():
    username = request.args.get('username')
    if not username or username not in noteup.users:
        flash_message("Invalid username.")
        return redirect(url_for('recover_password'))
    
    user = noteup.users[username]
    question1 = user['security_question1']
    print(f"DEBUG: question1={question1}")  # Debugging line
    
    if request.method == 'POST':
        answer1 = request.form['security_answer1']
        if noteup.check_password(answer1, user['security_answer1']):
            return redirect(url_for('reset_password', username=username))
        flash_message("Incorrect security answer.")
        return redirect(url_for('security_questions', username=username))
    
    return render_template('security_questions.html', username=username, question1=question1)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    username = request.args.get('username')
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        password_strength = noteup.check_password_strength(new_password)
        if password_strength is not True:
            flash_message(password_strength)
            return redirect(url_for('reset_password', username=username))
        encrypted_password = noteup.encrypt_password(new_password)
        noteup.users[username]['password'] = encrypted_password
        noteup.save_users()
        flash_message("Success! You can now log in with your new password!")
        return redirect(url_for('login'))
    return render_template('reset_password.html', username=username)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == "__main__":
    app.run(debug=True)

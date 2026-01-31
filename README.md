# NoteUp 📒
**NoteUp** is a Flask-based account manager with registration, login, account storage, Google OAuth, and inactivity logout.

![NoteUp Logo](assets/noteup.png)

## Features
- User registration and login
- Add, update, and delete accounts
- Password recovery via security questions
- Google OAuth
- Auto-logout after inactivity
 
![NoteUp Dashboard](assets/noteup_dashboard.webp)


## ✅ Two ways to try MAT
1) 🧪 Live Demo (Render)
Try the hosted demo here: [https://noteup-qej0.onrender.com/](https://noteup-qej0.onrender.com/)

Note: This demo uses ephemeral storage. Data resets on restarts, so links may stop working.

2) 💻 Run locally (LAN)
Run the app on your own network so files persist with MySQL and sharing works within your LAN.

## Quick Start
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Set up `.env` with Google Client ID and Secret
4. Run: `python app.py`
5. Open: `http://127.0.0.1:5000`

## Folder Structure
```plaintext
NOTEUP_WEB/
│
├── company_info/
│   ├── company_logos.py
│   ├── company_banner.py
│   ├── circular_logos.py
│   ├── company_link.py
│   ├── company_categories.py
│
├── scripts/
│   ├── background.js
│   ├── company-config.js
│   ├── inactivity.js
│   ├── view.js
│
├── static/
├── templates/
│
├── .env
├── .gitignore
├── app.py
├── requirements.txt
```

# Adding Company Brands ➕
To add more companies to NoteUp, you need to update the following files:
1. **Company Info**: Modify all Python files in the [company_info/](company_info/) folder.
2. **Scripts**: Update [scripts/company-config.js](scripts/company-config.js) in the [scripts/](scripts/) folder.
3. **App Configuration**: If you want a company name to appear in all capital letters (like BBC, CNN, or UPS), modify the [app.py](app.py) file in the `@app.template_filter('capitalize_full')` section.

```python
@app.template_filter('capitalize_full')
def capitalize_full(name):
		# List of company names that should remain fully capitalized
		exceptions = ["CNN", "BBC", "BBVA", "ATT", "CNBC", "DELL", "HSBC", "ICICI", "UPS", "KPMG", "TATA", "SDU", "KTH"]
		...
```

## Customization 🎨
You can customize NoteUp by:
- **Changing Profile Pictures**: Update the URLs in the `get_random_profile_picture` method in the `NoteUp` class.
- **UI Enhancements**: Modify HTML files in the [templates/](templates/) folder and CSS/JS files in the [static/](static/) folder.

## Security Precautions 🔒

To ensure the security of user data, NoteUp implements several key precautions:

- **Password Encryption**: Instead of using SHA256 for password hashing, NoteUp uses `bcrypt`, a robust and secure method for hashing passwords. This enhances security by making it more difficult for attackers to crack passwords using brute force methods.

	```python
	def encrypt_password(self, password):
			return bcrypt.generate_password_hash(password).decode('utf-8')
  
	def check_password(self, password, hashed):
			return bcrypt.check_password_hash(hashed, password)
	```

- **Automatic Logout**: As an additional security measure, the app automatically logs out users after one minute of inactivity. This function helps prevent unauthorized access if a user leaves their session unattended. You can review the implementation of this feature in `inactivity.js` located in the [scripts/](scripts/) folder.

	```javascript
	// inactivity.js
	let inactivityTime = function () {
		let time;
		// Automatically log out the user after 1 min of inactivity to enhance app security
		let maxInactivityTime = 1 * 60 * 1000; // 1 minute in milliseconds

		function logout() {
				window.location.href = "/timepass";
		}

		function resetTimer() {
				clearTimeout(time);
				time = setTimeout(logout, maxInactivityTime);
		}
	```

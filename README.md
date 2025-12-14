---

# NoteUp 📒

<p align="center">
  <img src="assets/noteup.png" alt="NoteUp Logo" width="200">
</p>

Welcome to **NoteUp**! This application is designed to help you manage your accounts efficiently and securely. Below is a detailed description of the app and its features.

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Usage](#usage)
4. [Demo and Secure Deployment](#demo-and-secure-deployment)
5. [Folder Structure](#folder-structure)
6. [Adding New Accounts](#adding-new-accounts)
7. [Customization](#customization)
8. [Detailed Comments](#detailed-comments)
9. [Security Precautions](#security-precautions)
10. [Questions](#questions)

## Introduction 📝
**NoteUp** is a secure account management application built with Flask. It allows users to register, log in, and manage their accounts. The app supports Google OAuth for easy and secure login and includes detailed comments to help understand the functionality.

![NoteUp Dashboard](assets/noteup_dashboard.webp)

## Features ✨
- **User Registration and Login**: Secure user registration and login with password encryption.
- **Account Management**: Add, update, and delete accounts.
- **Profile Pictures**: Random profile picture assignment for new users.
- **Password Recovery**: Recover passwords using security questions.
- **Google OAuth**: Log in with Google account.
- **Session Management**: Auto-logout after inactivity.

## Usage 🚀
To use the app, follow these steps:
1. **Clone the repository**: `git clone <repository_url>`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Set up environment variables**: Create a `.env` file with your Google Client ID and Secret.
4. **Run the app**: `python app.py`
5. **Access the app**: Open your browser and navigate to `http://127.0.0.1:5000`

## Demo and Secure Deployment 🌐
You can try a demo of NoteUp by visiting [this link](https://noteup-qej0.onrender.com).

For enhanced security, especially if you plan to enter important information, it is highly recommended to download the files and deploy the app locally or using a secure Flask deployment service such as Render.com or Heroku. This approach allows you to host a private version of your app, avoiding the need to share it with others. Note that this app is a concept and should not be deployed for general use, as important information may be at risk of exposure despite the security measures implemented, such as password and data encryption. Hosting the app locally or on your own server without sharing it is the best way to ensure your data remains secure.

Feel free to reach out if you have any questions or need assistance. You can contact me at mbmanishweb@gmail.com.

## Folder Structure 📂
Here's an overview of the project's folder structure:

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

## Adding Company Brands ➕
To add more companies to NoteUp, you need to update the following files:
1. **Company Info**: Modify all Python files in the `company_info` folder.
2. **Scripts**: Update `company-config.js` in the `scripts` folder.
3. **App Configuration**: If you want a company name to appear in all capital letters (like BBC, CNN, or UPS), modify the `app.py` file in the `@app.template_filter('capitalize_full')` section.

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
- **UI Enhancements**: Modify HTML files in the `templates` folder and CSS/JS files in the `static` folder.

## Detailed Comments 🖋️
The code contains detailed comments explaining the functionality of the app and its multiple features. These comments are aimed to help developers understand the application with ease.

## Security Precautions 🔒

To ensure the security of user data, NoteUp implements several key precautions:

- **Password Encryption**: Instead of using SHA256 for password hashing, NoteUp uses `bcrypt`, a robust and secure method for hashing passwords. This enhances security by making it more difficult for attackers to crack passwords using brute force methods.

  ```python
  def encrypt_password(self, password):
      return bcrypt.generate_password_hash(password).decode('utf-8')
  
  def check_password(self, password, hashed):
      return bcrypt.check_password_hash(hashed, password)
  ```

- **Automatic Logout**: As an additional security measure, the app automatically logs out users after one minute of inactivity. This function helps prevent unauthorized access if a user leaves their session unattended. You can review the implementation of this feature in `inactivity.js` located in the `scripts` folder.

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
  
## Questions ❓

For any inquiries regarding the app's functionality or features, please do not hesitate to contact me at mbmanishweb@gmail.com.

**Disclaimer:**
This code and application are provided "as-is" without any warranties or guarantees. The code may not be claimed as proprietary; any use or reference must acknowledge the author as the intellectual owner. This application is intended solely for personal use and may not be sold, redistributed, or used for commercial purposes.

---

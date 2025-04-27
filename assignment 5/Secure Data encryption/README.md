# Secure Data Encryption System

A Streamlit-based application for securely storing and retrieving encrypted data.

## Features

- Multi-user authentication system with secure login
- Store data with a unique passkey
- Decrypt data by providing the correct passkey
- Persistent data storage using JSON files
- Security mechanism with lockout after multiple failed attempts
- Modern, responsive UI with improved user experience
- Manage and organize your encrypted data with labels

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

Run the application with:
```
streamlit run secure_encryption_app.py
```

## How to Use

1. **Login**: Use the following demo accounts:
   - Username: admin, Password: admin123
   - Username: user1, Password: password1

2. **Home Page**: View general information about the application

3. **Store Data**: 
   - Give your data a descriptive label
   - Enter your sensitive data
   - Create and confirm a passkey
   - Your data will be encrypted and stored securely

4. **Retrieve Data**:
   - Enter the encrypted text
   - Provide the passkey
   - After 3 failed attempts, you'll be locked out for 30 seconds

5. **My Stored Data**:
   - View all your encrypted data entries
   - Decrypt individual entries with their passkeys
   - Manage and delete entries as needed

6. **Logout**: Securely end your session

## Security Notes

- Data is persistently stored in an encrypted JSON file
- Passkeys are hashed using SHA-256
- Data is encrypted using Fernet symmetric encryption
- The system includes a time-based lockout feature after multiple failed attempts
- All user interactions are secured with proper authentication 
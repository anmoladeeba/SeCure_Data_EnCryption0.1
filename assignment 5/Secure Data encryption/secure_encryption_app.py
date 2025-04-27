import streamlit as st
import hashlib
from cryptography.fernet import Fernet
import time
import json
import os
import base64
import io
from PIL import Image
import numpy as np
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# App configuration and environment variables
DATA_FILE = os.getenv('SECURE_APP_DATA_FILE', 'encrypted_data.json')
MAX_FILE_SIZE = int(os.getenv('SECURE_APP_MAX_FILE_SIZE', 200 * 1024 * 1024))  # 200MB default
SESSION_TIMEOUT = int(os.getenv('SECURE_APP_SESSION_TIMEOUT', 30 * 60))  # 30 minutes default
LOCKOUT_DURATION = int(os.getenv('SECURE_APP_LOCKOUT_DURATION', 30))  # 30 seconds default

# App configuration and styling
st.set_page_config(
    page_title="Secure Data Encryption System",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the app
st.markdown("""
<style>
    /* Logo Styles */
    .logo-container {
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    .logo-text {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        font-family: 'Arial', sans-serif;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 0;
        padding: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .logo-subtitle {
        color: #666;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* Footer Styles */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(90deg, rgba(78,205,196,0.1), rgba(255,107,107,0.1));
        padding: 1rem;
        text-align: center;
        font-size: 0.9rem;
        color: #666;
        border-top: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
    }
    .footer span {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* Main container styling */
    .main-header {
        font-size: 2.5rem;
        color: #4FB0FF;
        text-align: center;
        font-weight: 500;
        margin-bottom: 1.5rem;
        text-shadow: 0 0 10px rgba(79, 176, 255, 0.5);
    }
    
    /* Shield icon and styling */
    .shield-icon {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .shield-icon img {
        width: 120px;
        height: 120px;
        filter: drop-shadow(0 0 15px rgba(79, 176, 255, 0.7));
    }
    
    /* Panel styling */
    .panel {
        background-color: rgba(13, 25, 42, 0.7);
        border: 1px solid rgba(79, 176, 255, 0.3);
        border-radius: 10px;
        padding: 2rem;
        margin-bottom: 1rem;
        box-shadow: 0 0 20px rgba(79, 176, 255, 0.2);
        backdrop-filter: blur(5px);
    }
    
    /* Subheader styling */
    .subheader {
        font-size: 1.5rem;
        color: #4FB0FF;
        margin-bottom: 1.5rem;
        font-weight: 400;
        text-shadow: 0 0 10px rgba(79, 176, 255, 0.3);
    }
    
    /* Message styling */
    .success-msg {
        padding: 1rem;
        background-color: rgba(0, 128, 0, 0.2);
        border-left: 5px solid #00FF00;
        margin-bottom: 1rem;
        color: #00FF00;
        border-radius: 5px;
    }
    
    .error-msg {
        padding: 1rem;
        background-color: rgba(255, 0, 0, 0.2);
        border-left: 5px solid #FF0000;
        margin-bottom: 1rem;
        color: #FF0000;
        border-radius: 5px;
    }
    
    .info-box {
        padding: 1.5rem;
        background-color: rgba(79, 176, 255, 0.1);
        border-left: 5px solid #4FB0FF;
        margin: 1rem 0;
        border-radius: 5px;
        color: #FFFFFF;
    }
    
    /* Input field styling */
    .stTextInput > div > div {
        background-color: rgba(30, 45, 70, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(79, 176, 255, 0.3) !important;
        border-radius: 5px !important;
        padding: 0.5rem !important;
    }
    
    .stTextInput > div > div > input {
        color: white !important;
    }
    
    .stTextArea > div > div {
        background-color: rgba(30, 45, 70, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(79, 176, 255, 0.3) !important;
        border-radius: 5px !important;
    }
    
    .stTextArea > div > div > textarea {
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #0D47A1, #2196F3) !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        box-shadow: 0 0 10px rgba(33, 150, 243, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #1565C0, #42A5F5) !important;
        box-shadow: 0 0 15px rgba(33, 150, 243, 0.7) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-163ttbj, .css-10oheav {
        background-color: rgba(13, 25, 42, 0.8) !important;
    }
    
    .css-pkbazv {
        color: white !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(79, 176, 255, 0.1) !important;
        border-radius: 5px !important;
        color: white !important;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(30, 45, 70, 0.6) !important;
        border-radius: 5px !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(30, 45, 70, 0.6) !important;
        border-radius: 5px 5px 0 0;
        color: white;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(79, 176, 255, 0.2) !important;
        border-bottom: 2px solid #4FB0FF !important;
    }
    
    /* Code display */
    .stCodeBlock {
        background-color: rgba(30, 45, 70, 0.8) !important;
    }
    
    /* Global text color */
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, .stSelectbox label, .stTextInput label, .stTextArea label {
        color: white !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: rgba(30, 45, 70, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(79, 176, 255, 0.3) !important;
    }
    
    .stSelectbox > div > div > div {
        color: white !important;
    }
    
    /* Glowing connection dots */
    .connection-dots {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        z-index: -1;
        opacity: 0.3;
    }
    
    /* Login button pulse effect */
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(79, 176, 255, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(79, 176, 255, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(79, 176, 255, 0);
        }
    }
    
    .pulse-button {
        animation: pulse 2s infinite;
    }

    /* Thin login container */
    .thin-container {
        max-width: 400px !important;
        margin: 0 auto;
        padding: 2rem;
        background-color: rgba(13, 25, 42, 0.7);
        border: 1px solid rgba(79, 176, 255, 0.3);
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(79, 176, 255, 0.2);
    }

    /* Top right button */
    .top-right {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }

    /* Change password form */
    .change-password-form {
        background-color: rgba(13, 25, 42, 0.9);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(79, 176, 255, 0.3);
        margin-top: 1rem;
    }

    /* Divider */
    .divider {
        margin: 1rem 0;
        border-top: 1px solid rgba(79, 176, 255, 0.2);
    }

    /* Small text */
    .small-text {
        font-size: 0.8rem;
        color: #aaa;
        text-align: center;
        margin: 0.5rem 0;
    }

    /* Card hover effect */
    .data-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(79, 176, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    /* Button hover effects */
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(79, 176, 255, 0.4);
    }
    
    /* Modal backdrop */
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.8);
        z-index: 1000;
    }
    
    /* Modal content */
    .modal-content {
        max-width: 500px;
        margin: 2rem auto;
        background-color: rgba(13, 25, 42, 0.95);
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid rgba(79, 176, 255, 0.3);
    }
</style>

<!-- Logo -->
<div class="logo-container">
    <h1 class="logo-text">AnmolAdeeba</h1>
    <p class="logo-subtitle">Secure Data Encryption System</p>
</div>

<!-- Footer -->
<div class="footer">
    Prepared with ❤️ by <span>AnmolAdeeba</span> | © 2024
</div>
""", unsafe_allow_html=True)

# Shield icon HTML (base64 encoded)
shield_icon = '''
<div class="shield-icon">
    <svg width="120" height="120" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M256 0L472 83.2V208C472 338.8 379.6 460.4 256 512C132.4 460.4 40 338.8 40 208V83.2L256 0Z" fill="rgba(13, 25, 42, 0.6)" stroke="#4FB0FF" stroke-width="10"/>
        <path d="M256 128L256 320" stroke="#4FB0FF" stroke-width="30" stroke-linecap="round"/>
        <circle cx="256" cy="368" r="25" fill="#4FB0FF"/>
    </svg>
</div>
'''

# Session state initialization with error handling
def initialize_session_state():
    try:
        if 'init_complete' not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.stored_data = {}
            st.session_state.failed_attempts = 0
            st.session_state.lockout_time = 0
            st.session_state.last_activity = time.time()
            st.session_state.key = Fernet.generate_key()
            st.session_state.cipher = Fernet(st.session_state.key)
            st.session_state.user_accounts = {
                "admin": hashlib.sha256("admin123".encode()).hexdigest(),
                "user1": hashlib.sha256("password1".encode()).hexdigest()
            }
            st.session_state.init_complete = True
            logger.info("Session state initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing session state: {str(e)}")
        st.error("Error initializing application. Please refresh the page.")

# Call initialization
initialize_session_state()

# Add session timeout check
def check_session_timeout():
    if st.session_state.authenticated:
        current_time = time.time()
        if current_time - st.session_state.last_activity > SESSION_TIMEOUT:
            logger.info(f"Session timeout for user: {st.session_state.username}")
            logout()
            st.warning("⚠️ Your session has expired. Please log in again.")
            st.rerun()
        st.session_state.last_activity = current_time

# Update save_data function with better error handling and backup
def save_data():
    try:
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{DATA_FILE}.{timestamp}.backup"
        
        if os.path.exists(DATA_FILE):
            os.replace(DATA_FILE, backup_file)
            logger.info(f"Created backup: {backup_file}")
        
        # Save new data
        with open(DATA_FILE, "w") as f:
            json.dump(st.session_state.stored_data, f, indent=2)
        logger.info("Data saved successfully")
        
        # Keep only last 5 backups
        backups = sorted([f for f in os.listdir() if f.startswith(DATA_FILE) and f.endswith('.backup')])
        for old_backup in backups[:-5]:
            os.remove(old_backup)
            logger.info(f"Removed old backup: {old_backup}")
            
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        # Restore from backup if available
        if os.path.exists(backup_file):
            os.replace(backup_file, DATA_FILE)
            logger.info("Restored from backup after save error")
        raise

# Update load_data function with better error handling
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                st.session_state.stored_data = data
                logger.info("Data loaded successfully")
        else:
            logger.info("No existing data file found")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding data file: {str(e)}")
        st.error("Error loading data: Corrupted data file")
        # Try to restore from latest backup
        backups = sorted([f for f in os.listdir() if f.startswith(DATA_FILE) and f.endswith('.backup')], reverse=True)
        if backups:
            try:
                with open(backups[0], "r") as f:
                    data = json.load(f)
                    st.session_state.stored_data = data
                    logger.info(f"Restored data from backup: {backups[0]}")
                    st.success("✅ Data restored from backup")
            except Exception as backup_error:
                logger.error(f"Error restoring from backup: {str(backup_error)}")
                st.error("Unable to restore data from backup")
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        st.error(f"Error loading data: {str(e)}")

# Add file size check
def validate_file_size(file):
    if file.size > MAX_FILE_SIZE:
        return False, f"File size ({file.size/1024/1024:.1f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE/1024/1024:.1f}MB)"
    return True, ""

# Update the main display_store_data function
def display_store_data():
    check_session_timeout()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">📂 Store Data Securely</h2>', unsafe_allow_html=True)
    
    # Initialize user data storage
    if st.session_state.username not in st.session_state.stored_data:
        st.session_state.stored_data[st.session_state.username] = {}
    
    # Create tabs for different data types
    tab1, tab2 = st.tabs(["📝 Text Data", "📁 File Data"])
    
    with tab1:
        # Text data encryption (existing code)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            data_name = st.text_input("💼 Data Label", 
                                    placeholder="Enter a name for your data",
                                    help="This label will help you identify your data later",
                                    key="text_label")
            
            user_data = st.text_area("📝 Data to Encrypt", 
                                    height=150,
                                    placeholder="Enter the sensitive data you want to encrypt",
                                    help="Enter the text you want to encrypt securely")
            
            passkey = st.text_input("🔑 Encryption Key", 
                                   type="password",
                                   placeholder="Enter a strong passkey",
                                   help="This key will be required to decrypt your data",
                                   key="text_passkey")
            
            confirm_passkey = st.text_input("🔄 Confirm Key", 
                                          type="password",
                                          placeholder="Confirm your passkey",
                                          help="Re-enter the same passkey to confirm",
                                          key="text_confirm")
        
        with col2:
            st.markdown("""
            <div class="info-box" style="margin-top: 3.7rem;">
                <h4 style="color: #4FB0FF; margin-bottom: 1rem;">📋 Text Guidelines</h4>
                <ul style="font-size: 0.9rem;">
                    <li>Use a descriptive label</li>
                    <li>Keep your passkey safe</li>
                    <li>Avoid sharing sensitive data</li>
                    <li>Use strong passkeys</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Text data buttons
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        with btn_col1:
            if st.button("🗑️ CLEAR", use_container_width=True, key="text_clear"):
                st.session_state.clear_fields = True
                st.rerun()
        with btn_col2:
            preview_btn = st.button("👁️ PREVIEW", use_container_width=True, key="text_preview")
        with btn_col3:
            save_text_btn = st.button("💾 SAVE", use_container_width=True, type="primary", key="text_save")
    
    with tab2:
        # File data encryption
        col1, col2 = st.columns([2, 1])
        
        with col1:
            file_name = st.text_input("💼 File Label", 
                                    placeholder="Enter a name for your file",
                                    help="This label will help you identify your file later",
                                    key="file_label")
            
            uploaded_file = st.file_uploader("📁 Upload File", 
                                           help="Select a file to encrypt",
                                           key="file_upload")
            
            file_passkey = st.text_input("🔑 Encryption Key", 
                                        type="password",
                                        placeholder="Enter a strong passkey",
                                        help="This key will be required to decrypt your file",
                                        key="file_passkey")
            
            confirm_file_passkey = st.text_input("🔄 Confirm Key", 
                                               type="password",
                                               placeholder="Confirm your passkey",
                                               help="Re-enter the same passkey to confirm",
                                               key="file_confirm")
        
        with col2:
            st.markdown("""
            <div class="info-box" style="margin-top: 3.7rem;">
                <h4 style="color: #4FB0FF; margin-bottom: 1rem;">📁 File Guidelines</h4>
                <ul style="font-size: 0.9rem;">
                    <li>Supported file types: All</li>
                    <li>Max file size: 200MB</li>
                    <li>Use unique passkeys</li>
                    <li>Keep original files safe</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # File preview area with debug info
        if uploaded_file is not None:
            is_valid, error_message = validate_file_size(uploaded_file)
            if not is_valid:
                st.error(error_message)
                return
            
            try:
                file_type = uploaded_file.type if uploaded_file.type else 'application/octet-stream'
                file_size = uploaded_file.size
                
                # Debug information
                st.markdown("#### 📄 File Information")
                st.write(f"File Name: {uploaded_file.name}")
                st.write(f"File Type: {file_type}")
                st.write(f"File Size: {file_size/1024:.2f} KB")
                
                # Show different previews based on file type
                if file_type.startswith('image'):
                    st.image(uploaded_file, caption="Image Preview", use_column_width=True)
                elif file_type.startswith('text') or file_type in ['application/json', 'application/xml']:
                    try:
                        content = uploaded_file.getvalue().decode('utf-8')
                        st.text_area("File Content Preview", content[:1000] + ('...' if len(content) > 1000 else ''), height=150)
                    except UnicodeDecodeError:
                        st.warning("⚠️ File content preview not available for this file type")
                else:
                    st.info("ℹ️ Preview not available for this file type")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        # File data buttons with debug info
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🗑️ CLEAR", use_container_width=True, key="file_clear"):
                st.session_state.clear_fields = True
                st.rerun()
        with btn_col2:
            save_file_btn = st.button("💾 SAVE", use_container_width=True, type="primary", key="file_save")
        
        # Handle file data saving with improved error handling
        if save_file_btn:
            try:
                if not file_name:
                    st.error("⚠️ Please provide a file label!")
                elif not uploaded_file:
                    st.error("⚠️ Please upload a file!")
                elif not file_passkey:
                    st.error("⚠️ Please enter a passkey!")
                elif file_passkey != confirm_file_passkey:
                    st.error("⚠️ Passkeys do not match!")
                else:
                    # Debug progress
                    st.info("🔄 Processing file...")
                    
                    # Read file data
                    file_data = uploaded_file.getvalue()
                    st.info(f"📦 Read {len(file_data)} bytes from file")
                    
                    file_info = {
                        "filename": uploaded_file.name,
                        "type": uploaded_file.type if uploaded_file.type else 'application/octet-stream',
                        "size": uploaded_file.size
                    }
                    
                    # Encrypt file data
                    st.info("🔒 Encrypting file data...")
                    hashed_passkey = hash_passkey(file_passkey)
                    encrypted_file = encrypt_data(file_data, file_passkey, is_binary=True)
                    
                    if encrypted_file:
                        # Store encrypted file data
                        if st.session_state.username not in st.session_state.stored_data:
                            st.session_state.stored_data[st.session_state.username] = {}
                        
                        st.session_state.stored_data[st.session_state.username][file_name] = {
                            "encrypted_text": encrypted_file,
                            "passkey": hashed_passkey,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "type": "file",
                            "file_info": file_info
                        }
                        
                        # Save to file
                        st.info("💾 Saving encrypted data...")
                        save_data()
                        st.success("✅ File encrypted and stored successfully!")
                        
                        # Debug information
                        st.write("File Details:")
                        st.json({
                            "label": file_name,
                            "original_size": file_info["size"],
                            "encrypted_size": len(encrypted_file),
                            "type": file_info["type"]
                        })
                        
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Encryption failed! Please try again.")
            except Exception as e:
                st.error(f"❌ Error storing file: {str(e)}")
                st.error("Detailed error information:")
                st.exception(e)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Update the main function
def main():
    check_session_timeout()
    
    # Add version information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Information")
    st.sidebar.text(f"Version: 1.0.0")
    st.sidebar.text(f"Last Update: 2024-03-19")
    
    st.markdown('<h1 class="main-header">Secure Data Encryption System</h1>', unsafe_allow_html=True)
    
    # Check if user is locked out
    current_time = time.time()
    if st.session_state.lockout_time > current_time:
        st.markdown(f'<div class="error-msg">🔒 Account locked. Try again in {int(st.session_state.lockout_time - current_time)} seconds.</div>', unsafe_allow_html=True)
        st.session_state.authenticated = False
    
    # Show login form if not authenticated
    if not st.session_state.authenticated:
        display_login()
    else:
        # Navigation
        menu = ["Home", "Store Data", "Retrieve Data", "My Stored Data", "Change Password"]
        choice = st.sidebar.selectbox("Navigation", menu)
        
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
        
        if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
            logout()
            st.rerun()
        
        if choice == "Home":
            display_home()
        elif choice == "Store Data":
            display_store_data()
        elif choice == "Retrieve Data":
            display_retrieve_data()
        elif choice == "My Stored Data":
            display_my_data()
        elif choice == "Change Password":
            display_login()

# Login page
def display_login():
    # Show logout button if authenticated
    if st.session_state.authenticated:
        st.markdown(
            '<div class="top-right">',
            unsafe_allow_html=True
        )
        if st.button("🚪 LOGOUT", key="logout_button"):
            logout()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Main login container
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown('<div class="thin-container">', unsafe_allow_html=True)
        
        # Shield icon
        st.markdown(shield_icon, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px; color: #4FB0FF;">
            <div style="font-size: 1.5rem; font-weight: 500;">Secure Access Portal</div>
            <div class="small-text">Enter credentials to continue</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Login Form
        if not st.session_state.authenticated:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.checkbox("Remember Me", key="remember")
            with col_b:
                st.markdown('<div style="text-align: right;"><a href="#" style="color: #4FB0FF; text-decoration: none; font-size: 0.9rem;">Forgot Password?</a></div>', unsafe_allow_html=True)
            
            if st.button("LOGIN", use_container_width=True, key="login_button"):
                if authenticate(username, password):
                    st.markdown('<div class="success-msg">✅ Login successful!</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.failed_attempts += 1
                    if st.session_state.failed_attempts >= 3:
                        st.session_state.lockout_time = time.time() + 30
                        st.markdown('<div class="error-msg">🔒 Too many failed attempts! Account locked for 30 seconds.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-msg">❌ Invalid credentials! Attempts remaining: {3 - st.session_state.failed_attempts}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            if st.button("REGISTER", use_container_width=True):
                st.info("Registration feature coming soon!")
            
            # Demo account information
            with st.expander("Demo Accounts"):
                st.markdown("""
                For testing, you can use:
                - Username: admin, Password: admin123
                - Username: user1, Password: password1
                """)
        
        # Change Password Form (only shown when logged in)
        else:
            st.markdown('<div class="change-password-form">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #4FB0FF; font-size: 1.2rem; margin-bottom: 1rem;">Change Password</h3>', unsafe_allow_html=True)
            
            old_password = st.text_input("Current Password", type="password", key="old_password")
            new_password = st.text_input("New Password", type="password", key="new_password")
            confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_new_password")
            
            if st.button("UPDATE PASSWORD", use_container_width=True, key="change_password_button"):
                if not old_password or not new_password or not confirm_new_password:
                    st.markdown('<div class="error-msg">⚠️ All fields are required!</div>', unsafe_allow_html=True)
                elif new_password != confirm_new_password:
                    st.markdown('<div class="error-msg">⚠️ New passwords do not match!</div>', unsafe_allow_html=True)
                elif change_password(st.session_state.username, old_password, new_password):
                    st.markdown('<div class="success-msg">✅ Password updated successfully!</div>', unsafe_allow_html=True)
                    time.sleep(1)
                    logout()
                    st.rerun()
                else:
                    st.markdown('<div class="error-msg">❌ Current password is incorrect!</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Home page
def display_home():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">🏠 Welcome to the Secure Data System</h2>', unsafe_allow_html=True)
    st.write("Use this app to **securely store and retrieve data** using unique passkeys.")
    
    # Display sample instructions
    st.markdown("""
    <div class="info-box">
    <h3>How to use this app:</h3>
    <ol>
        <li><strong>Store Data</strong>: Encrypt and save your sensitive information</li>
        <li><strong>Retrieve Data</strong>: Access your encrypted data using your passkey</li>
        <li><strong>My Stored Data</strong>: View a list of your stored encrypted data</li>
    </ol>
    <p>All data is stored securely and encrypted with strong cryptography.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display security features
    st.markdown("""
    <div class="info-box">
    <h3>Security Features:</h3>
    <ul>
        <li>Data is encrypted using Fernet symmetric encryption</li>
        <li>Passkeys are hashed using SHA-256</li>
        <li>Built-in protection against brute force attacks</li>
        <li>Data is stored persistently but securely</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Retrieve data page
def display_retrieve_data():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">🔍 Retrieve Your Data</h2>', unsafe_allow_html=True)
    
    username = st.session_state.username
    
    if username in st.session_state.stored_data and st.session_state.stored_data[username]:
        # Show list of stored data
        st.markdown('<div class="info-box">Select data to decrypt:</div>', unsafe_allow_html=True)
        
        for data_name, data_info in st.session_state.stored_data[username].items():
            with st.expander(f"{'📄' if data_info['type'] == 'text' else '📁'} {data_name} - {data_info['type'].upper()}"):
                # Show data info
                st.markdown(f"""
                **Type:** {data_info['type'].upper()}
                **Created:** {data_info.get('timestamp', 'Unknown')}
                """)
                
                if data_info['type'] == 'file':
                    st.markdown(f"""
                    **Original Filename:** {data_info['file_info']['filename']}
                    **File Type:** {data_info['file_info']['type']}
                    **Size:** {data_info['file_info']['size']/1024:.2f} KB
                    """)
                
                # Decryption interface
                decrypt_passkey = st.text_input("🔑 Enter passkey", 
                                              type="password",
                                              key=f"decrypt_{data_name}")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("🔓 DECRYPT", key=f"btn_decrypt_{data_name}", use_container_width=True):
                        if hash_passkey(decrypt_passkey) == data_info["passkey"]:
                            try:
                                # Decrypt data
                                decrypted_data = decrypt_data(
                                    data_info["encrypted_text"],
                                    decrypt_passkey,
                                    is_binary=(data_info['type'] == 'file')
                                )
                                
                                if decrypted_data:
                                    st.markdown('<div class="success-msg">✅ Decryption successful!</div>', unsafe_allow_html=True)
                                    
                                    if data_info['type'] == 'text':
                                        # Show decrypted text
                                        st.code(decrypted_data)
                                    else:
                                        # Provide file download
                                        file_info = data_info['file_info']
                                        st.download_button(
                                            label="📥 DOWNLOAD DECRYPTED FILE",
                                            data=decrypted_data,
                                            file_name=file_info['filename'],
                                            mime=file_info['type']
                                        )
                                        
                                        # Preview for supported file types
                                        if file_info['type'].startswith('image'):
                                            st.image(decrypted_data, caption="Decrypted Image")
                                        elif file_info['type'].startswith('text'):
                                            st.text_area("Decrypted Content", decrypted_data.decode(), height=100)
                            except Exception as e:
                                st.markdown(f'<div class="error-msg">⚠️ Decryption failed: {str(e)}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-msg">❌ Incorrect passkey!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">No encrypted data found. Store some data first!</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# My Stored Data page
def display_my_data():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">📋 My Stored Data</h2>', unsafe_allow_html=True)
    
    username = st.session_state.username
    
    if username not in st.session_state.stored_data or not st.session_state.stored_data[username]:
        st.markdown("""
        <div class="info-box">
            <h4 style="color: #4FB0FF; margin-bottom: 1rem;">No Data Found</h4>
            <p>You haven't stored any data yet. Go to the Store Data page to add some!</p>
            <div style="margin-top: 1rem;">
                <a href="?page=Store+Data" style="color: #4FB0FF; text-decoration: none;">
                    → Go to Store Data
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📊 Grid View", "📑 List View"])
        
        with tab1:
            # Create a grid of cards for data items
            for i in range(0, len(st.session_state.stored_data[username]), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(st.session_state.stored_data[username]):
                        data_name = list(st.session_state.stored_data[username].keys())[i + j]
                        data_info = st.session_state.stored_data[username][data_name]
                        
                        with cols[j]:
                            st.markdown(f"""
                            <div style="padding: 1rem; background-color: rgba(13, 25, 42, 0.7); border-radius: 8px; border: 1px solid rgba(79, 176, 255, 0.3); margin-bottom: 1rem;">
                                <h4 style="color: #4FB0FF; margin-bottom: 0.5rem;">{data_name}</h4>
                                <p style="font-size: 0.8rem; color: #aaa;">Created: {data_info.get('timestamp', 'Unknown')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add buttons for each card
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🔓 VIEW", key=f"view_{data_name}", use_container_width=True):
                                    st.session_state.selected_data = data_name
                                    st.session_state.view_mode = True
                            with col2:
                                if st.button("🗑️ DELETE", key=f"delete_{data_name}", use_container_width=True):
                                    st.session_state.selected_data = data_name
                                    st.session_state.delete_mode = True
        
        with tab2:
            for data_name, data_info in st.session_state.stored_data[username].items():
                with st.expander(f"📄 {data_name} - Created: {data_info.get('timestamp', 'Unknown date')}"):
                    st.text_area("🔒 Encrypted Data", data_info["encrypted_text"], height=100, disabled=True)
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        decrypt_passkey = st.text_input("🔑 Enter passkey", 
                                                      type="password", 
                                                      key=f"decrypt_{data_name}")
                    
                    with col2:
                        if st.button("🔓 DECRYPT", key=f"btn_decrypt_{data_name}", use_container_width=True):
                            if hash_passkey(decrypt_passkey) == data_info["passkey"]:
                                try:
                                    decrypted = decrypt_data(data_info["encrypted_text"], decrypt_passkey)
                                    st.markdown('<div class="success-msg">✅ Decryption successful!</div>', unsafe_allow_html=True)
                                    st.code(decrypted)
                                except:
                                    st.markdown('<div class="error-msg">⚠️ Decryption failed!</div>', unsafe_allow_html=True)
                    
                    with col3:
                        if st.button("🗑️ DELETE", key=f"btn_delete_{data_name}", use_container_width=True):
                            if data_name in st.session_state.stored_data[username]:
                                del st.session_state.stored_data[username][data_name]
                                save_data()
                                st.markdown('<div class="success-msg">✅ Data deleted successfully!</div>', unsafe_allow_html=True)
                                st.rerun()
    
    # Handle view/delete modes
    if hasattr(st.session_state, 'view_mode') and st.session_state.view_mode:
        data_name = st.session_state.selected_data
        data_info = st.session_state.stored_data[username][data_name]
        
        st.markdown("""
        <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0,0,0,0.8); z-index: 1000; padding: 2rem;">
            <div style="max-width: 600px; margin: 2rem auto; background-color: rgba(13, 25, 42, 0.95); padding: 2rem; border-radius: 10px; border: 1px solid rgba(79, 176, 255, 0.3);">
        """, unsafe_allow_html=True)
        
        st.markdown(f"### 🔍 Viewing: {data_name}")
        st.text_area("Encrypted Data", data_info["encrypted_text"], height=100, disabled=True)
        
        decrypt_passkey = st.text_input("Enter passkey to decrypt", type="password", key="modal_decrypt")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 DECRYPT", use_container_width=True):
                if hash_passkey(decrypt_passkey) == data_info["passkey"]:
                    try:
                        decrypted = decrypt_data(data_info["encrypted_text"], decrypt_passkey)
                        st.markdown('<div class="success-msg">✅ Decryption successful!</div>', unsafe_allow_html=True)
                        st.code(decrypted)
                    except:
                        st.markdown('<div class="error-msg">⚠️ Decryption failed!</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-msg">❌ Incorrect passkey!</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("❌ CLOSE", use_container_width=True):
                del st.session_state.view_mode
                del st.session_state.selected_data
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    if hasattr(st.session_state, 'delete_mode') and st.session_state.delete_mode:
        data_name = st.session_state.selected_data
        
        st.markdown("""
        <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0,0,0,0.8); z-index: 1000; padding: 2rem;">
            <div style="max-width: 400px; margin: 2rem auto; background-color: rgba(13, 25, 42, 0.95); padding: 2rem; border-radius: 10px; border: 1px solid rgba(79, 176, 255, 0.3);">
        """, unsafe_allow_html=True)
        
        st.markdown(f"### ⚠️ Delete Confirmation")
        st.markdown(f"Are you sure you want to delete **{data_name}**? This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ DELETE", use_container_width=True, type="primary"):
                del st.session_state.stored_data[username][data_name]
                save_data()
                del st.session_state.delete_mode
                del st.session_state.selected_data
                st.markdown('<div class="success-msg">✅ Data deleted successfully!</div>', unsafe_allow_html=True)
                st.rerun()
        
        with col2:
            if st.button("❌ CANCEL", use_container_width=True):
                del st.session_state.delete_mode
                del st.session_state.selected_data
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Add these core functions after the logging setup and before the main app code

def hash_passkey(passkey):
    """Hash the passkey using SHA-256"""
    return hashlib.sha256(passkey.encode()).hexdigest()

def encode_binary_data(binary_data):
    """Convert binary data to base64 string for storage"""
    return base64.b64encode(binary_data).decode('utf-8')

def decode_binary_data(encoded_data):
    """Convert base64 string back to binary data"""
    return base64.b64decode(encoded_data.encode('utf-8'))

def encrypt_data(data, passkey, is_binary=False):
    """Encrypt data using Fernet encryption"""
    try:
        if is_binary:
            if not isinstance(data, bytes):
                raise ValueError("Binary data must be bytes")
            data_to_encrypt = data
        else:
            if not isinstance(data, str):
                raise ValueError("Text data must be string")
            data_to_encrypt = data.encode()
        
        encrypted_data = st.session_state.cipher.encrypt(data_to_encrypt)
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        return None

def decrypt_data(encrypted_data, passkey, is_binary=False):
    """Decrypt data using Fernet decryption"""
    try:
        decoded_data = decode_binary_data(encrypted_data)
        decrypted_data = st.session_state.cipher.decrypt(decoded_data)
        
        if is_binary:
            return decrypted_data
        else:
            return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return None

def authenticate(username, password):
    """Authenticate user credentials"""
    if username in st.session_state.user_accounts:
        hashed_password = hash_passkey(password)
        if st.session_state.user_accounts[username] == hashed_password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.failed_attempts = 0
            return True
    return False

def logout():
    """Logout user and clear session"""
    st.session_state.authenticated = False
    st.session_state.username = ""
    logger.info("User logged out successfully")

def change_password(username, old_password, new_password):
    """Change user password"""
    if username in st.session_state.user_accounts:
        hashed_old_password = hash_passkey(old_password)
        if st.session_state.user_accounts[username] == hashed_old_password:
            st.session_state.user_accounts[username] = hash_passkey(new_password)
            logger.info(f"Password changed for user: {username}")
            return True
    return False

# Load data at startup
load_data()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please refresh the page or contact support.") 
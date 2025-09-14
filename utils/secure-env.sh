#!/bin/bash

# Interactive script to securely create a .env file and install dependencies

# --- Helper Functions ---

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to prompt for user input with a message
prompt() {
    echo -n "$1: "
    read -r val
    echo "$val"
}

# Function to validate that input is not empty
require_input() {
    local prompt_msg="$1"
    local value=""
    while [[ -z "$value" ]]; do
        value=$(prompt "$prompt_msg")
        if [[ -z "$value" ]]; then
            echo "This field is required. Please try again."
        fi
    done
    echo "$value"
}

# --- Main Script ---

# Introduction
echo "-------------------------------------"
echo " Memorae Full Setup"
echo "-------------------------------------"
echo "This script will guide you through:"
echo "1. Installing necessary Python packages."
echo "2. Creating a secure .env file for your assistant."
echo

# --- Dependency Installation ---
echo "--- Step 1: Installing Python Dependencies ---"
if [ -f "requirements.txt" ]; then
    if command_exists pip; then
        echo "Found 'pip'. Installing packages from requirements.txt..."
        if pip install -r requirements.txt; then
            echo "✅ Python packages installed successfully."
        else
            echo "❌ Error installing Python packages. Please check your pip and Python environment."
            exit 1
        fi
    elif command_exists pip3; then
        echo "Found 'pip3'. Installing packages from requirements.txt..."
        if pip3 install -r requirements.txt; then
            echo "✅ Python packages installed successfully."
        else
            echo "❌ Error installing Python packages. Please check your pip3 and Python environment."
            exit 1
        fi
    else
        echo "⚠️ 'pip' or 'pip3' command not found. Cannot install Python packages."
        echo "Please install Python and pip, then run this script again or install the packages manually:"
        echo "pip install -r requirements.txt"
    fi
else
    echo "⚠️ 'requirements.txt' not found. Skipping dependency installation."
fi
echo

# --- .env File Generation ---
echo "--- Step 2: Secure Environment Setup ---"
echo "This will help you create a secure .env file for your assistant."
echo "You can press Enter to accept the default values in brackets [like this]."
echo

# Get user's name (optional, with default)
user_name=$(prompt "Enter your name [User]")

# Get email credentials (required)
email_user=$(require_input "Enter your Gmail address (for sending notifications)")
email_pass=$(require_input "Enter your Gmail App Password (search Google for 'Gmail App Password')")

# Get WhatsApp number (optional)
whatsapp_number=$(prompt "Enter your WhatsApp number (e.g., +11234567890)")

# Get Ollama model (optional, with default)
ollama_model=$(prompt "Enter the Ollama model to use [llama3]")

# --- File Generation ---

# Set defaults if empty
: "${user_name:=User}"
: "${ollama_model:=llama3}"

# Create .env file content
ENV_CONTENT="# .env - Secure environment variables for Memorae

# -- User Information --
USER_NAME=\"${user_name}\"

# -- Email Configuration (for sending notifications) --
EMAIL_USER=\"${email_user}\"
EMAIL_PASS=\"${email_pass}\"

# -- WhatsApp Configuration --
# Your full number, including country code (e.g., +11234567890)
WHATSAPP_NUMBER=\"${whatsapp_number}\"

# -- Ollama LLM Configuration --
# The model to use for generating responses (e.g., llama3, phi3)
OLLAMA_MODEL=\"${ollama_model}\"

# -- Ollama Connection --
# For local setup, Ollama runs on the host machine.
# For Docker, this will be automatically overridden.
OLLAMA_HOST=http://127.0.0.1:11434
"

# Write the .env file
if echo -e "$ENV_CONTENT" > .env; then
    echo
    echo "✅ Success! Your .env file has been created."
else
    echo
    echo "❌ Error! Could not create the .env file."
    echo "Please check your permissions and try again."
    exit 1
fi

# --- Final Instructions ---
echo
echo "--- Setup Complete! ---"
echo "Next Steps:"
echo "1. If using Google Calendar, add your 'credentials.json' file to the project root."
echo "2. To run the assistant:"
echo "   - In your terminal: python jdmmitagente.py"
echo "   - Using the web interface: streamlit run streamlit_app.py"
echo "   - Using Docker: ./run-docker.sh"

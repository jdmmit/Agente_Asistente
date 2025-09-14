#!/bin/bash

# Interactive script to securely create a .env file

# --- Helper Functions ---

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
echo " Memorae Environment Setup"
echo "-------------------------------------"
echo "This script will help you create a secure .env file for your assistant."
echo "You can press Enter to accept the default values in brackets [like this]."

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
    echo ""
    echo "✅ Success! Your .env file has been created."
    echo "You can now run the assistant."
else
    echo ""
    echo "❌ Error! Could not create the .env file."
    echo "Please check your permissions and try again."
fi

# --- Final Instructions ---
echo ""
echo "Next Steps:"
echo "1. If you want to use Google Calendar, make sure to add your \"credentials.json\" file to this directory."
echo "2. Run the assistant with: python jdmmitagente.py or streamlit run jdmmitagente.py"

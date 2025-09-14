import os
from dotenv import load_dotenv, set_key

# Cargar .env existente si existe
load_dotenv()

def setup_config():
    print("=== Setup de Configuración para Memorae ===")
    print("Este script te ayudará a configurar tus datos sensibles. Presiona Enter para usar defaults.")

    # Modelo LLM
    model = input("Modelo LLM (default: llama3): ") or 'llama3'
    set_key('.env', 'MODEL', model)

    # Paths
    db_path = input("Path de DB (default: memoria.db): ") or 'memoria.db'
    set_key('.env', 'DB_PATH', db_path)

    credentials_path = input("Path de credentials.json para Google Calendar (default: credentials.json): ") or 'credentials.json'
    set_key('.env', 'CREDENTIALS_PATH', credentials_path)

    # Email
    email_smtp = input("SMTP server (default: smtp.gmail.com): ") or 'smtp.gmail.com'
    set_key('.env', 'EMAIL_SMTP', email_smtp)

    email_port = input("Email port (default: 587): ") or '587'
    set_key('.env', 'EMAIL_PORT', email_port)

    email_user = input("Email usuario (e.g., tu_email@gmail.com): ")
    if email_user:
        set_key('.env', 'EMAIL_USER', email_user)

    email_pass = input("Email password/app password: ")
    if email_pass:
        set_key('.env', 'EMAIL_PASS', email_pass)

    # WhatsApp
    whatsapp_number = input("Número WhatsApp (formato internacional, e.g., +573xxxxxxxxx): ")
    if whatsapp_number:
        set_key('.env', 'WHATSAPP_NUMBER', whatsapp_number)

    print("\nConfiguración guardada en .env. No olvides agregar .env a .gitignore para seguridad.")
    print("Ejecuta 'python agente.py' para iniciar.")

if __name__ == '__main__':
    setup_config()
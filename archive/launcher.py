#!/usr/bin/env python3
"""
Launcher para JDMMItAsistente - Asistente AI
Permite elegir entre diferentes modos de ejecución
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    try:
        import ollama
        import sqlite3
        from config import MODEL
        print("✅ Dependencias básicas disponibles")
        return True
    except ImportError as e:
        print(f"❌ Faltan dependencias: {e}")
        print("Ejecuta: pip install -r requirements.txt")
        return False

def check_ollama_service():
    """Verificar que Ollama esté ejecutándose"""
    try:
        import ollama
        models = ollama.list()
        print(f"✅ Ollama funcionando. Modelos disponibles: {len(models['models'])}")
        return True
    except Exception as e:
        print(f"⚠️ Ollama no está disponible: {e}")
        print("Asegúrate de que Ollama esté instalado e iniciado.")
        return False

def run_original():
    """Ejecutar versión original del agente"""
    print("🚀 Iniciando JDMMItAsistente (versión original)...")
    os.system("python agente.py")

def run_optimized():
    """Ejecutar versión optimizada del agente"""
    print("🚀 Iniciando JDMMItAsistente (versión optimizada)...")
    os.system("python agente_optimizado.py")

def run_gui():
    """Ejecutar versión con interfaz gráfica"""
    print("🚀 Iniciando JDMMItAsistente (interfaz gráfica)...")
    
    # Verificar que tkinter esté disponible
    try:
        import tkinter
        os.system("python gui_agente.py")
    except ImportError:
        print("❌ tkinter no está disponible. Instala: apt-get install python3-tk")

def show_menu():
    """Mostrar menú de opciones"""
    print("""
🤖 JDMMItAsistente - Asistente AI Personal
═══════════════════════════════════

Selecciona el modo de ejecución:

1️⃣  Versión Original (Terminal)
2️⃣  Versión Optimizada (Terminal) 
3️⃣  Interfaz Gráfica (GUI)
4️⃣  Verificar Sistema
5️⃣  Salir

═══════════════════════════════════
""")

def verify_system():
    """Verificar el estado del sistema"""
    print("🔍 Verificando sistema...\n")
    
    print("📁 Archivos del proyecto:")
    files = ['agente.py', 'agente_optimizado.py', 'gui_agente.py', 'config.py', 'requirements.txt']
    for file in files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (faltante)")
    
    print("\n🔧 Dependencias:")
    check_dependencies()
    
    print("\n🤖 Ollama:")
    check_ollama_service()
    
    print("\n💾 Base de datos:")
    if os.path.exists('memoria.db'):
        print("   ✅ memoria.db existe")
    else:
        print("   ℹ️ memoria.db se creará al primer uso")

def main():
    """Función principal del launcher"""
    parser = argparse.ArgumentParser(description="Launcher para JDMMItAsistente")
    parser.add_argument("--mode", choices=['original', 'optimized', 'gui'], 
                       help="Modo de ejecución directo")
    parser.add_argument("--check", action='store_true', 
                       help="Solo verificar sistema")
    
    args = parser.parse_args()
    
    # Cambiar al directorio del script
    os.chdir(Path(__file__).parent)
    
    if args.check:
        verify_system()
        return
    
    if args.mode:
        if not check_dependencies():
            sys.exit(1)
            
        if args.mode == 'original':
            run_original()
        elif args.mode == 'optimized':
            run_optimized()
        elif args.mode == 'gui':
            run_gui()
        return
    
    # Modo interactivo
    while True:
        show_menu()
        try:
            choice = input("Selecciona una opción (1-5): ").strip()
            
            if choice == '1':
                if check_dependencies():
                    run_original()
                else:
                    input("\nPresiona Enter para continuar...")
                    
            elif choice == '2':
                if check_dependencies():
                    run_optimized()
                else:
                    input("\nPresiona Enter para continuar...")
                    
            elif choice == '3':
                if check_dependencies():
                    run_gui()
                else:
                    input("\nPresiona Enter para continuar...")
                    
            elif choice == '4':
                verify_system()
                input("\nPresiona Enter para continuar...")
                
            elif choice == '5':
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida. Selecciona 1-5.")
                input("Presiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except EOFError:
            print("\n\n👋 ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()


import logging
import os
import sys
import tempfile

from config import GOOGLE_SPEECH_LANGUAGE

logger = logging.getLogger(__name__)

# Disponibilidad de GUI y voz
PWK_AVAILABLE = os.environ.get('DISPLAY') is not None
VOICE_AVAILABLE = False
GTTS_AVAILABLE = False

# Importaciones opcionales
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Funcionalidades de voz no disponibles: {e}")

try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    logger.warning("gTTS no disponible como fallback")


class VoiceManager:
    """Gestor de funcionalidades de voz optimizado"""

    def __init__(self):
        self.engine = None
        self.recognizer = None
        self.voice_mode = None
        self.setup_voice()

    def setup_voice(self):
        """Configurar sistema de voz con fallbacks"""
        if not VOICE_AVAILABLE:
            logger.warning("Módulo de voz no disponible.")
            return

        # Configurar reconocimiento de voz
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 400  # Ajuste para sensibilidad
            self.recognizer.dynamic_energy_threshold = True
            logger.info("Reconocimiento de voz configurado.")
        except Exception as e:
            logger.error(f"Error configurando reconocimiento: {e}")

        # Configurar síntesis de voz (pyttsx3 o gTTS)
        try:
            self.engine = pyttsx3.init()
            self.voice_mode = 'pyttsx3'
            # Ajustar propiedades de voz para mejor calidad
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 0.9)
            logger.info("Motor de voz pyttsx3 configurado.")
        except Exception as e:
            logger.warning(f"pyttsx3 falló: {e}. Intentando fallback con gTTS.")
            if GTTS_AVAILABLE:
                try:
                    pygame.mixer.init()
                    self.engine = 'gtts'
                    self.voice_mode = 'gtts'
                    logger.info("Motor de voz gTTS configurado como fallback.")
                except Exception as gtts_e:
                    logger.error(f"Fallback gTTS también falló: {gtts_e}")
                    self.voice_mode = None
            else:
                self.voice_mode = None

    def listen(self, timeout=5):
        """Escuchar entrada de voz con manejo de errores robusto"""
        if not self.recognizer:
            logger.warning("Reconocimiento de voz no disponible.")
            return None

        try:
            with sr.Microphone() as source:
                print("🎤 Escuchando...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)

            print("🔍 Procesando audio...")
            text = self.recognizer.recognize_google(audio, language=GOOGLE_SPEECH_LANGUAGE)
            logger.info(f"Texto reconocido: '{text}'")
            return text

        except sr.WaitTimeoutError:
            # Es normal que ocurra si no se habla, no necesita ser un error
            logger.debug("Tiempo de espera agotado, no se detectó habla.")
            return None
        except sr.UnknownValueError:
            logger.warning("No se pudo entender el audio.")
            self.speak("Disculpa, no te he entendido.")
            return None
        except sr.RequestError as e:
            logger.error(f"Error en la API de Google Speech: {e}")
            self.speak("Hay un problema con el servicio de reconocimiento de voz.")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en reconocimiento de voz: {e}")
            return None

    def speak(self, text):
        """Síntesis de voz con manejo de errores y fallback a print"""
        if self.voice_mode == 'pyttsx3':
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Error con pyttsx3: {e}")
                print(f"🤖 {text}")  # Fallback a consola

        elif self.voice_mode == 'gtts':
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                    tts = gTTS(text=text, lang='es')
                    tts.save(fp.name)
                    pygame.mixer.music.load(fp.name)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(100)
                os.remove(fp.name)
            except Exception as e:
                logger.error(f"Error con gTTS: {e}")
                print(f"🤖 {text}")  # Fallback a consola
        else:
            # Si no hay motor de voz, simplemente imprimir
            print(f"🤖 {text}")


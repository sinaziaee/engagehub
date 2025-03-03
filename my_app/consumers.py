import base64
import json
import os
import speech_recognition as sr
from pydub import AudioSegment
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.recognizer = sr.Recognizer()
        print("WebSocket Connected")

    async def disconnect(self, close_code):
        print("WebSocket Disconnected")

    async def receive(self, text_data):
        if not text_data:
            print("⚠ Received empty message, ignoring...")
            return

        try:
            data = json.loads(text_data)
            if "audio" in data:
                audio_bytes = base64.b64decode(data["audio"])
                file_path = "temp_audio.webm"  # Save as WebM first

                with open(file_path, "wb") as f:
                    f.write(audio_bytes)

                # Convert to WAV using pydub
                wav_path = "temp_audio.wav"
                AudioSegment.from_file(file_path).export(wav_path, format="wav")

                transcript = await self.speech_to_text(wav_path)
                await self.send(json.dumps({"text": transcript}))

                # Cleanup files
                os.remove(file_path)
                os.remove(wav_path)

            elif text_data == "STOP":
                print("Recording Stopped")

        except json.JSONDecodeError:
            print("⚠ Invalid JSON received, ignoring...")
            return
        except Exception as e:
            print(f"⚠ Error processing audio: {e}")

    async def speech_to_text(self, file_path):
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError:
            return "Error with Speech Recognition API"

import pyttsx3
import speech_recognition as sr


def speak(text):
    engine.say(text)
    engine.runAndWait()

def speech_to_text(audio, recognizer):
    try:
        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio)
        print("You said: " + text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Initialize the text to speech engine
engine = pyttsx3.init()
# Optionally, adjust properties like rate (speed) and volume
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.8)
# Initialize the speech recognizer
speech_recognizer = sr.Recognizer()
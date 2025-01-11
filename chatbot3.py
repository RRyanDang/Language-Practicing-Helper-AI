import google.generativeai as genai
import os,vertexai
from vertexai.generative_models import ChatSession
import speech_recognition as sr
import os
import whisper
import time
import webrtcvad
import numpy as np
import webrtcvad
import pyaudio
import wave
import keyboard

OUTPUT_FILENAME = 'voice_placeholder.wav'

# Set audio parameters
FORMAT = pyaudio.paInt16  # 16-bit PCM
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate in Hz (must match WebRTC VAD supported rates)
FRAME_DURATION = 10  # Frame duration in ms (10, 20, or 30)
FRAME_SIZE = int(RATE * FRAME_DURATION / 1000)  # Frame size in samples
CHUNK = FRAME_SIZE * 2  # Frame size in bytes (16-bit = 2 bytes per sample)


genai.configure(api_key="AIzaSyBOtrzDEi16T5umPpea0kNhf4_WyOO7S04")
generation_config = {
    'max_output_tokens' : 250, 
    'temperature' : 1,
    'top_p' : 0.92,
    'top_k' : 31,
}
model = genai.GenerativeModel(
    model_name = 'gemini-1.5-flash',
    generation_config = generation_config,
)


def get_response(chat: ChatSession, prompt: str) -> str:
    output = []
    response = chat.send_message(prompt)
    for chunk in response:
        output.append(chunk.text)
    return ''.join(output)


def start_chatbot(history_placeholder: list):
    print('You have initiated the ChatBot AI. Please input prompts as needed to proceed.')
    user_name = input('Name: ')
    language_desire = input('Language: ')
    language_proficiency = input('Language proficiency (beginner, intermediate, advance, native): ')
    context_desire = input('Please enter a context where you would like to stimulate the conversation: ')
    print('You have started ChatBot. Type/Say exit to leave.')
    chat_session = model.start_chat(
        history = [
            # IDENTITY INTRODUCTION
            {'role':'user','parts':'Hello, my name is {user_name} and my level of mastery in this language is {language_proficiency}. I would like to stimulate a conversation with you so I can pratice my language.'},
            {'role': 'model','parts':'Understood. I will play the role of another individual talking to you. I will response with your level of proficiency in terms of vocabulary ranges and grammer so you can learn better.'},
            {'role': 'model','parts':'Is there a preferred context you would like to talk about?'},
            {'role': 'user','parts':'Yes. I would like to stimulate a conversation of {context_desire}'},
            {'role':'model','parts':'I will play response using a bit of wider range of words compared to your {language_proficiency} so you can learn more more words.'},
        ]
    )

    r = sr.Recognizer()
    while True:
        print('Press space to start speaking')
        keyboard.wait('space')
        print('Recording answer. Press space again to stop.')
        time.sleep(0.2)

        # Initialize PyAudio
        p = pyaudio.PyAudio()
        # Open audio stream
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frame=[]
  
        while True:
            try:
                audio_data = stream.read(CHUNK)
                frame.append(audio_data)
            except KeyBoardInterupt:
                break
            if keyboard.is_pressed('space'):
                time.sleep(0.2)
                break
            
        waveFile = wave.open(OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(p.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frame)) 
        waveFile.close()

        try:
            # OPEN THE AUDIO FILE
            with sr.AudioFile(OUTPUT_FILENAME) as source:
                audio_info = r.record(source)
                sentence_input = r.recognize_whisper(audio_info,language=language_desire,model='small') #tiny, base (default), small, medium, and large
        except sr.UnknownValueError:
            print("Chatbot could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Whisper; {e}")

        print(f'You: {sentence_input}')

        if sentence_input.lower() == 'exit':
            break
        if sentence_input is not None:
            response = get_response(chat_session,sentence_input)
            print(response)
        else:
            print('Microphone has no input. Please try again!')
        
        time.sleep(0.25)
   
    history_placeholer.append(chat_session.history)    

def view_history(history_placeholder: list) -> None:
    print(f'{len(history_placeholder) history record(s)}')
    if len(history_placeholder) >= 1:
        while True:
            record_desire = input('Please choose a record: ')
            if record_desire == 'exit':
                break
            print(history_placeholder[record_desire-1])
    else:
        print('No available record being stored at the moment!')

    print('You have left the history record section')

def start_UI():
    START_CHATBOT = 'START_CHATBOT'
    VIEW_CHAT_HISTORY = 'VIEW_CHAT_HISTORY'
    TERMINATE_PROGRAM = 'TERMINATE_PROGRAM'
    history_placeholder = []
    print('Welcome to the ChatBot AI main panel! Follow the pre-defined commands to starting using it')

    while True:
        print(f'1: {START_CHATBOT}')
        print(f'2: {VIEW_CHAT_HISTORY}')
        print(f'3: {TERMINATE_PROGRAM}')
        user_input = input("Please enter a number here: ")

        if user_input == '1':
            start_chatbot(history_holder)
        elif user_input == '2':
            view_history(history_placeholder)
        elif user_input == '3':
            break
        else:
            print('Invalid entry! Please choose again!')
    
    print('You have successfully terminated the program!')

start_UI()




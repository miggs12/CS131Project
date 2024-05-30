import zmq
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech
import os
import pygame

def receive_file():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://10.0.1.223:5000")

    print("Waiting for a connection...")

    # Receive language code
    language_code = socket.recv_string()
    socket.send_string("ACK")
    print(f"Received language code: {language_code}")

    # Receive file data
    with open('received_file.txt', 'wb') as file:
        while True:
            data = socket.recv()
            print(f"Received data: {data[:20]}...")  # 添加调试信息
            if data == b"END":
                socket.send(b"ACK")
                break
            file.write(data)
            socket.send(b"ACK")
            print("Sent ACK")  # 添加调试信息

    print("File received successfully")
    socket.close()
    context.term()
    return language_code

def translate_text(text, target_language):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/ml/Downloads/my-first-project-424303-336fcb4c7878.json'
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language)
    return result['translatedText']

def text_to_speech(text, output_file, language_code, voice_name):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{output_file}"')

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

if __name__ == "__main__":
    while True:
        language_code = receive_file()

        with open('received_file.txt', 'r', encoding='utf-8') as file:
            text = file.read()

        if language_code == 'en-US':
            target_language = "zh-CN"
            voice_language_code = "cmn-CN"
            voice_name = "cmn-CN-Standard-B"
        elif language_code == 'zh-CN':
            target_language = "en"
            voice_language_code = "en-US"
            voice_name = "en-US-Standard-B"
        else:
            print("Invalid language code received.")
            continue

        translated_text = translate_text(text, target_language)
        print(f"Original text: {text}")
        print(f"Translated text: {translated_text}")

        output_mp3_file = "output.mp3"
        text_to_speech(translated_text, output_mp3_file, voice_language_code, voice_name)
        play_audio(output_mp3_file)

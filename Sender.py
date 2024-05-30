import zmq
import subprocess
from google.cloud import speech_v1
from pydub import AudioSegment

def record_audio(duration, file_path):
    command = f'arecord -d {duration} -r 16000 -f S16_LE -D plughw:2,0 {file_path}'
    subprocess.run(command, shell=True)
    print(f'Audio recorded and saved to "{file_path}"')

def sendfile(filepath, language_code):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://10.0.1.223:5000")

    try:
        # Send language code
        socket.send_string(language_code)
        ack = socket.recv_string()
        print(f"Language code sent. Received ACK: {ack}")

        # Send file data
        with open(filepath, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    print("No more data to send, breaking the loop.")
                    break
                print(f"Sending data chunk: {data[:20]}...")  # 添加调试信息
                socket.send(data)
                ack = socket.recv()
                print(f"Received ACK: {ack}")  # 添加调试信息

        print("Sending END signal.")
        socket.send(b"END")
        final_ack = socket.recv()
        print(f"Received final ACK: {final_ack}")  # 添加调试信息
        print("File sent successfully")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        socket.close()
        context.term()

def transcribe_and_identify(file_path, language_code):
    wav_file = AudioSegment.from_wav(file_path)
    wav_file.export("myfile.mp3", format="mp3")
    print('Conversion complete. "myfile.mp3" has been created')

    client = speech_v1.SpeechClient.from_service_account_file('key.json')
    with open("myfile.mp3", 'rb') as f:
        audio_data = f.read()
    audio = speech_v1.RecognitionAudio(content=audio_data)
    config = {
        "sample_rate_hertz": 16000,
        "language_code": language_code,
        "enable_automatic_punctuation": True
    }
    response = client.recognize(config=config, audio=audio)
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "
    print("Transcript:", transcript)

    with open("path_to_file.txt", 'w') as w:
        w.write(transcript)

    print("Sending...\n")
    sendfile("path_to_file.txt", language_code)
    print("Sent\n")

def main_loop():
    while True:
        lang_input = input("Enter 'e' for English or 'c' for Chinese: ").strip().lower()
        if lang_input == 'e':
            language_code = 'en-US'
        elif lang_input == 'c':
            language_code = 'zh-CN'
        else:
            print("Invalid input. Please enter 'e' or 'c'.")
            continue

        try:
            duration = int(input("Enter the recording duration in seconds: ").strip())
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue

        record_audio(duration, 'test.wav')
        transcribe_and_identify('test.wav', language_code)

if __name__ == "__main__":
    main_loop()

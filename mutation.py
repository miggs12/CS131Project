import zmq
from google.cloud import speech_v1
from pydub import AudioSegment
import torchaudio
from speechbrain.inference.classifiers import EncoderClassifier
#libaries
def sendfile(filepath):
    # Create a ZeroMQ context
    context = zmq.Context()

    # Create a REQ (request) socket
    socket = context.socket(zmq.REQ)
    server_ip = '10.0.1.223'  # Replace with the server's IP address
    socket.connect(f"tcp://{server_ip}:5000")

    # Send file data
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            socket.send(data)
            # Wait for acknowledgment from the server
            socket.recv()

    # Send a message indicating the end of file transmission
    socket.send(b"END")
    socket.recv()

    print("File sent successfully")
    socket.close()
    context.term()

def transcribe_and_identify(file_path):
    # Convert WAV to MP3
    wav_file = AudioSegment.from_wav(file_path)
    wav_file.export("myfile.mp3", format="mp3")
    print('Conversion complete. "myfile.mp3" has been created')

    # Perform speech-to-text conversion
    client = speech_v1.SpeechClient.from_service_account_file('key.json')
    with open("myfile.mp3", 'rb') as f:
        audio_data = f.read()
    audio = speech_v1.RecognitionAudio(content=audio_data)
    config = {
        "sample_rate_hertz": 16000,
        "language_code": 'en-US',
        "enable_automatic_punctuation": True
    }
    response = client.recognize(config=config, audio=audio)
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "
    print("Transcript:", transcript)

    w = open("path_to_file.txt", 'w')
    w.write(transcript)
    w.close()

    # Send the transcript and language code to the server
    print("Sending...\n")
    sendfile("path_to_file.txt")  # Replace with the path to the file you want to send
    print("Sent\n")

if __name__ == "__main__":
    transcribe_and_identify('16000')  # Replace with the path to your WAV file

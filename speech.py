from google.cloud import speech_v1
from pydub import AudioSegment
# import main


wav_file = AudioSegment.from_wav("16000")
wav_file.export("myfile.mp3",format="mp3")

print('Conversion complete. "output.mp3" has been created')

client = speech_v1.SpeechClient.from_service_account_file('key.json')

file_name = "myfile.mp3"

with open(file_name, 'rb') as f:
    audio_data = f.read()

audio = speech_v1.RecognitionAudio(content=audio_data)

config = {
    "sample_rate_hertz": 16000,
    # "language_code": main.code,
    "language_code": 'en-US',
    # "language_code": 'zh-CN',
    "enable_automatic_punctuation": True
}

response = client.recognize(config=config, audio=audio)

for result in response.results:
    print("Transcript: {}".format(result.alternatives[0].transcript))


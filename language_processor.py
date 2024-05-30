import torchaudio
from speechbrain.inference.classifiers import EncoderClassifier

def id_lang(audio_file):
    language_id = EncoderClassifier.from_hparams(source="speechbrain/lang-id-voxlingua107-ecapa", savedir="tmp")
    signal = language_id.load_audio(audio_file)
    prediction =  language_id.classify_batch(signal)

    # The identified language ISO code is given in prediction[3]
    language_code = prediction[3][0]
    print(language_code)
    code = language_code.split(':')[0].strip()

    return code

lang_code = id_lang("test.wav")


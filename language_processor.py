import torchaudio
from speechbrain.inference.classifiers import EncoderClassifier
language_id = EncoderClassifier.from_hparams(source="speechbrain/lang-id-voxlingua107-ecapa", savedir="tmp")

signal = language_id.load_audio("test.wav")
prediction =  language_id.classify_batch(signal)
#print(prediction)

# The linear-scale likelihood can be retrieved using the following:
print(prediction[1].exp())

# The identified language ISO code is given in prediction[3]
print(prediction[3])
#  ['th: Thai']

# Speech.py code 
language_code = prediction[3][0]
code = language_code.split(':')[0].strip()

  
# Alternatively, use the utterance embedding extractor:
emb =  language_id.encode_batch(signal)
#print(emb.shape)


import torch
import sounddevice as sd
import time

language = 'ru'
model_id = 'v4_ru'
sample_rate = 48000
speaker = 'xenia'
device = torch.device('cpu')
words = "Привет, я умный голосовой помощник Галя!"

model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
model='silero_tts',
language=language,
speaker=model_id)

model.to(device)


def speak_text(text):
    audio = model.apply_tts(text=text,
                            speaker=speaker,
                            sample_rate=sample_rate)
    print(text)
    sd.play(audio, sample_rate * 1.05)
    time.sleep((len(audio) / sample_rate) + 0.5)
    sd.stop()

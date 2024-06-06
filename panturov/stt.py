import vosk
import sounddevice as sd
import sys
import json
import queue

model = vosk.Model("model_small")
samplerate = 16000
device = 1
audio_storage = queue.Queue()


def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_storage.put(bytes(indata))


def listen_text(callback):
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16',
                           channels=1, callback=audio_callback):

        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = audio_storage.get()
            if rec.AcceptWaveform(data):
                callback(json.loads(rec.Result())["text"])
            else:
                print(rec.PartialResult())
                

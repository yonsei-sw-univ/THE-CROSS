import scipy
import tensorflow_hub as hub
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

siren_classesNum = [317, 318, 319, 390]


class SirenDetector:

    def __init__(self):
        self.model = hub.load('https://tfhub.dev/google/yamnet/1')
        self.fs = 16000
        self.duration = 2  # seconds
        self.isRun = True

    def run(self):
        while self.isRun:
            result = sd.rec(self.duration * self.fs, samplerate=self.fs, channels=1, dtype=np.float32).reshape(-1)
            sd.wait()
            scores, embeddings, log_mel_spectrogram = self.model(result)
            print('scores : ', scores.numpy().mean(axis=0).argmax())


if __name__ == "__main__":
    siren = SirenDetector()
    siren.run()

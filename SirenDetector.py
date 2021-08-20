import threading

import tensorflow_hub as hub
import sounddevice as sd
import numpy as np

siren_classesNum = [316, 317, 318, 319, 390, 391]


class SirenDetector(threading.Thread):

    def __init__(self):
        self.model = hub.load('https://tfhub.dev/google/yamnet/1')
        self.fs = 16000
        self.duration = 2  # seconds
        self.isRun = True
        self.isSirenDetected = False

    def run(self):
        self.isRun = True
        while self.isRun:
            result = sd.rec(self.duration * self.fs, samplerate=self.fs, channels=1, dtype=np.float32).reshape(-1)
            sd.wait()
            scores, embeddings, log_mel_spectrogram = self.model(result)
            prediction = np.mean(scores, axis=0)
            top5 = np.argsort(prediction)[::-1][:5]

            siren_result = False
            for wavNum in top5:
                if wavNum in siren_classesNum:
                    siren_result = True

            self.isSirenDetected = siren_result

    def isSiren(self):
        return self.isSirenDetected

    def stop(self):
        self.isRun = False
        self.stop()


if __name__ == "__main__":
    siren = SirenDetector()
    siren.run()

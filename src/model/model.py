from transformers import pipeline

class AutoSpeechRecognition():
    def __init__(self, path):
        self.transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small")
        output = self.transcriber(path)['text']
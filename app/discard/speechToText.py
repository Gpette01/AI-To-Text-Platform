import speech_recognition as sr

from pydub import AudioSegment
import math

import subprocess
class SplitWavAudioMubin():
    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '/' + filename
        self.audio = AudioSegment.from_wav(self.filepath)
        

    
    def get_duration(self):
        return self.audio.duration_seconds
    
    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 60 * 1000
        t2 = to_min * 60 * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(self.folder + '/' + split_filename, format="wav")
        
    def multiple_split(self, min_per_split):
        totalFiles = 0
        total_mins = math.ceil(self.get_duration() / 60)
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + self.filename
            self.single_split(i, i+min_per_split, split_fn)
            print(str(i) + ' Done')
            totalFiles += 1
            if i == total_mins - min_per_split:
                print('All splited successfully')
        
        return totalFiles


def speech_to_text(audio_file, language="en-US"):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language=language)
        return text

# Example usage
if __name__ == "__main__":
    folder = './'
    file = 'file2.wav'
    
    split_wav = SplitWavAudioMubin(folder, file)
    totalFiles = split_wav.multiple_split(min_per_split=1)
    print("Total files: ", totalFiles)
    for i in range(totalFiles):
        name = str(i) + '_' + file
        print(name)
        try:
            text = speech_to_text(name, language="el-GR")
            # Write the transcription to a file
            with open("transcription.txt", "a") as log:
                log.write(text)
            print("Transcription: ", text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
    print("DONE")
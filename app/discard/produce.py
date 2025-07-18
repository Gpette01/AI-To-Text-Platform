import subprocess
import os
import glob
import time


from pydub import AudioSegment
import math

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

def main():
    
    # Start the subprocess and ensure the parent script waits
    # wait_time = int(os.getenv("SAMPLE_TIME"))
    # run = subprocess.Popen(['python3', 'record.py', '--frequency', '97.2e6'])
    # time.sleep(wait_time)
    # print("Recording stoped")
    # run.terminate()
    # run.wait()
    # Optionally wait for the process to finish if needed
    # run.wait()
   

    # Uncomment and adjust as needed
    # time.sleep(int(os.getenv("SAMPLE_TIME", 10)))
    # run.kill()

    # Uncomment and adjust as needed
    

    # folder = './'
    # file = 'file.wav'
    
    # split_wav = SplitWavAudioMubin(folder, file)
    # totalFiles = split_wav.multiple_split(min_per_split=1)
    # print("Total files: ", totalFiles)
    
    subprocess.run(['python3','speechToTextLocal.py', 'file.wav'])
    
    # subprocess.run(['python3','speakerDiarization.py', 'file.wav'])
    
    # Uncomment and adjust as needed
    # # Remove all .wav files in the current directory
    # wav_files = glob.glob("*.wav")
    # for file in wav_files:
    #     os.remove(file)

if __name__ == "__main__":
    main()

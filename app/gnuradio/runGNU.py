from gnuradio.findChannel import findChannel
import subprocess
import time
import os
import wave

from gnuradio.receiver import send_fc

from dotenv import load_dotenv
load_dotenv('/etc/profile.d/rtl_device_index.sh')

from clustering import SpeakerIdentifier

import sys
import re

RTL_INDEX_DEVICE = int(os.getenv('RTL_DEVICE_INDEX'))

def nextFile():
    directory = "/app/gnuradio/wavFiles/"
    files = [f for f in os.listdir(directory) if f.startswith("file_") and f.endswith(".wav")]
    if not files:
        return f"{directory}file_01.wav"
    files.sort()
    last_file = files[-1]
    last_number = int(last_file.split('_')[1].split('.')[0])
    next_number = last_number + 1
    return f"{directory}file_{next_number:02d}.wav"

def runGNU(createNewFile, file, identifier):
    print("Scanning for channels...")
    channel = findChannel()
    if createNewFile:
        print("Creating a new file")
        filePath = nextFile()
         # Check if the file exists, if not, create it
        if not os.path.exists(filePath):
            print(f"File {filePath} does not exist. Creating a new file.")
            with wave.open(filePath, "w") as wav_file:
                wav_file.setnchannels(1)  # Mono (1 channel)
                wav_file.setsampwidth(2)  # 16-bit (2 bytes per sample)
                wav_file.setframerate(48000)  # 48 kHz sample rate
                wav_file.writeframes(b"")  # No audio data, just a valid header
                
    else:
        # Use the provided file path
        filePath = file
        
    
    print("Channel found: ", channel)
    print("Running GNU Radio...")
    gnuProcess = subprocess.Popen(["python3.11", "gnuradio/Thesis.py", "--fc", str(channel)+"e6", "--file", filePath, "--device", str(RTL_INDEX_DEVICE)],
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
                                            )
    silence_duration = 0  # Default if no silence message appears
    pattern = re.compile(r"Inserting ([\d.]+) seconds of silence")

    # Read process output in real-time and print it while scanning for silence info
    for line in iter(gnuProcess.stdout.readline, ''):
        sys.stdout.write(line)  # Print the output to the console immediately
        sys.stdout.flush()      # Ensure real-time printing

        match = pattern.search(line)
        if match:
            silence_duration = float(match.group(1))
            break  # Stop reading after detecting silence duration

    gnuProcess.stdout.close()
    
    print("FOUND: ", silence_duration)
    
    if createNewFile:
        return gnuProcess, filePath, SpeakerIdentifier(), silence_duration
    else:
        return gnuProcess, filePath, identifier, silence_duration

def updateFc():
    print("Finding new frequency...")
    channel = findChannel()
    send_fc(channel + "e6")
    

if __name__ == "__main__":
   a = runGNU()
   time.sleep(10)
   a[0].kill()

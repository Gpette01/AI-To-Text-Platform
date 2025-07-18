import sys
import os
import threading
import customtkinter as ctk  # Import CustomTkinter
from tkintermapview import TkinterMapView
from tkinter import PhotoImage
import math
import random
import re
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from tkinter.scrolledtext import ScrolledText
from speechToTextLocal import transcribe_audio, defineModel, checkForSilence
from threadPlot import start_server
from gnuradio.runGNU import runGNU
from gnuradio.runGNU import updateFc

import subprocess

from stop_flag import transcription_stop_flag
from stop_flag import plot_stop_flag
from stop_flag import doa_stop_flag

from db.connect import connect_to_database, retreive_text, insert_doa

import socket
from kraken.runKraken import startKrakenMock, stopKrakenMock
import json

from httpRequests import postWebServerData

from PIL import Image, ImageTk

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QGuiApplication

# Initialize CustomTkinter
ctk.set_appearance_mode("Dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

# Global variables to hold references
transcription_thread = None
print_transcription_thread = None
receiveUpdateMapThread = None
gnu_thread = None
silence_thread = None
wavFile = None
last_position = None

plot_process = []

identifier = None

def get_wav_files(directory="/app/gnuradio/wavFiles"):
    try:
        # List all files in the directory
        files = os.listdir(directory)
        # Filter only .wav files
        wav_files = [wavFile for wavFile in files if wavFile.endswith(".wav")]
        # print(wav_files)
        # Sort files by extracting numbers using a regex pattern
        wav_files_filtered = [f for f in wav_files if re.search(r'\d+', f)]
        sorted_wav_files = sorted(wav_files_filtered, key=lambda x: int(re.search(r'\d+', x).group()))   
        # print(wav_files_filtered)     
        return wav_files
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# def update_selected_file(selected_file):
#     global secondWavFile
#     secondWavFile = "/app/gnuradio/wavFiles/" + selected_file
#     print(f"Selected wavFile: {secondWavFile}")

import sounddevice as sd
import wave
import numpy as np


def play_wav(file_path):
    subprocess.Popen([
        'ffmpeg', '-hide_banner', '-loglevel', 'error',  # Suppress unnecessary output
        '-i', file_path,  # Input file
        '-f', 'alsa', 'default'  # Output to ALSA (Linux) or replace with proper audio output
    ])

def showDatabaseTranscriptions(text_widget, timeReference, selected_file):
    print(f"File: {selected_file}")
    if(selected_file == None or os.path.basename(selected_file) == "Choose wav file"):
        text_widget.insert(ctk.END, "Choose wav file" + "\n")
        text_widget.see(ctk.END)
        return
    
    # text_widget.insert(ctk.END, "Transcription from DB: " + selected_file + "\n")
    text_widget.see(ctk.END)
    conn = connect_to_database()
    # secondWavFile = "/app/gnuradio/wavFiles/distanceTest.wav"
    selected_file = "/app/gnuradio/wavFiles/" + selected_file
    
    play_wav(selected_file)

    transcriptions = retreive_text(conn, selected_file)
    processed_texts = set()  # To track already processed texts
    for text, timeStart, timeEnd, speaker, avg_doa, band in transcriptions:
        if text not in processed_texts:
            processed_texts.add(text)
            transcription_entry = (
                f"\n{'-'*50}\n"  # Separator line
                f"📌 [{(timeReference + timedelta(seconds=float(timeStart))).strftime('%Y-%m-%d %H:%M:%S')} - "
                f"{(timeReference + timedelta(seconds=float(timeEnd))).strftime('%Y-%m-%d %H:%M:%S')}]\n"
                f"🎙️ Speaker: {speaker}\n"
                f"📝 {text}\n"
                f"🎯 Avg DOA: {avg_doa}\n"
                f"🔊 Band: {band}\n"
                f"Wav File: {selected_file}\n"
                
            )  
            # ******************
            # data = {
            #     "text": text,
            #     "start_time": (timeReference + timedelta(seconds=float(timeStart))).strftime('%Y-%m-%d %H:%M:%S%z'),
            #     "end_time": (timeReference + timedelta(seconds=float(timeEnd))).strftime('%Y-%m-%d %H:%M:%S%z'),
            #     "speaker": speaker,
            #     "avg_doa": str(avg_doa),
            #     "band": band
            # }
            # thread = threading.Thread(target=postWebServerData, args=(data,))
            # thread.daemon = True  # Allows program to exit even if thread is running
            # thread.start()
            # ******************
            print(transcription_entry, end=" ", flush=True)
            text_widget.insert(ctk.END, transcription_entry + " ")
            text_widget.see(ctk.END)
        
        
def print_transcription(text_widget, timeReference):
    global wavFile
    conn = connect_to_database()
    # text_widget.insert(ctk.END, "Wav wavFile: " + wavFile + "\n")
    try:
        processed_texts = set()  # To track already processed texts

        while not transcription_stop_flag.is_set():
            # Retrieve text entries for the given wav wavFile
            transcriptions = retreive_text(conn, wavFile)
            
            # Process and display any new transcriptions
            for text, timeStart, timeEnd, speaker, avg_doa, band in transcriptions:
                if text not in processed_texts:
                    processed_texts.add(text)
                    if transcription_stop_flag.is_set():
                        print("Stop flag set during word processing, breaking...")
                        break
                    transcription_entry = (
                        f"\n{'-'*50}\n"  # Separator line
                        f"📌 [{(timeReference + timedelta(seconds=float(timeStart))).strftime('%Y-%m-%d %H:%M:%S')} - "
                        f"{(timeReference + timedelta(seconds=float(timeEnd))).strftime('%Y-%m-%d %H:%M:%S')}]\n"
                        f"🎙️ Speaker: {speaker}\n"
                        f"📝 {text}\n"
                        f"🎯 Avg DOA: {avg_doa}\n"
                        f"🔊 Band: {band}\n"
                        f"Wav File: {wavFile}\n"

                    ) 
                    # ******************
                    # data = {
                    #     "text": text,
                    #     "start_time": (timeReference + timedelta(seconds=float(timeStart))).strftime('%Y-%m-%d %H:%M:%S%z'),
                    #     "end_time": (timeReference + timedelta(seconds=float(timeEnd))).strftime('%Y-%m-%d %H:%M:%S%z'),
                    #     "speaker": speaker,
                    #     "avg_doa": str(avg_doa),
                    #     "band": band
                    # }
                    # thread = threading.Thread(target=postWebServerData, args=(data,))
                    # thread.daemon = True  # Allows program to exit even if thread is running
                    # thread.start()
                    # ******************
                    print(transcription_entry, end=" ", flush=True)
                    text_widget.insert(ctk.END, transcription_entry + " ")
                    text_widget.see(ctk.END)
            
            # Check for new entries every second
            time.sleep(1)
    except KeyboardInterrupt:
        print("Printing stopped by user")
    except Exception as e:
        print(f"Error during transcription printing: {e}")
    finally:
        print("Database connection closed. Printing finished.")

from clustering import SpeakerIdentifier
def start_transcription(text_widget, model, timeReference):
    print("Starting transcription...")
    
    transcription_stop_flag.clear()  # Clear the stop flag to start the threads
    global transcription_thread, print_transcription_thread, wavFile, identifier
    # ******************
    identifier = SpeakerIdentifier()
    # time.sleep(50)
    wavFile = "/app/gnuradio/wavFiles/FinalExperiment.wav"
    # ******************
    if wavFile is None:
        text_widget.insert(ctk.END, "Choose wav file" + "\n")
        text_widget.see(ctk.END)
        return
    # wavFile = "/app/gnuradio/wavFiles/file_22.wav"
    transcription_thread = threading.Thread(target=transcribe_audio, args=(wavFile, model, identifier))
    transcription_thread.daemon = True  # Set thread as daemon so it exits when main program exits
    transcription_thread.start()
        
    print_transcription_thread = threading.Thread(target=print_transcription, args=(text_widget,timeReference))
    print_transcription_thread.daemon = True  # Set thread as daemon so it exits when main program exits
    print_transcription_thread.start()

def stop_transcription():
    transcription_stop_flag.set()  # Set the stop flag to stop the threads
    transcription_thread.join()
    print_transcription_thread.join()
    print("Threads stopped.")

def startSilenceCheck(silence_duration, seconds=5):
    global wavFile, gnu_thread, plot_stop_flag, last_position
    print(f"Stop flag {not plot_stop_flag.is_set()}")
    if not plot_stop_flag.is_set():
        last_position = checkForSilence(wavFile, plot_stop_flag, last_position, seconds, silence_duration)
        print("Silence check complete.")
        # updateFc()
        if not plot_stop_flag.is_set():
            gnu_thread.kill()
            time.sleep(1)
            startCapture(False)
        

def startCapture(createNewFile):
    print("Running capture...")
    global gnu_thread, wavFile, silence_thread, last_position, identifier
    plot_stop_flag.clear()
    silence_duration = 0
    if createNewFile:
        last_position = 0
        # identifier = SpeakerIdentifier()
        gnu_thread, wavFile, identifier, _ = runGNU(createNewFile, wavFile, identifier)
    else:
        gnu_thread, wavFile, identifier, silence_duration  = runGNU(createNewFile, wavFile, identifier)
        
    print("Running silence check...")
    
    silence_thread = threading.Thread(target=startSilenceCheck, args=(silence_duration, 200, ))
    silence_thread.daemon = True  # Set thread as daemon so it exits when main program exits
    silence_thread.start()

def stopCapture():
    global gnu_thread, silence_thread
    print("Stopping capture...")
    gnu_thread.kill()
    plot_stop_flag.set()
    
# class DOAMap:
#     def __init__(self, parent):
#         self.parent = parent
#         self.map_widget = None
#         self.lines = []
#         self.map_window = None

#     def show_map(self):
#         """Create and show the map window."""
#         # Create a new map window
#         self.map_window = ctk.CTkToplevel(self.parent)
#         self.map_window.title("DOA Map")
#         self.map_window.geometry("800x500")

#         # Set the custom behavior for the X button
#         self.map_window.protocol("WM_DELETE_WINDOW", lambda: stopDOA(self))
        
#         # Initialize map widget
#         self.map_widget = TkinterMapView(self.map_window, corner_radius=0)
#         self.map_widget.pack(fill="both", expand=True)

#         # Set initial position
#         self.map_widget.set_position(
#             float(os.getenv("CURRENT_LAT", 0)), float(os.getenv("CURRENT_LONG", 0))
#         )
#         self.map_widget.set_zoom(15)

#     def add_line(self, angle):
#         """Add a line on the map."""
#         if not self.map_widget:
#             print("Map widget is not initialized.")
#             return

#         current_location = (float(os.getenv("CURRENT_LAT", 0)), float(os.getenv("CURRENT_LONG", 0)))
#         line_length = 0.009  # Line length in degrees (adjust as needed)

#         # Calculate endpoint using direction and length
#         end_latitude = current_location[0] + line_length * math.sin(math.radians(angle))
#         end_longitude = current_location[1] + line_length * math.cos(math.radians(angle))

#         # Draw the line on the map and store the reference
#         line = self.map_widget.set_path([current_location, (end_latitude, end_longitude)])
#         self.lines.append(line)

#     def remove_line(self):
#         """Remove the last added line from the map."""
#         if not self.map_widget:
#             print("Map widget is not initialized.")
#             return

#         if self.lines:
#             line = self.lines.pop()
#             line.delete()  # Delete the line from the map
#         else:
#             print("No lines to remove.")
    
#     def update_elements(self):
#         self.map_widget.update_idletasks()
    
#     def close_map(self):
#         """Close the map window."""
#         if self.map_window:
#             self.map_window.destroy()
#             print("Map window closed.")
#             self.map_window = None  # Clear reference to the map window

class DOAMap:
    def __init__(self, parent):
        self.parent = parent
        self.map_widget = None
        self.lines = []

        # Create a frame for the map inside the main window
        self.map_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.map_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initialize map widget
        self.map_widget = TkinterMapView(self.map_frame, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)

        # Set initial position
        self.map_widget.set_position(
            float(os.getenv("CURRENT_LAT", 0)), float(os.getenv("CURRENT_LONG", 0))
        )
        self.map_widget.set_zoom(15)

    # def add_line(self, angle):
    #     """Add a line on the map."""
    #     if not self.map_widget:
    #         print("Map widget is not initialized.")
    #         return

    #     current_location = (float(os.getenv("CURRENT_LAT", 0)), float(os.getenv("CURRENT_LONG", 0)))
    #     line_length = 0.009  # Line length in degrees (adjust as needed)

    #     # Calculate endpoint using direction and length
    #     end_latitude = current_location[0] + line_length * math.sin(math.radians(angle))
    #     end_longitude = current_location[1] + line_length * math.cos(math.radians(angle))

    #     # Draw the line on the map and store the reference
    #     line = self.map_widget.set_path([current_location, (end_latitude, end_longitude)])
    #     self.lines.append(line)
    def add_line(self, angle, line_width=1):
        """Add a line on the map with an optional icon at the starting point.

        Args:
            angle (float): The angle in degrees for the line's direction.
            line_width (int, optional): Thickness of the line. Defaults to 1.
            icon_source (str, optional): Path to the icon image file to display at the start.
                                        If None, no icon is added.
        """
        icon_source = "images/receiver.png"
        icon_size= (32,32)
        
        if not self.map_widget:
            print("Map widget is not initialized.")
            return

        # Get the current location from environment variables.
        current_lat = float(os.getenv("CURRENT_LAT", 0))
        current_lon = float(os.getenv("CURRENT_LONG", 0))
        current_location = (current_lat, current_lon)

        line_length = 0.009  # Line length in degrees (adjust as needed)

        # Calculate the endpoint using the provided angle.
        end_lat = current_lat + line_length * math.sin(math.radians(angle))
        end_lon = current_lon + line_length * math.cos(math.radians(angle))
        endpoint = (end_lat, end_lon)

        # Draw the line on the map (assuming set_path supports a width parameter).
        line = self.map_widget.set_path([current_location, endpoint], width=line_width)
        self.lines.append(line)

        # If an icon source is provided, resize and add the marker.
        if icon_source:
            try:
                # Open the image using Pillow and resize it
                pil_image = Image.open(icon_source)
                pil_image = pil_image.resize(icon_size, Image.Resampling.LANCZOS)

                # Convert to a Tkinter-compatible PhotoImage
                icon_image = ImageTk.PhotoImage(pil_image)

                # Place the marker on the map at the current location
                marker = self.map_widget.set_marker(current_lat, current_lon, icon=icon_image)

                # Store the reference to prevent garbage collection
                if not hasattr(self, "marker_images"):
                    self.marker_images = []
                self.marker_images.append(icon_image)

            except Exception as e:
                print(f"Error loading icon: {e}")
        
        return line
        
    def remove_line(self):
        """Remove the last added line from the map."""
        if self.lines:
            line = self.lines.pop()
            line.delete()  # Delete the line from the map
        else:
            print("No lines to remove.")

    def update_elements(self):
        self.map_widget.update_idletasks()

    def clear_map(self):
        """Clear all lines from the map."""
        for line in self.lines:
            line.delete()
        self.lines.clear()


def delayed_line_removal(doa_map, line, delay_seconds):
    """Remove a line after a specified delay."""
    time.sleep(delay_seconds)
    # print(line, "Removing line after delay")
    if line in doa_map.lines:  # Check if line still exists in the list
        print("Removing line from map")
        doa_map.lines.remove(line)
        line.delete()

def receiveUpdateMap(doa_map):
    conn = connect_to_database()
    UDP_IP = os.getenv("DOA_UDP_IP")
    UDP_PORT = int(os.getenv("DOA_UDP_PORT"))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}")
    
    while not doa_stop_flag.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            value = data.decode('utf-8')
            
            try:
                json_data = json.loads(value)
                timestamp = json_data.get("timestamp").replace("T", " ")
                theta_0 = json_data.get("theta_0")
                
                if theta_0 is None:
                    print(f"Invalid JSON received: {value}")
                    continue
                
                print(f"Received message: {theta_0} from {addr}")
                print(f"DOA INSERT TIMESTAMP: {timestamp}")
                insert_doa(conn, timestamp, int(float(theta_0)))
                
                # Add new line
                line = doa_map.add_line(int(float(theta_0)), 5)
                doa_map.update_elements()
                # print(line)
                # Start a thread to remove the line after 5 seconds
                removal_thread = threading.Thread(
                    target=delayed_line_removal,
                    args=(doa_map, line, 5)  # 5 seconds delay
                )
                removal_thread.daemon = True
                removal_thread.start()
                
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {value}")
        except KeyboardInterrupt:
            print("\nStopping UDP receiver.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
    
    sock.close()
        
    
def startDOA(doa_map):
    global receiveUpdateMapThread
    # doa_map.show_map()
    # startKrakenMock()
    receiveUpdateMapThread = threading.Thread(target=receiveUpdateMap, args=(doa_map,))
    receiveUpdateMapThread.daemon = True  # Set thread as daemon so it exits when main program exits
    receiveUpdateMapThread.start()
    # stopKraken()

def stopDOA(doa_map):
    # stopKrakenMock()
    doa_map.close_map()
    doa_stop_flag.set()
    
def toggle_receiving_buttons(start_button, stop_button, is_start_clicked):
    """Toggle the appearance of receiving buttons."""
    if is_start_clicked:
        start_button.configure(fg_color="#427fb4")  # Green when active
        stop_button.configure(fg_color="transparent")
    else:
        start_button.configure(fg_color="transparent")
        stop_button.configure(fg_color="#427fb4")  # Dark red when active

def toggle_transcription_buttons(start_button, stop_button, is_start_clicked):
    """Toggle the appearance of transcription buttons."""
    if is_start_clicked:
        start_button.configure(fg_color="#427fb4")  # Green when active
        stop_button.configure(fg_color="transparent")
    else:
        start_button.configure(fg_color="transparent")
        stop_button.configure(fg_color="#427fb4")  # Dark red when active
    
    
    

if __name__ == "__main__":
    model = defineModel()
    transcription_file = "transcription.txt"
    
    timeReference = datetime.now(ZoneInfo("Etc/GMT-2"))
    
    # Initialize main window
    root = ctk.CTk()
    root.title("Transcription Output")
    
    app = QApplication([])  # Needed for GUI operations
    screen = QGuiApplication.primaryScreen()
    available_geometry = screen.availableGeometry()
    
    usable_height = available_geometry.height()
    usable_width = available_geometry.width()

    # print(usable_width)
    # Set window size to half of the screen width and a fixed height
    window_width = usable_width // 2
    window_height = usable_height  # You can adjust this height as needed
    root.geometry(f"{window_width}x{window_height}+0+0")
    
    # Dropdown menu to select WAV files
    wav_files = get_wav_files()  # Get the list of WAV files
    wav_files.insert(0, "Choose wav file")
        
    # Create a main content frame to hold text box and dropdown list
    main_content_frame = ctk.CTkFrame(root, fg_color="transparent")
    main_content_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Textbox (Left Side)
    text_widget = ctk.CTkTextbox(
        main_content_frame, wrap="word", font=("Symbola", 15), 
        spacing3=8, padx=10, pady=10
    )    
    text_widget.pack(side="left", expand=True, fill="both", padx=10, pady=10)

    # Frame for Dropdown List (Right Side)
    dropdown_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
    dropdown_frame.pack(side="right", fill="y", padx=10)

    # Label for dropdown list
    dropdown_label = ctk.CTkLabel(dropdown_frame, text="Select WAV File")
    dropdown_label.pack(pady=5)
        
    # # Create a list-style dropdown (CTkOptionMenu) inside the frame
    # wav_file_dropdown = ctk.CTkOptionMenu(
    #     dropdown_frame,
    #     values=wav_files,  # List of WAV files
    #     command=update_selected_file  # Function to call when a selection is made
    # )
    # wav_file_dropdown.pack(fill="x", pady=5)

    # Scrollable frame to hold WAV file list
    wav_listbox = ctk.CTkScrollableFrame(dropdown_frame, fg_color="transparent", width=200, height=300)
    wav_listbox.pack(fill="both", expand=True, pady=5)

    for wav_file in wav_files[1:]:  # Skip "Choose wav file" entry
        file_button = ctk.CTkButton(
            wav_listbox, text=wav_file, fg_color="gray20", command=lambda f=wav_file: showDatabaseTranscriptions(text_widget, timeReference, f)
        )
        file_button.pack(fill="x", pady=2)

    
    # Load images using PIL
    start_transcription_img = Image.open("images/start.png")  # Ensure the path is correct
    stop_transcription_img = Image.open("images/stop.png")    # Ensure the path is correct
    start_receiving_img = Image.open("images/start.png")  # Ensure the path is correct
    stop_receiving_img = Image.open("images/stop.png")    # Ensure the path is correct

    # Convert PIL images to CTkImage
    start_transcription_ctk = ctk.CTkImage(light_image=start_transcription_img, dark_image=start_transcription_img, size=(50, 50))
    stop_transcription_ctk = ctk.CTkImage(light_image=stop_transcription_img, dark_image=stop_transcription_img, size=(50, 50))
    start_receiving_ctk = ctk.CTkImage(light_image=start_receiving_img, dark_image=start_receiving_img, size=(50, 50))
    stop_receiving_ctk = ctk.CTkImage(light_image=stop_receiving_img, dark_image=stop_receiving_img, size=(50, 50))

    # Create a parent frame to hold both sections
    main_buttons_frame = ctk.CTkFrame(root, fg_color="transparent")
    main_buttons_frame.pack(fill="x", pady=10)

    # Transcription Section (Left Side)
    transcription_frame = ctk.CTkFrame(main_buttons_frame, fg_color="transparent")
    transcription_frame.pack(side="left", expand=True, fill="both", padx=20)

    transcription_label = ctk.CTkLabel(transcription_frame, text="Transcription")
    transcription_label.pack()

    transcription_buttons_frame = ctk.CTkFrame(transcription_frame, fg_color="transparent")
    transcription_buttons_frame.pack(pady=5)

    start_transcription_button = ctk.CTkButton(
        transcription_buttons_frame, image=start_transcription_ctk, text="", fg_color="transparent", 
        width=50, height=50, command=lambda: [ 
            start_transcription(text_widget, model, timeReference),
            toggle_transcription_buttons(start_transcription_button, stop_transcription_button, True)
        ]
    )
    start_transcription_button.pack(side="left", padx=10)

    stop_transcription_button = ctk.CTkButton(
        transcription_buttons_frame, image=stop_transcription_ctk, text="", fg_color="transparent", 
        width=50, height=50, command=lambda: [
            stop_transcription(),
            toggle_transcription_buttons(start_transcription_button, stop_transcription_button, False)
        ]
    )
    stop_transcription_button.pack(side="left", padx=10)

    # Receiving Section (Right Side)
    receiving_frame = ctk.CTkFrame(main_buttons_frame, fg_color="transparent")
    receiving_frame.pack(side="right", expand=True, fill="both", padx=20)

    receiving_label = ctk.CTkLabel(receiving_frame, text="Receiving")
    receiving_label.pack()

    receiving_buttons_frame = ctk.CTkFrame(receiving_frame, fg_color="transparent")
    receiving_buttons_frame.pack(pady=5)

    start_plots_button = ctk.CTkButton(
        receiving_buttons_frame, image=start_receiving_ctk, text="", fg_color="transparent", 
        width=50, height=50, command=lambda: [
            startCapture(True),
            toggle_receiving_buttons(start_plots_button, stop_plots_button, True)
        ]
    )
    start_plots_button.pack(side="left", padx=10)

    stop_plots_button = ctk.CTkButton(
        receiving_buttons_frame, image=stop_receiving_ctk, text="", fg_color="transparent", 
        width=50, height=50, command=lambda: [
            stopCapture(),
            toggle_receiving_buttons(start_plots_button, stop_plots_button, False)
        ]
    )
    stop_plots_button.pack(side="left", padx=10)


    doa_map = DOAMap(root)
    startDOA(doa_map)
    
    # Button to open the DOA map
    # Correcting the button creation
    # open_map_button = ctk.CTkButton(root, text="Open DOA Map", command=lambda: startDOA(doa_map))
    # open_map_button.pack(pady=10)

    # Button to add a line programmatically
    # add_line_button = ctk.CTkButton(
    #     root, text="Add Line to Map", command=lambda: loopLines(doa_map)
    # )
    # add_line_button.pack(pady=10)
    
    
    root.mainloop()

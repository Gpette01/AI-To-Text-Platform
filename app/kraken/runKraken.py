import socket
import os
import time
import threading
import numpy as np
from pynput import keyboard  # Using pynput for keyboard events

import json
from datetime import datetime
from zoneinfo import ZoneInfo

# Configure the UDP sender
UDP_IP = os.getenv("DOA_UDP_IP", "127.0.0.1")  # Default to localhost if DOA_UDP_IP is not set
UDP_PORT = int(os.getenv("DOA_UDP_PORT", 4200))  # Default port if DOA_UDP_PORT is not set

# Create the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

krakenMockThread = None  # To control the thread
krakenMockRunning = False  # To manage the sending loop

# Predefined means array
means_array = [250, 180, 100, 30]
current_mean = 30  # Default mean
key_pressed = False  # Track if 's' is pressed

def on_press(key):
    global current_mean, key_pressed
    try:
        if key.char == 's' and not key_pressed:  # Press 's' to select the next mean
            key_pressed = True
            # Select the next mean from the array
            current_mean_index = means_array.index(current_mean)
            next_index = (current_mean_index + 1) % len(means_array)  # Cycle through the array
            current_mean = means_array[next_index]
    except AttributeError:
        pass

def on_release(key):
    global key_pressed
    try:
        if key.char == 's':
            key_pressed = False  # Release 's' stops changing the mean
    except AttributeError:
        pass

# Set up listener for keyboard events
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def startKrakenMock():
    """Start the Kraken Mock UDP sender in a separate thread."""
    global krakenMockThread, krakenMockRunning
    if krakenMockThread and krakenMockThread.is_alive():
        print("Kraken mock is already running.")
        return

    krakenMockRunning = True
    krakenMockThread = threading.Thread(target=krakenMockLoop, daemon=True)
    krakenMockThread.start()
    print("Kraken mock started.")


def krakenMockLoop():
    """The loop that sends UDP messages."""
    global current_mean
    try:
        while krakenMockRunning:
            if key_pressed:  # Check if 's' is pressed
                # Use the selected mean to generate a normal distribution
                random_number = int(np.clip(np.random.normal(current_mean, 1), 1, 360))
            else:
                # Send 0 when 's' is not pressed
                random_number = 0
            
            # Create JSON payload
            payload = {
                "timestamp": datetime.now(ZoneInfo("Etc/GMT-1")).isoformat(),
                "theta_0": random_number
            }
            
            # Convert to JSON string and encode
            message = json.dumps(payload).encode('utf-8')
            print(f"Sent: {payload}")
            
            sock.sendto(message, (UDP_IP, UDP_PORT))
            time.sleep(0.3)  # Wait before sending the next message
    except Exception as e:
        print(f"Error in Kraken mock: {e}")
    finally:
        print("Kraken mock loop exited.")


def stopKrakenMock():
    """Stop the Kraken Mock UDP sender."""
    global krakenMockRunning
    krakenMockRunning = False
    if krakenMockThread:
        krakenMockThread.join()  # Wait for the thread to finish
    print("Kraken mock stopped.")


if __name__ == "__main__":
    print("Testing Kraken Mock...")
    startKrakenMock()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stopKrakenMock()

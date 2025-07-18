import numpy as np
import wave
import os
import time
from gnuradio import gr

class blk(gr.sync_block):  # Inherits from gr.sync_block
    """WAV File Appender Block with Gap Detection and Silence Insertion"""

    def __init__(self, file='/app/file.wav'):
        """Initialize the block with the file path"""
        gr.sync_block.__init__(
            self,
            name='WAV File Appender',   # Will show up in GRC
            in_sig=[np.float32],        # Input signature
            out_sig=None                # No output
        )
        self.file = file
        self.file_handle = None
        
    def is_new_file(self, file_path):
        """Check if the file is new (creation time == modification time)."""
        try:
            return True if os.path.getsize(file_path) == 44 else False
        except Exception as e:
            print(f"Error checking file: {e}")
            return False

    def start(self):
        """
        Open the WAV file for appending (or create it if it doesn't exist).
        If the file already exists, check its last modification time.
        Calculate the time gap between that modification and now, and if
        the gap is significant, insert the corresponding duration of silence.
        """
        if os.path.exists(self.file):
            # Open existing WAV file in read/write binary mode without truncating.
            self.file_handle = open(self.file, 'rb+')
            # Use the wave module to read the existing header.
            wav_reader = wave.open(self.file_handle, 'rb')
            self.params = wav_reader.getparams()
            self.n_frames = self.params.nframes
            wav_reader.close()
            # Move the file pointer to the end of the data chunk.
            self.file_handle.seek(0, os.SEEK_END)

            # **Skip silence insertion if the file is empty (newly created)**
            if self.is_new_file(self.file):
                print("Inserting 0 seconds of silence new wav file.")
                return True
            # print("PATH: ", self.file)
            # print(self.is_new_file(self.file))

            # Check the file's last modification time.
            last_modified = os.path.getmtime(self.file)
            now = time.time()
            gap = now - last_modified  # gap in seconds
            threshold = 0.1  # Only add silence if the gap is more than 100 ms.
            if gap > threshold:
                print(f"Inserting {gap:.2f} seconds of silence due to gap in file modification time.")
                self.append_silence(gap)
        else:
            # Create a new WAV file.
            self.file_handle = open(self.file, 'wb')
            n_channels = 1
            sampwidth = 2  # 16 bits per sample
            framerate = 48000
            comptype = 'NONE'
            compname = 'not compressed'
            # Save parameters as a tuple.
            self.params = (n_channels, sampwidth, framerate, 0, comptype, compname)
            # Write the initial header.
            wav_writer = wave.open(self.file_handle, 'wb')
            wav_writer.setparams(self.params)
            wav_writer.close()
            self.n_frames = 0
        return True

    def append_silence(self, duration_seconds):
        """
        Append a block of silence to the WAV file.
        
        :param duration_seconds: The duration of silence (in seconds) to append.
        """
        try:
            # Try to get framerate from a namedtuple (if available)
            framerate = self.params.framerate
        except AttributeError:
            # Otherwise, use index 2 from the parameters tuple.
            framerate = self.params[2]
        # Calculate the number of samples needed.
        n_samples = int(duration_seconds * framerate)
        # Create an array of zeros (16-bit PCM silence).
        silence = np.zeros(n_samples, dtype=np.int16)
        # Write the silence samples to the file.
        self.file_handle.write(silence.tobytes())
        # Update the frame count.
        self.n_frames += n_samples

    def work(self, input_items, output_items):
        """Write the incoming audio data to the WAV file."""
        in0 = input_items[0]
        # Convert float32 data to int16.
        data = (in0 * 32767).astype(np.int16)
        self.file_handle.write(data.tobytes())
        self.n_frames += len(data)
        return len(in0)

    def stop(self):
        """Update the WAV file header and close the file when the flowgraph stops."""
        self.file_handle.seek(0)
        wav_writer = wave.open(self.file_handle, 'rb+')
        try:
            # If self.params is a namedtuple, update nframes using _replace.
            params = self.params._replace(nframes=self.n_frames)
        except AttributeError:
            # Otherwise, rebuild the tuple manually.
            n_channels, sampwidth, framerate, _, comptype, compname = self.params
            params = (n_channels, sampwidth, framerate, self.n_frames, comptype, compname)
        wav_writer.setparams(params)
        wav_writer.close()
        self.file_handle.close()
        return True

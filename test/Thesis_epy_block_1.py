"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
import wave
import os
from gnuradio import gr

class blk(gr.sync_block):  # Inherits from gr.sync_block
    """WAV File Appender Block"""

    def __init__(self, file='/app/file.wav'):  # default arguments only
        """Initialize the block with the file path"""
        gr.sync_block.__init__(
            self,
            name='WAV File Appender',   # Will show up in GRC
            in_sig=[np.float32],        # Input signature
            out_sig=None                # No output
        )
        self.file = file
        self.file_handle = None

    def start(self):
        """Open the WAV file for appending or create it if it doesn't exist"""
        if os.path.exists(self.file):
            # Open existing WAV file in read/write binary mode without truncating
            self.file_handle = open(self.file, 'rb+')
            # Use wave module to read existing header
            wav_reader = wave.open(self.file_handle, 'rb')
            self.params = wav_reader.getparams()
            self.n_frames = self.params.nframes
            wav_reader.close()
            # Move file pointer to the end of the data chunk
            self.file_handle.seek(0, os.SEEK_END)
        else:
            # Create a new WAV file
            self.file_handle = open(self.file, 'wb')
            # Set parameters
            n_channels = 1
            sampwidth = 2  # 16 bits per sample
            framerate = 48000
            comptype = 'NONE'
            compname = 'not compressed'
            self.params = (n_channels, sampwidth, framerate, 0, comptype, compname)
            # Write initial header
            wav_writer = wave.open(self.file_handle, 'wb')
            wav_writer.setparams(self.params)
            wav_writer.close()
            self.n_frames = 0
        return True

    def work(self, input_items, output_items):
        """Write the incoming audio data to the WAV file"""
        in0 = input_items[0]
        # Convert float32 data to int16
        data = (in0 * 32767).astype(np.int16)
        # Write the data to the file
        self.file_handle.write(data.tobytes())
        # Update the frame count
        self.n_frames += len(data)
        return len(in0)

    def stop(self):
        """Update the WAV file header and close the file when the flowgraph stops"""
        # Update the header with the new frame count
        self.file_handle.seek(0)
        wav_writer = wave.open(self.file_handle, 'rb+')
        # Update nframes in the params
        params = self.params._replace(nframes=self.n_frames)
        wav_writer.setparams(params)
        wav_writer.close()
        # Close the file handle
        self.file_handle.close()
        return True


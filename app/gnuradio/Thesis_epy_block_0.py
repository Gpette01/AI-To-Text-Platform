import numpy as np
from gnuradio import gr

class complex_threshold(gr.sync_block):
    def __init__(self, low_threshold=1.0):
        gr.sync_block.__init__(self,
            name="Noise Threshold",
            in_sig=[np.complex64],
            out_sig=[np.complex64])
        self.low_threshold = low_threshold

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        # Apply threshold efficiently using numpy operations
        magnitude = np.abs(in0)

        # Zero the values below the low threshold
        out[:] = np.where(magnitude >= self.low_threshold, in0, 0)

        return len(output_items[0])


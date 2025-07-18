import threading

# Global stop flag
transcription_stop_flag = threading.Event()

plot_stop_flag = threading.Event()

doa_stop_flag = threading.Event()
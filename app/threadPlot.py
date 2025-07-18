import socket
import numpy as np
import matplotlib.pyplot as plt
import sys
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5 import FigureManagerQT


from stop_flag import plot_stop_flag


def initialize_plot(plot_name):
    global fig, ax, line
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'r-')  # Initialize an empty plot
    
    plt.show(block=False)  # Non-blocking show to allow code execution to continue
    # Get the current figure manager and disable the close button
    manager = plt.get_current_fig_manager()
    if isinstance(manager, FigureManagerQT):
        manager.window.setWindowFlags(manager.window.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        manager.window.setWindowTitle(plot_name)
        manager.window.show()
        # Move the window to the right side of the screen
        screen_geometry = manager.window.screen().geometry()
        window_width = manager.window.frameGeometry().width()
        window_height = manager.window.frameGeometry().height()
        manager.window.move(screen_geometry.width() - window_width, (screen_geometry.height() - window_height) // 2)

def update_plot(data):
    # Convert the binary data back to a numpy array
    data_array = np.frombuffer(data, dtype=np.float32)
    
    # Update the plot with the new data
    line.set_xdata(np.arange(len(data_array)))
    line.set_ydata(data_array)
    
    ax.relim()  # Recompute the data limits
    ax.autoscale_view()  # Rescale the view
    plt.draw()
    plt.pause(0.01)  # Pause to update the plot


def start_server(port_num, host, name):
    global fig
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (host, port_num)
    print(f'Starting up on {server_address[0]}:{server_address[1]}')
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)

    # Initial plot setup
    initialize_plot(name)

    while not plot_stop_flag.is_set():
        try:
            print('Waiting for a connection...')
            # Accept a connection
            client_socket, client_address = server_socket.accept()
            try:
                print(f'Connection from {client_address}')

                # Receive the data in small chunks and handle it as binary
                while not plot_stop_flag.is_set():
                    data = client_socket.recv(4096)  # Increase buffer size for real-time data
                    if data:
                        # Print the raw bytes, or process them directly
                        # print(f'Received binary data: {data}')

                        # Update the plot with the received data
                        update_plot(data)

                        # Echo the data back (optional)
                        client_socket.sendall(data)
                    else:
                        print('No more data from', client_address)
                        break

                    
            except Exception as e:
                print(f"Error during connection handling: {e}")
            finally:
                client_socket.close()
                print(f'Connection closed from {client_address}')
        except KeyboardInterrupt:
            print("Server interrupted by user.")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")

    server_socket.close()
    print("Server socket closed.")
    plt.close(fig)  # Close the plot window
    plt.close('all')  # Ensure all plot windows are closed
    print(plt.fignum_exists(fig.number))    

if __name__ == '__main__':
    start_server(int(sys.argv[1]), sys.argv[2], sys.argv[3])

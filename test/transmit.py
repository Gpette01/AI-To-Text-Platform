import socket
import numpy as np
import time
import sys

def transmit_data():
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address
    server_address = ('localhost', int(sys.argv[1]))
    print(f'Connecting to server on {server_address[0]}:{server_address[1]}')
    client_socket.connect(server_address)

    try:
        while True:
            # Generate fake plot data from a normal distribution with mean 0 and standard deviation 1
            fake_data = np.random.normal(loc=0.0, scale=1.0, size=100).astype(np.float32)  # 100 random float32 numbers from normal distribution
            
            # Convert the numpy array to raw binary data
            data = fake_data.tobytes()

            # Send data to the server
            client_socket.sendall(data)
            print(f'Sent data: {fake_data}')

            # Wait for a short period before sending the next batch of data
    except KeyboardInterrupt:
        print("Transmission interrupted by user.")
    finally:
        print("Closing connection.")
        client_socket.close()

if __name__ == "__main__":
    transmit_data()
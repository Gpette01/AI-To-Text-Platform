import socket
import json
from queue import Queue

host = "localhost"
port = 4200

def fc_receiver(data_queue):
    try:
        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind((host, port))  # Bind to the host and port
            print(f"Listening for UDP packets on {host}:{port}...")

            while True:
                # Receive data from a client
                data, client_address = udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes
                print(f"Received data from {client_address}: {data.decode('utf-8')}")

                try:
                    # Parse the JSON data
                    json_data = json.loads(data.decode('utf-8'))
                    fc_value = json_data.get("fc")

                    if fc_value is not None:
                        print(f"Extracted fc value: {fc_value}")
                        data_queue.put(fc_value)
                        # Perform your action with fc_value here
                    else:
                        print("fc key not found in JSON data.")

                except json.JSONDecodeError:
                    print("Error: Received data is not valid JSON.")
                except Exception as e:
                    print(f"An error occurred: {e}")

    except Exception as e:
        print(f"An error occurred with the receiver: {e}")
        
def send_fc(fc_value, host='localhost', port=4200):
    try:
        # Prepare JSON data
        data = json.dumps({"fc": fc_value}).encode('utf-8')

        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Send the data to the specified host and port
            udp_socket.sendto(data, (host, port))
            print(f"Data sent to {host}:{port}: {data.decode('utf-8')}")

    except Exception as e:
        print(f"An error occurred: {e}")
    

# # Run the receiver
if __name__ == "__main__":
    # fc_receiver()
    send_fc(120e6)

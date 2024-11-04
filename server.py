import hashlib
import socket
import os

def start_server(host='localhost', port=5000):
    """Start the server and listen for incoming client connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    try:
        while True:
            # Accept a new client connection
            client_socket, addr = server_socket.accept()
            print(f"Connection established from {addr}")
            receive_file(client_socket)
            client_socket.close()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()
        print("Server closed.")

def receive_file(client_socket):
    """Receive a file from the client and save it to the backup directory."""
    file_name = client_socket.recv(1024).decode().strip()
    print(f"Received file name: '{file_name}'")
    client_socket.sendall(b'ACK')  # Send acknowledgment

    try:
        file_size_str = client_socket.recv(1024).decode().strip()
        file_size = int(file_size_str)
        print(f"File size received: {file_size} bytes")
        client_socket.sendall(b'ACK')  # Send acknowledgment
    except ValueError:
        print(f"Invalid file size received: {file_size_str}")
        return

    file_path = os.path.join("backup", file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Initialize hasher for checksum calculation
    hasher = hashlib.sha256()

    with open(file_path, 'wb') as f:
        bytes_received = 0
        while bytes_received < file_size:
            data = client_socket.recv(4096)
            if not data:  # Break if no more data is received
                break
            f.write(data)
            hasher.update(data)  # Update checksum
            bytes_received += len(data)
            print(f"Bytes received: {bytes_received}/{file_size}")

    client_socket.sendall(b'ACK')  # Send acknowledgment for file reception

    # Receive and verify the checksum
    checksum = client_socket.recv(1024).decode().strip()
    received_checksum = hasher.hexdigest()
    if received_checksum == checksum:
        print(f"Received and saved file: {file_path} (Checksum verified)")
    else:
        print(f"Checksum mismatch for file: {file_path} (Expected: {checksum}, Received: {received_checksum})")

if __name__ == "__main__":
    os.makedirs("backup", exist_ok=True)  # Create the backup directory if it doesn't exist
    start_server()  # Start the server

import hashlib
import socket
import os
import threading


def handle_client(client_socket, addr):
    """Handle the client communication and receive files."""
    print(f"Connection established from {addr}")

    # Receive username from the client
    username = client_socket.recv(1024).decode().strip()
    print(f"Received username: {username}")
    client_socket.sendall(b"ACK")  # Send acknowledgment

    # Create a folder for the client if it doesn't exist
    user_dir = os.path.join("backup", username)
    os.makedirs(user_dir, exist_ok=True)

    # Continuously receive files until the client closes the connection
    try:
        while True:
            receive_file(client_socket, user_dir)
    except (ConnectionResetError, BrokenPipeError):
        print(f"Connection closed by {addr}")

    client_socket.close()


def receive_file(client_socket, user_dir):
    """Receive a file from the client and save it to the user-specific directory."""
    # Receive the file name from the client
    file_name = client_socket.recv(1024).decode().strip()
    if not file_name:
        return  # If the file name is empty, stop the session

    print(f"Received file name: '{file_name}'")
    client_socket.sendall(b"ACK")  # Send acknowledgment

    try:
        # Receive the file size from the client
        file_size_str = client_socket.recv(1024).decode().strip()
        file_size = int(file_size_str)
        print(f"File size received: {file_size} bytes")
        client_socket.sendall(b"ACK")  # Send acknowledgment
    except ValueError:
        print(f"Invalid file size received: {file_size_str}")
        return

    # Save file in the user-specific directory
    file_path = os.path.join(user_dir, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Initialize hasher for checksum calculation
    hasher = hashlib.sha256()

    with open(file_path, "wb") as f:
        if file_size == 0:
            print(f"Received and saved empty file: {file_path}")
        else:
            bytes_received = 0
            while bytes_received < file_size:
                data = client_socket.recv(4096)
                if not data:  # Break if no more data is received
                    break
                f.write(data)
                hasher.update(data)  # Update checksum
                bytes_received += len(data)
                print(f"Bytes received: {bytes_received}/{file_size}")

            client_socket.sendall(b"ACK")  # Send acknowledgment for file reception

            # Receive and verify the checksum
            checksum = client_socket.recv(1024).decode().strip()
            client_socket.sendall(b"ACK")  # Send acknowledgment
            received_checksum = hasher.hexdigest()
            if received_checksum == checksum:
                print(f"Received and saved file: {file_path} (Checksum verified)")
            else:
                print(f"Checksum mismatch for file: {file_path} (Expected: {checksum}, Received: {received_checksum})")


def start_server(host, port):
    """Start the server and listen for incoming client connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    try:
        while True:
            # Accept a new client connection
            client_socket, addr = server_socket.accept()

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()
        print("Server closed.")


if __name__ == "__main__":
    os.makedirs("backup", exist_ok=True)  # Create the root backup directory if it doesn't exist
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 5000
    start_server(HOST, PORT)  # Start the server

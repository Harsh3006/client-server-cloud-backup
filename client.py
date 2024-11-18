import hashlib
import os
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events and uploads changed files to the server."""

    def __init__(self, directory_to_monitor, sock):
        self.directory_to_monitor = directory_to_monitor
        self.sock = sock

    def on_modified(self, event):
        """Upload the file when it is modified."""
        if not event.is_directory:
            print(f"File modified: {event.src_path}")
            self.upload_file(event.src_path)

    def on_created(self, event):
        """Upload the file when it is created."""
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            self.upload_file(event.src_path)

    def upload_file(self, file_path):
        """Upload the specified file to the server."""
        relative_path = os.path.relpath(file_path, self.directory_to_monitor)
        file_name = relative_path
        file_size = os.path.getsize(file_path)

        try:
            # Send the file name
            self.sock.sendall(f"{file_name}\n".encode())
            self.sock.recv(1024)  # Wait for acknowledgment
            print(f"Sent file name: {file_name}.")

            # Send file size
            self.sock.sendall(f"{file_size}\n".encode())
            self.sock.recv(1024)  # Wait for acknowledgment
            print(f"Sent file size: {file_size}.")

            if file_size != 0:
                hasher = hashlib.sha256()

                # Send the file content in chunks
                with open(file_path, "rb") as f:
                    while chunk := f.read(4096):
                        self.sock.sendall(chunk)  # Ensure all data is sent
                        hasher.update(chunk)
                    self.sock.recv(1024)  # Wait for acknowledgment

                # Calculate and send the checksum
                checksum = hasher.hexdigest()
                self.sock.sendall(f"{checksum}\n".encode())  # Send checksum with newline
                self.sock.recv(1024)  # Wait for ACK
                print(f"Uploaded file: {file_name} with checksum {checksum}")

        except Exception as e:
            print(f"Error uploading {file_name}: {e}")

        print(f"Finished uploading: {file_name}")


def initial_backup(directory, sock):
    """Upload existing files in the directory to the server."""
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            print(f"Backing up existing file: {file_path}")
            handler = FileChangeHandler(directory, sock)
            handler.upload_file(file_path)


def monitor_directory(directory, sock):
    """Monitor the directory for changes and handle file uploads."""
    event_handler = FileChangeHandler(directory, sock)
    observer = Observer()
    observer.schedule(event_handler, path=directory, recursive=True)

    observer.start()
    print(f"Monitoring changes in directory: {directory}")

    try:
        while True:
            pass  # Keep the script running to monitor the directory
    except KeyboardInterrupt:
        observer.stop()
        print("Stopped monitoring directory.")
    observer.join()


def start_connection(server_address, username):
    """Start the connection to the server and send the username."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    # Send the username once when the connection is established
    sock.sendall(f"{username}\n".encode())
    sock.recv(1024)  # Wait for acknowledgment
    return sock


if __name__ == "__main__":
    SERVER_ADDRESS = ("192.168.x.x", 5000)
    DIRECTORY_TO_MONITOR = "source"
    USERNAME = input("Enter your username: ")

    # Start the connection to the server
    SOCK = start_connection(SERVER_ADDRESS, USERNAME)

    # Perform initial backup of existing files
    initial_backup(DIRECTORY_TO_MONITOR, SOCK)

    # Start monitoring for further changes
    monitor_directory(DIRECTORY_TO_MONITOR, SOCK)

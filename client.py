import hashlib
import os
import socket
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events and uploads changed files to the server."""

    def __init__(self, server_address, directory_to_monitor):
        self.server_address = server_address
        self.directory_to_monitor = directory_to_monitor

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

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect(self.server_address)

                # Send the file name
                sock.sendall(f"{file_name}\n".encode())
                sock.recv(1024)  # Wait for acknowledgment
                print(f"Sent file name: {file_name}.")

                # Send file size
                sock.sendall(f"{file_size}\n".encode())
                sock.recv(1024)  # Wait for acknowledgment
                print(f"Sent file size: {file_size}.")

                hasher = hashlib.sha256()

                # Send the file content in chunks
                with open(file_path, "rb") as f:
                    while chunk := f.read(4096):
                        sock.sendall(chunk)  # Ensure all data is sent
                        hasher.update(chunk)
                    ack = sock.recv(1024)  # Wait for acknowledgment

                # Calculate and send the checksum
                checksum = hasher.hexdigest()
                sock.sendall(f"{checksum}\n".encode())  # Send checksum with newline
                sock.recv(1024)  # Wait for ACK
                print(f"Uploaded file: {file_name} with checksum {checksum}")

            except Exception as e:
                print(f"Error uploading {file_name}: {e}")

            print(f"Finished uploading: {file_name}")


def initial_backup(directory, server_address):
    """Upload existing files in the directory to the server."""
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            print(f"Backing up existing file: {file_path}")
            FileChangeHandler(server_address, directory).upload_file(file_path)


def monitor_directory(directory, server_address):
    """Monitor the directory for changes and handle file uploads."""
    event_handler = FileChangeHandler(server_address, directory)
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


if __name__ == "__main__":
    SERVER_ADDRESS = ("localhost", 5000)
    DIRECTORY_TO_MONITOR = "source"

    # Perform initial backup of existing files
    initial_backup(DIRECTORY_TO_MONITOR, SERVER_ADDRESS)

    # Start monitoring for further changes
    monitor_directory(DIRECTORY_TO_MONITOR, SERVER_ADDRESS)

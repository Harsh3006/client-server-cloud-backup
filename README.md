# Cloud Backup Client-Server Application

This project implements a simple client-server application for cloud backup using Python. The client monitors a specified directory for changes and uploads files to the server when they are created or modified. The server receives and stores these files in a designated backup directory.

## Features

- **Real-time Monitoring:** Monitors a specified directory recursively for file changes.
- **Automatic Uploads:** Uploads newly created or modified files to the server.
- **Initial Backup:** Performs an initial backup of existing files in the directory.
- **Checksum Verification:** Ensures file integrity with checksum verification.

## Requirements

- **Python**: Version 3.x
- **Required Python packages**: 
  - `watchdog`

## Installation

1. **Clone the repository**:
     ```bash
     git clone https://github.com/Harsh3006/client-server-cloud-backup.git
     cd client-server-cloud-backup
     ```
     
2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**:
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4. **Install the required packages**:
    ```bash
    pip install watchdog
    ```

## Usage

1. **Start the server**:
    ```bash
    python server.py
    ```
   - The server will listen for incoming connections on `localhost:5000` by default.

2. **Run the client**:
    ```bash
    python client.py
    ```
   - The client will monitor the specified directory (default is `source`) for any file changes.

3. **Modify or add files** in the specified directory to test the functionality. The repository includes a source folder with a `sample.txt` file for initial testing. You can modify this file or add new files to see the client automatically upload changes to the server.

## Configuration

You can modify the server address and the directory to monitor by editing the constants in `client.py`:
```python
SERVER_ADDRESS = ("localhost", 5000)
DIRECTORY_TO_MONITOR = "source"

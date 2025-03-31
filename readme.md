# Video Button Interface

The **Video Button Interface** is a Raspberry Pi project that provides a web-based interface for controlling video playback and image display. It integrates a Flask web server with hardware control via GPIO pins and uses system utilities like `fbi` and `mpv` for media display. Physical buttons connected to the Raspberry Pi trigger video playback, while the web interface allows remote configuration and testing.

## Features

- **Web Interface**
  - Displays current settings (active image and button-to-video assignments).
  - Provides flash messages for success, error, or warning feedback.
  - Allows file selection from available media and uploading of new files.
  - Includes test playback buttons to simulate physical button presses.

- **Hardware Integration**
  - Uses GPIO pins (default pins: 17, 27, 22) for physical button input.
  - Implements a debounce mechanism to avoid false triggers.
  - Supports three physical buttons to play corresponding videos.

- **Media Playback**
  - Displays images using `fbi`.
  - Plays videos in full-screen mode using `mpv`.

- **Logging & Error Handling**
  - Detailed logging to both console and a log file.
  - Graceful error handling using Flask flash messages.
  - Checks for required system programs and directories during startup.

## Prerequisites

Before installing the software, ensure your Raspberry Pi 4 meets the following requirements:

- **Operating System:** Raspbian (or a compatible Debian-based OS)
- **Python:** Python 3.x installed
- **Hardware:** Raspberry Pi 4 with buttons connected to GPIO pins
- **System Tools:** `fbi` (for image display) and `mpv` (for video playback)

### Installing Required System Packages

Open a terminal on your Raspberry Pi and run:

```bash
sudo apt update
sudo apt install python3 python3-pip fbi mpv git
Installing Python Dependencies
Install the required Python libraries using pip:

bash
Copy
pip3 install flask RPi.GPIO werkzeug
Software Installation
Clone the Repository

Clone your project repository into the base directory (for example, /home/tech):

bash
Copy
git clone https://your-repository-url.git
cd your-repository-directory
Project Structure Overview

Your project directory might look like this:

bash
Copy
/home/tech/
├── app.py                    # Main Python script (Flask and GPIO integration)
├── video_button.log          # Log file for debugging
├── default_image.png         # Default image to display
├── default_video1.mp4        # Default video for button 1
├── default_video2.mp4        # Default video for button 2
├── default_video3.mp4        # Default video for button 3
├── uploads/                  # Directory for uploaded media files
└── templates/
    └── index.html            # HTML template for the web interface
Configuration

The application uses hardcoded paths and constants (like BASE_DIR and button GPIO pins) in app.py. Modify these values if your setup differs.

Running as a System Service
To run the Video Button Interface as a systemd service on your Raspberry Pi 4, follow these steps:

Create the Systemd Service File

Create a new service file named video_button.service:

bash
Copy
sudo nano /etc/systemd/system/video_button.service
Paste the following configuration into the file:

ini
Copy
[Unit]
Description=Video Button Interface Service
After=network.target

[Service]
User=pi
WorkingDirectory=/home/tech
ExecStart=/usr/bin/python3 /home/tech/app.py
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
Note:

Replace User=pi with your appropriate username if different.

Ensure the WorkingDirectory and ExecStart paths point to your project directory and main script (app.py).

Reload the Systemd Daemon

Reload systemd to recognize the new service:

bash
Copy
sudo systemctl daemon-reload
Enable the Service

Enable the service to start on boot:

bash
Copy
sudo systemctl enable video_button.service
Start the Service

Start the service immediately:

bash
Copy
sudo systemctl start video_button.service
Verify the Service Status

Check that the service is running properly:

bash
Copy
sudo systemctl status video_button.service
You should see that the service is active and running. For troubleshooting, consult the logs using:

bash
Copy
journalctl -u video_button.service
Troubleshooting
GPIO Issues:
Verify that your physical buttons are correctly wired to the designated GPIO pins (default: 17, 27, 22).

Media Playback Issues:
Ensure that fbi and mpv are installed and that your media files (images and videos) are located in the expected directories.

Logging:
Check the log file (/home/tech/video_button.log) for any errors or debugging information.

Conclusion
This guide outlines how to install and run the Video Button Interface on a Raspberry Pi 4 as a system service. The system integrates a Flask-based web interface with physical button controls via GPIO, allowing for flexible media playback control. For further customization or troubleshooting, refer to the project source code and log files.

Happy hacking!

yaml
Copy

---

Feel free to adjust paths, user names, or repository URLs as needed for your setup. This document sho

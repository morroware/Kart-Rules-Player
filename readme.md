# Video Button Interface for Raspberry Pi

## Overview

The **Video Button Interface** is an interactive media control system designed specifically for Raspberry Pi 4. This application combines physical GPIO button controls with a web-based management interface to create an easy-to-use digital signage or interactive kiosk system.

When a physical button is pressed, the system plays a designated video in full-screen mode on the connected display. When no video is playing, a configurable image is shown. The accompanying web interface allows administrators to change videos, update the display image, and test functionality without physical access to the buttons.

This system is ideal for:
- Museum or gallery interactive displays
- Information kiosks in public spaces
- Educational exhibits
- Retail product demonstrations
- Trade show presentations

## Key Features

### Hardware Integration
- **Physical Button Control**: Connects to three physical buttons via GPIO pins (default: 17, 27, 22)
- **Debounce Protection**: Sophisticated debounce algorithm prevents accidental double-triggers
- **Visual Feedback**: Automatically returns to display image after video playback

### Web Management Interface
- **Remote Administration**: Configure the system from any device on the same network
- **Real-time Status**: View current configuration and playback status
- **Media Management**: Upload new videos/images or select from existing files
- **Button Testing**: Trigger videos directly from the web interface

### Media Handling
- **Image Display**: Shows a configurable standby image using `fbi` (Frame Buffer Imageviewer)
- **Video Playback**: Full-screen, high-quality video using `mpv` with hardware acceleration
- **Format Support**: Compatible with common image formats (PNG, JPG, GIF) and video formats (MP4, MOV, AVI, MKV)
- **Flexible Assignment**: Assign different videos to each button

### System Design
- **Responsive Design**: Web interface works on desktops, tablets, and smartphones
- **Robust Error Handling**: Comprehensive logging and user-friendly error messages
- **Security Measures**: Input validation and secure file handling
- **System Service**: Runs as a systemd service for automatic startup and recovery

## Hardware Requirements

- **Raspberry Pi 4** (2GB+ RAM recommended)
- **Display**: HDMI-connected monitor or TV
- **Storage**: MicroSD card (16GB+ recommended) with Raspberry Pi OS
- **Input**: Three momentary push buttons connected to GPIO pins
- **Power**: Stable 5V/3A power supply
- **Network**: Ethernet connection or WiFi for accessing the web interface

## Software Prerequisites

- **Operating System**: Raspberry Pi OS (formerly Raspbian) Bullseye or newer
- **Python**: Python 3.7+ (included with Raspberry Pi OS)
- **System Utilities**: `fbi` for image display and `mpv` for video playback
- **Network**: Configured network connection with assigned IP address

## Installation Guide

### 1. System Preparation

Start with a fresh installation of Raspberry Pi OS (Lite version is sufficient). Open a terminal and update your system:

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Required System Packages

Install the necessary system utilities and development tools:

```bash
sudo apt install -y python3-pip python3-dev git fbi mpv
```

### 3. Install Python Dependencies

Install the required Python libraries:

```bash
sudo pip3 install flask werkzeug RPi.GPIO
```

### 4. Create Project Directory Structure

Set up the project directory structure:

```bash
sudo mkdir -p /home/tech/uploads
sudo mkdir -p /home/tech/templates
sudo chown -R pi:pi /home/tech  # Replace 'pi' with your username if different
```

### 5. Download the Software

Clone the repository (or download and place the files manually):

```bash
cd /home/tech
git clone https://your-repository-url.git .
# Or manually copy app.py to /home/tech and index.html to /home/tech/templates
```

### 6. Prepare Default Media Files

Place your default image and videos in the base directory:

```bash
# Ensure these files exist (create empty ones if needed for testing)
touch /home/tech/default_image.png
touch /home/tech/default_video1.mp4
touch /home/tech/default_video2.mp4
touch /home/tech/default_video3.mp4
```

### 7. Setting Up the System Service

Creating a system service allows the Video Button Interface to start automatically when your Raspberry Pi boots and restart if it crashes.

#### Create the Service File

```bash
sudo nano /etc/systemd/system/video-button.service
```

Add the following content, adjusting the user and paths as needed:

```ini
[Unit]
Description=Video Button Interface
After=network.target

[Service]
User=pi
WorkingDirectory=/home/tech
ExecStart=/usr/bin/python3 /home/tech/app.py
Restart=on-failure
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=video-button
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

#### Enable and Start the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable video-button.service

# Start the service immediately
sudo systemctl start video-button.service

# Check the status
sudo systemctl status video-button.service
```

The service should now be running. The web interface will be available at `http://[raspberry-pi-ip]:5000`

### 8. Testing the Installation

1. **Check Service Status**:
   ```bash
   sudo systemctl status video-button.service
   ```
   Look for "active (running)" in the output.

2. **View Logs**:
   ```bash
   sudo journalctl -u video-button.service -f
   ```
   This shows live logs from the service.

3. **Access Web Interface**:
   Open a browser on another device and navigate to `http://[raspberry-pi-ip]:5000`

4. **Test Button Functionality**:
   Press the physical buttons connected to GPIO pins to verify video playback.

## Hardware Setup Guide

### Connecting Buttons to GPIO

1. **Button Wiring**:
   - Connect one terminal of each button to the respective GPIO pin (default: 17, 27, 22)
   - Connect the other terminal of each button to a GND pin on the Raspberry Pi

2. **Pin References**:
   The default configuration uses these pins:
   - Button 1: GPIO 17
   - Button 2: GPIO 27
   - Button 3: GPIO 22

3. **GPIO Diagram**:
   For pin locations, refer to the [Raspberry Pi GPIO pinout diagram](https://pinout.xyz/).

### Display Connection

Connect your display to the Raspberry Pi's HDMI port. The application is configured to use the primary HDMI output.

## Customization

### Changing GPIO Pins

To use different GPIO pins, modify the `BUTTON_PINS` list in `app.py`:

```python
# Define three button pins
BUTTON_PINS = [17, 27, 22]  # Change these numbers to your preferred GPIO pins
```

### Directory Configuration

If you want to use a different base directory, update the `BASE_DIR` variable:

```python
BASE_DIR = "/home/tech"  # Change to your preferred directory
```

## Troubleshooting

### Service Won't Start

Check the logs for detailed error messages:

```bash
sudo journalctl -u video-button.service -e
```

Common issues:
- **GPIO Access**: Ensure the service is running as a user with GPIO access
- **Missing Files**: Check if all required paths and files exist
- **Port Conflict**: Ensure no other service is using port 5000

### Video Playback Issues

1. **Check MPV Installation**:
   ```bash
   mpv --version
   ```

2. **Test Video Playback Manually**:
   ```bash
   mpv --vo=gpu --fullscreen /home/tech/default_video1.mp4
   ```

3. **Check Video Format Compatibility**:
   Ensure your video files are in a format supported by mpv.

### Web Interface Not Accessible

1. **Check Network Configuration**:
   ```bash
   hostname -I
   ```
   Verify you're using the correct IP address.

2. **Check Firewall Settings**:
   ```bash
   sudo ufw status
   ```
   Ensure port 5000 is allowed if the firewall is active.

3. **Test Local Access**:
   ```bash
   curl http://localhost:5000
   ```
   If this works but remote access doesn't, it's likely a network issue.

## Maintenance

### Updating the Software

To update the software to the latest version:

```bash
cd /home/tech
git pull

# Restart the service
sudo systemctl restart video-button.service
```

### Backing Up Configuration

Back up your media files and configuration:

```bash
sudo cp -r /home/tech /backup/video-button-$(date +%Y%m%d)
```

## Technical Details

### Application Architecture

The Video Button Interface consists of:

1. **Flask Web Server**: Handles HTTP requests, renders the web interface, and manages file uploads
2. **GPIO Monitor Thread**: Continuously monitors button presses in a separate thread
3. **Media Manager**: Controls the display of images and playback of videos
4. **Event System**: Coordinates between button presses and the web interface

### File Structure

```
/home/tech/
├── app.py                    # Main application script
├── video_button.log          # Application log file
├── default_image.png         # Default display image
├── default_video1.mp4        # Video for button 1
├── default_video2.mp4        # Video for button 2
├── default_video3.mp4        # Video for button 3
├── uploads/                  # Directory for uploaded media
└── templates/
    └── index.html            # Web interface template
```

## License and Contributions

This project is distributed under the [appropriate license]. Contributions are welcome via pull requests or issue reports on the GitHub repository.

## Support

For additional support:
- Check the [GitHub repository](https://your-repository-url.git) for updates
- Open an issue on GitHub for bug reports
- Contact the developer at [your-email]

---

This project makes use of several open-source technologies, including Flask, RPi.GPIO, fbi, and mpv. Thank you to the developers of these tools for making this project possible.

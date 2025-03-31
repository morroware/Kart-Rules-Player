#!/usr/bin/env python3

import os
import time
import threading
import subprocess
import logging
import RPi.GPIO as GPIO
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, flash

# Constants
BASE_DIR = "/home/tech"
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "mkv"}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024
BUTTON_PINS = [17, 27, 22]  # Define three button pins
DEBOUNCE_DELAY = 2.0

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(BASE_DIR, "video_button.log"))
    ]
)
logger = logging.getLogger(__name__)

# File paths
IMAGE_PATH = os.path.join(BASE_DIR, "default_image.png")
# Three default video paths
VIDEO_PATH_1 = os.path.join(BASE_DIR, "default_video1.mp4")
VIDEO_PATH_2 = os.path.join(BASE_DIR, "default_video2.mp4")
VIDEO_PATH_3 = os.path.join(BASE_DIR, "default_video3.mp4")

# Global state
is_playing = False
current_process = None
shutting_down = False

# Flask app configuration
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH
)

def check_environment():
    """Check if all required programs and directories exist"""
    logger.info("Checking environment setup...")
    for prog in ["fbi", "mpv"]:
        try:
            subprocess.run(["which", prog], check=True, capture_output=True)
            logger.info(f"{prog} is installed.")
        except subprocess.CalledProcessError:
            logger.error(f"{prog} is NOT installed or not in PATH.")

    logger.info(f"BASE_DIR exists: {os.path.exists(BASE_DIR)}")
    logger.info(f"UPLOAD_FOLDER exists: {os.path.exists(UPLOAD_FOLDER)}")
    logger.info(f"Default image exists: {os.path.exists(IMAGE_PATH)}")
    # Check each default video file
    for i, path in enumerate([VIDEO_PATH_1, VIDEO_PATH_2, VIDEO_PATH_3], start=1):
        logger.info(f"Default video{i} exists: {os.path.exists(path)}")

def get_available_files():
    """Get lists of available image and video files"""
    images = []
    videos = []

    # Add default image
    if os.path.exists(os.path.join(BASE_DIR, "default_image.png")):
        images.append(("default_image.png", os.path.join(BASE_DIR, "default_image.png")))
    # Add default videos for each button
    for i in range(1, 4):
        default_video = os.path.join(BASE_DIR, f"default_video{i}.mp4")
        if os.path.exists(default_video):
            videos.append((f"default_video{i}.mp4", default_video))

    # Add uploaded files
    if os.path.exists(UPLOAD_FOLDER):
        for file in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, file)
            if is_image_file(file):
                images.append((file, filepath))
            elif is_video_file(file):
                videos.append((file, filepath))

    return images, videos

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_video_file(filename):
    """Check if the file is a video file"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"mp4", "mov", "avi", "mkv"}

def is_image_file(filename):
    """Check if the file is an image file"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg", "gif"}

def setup_gpio():
    """Set up GPIO pins for the buttons"""
    logger.info("Setting up GPIO...")
    try:
        GPIO.setmode(GPIO.BCM)
        # Setup each button pin as input with pull-up resistor
        for pin in BUTTON_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        logger.info("GPIO setup complete.")
    except Exception as e:
        logger.error(f"GPIO setup failed: {e}")
        raise

def kill_processes():
    """Kill any running display processes"""
    global current_process
    logger.debug("Attempting to kill existing processes...")

    subprocess.run(["sudo", "pkill", "-9", "fbi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["pkill", "-9", "mpv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if current_process:
        try:
            current_process.terminate()
        except Exception:
            pass
        current_process = None

def show_image():
    """Display the current image using fbi"""
    global current_process
    logger.info(f"Attempting to show image: {IMAGE_PATH}")

    try:
        kill_processes()
        if os.path.exists(IMAGE_PATH):
            with open(os.devnull, 'w') as devnull:
                cmd = ["sudo", "fbi", "--noverbose", "-T", "1", "-a", IMAGE_PATH]
                current_process = subprocess.Popen(
                    cmd,
                    stdout=devnull,
                    stderr=devnull
                )
                time.sleep(0.5)
        else:
            logger.error(f"Image file not found: {IMAGE_PATH}")
    except Exception as e:
        logger.error(f"Error showing image: {e}")

def play_video(video_path):
    """Play a video using mpv"""
    global is_playing, current_process
    logger.info(f"Attempting to play video: {video_path}")

    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        is_playing = False
        return

    try:
        subprocess.run(["sudo", "pkill", "-9", "fbi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["clear"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        cmd = [
            "mpv",
            "--vo=gpu",
            "--gpu-context=drm",
            "--gpu-api=opengl",
            "--drm-connector=HDMI-A-1",
            "--fullscreen",
            "--no-osc",
            "--loop=no",
            "--no-osd-bar",
            "--no-terminal",
            "--really-quiet",
            "--msg-level=all=no",
            "--audio-device=alsa/hdmi:CARD=vc4hdmi0,DEV=0",
            "--volume=100",
            video_path
        ]

        with open(os.devnull, 'w') as devnull:
            video_process = subprocess.Popen(
                cmd,
                stdout=devnull,
                stderr=devnull,
                env={
                    "SDL_VIDEODRIVER": "drm",
                    "DISPLAY": ""
                }
            )
            video_process.wait()

    except Exception as e:
        logger.error(f"Error playing video: {e}")
    finally:
        is_playing = False
        subprocess.run(["clear"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        show_image()

def button_monitor_loop():
    """Monitor button presses and play videos accordingly"""
    global is_playing, shutting_down, VIDEO_PATH_1, VIDEO_PATH_2, VIDEO_PATH_3
    logger.info("Starting button monitor loop.")
    # Create a per-button debounce timer
    last_press_times = {pin: 0 for pin in BUTTON_PINS}

    while not shutting_down:
        try:
            now = time.time()
            for pin in BUTTON_PINS:
                if not is_playing and GPIO.input(pin) == GPIO.LOW:
                    if (now - last_press_times[pin]) > DEBOUNCE_DELAY:
                        last_press_times[pin] = now
                        logger.debug(f"Button press detected on pin {pin} (debounced).")
                        is_playing = True
                        # Determine which video to play based on which button was pressed
                        if pin == 17:
                            video_to_play = VIDEO_PATH_1
                        elif pin == 27:
                            video_to_play = VIDEO_PATH_2
                        elif pin == 22:
                            video_to_play = VIDEO_PATH_3
                        else:
                            video_to_play = None
                        if video_to_play:
                            threading.Thread(target=play_video, args=(video_to_play,), daemon=True).start()
            time.sleep(0.05)
        except Exception as e:
            logger.error(f"Error in button monitor: {e}")
            time.sleep(0.5)

    logger.info("Button monitor loop exiting...")

@app.route("/", methods=["GET"])
def index():
    """Render the main page"""
    logger.debug("Index page requested.")
    images, videos = get_available_files()
    # Pass the current settings
    current_videos = [
        {"id": 1, "path": VIDEO_PATH_1, "name": os.path.basename(VIDEO_PATH_1)},
        {"id": 2, "path": VIDEO_PATH_2, "name": os.path.basename(VIDEO_PATH_2)},
        {"id": 3, "path": VIDEO_PATH_3, "name": os.path.basename(VIDEO_PATH_3)}
    ]
    current_image_name = os.path.basename(IMAGE_PATH)
    
    return render_template(
        "index.html",
        current_image=IMAGE_PATH,
        current_image_name=current_image_name,
        current_videos=current_videos,
        is_playing=is_playing,
        images=images,
        videos=videos
    )

@app.route("/play", methods=["GET"])
def play():
    """Endpoint to trigger video playback from the web interface"""
    global is_playing, VIDEO_PATH_1, VIDEO_PATH_2, VIDEO_PATH_3
    logger.debug("Play endpoint triggered.")

    button = request.args.get("button")
    if button not in ["1", "2", "3"]:
        flash("Invalid button selection.", "error")
        return redirect(url_for("index"))

    # Map button number to video file
    if button == "1":
        video_to_play = VIDEO_PATH_1
    elif button == "2":
        video_to_play = VIDEO_PATH_2
    elif button == "3":
        video_to_play = VIDEO_PATH_3

    if not is_playing:
        is_playing = True
        threading.Thread(target=play_video, args=(video_to_play,), daemon=True).start()
        flash(f"Video {button} playback triggered!", "success")
    else:
        flash("A video is already playing. Try again later.", "warning")

    return redirect(url_for("index"))

@app.route("/select", methods=["POST"])
def select_file():
    """Endpoint to select an existing file"""
    global IMAGE_PATH, VIDEO_PATH_1, VIDEO_PATH_2, VIDEO_PATH_3
    file_type = request.form.get("type")
    file_path = request.form.get("path")

    if not file_path:
        flash("No file selected.", "error")
        return redirect(url_for("index"))
    
    if not os.path.exists(file_path):
        flash(f"Selected file does not exist: {file_path}", "error")
        return redirect(url_for("index"))

    if file_type == "image":
        IMAGE_PATH = file_path
        if not is_playing:
            show_image()
        flash(f"Image selection updated to {os.path.basename(file_path)}!", "success")
    elif file_type == "video":
        button = request.form.get("button")
        if button == "1":
            VIDEO_PATH_1 = file_path
        elif button == "2":
            VIDEO_PATH_2 = file_path
        elif button == "3":
            VIDEO_PATH_3 = file_path
        else:
            flash("Invalid button selection for video.", "error")
            return redirect(url_for("index"))
        flash(f"Video {button} selection updated to {os.path.basename(file_path)}!", "success")

    return redirect(url_for("index"))

@app.route("/upload", methods=["POST"])
def upload():
    """Endpoint to upload a new file"""
    logger.debug("Upload endpoint triggered.")
    global IMAGE_PATH, VIDEO_PATH_1, VIDEO_PATH_2, VIDEO_PATH_3

    if "file" not in request.files:
        logger.warning("No file in request.")
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        logger.warning("Empty filename.")
        flash("No selected file.", "error")
        return redirect(url_for("index"))

    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            logger.info(f"File saved to: {filepath}")

            if is_image_file(filename):
                IMAGE_PATH = filepath
                if not is_playing:
                    show_image()
                flash(f"New image '{filename}' uploaded successfully!", "success")
            elif is_video_file(filename):
                button = request.form.get("button")
                if button == "1":
                    VIDEO_PATH_1 = filepath
                elif button == "2":
                    VIDEO_PATH_2 = filepath
                elif button == "3":
                    VIDEO_PATH_3 = filepath
                else:
                    flash("Invalid button selection for video.", "error")
                    return redirect(url_for("index"))
                flash(f"New video '{filename}' uploaded successfully for button {button}!", "success")
        else:
            logger.warning(f"Invalid file type: {file.filename}")
            flash("File type not allowed.", "error")

    except Exception as e:
        logger.error(f"Error in upload: {e}")
        flash(f"Error uploading file: {str(e)}", "error")

    return redirect(url_for("index"))

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors"""
    logger.error("File too large error.")
    flash("File too large! Maximum size is 100MB.", "error")
    return redirect(url_for("index"))

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {e}")
    flash(f"An error occurred: {str(e)}", "error")
    return redirect(url_for("index"))

def main():
    """Main entry point for the application"""
    global shutting_down

    try:
        logger.info("Starting application...")
        check_environment()
        os.makedirs(BASE_DIR, exist_ok=True)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        setup_gpio()

        logger.info("Attempting to show initial image...")
        show_image()

        logger.info("Starting button monitor thread...")
        t = threading.Thread(target=button_monitor_loop, daemon=True)
        t.start()

        logger.info("Starting Flask server on 0.0.0.0:5000...")
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        shutting_down = True
        time.sleep(0.5)
        GPIO.cleanup()
        logger.info("Application shutting down...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application terminated by user.")
    finally:
        logger.info("Cleaning up...")
        kill_processes()
        GPIO.cleanup()

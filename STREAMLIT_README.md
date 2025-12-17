# Robot Hand Controller - Streamlit Web App

This Streamlit web application allows you to control your robot hand wirelessly through a web browser from any device on your network.

## Features

- 🌐 **Wireless Control**: Access from any device on your network
- 📹 **Live Video Feed**: Real-time hand tracking visualization
- 🎮 **Easy Configuration**: Select COM ports and adjust settings via web UI
- 📊 **Real-time Metrics**: Monitor frame rates, joint angles, and connection status
- 🔧 **Flexible Setup**: Support for both OAK-D camera and standard webcams
- 🔌 **Serial Communication**: Send commands to your robot hand via USB

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App Locally

```bash
streamlit run streamlit_app.py
```

The app will open in your default browser at `http://localhost:8501`

### 3. Access from Other Devices

To access the controller from other devices (phones, tablets, other computers):

1. Find your computer's IP address:
   - **Windows**: Open Command Prompt and type `ipconfig`
   - Look for "IPv4 Address" (e.g., `192.168.1.100`)

2. On the other device, open a web browser and navigate to:
   ```
   http://<your-ip-address>:8501
   ```
   Example: `http://192.168.1.100:8501`

### 4. Run on Your Network (Accessible to All Devices)

To make the app accessible from any device on your network:

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```

## Usage Guide

### Initial Setup

1. **Connect Hardware**:
   - Connect your camera (OAK-D or webcam)
   - Connect your robot hand via USB

2. **Configure Settings** (in the sidebar):
   - **Serial Port**: Select your COM port from the dropdown
     - Click "Refresh Ports" if your device isn't listed
   - **Enable Serial Communication**: Check this to send commands to the robot
   - **Camera Settings**: Choose between OAK-D or webcam
   - **Processing Settings**: Adjust the low-pass filter for smoothing

3. **Start the System**:
   - Click the "▶️ Start" button
   - Grant camera permissions if prompted

4. **Control the Robot**:
   - Move your right hand in front of the camera
   - The robot hand will mimic your movements
   - Monitor joint angles in the status panel

### Configuration Options

#### Serial Port Settings
- **Serial FPS**: Controls how often commands are sent (1-60 Hz)
- Higher FPS = more responsive but more data transmission

#### Camera Settings
- **OAK-D Camera**: Use high-quality depth camera if available
  - Default resolution: 3840x2160
- **Webcam**: Standard USB webcam
  - Default resolution: 1920x1080
- **Preview Size**: Adjust display resolution (affects performance)

#### Processing Settings
- **Low Pass Filter**: Smooths movement (0.0-1.0)
  - 0.0 = maximum smoothing (slower response)
  - 1.0 = no smoothing (instant response, more jittery)
  - 0.25 = balanced (recommended)

## Troubleshooting

### Camera Not Working
- Grant camera permissions in your browser
- Make sure no other application is using the camera
- Try checking "Force Webcam" if OAK-D isn't detected

### COM Port Not Listed
- Ensure the robot is connected via USB
- Install required USB drivers
- Click "Refresh Ports" button
- Manually enter the port name if needed

### Cannot Access from Other Devices
- Ensure all devices are on the same network
- Check firewall settings (allow port 8501)
- Verify your IP address is correct
- Try running with `--server.address 0.0.0.0`

### Performance Issues
- Lower the preview resolution
- Reduce serial FPS
- Close other applications
- Use a more powerful computer/camera

## Advanced Usage

### Custom Port and Host

```bash
streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
```

### Running as Background Service

For Windows, you can create a batch file `run_robot_controller.bat`:

```batch
@echo off
cd /d "C:\Users\swaru\Documents\College Projects\Robot Hand\CodeBase"
call conda activate mediapipe_env
streamlit run streamlit_app.py --server.address 0.0.0.0
pause
```

### Network Security

When running on a network, consider:
- Using a VPN for external access
- Setting up password protection (Streamlit Cloud)
- Restricting access to specific IP addresses

## Files Overview

- `streamlit_app.py`: Main web application interface
- `robot_controller.py`: Core controller class (modular version)
- `controller.py`: Original standalone controller
- `opencv_cam.py`: Webcam interface
- `depthai_cam.py`: OAK-D camera interface
- `requirements.txt`: Python dependencies

## Technical Details

### Architecture
- **Frontend**: Streamlit web interface
- **Processing**: MediaPipe for hand/pose tracking
- **Communication**: PySerial for robot commands
- **Threading**: Background thread for video processing

### Data Flow
1. Camera captures video feed
2. MediaPipe processes hand and pose landmarks
3. Controller calculates 23 joint angles
4. Angles filtered and transmitted via serial
5. Robot hand receives and executes movements

### Serial Protocol
- Start bytes: `0xFE 0xFE`
- Data: 23 bytes (joint angles 0-255)
- Checksum: 1 byte
- End bytes: `0xFD 0xFD`

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the MediaPipe documentation
3. Verify hardware connections
4. Check serial port settings in Device Manager

## License

See LICENSE file in the repository.

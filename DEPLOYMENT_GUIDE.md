# Robot Hand Controller - Deployment Guide

## Important: Camera Access Requirement

⚠️ **This application CANNOT run on Streamlit Cloud** because it requires:
- Local camera access (webcam or OAK-D camera)
- Serial port communication with the robot hand
- Real-time video processing

## Deployment Options

### Option 1: Local Network Deployment (Recommended)

This is the **best option** for wireless control while maintaining camera and serial access.

#### Setup:

1. **Install Dependencies** on your local computer:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit App** with network access:
   ```bash
   streamlit run streamlit_app.py --server.address 0.0.0.0
   ```

3. **Find Your Local IP Address**:
   - **Windows**: 
     ```cmd
     ipconfig
     ```
     Look for "IPv4 Address" (e.g., `192.168.1.100`)
   
   - **Mac/Linux**:
     ```bash
     ifconfig
     ```

4. **Access from Other Devices** on the same network:
   - Open any web browser
   - Navigate to: `http://<your-ip>:8501`
   - Example: `http://192.168.1.100:8501`

5. **Control from Your Phone/Tablet**:
   - Connect your phone to the same WiFi network
   - Open browser and go to `http://<your-ip>:8501`
   - Configure COM port and start controlling!

#### Advantages:
✅ Full camera access  
✅ Serial port communication works  
✅ Access from any device on your network  
✅ Low latency  
✅ All features work  

---

### Option 2: Cloud Deployment with Local Client

For advanced users who want remote access from anywhere.

#### Architecture:
- **Server**: Runs locally with camera/serial access
- **Cloud**: Streamlit Cloud hosts a remote control interface
- **Communication**: WebSocket or REST API between them

This requires significant additional development and is not included in the current version.

---

### Option 3: Standalone Desktop App

Run without browser entirely.

#### Using the Original Controller:
```bash
python controller.py --enable-serial --serial-port COM14
```

This runs the original version without the web interface.

---

## Why Streamlit Cloud Won't Work

Streamlit Cloud limitations:
- ❌ No camera access
- ❌ No USB/serial port access
- ❌ Limited to web-based inputs only
- ❌ Cannot run hardware-dependent applications

The error you saw indicates MediaPipe can install, but the camera modules cannot function in the cloud environment.

---

## Recommended Setup for Wireless Control

### Best Practice:

1. **Host Computer** (connected to camera and robot):
   - Run Streamlit app: `streamlit run streamlit_app.py --server.address 0.0.0.0`
   - Keep this computer on and connected

2. **Control Devices** (phones, tablets, other computers):
   - Connect to same WiFi
   - Access via browser: `http://<host-ip>:8501`
   - Control and monitor from anywhere in your home/office

### Network Security:

For local network only:
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

To add basic password protection, create `.streamlit/secrets.toml`:
```toml
password = "your_secure_password"
```

Then modify the app to check the password on startup.

---

## Firewall Configuration

### Windows Firewall:

1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Click "Change settings" → "Allow another app"
4. Add Python or Streamlit
5. Enable for "Private" networks

### Port Forwarding (for external access):

⚠️ **Security Warning**: Only do this if you understand the risks

1. Access your router settings
2. Forward port 8501 to your computer's local IP
3. Access from anywhere using your public IP
4. **Strongly recommended**: Use a VPN instead

---

## Troubleshooting

### "Cannot access from other devices"

1. Check firewall settings
2. Ensure devices are on same network
3. Verify IP address is correct
4. Try `--server.address 0.0.0.0`

### "Camera not working"

1. Grant camera permissions
2. Close other apps using camera
3. Check camera is properly connected
4. Restart the Streamlit app

### "Serial port not found"

1. Connect robot via USB
2. Install USB drivers
3. Check Device Manager (Windows)
4. Try different USB ports

---

## Advanced: Running as a Service

### Windows (using NSSM):

1. Download NSSM: https://nssm.cc/download
2. Create batch file `start_robot.bat`:
   ```batch
   @echo off
   cd "C:\path\to\CodeBase"
   call conda activate mediapipe_env
   streamlit run streamlit_app.py --server.address 0.0.0.0
   ```
3. Install as service:
   ```cmd
   nssm install RobotHandController "C:\path\to\start_robot.bat"
   ```

### Linux (systemd):

Create `/etc/systemd/system/robot-hand.service`:
```ini
[Unit]
Description=Robot Hand Controller
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/CodeBase
ExecStart=/usr/local/bin/streamlit run streamlit_app.py --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable robot-hand
sudo systemctl start robot-hand
```

---

## Summary

For your use case (wireless control of robot hand):

1. ✅ **Use Local Network Deployment**
2. ✅ Run on computer with camera/robot connected
3. ✅ Access from phone/tablet via WiFi
4. ❌ Don't use Streamlit Cloud
5. ❌ Don't try to deploy to remote servers

This gives you wireless control while maintaining full hardware access!

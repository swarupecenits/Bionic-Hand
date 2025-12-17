# Robot Hand Controller - Complete Setup Guide

## 🎯 Overview

This system allows users to control a robotic hand using hand tracking. The architecture is designed for easy deployment:

- **Web Interface** (Deployed on Streamlit Cloud): User-friendly UI for downloading and configuring
- **Local Client** (Runs on user's computer): Handles camera, MediaPipe processing, and serial communication

## 🌐 Two Deployment Options

### Option 1: Web Interface (Recommended for Distribution)

**Purpose**: Help users download and configure the system  
**Deployment**: Streamlit Cloud  
**File**: `web_interface.py`

This is a **lightweight web app** that:
- ✅ Provides download links
- ✅ Shows installation instructions  
- ✅ Generates configuration commands
- ✅ Offers troubleshooting help
- ✅ **No camera or serial needed** (just a guide)

**To deploy this to Streamlit Cloud:**

1. Create `requirements_web.txt` with just:
   ```
   streamlit>=1.28.0
   ```

2. Deploy `web_interface.py` to Streamlit Cloud

3. Users access your deployed URL, download files, and run locally

### Option 2: Local Network Access (Full Features)

**Purpose**: Run the full app on local network  
**Deployment**: Local computer  
**File**: `streamlit_app.py`

This is the **full-featured app** that:
- ✅ Provides web UI
- ✅ Handles camera access
- ✅ Processes hand tracking
- ✅ Communicates with serial port
- ❌ Cannot deploy to Streamlit Cloud (needs hardware)

**To run locally with network access:**

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```

Then access from any device on your network at `http://<your-ip>:8501`

## 📥 For End Users

### Step 1: Visit the Web Interface

Go to your deployed Streamlit Cloud app (e.g., `https://your-app.streamlit.app`)

### Step 2: Download Files

Download the repository:
```bash
git clone https://github.com/swarupecenits/Bionic-Hand.git
cd Bionic-Hand
```

Or download ZIP from GitHub

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Find Your COM Port

```bash
python local_client.py --list-ports
```

### Step 5: Run the Controller

```bash
python local_client.py --serial-port COM14 --enable-serial
```

Replace `COM14` with your actual COM port.

## 📁 File Structure

```
Bionic-Hand/
├── web_interface.py          # Deploy THIS to Streamlit Cloud
├── requirements_web.txt      # Use THIS for Streamlit Cloud
├── local_client.py           # Users download and run locally
├── streamlit_app.py          # Alternative: Full app (local network only)
├── robot_controller.py       # Core controller class
├── controller.py             # Original standalone version
├── opencv_cam.py             # Webcam interface
├── depthai_cam.py            # OAK-D camera interface
├── requirements.txt          # Full dependencies (for local installation)
└── README.md                 # This file
```

## 🚀 Deployment Instructions

### For Streamlit Cloud (Public Access):

1. **Create a new app** on Streamlit Cloud
2. **Set Main file**: `web_interface.py`
3. **Set Requirements file**: `requirements_web.txt`
4. **Deploy!**

This creates a public website where users can:
- Get download links
- See installation instructions
- Generate configuration commands
- Get help troubleshooting

### For Local Network (Private Network):

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run with network access**:
   ```bash
   streamlit run streamlit_app.py --server.address 0.0.0.0
   ```

3. **Find your IP**:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`

4. **Access from other devices**:
   ```
   http://<your-ip>:8501
   ```

## 🔧 Configuration Options

### Local Client Arguments:

```bash
python local_client.py \
  --serial-port COM14 \        # Your COM port
  --enable-serial \            # Enable robot communication
  --serial-fps 20 \            # Commands per second
  --lpf-value 0.25 \          # Smoothing (0.0-1.0)
  --force-webcam              # Use webcam instead of OAK-D
```

### List Available Ports:

```bash
python local_client.py --list-ports
```

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│   Streamlit Cloud (Public Internet)     │
│                                         │
│  web_interface.py                       │
│  - Download instructions                │
│  - Configuration help                   │
│  - Troubleshooting guide                │
└─────────────────────────────────────────┘
                    │
                    │ User downloads files
                    ▼
┌─────────────────────────────────────────┐
│   User's Local Computer                 │
│                                         │
│  local_client.py                        │
│  ├─ Camera capture                      │
│  ├─ MediaPipe processing                │
│  ├─ Serial communication                │
│  └─ Video display                       │
│                                         │
│  Connected:                             │
│  ├─ Camera (USB/built-in)              │
│  └─ Robot Hand (USB serial)            │
└─────────────────────────────────────────┘
```

## 🆚 Comparison of Deployment Options

| Feature | Web Interface | Local Network App | Local Client |
|---------|--------------|-------------------|--------------|
| Deploy to Cloud | ✅ Yes | ❌ No | ❌ No |
| Camera Access | ❌ No | ✅ Yes | ✅ Yes |
| Serial Access | ❌ No | ✅ Yes | ✅ Yes |
| Network Access | ✅ Internet | ✅ Local WiFi | ❌ Single PC |
| Purpose | Instructions | Full UI | Full Control |
| File | `web_interface.py` | `streamlit_app.py` | `local_client.py` |

## 💡 Recommended Setup

**For Distribution to Multiple Users:**

1. **Deploy `web_interface.py`** to Streamlit Cloud
   - This gives users a public URL to access instructions
   - No hardware needed for deployment

2. **Users download** files from GitHub
   - Clone repo or download ZIP

3. **Users run `local_client.py`** on their own computers
   - Full hardware access
   - No network setup needed
   - Simple command-line interface

**For Single User / Lab Setup:**

1. **Run `streamlit_app.py`** on main computer
   - Full web UI with all features
   - Access from tablets/phones via WiFi

2. Or use **original `controller.py`**
   - Standalone desktop application
   - No web interface needed

## 🔒 Security Considerations

### Web Interface (Public):
- ✅ Safe to deploy publicly (no sensitive data)
- ✅ Read-only instructions
- ✅ No hardware access

### Local Network App:
- ⚠️ Only accessible on local network
- ⚠️ Don't expose to internet
- ⚠️ Use firewall rules

### Local Client:
- ✅ Runs entirely offline
- ✅ No network required
- ✅ Most secure option

## 📝 License

See LICENSE file

## 🤝 Contributing

Contributions welcome! Please open issues or pull requests on GitHub.

## 📧 Support

- GitHub Issues: [Report bugs](https://github.com/swarupecenits/Bionic-Hand/issues)
- Documentation: [Full docs](https://github.com/swarupecenits/Bionic-Hand/blob/main/README.md)

---

Made with ❤️ using MediaPipe, OpenCV, and Streamlit

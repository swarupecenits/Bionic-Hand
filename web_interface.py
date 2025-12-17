"""
Robot Hand Controller - Web Interface
This provides a simple UI for users to download and configure the local client
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Robot Hand Controller",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .step-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1E88E5;
        margin: 1rem 0;
    }
    .code-box {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 Robot Hand Controller</h1>', unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
    Control your bionic robot hand using hand tracking and pose detection
</div>
""", unsafe_allow_html=True)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Quick Start", "📥 Download", "⚙️ Configuration", "❓ Troubleshooting"])

with tab1:
    st.header("Quick Start Guide")
    
    st.markdown("""
    ### Welcome! 👋
    
    This system allows you to control a robotic hand by tracking your hand movements using a camera.
    The processing happens on **your local computer** to ensure real-time performance and USB access.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="step-box">
            <h3>1️⃣ Download Files</h3>
            <p>Download the complete codebase from GitHub</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="step-box">
            <h3>2️⃣ Install Dependencies</h3>
            <p>Install Python packages (one-time setup)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="step-box">
            <h3>3️⃣ Run Client</h3>
            <p>Connect your robot and start controlling</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("System Requirements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Hardware:**
        - ✅ Camera (webcam or OAK-D)
        - ✅ Robot hand with USB connection
        - ✅ Windows, Mac, or Linux computer
        - ✅ 4GB+ RAM recommended
        """)
    
    with col2:
        st.markdown("""
        **Software:**
        - ✅ Python 3.8 or higher
        - ✅ USB drivers for robot
        - ✅ Camera drivers
        - ✅ 2GB free disk space
        """)

with tab2:
    st.header("📥 Download & Installation")
    
    st.subheader("Option 1: Download from GitHub (Recommended)")
    
    st.markdown("""
    Download the complete project with all files:
    """)
    
    st.code("""
# Clone the repository
git clone https://github.com/swarupecenits/Bionic-Hand.git

# Navigate to the directory
cd Bionic-Hand
    """, language="bash")
    
    st.markdown("""
    Or download directly: [https://github.com/swarupecenits/Bionic-Hand/archive/refs/heads/main.zip](https://github.com/swarupecenits/Bionic-Hand/archive/refs/heads/main.zip)
    """)
    
    st.divider()
    
    st.subheader("Install Python Dependencies")
    
    st.markdown("""
    After downloading, install the required packages:
    """)
    
    tab_win, tab_mac, tab_linux = st.tabs(["Windows", "macOS", "Linux"])
    
    with tab_win:
        st.code("""
# Open Command Prompt or PowerShell
cd path\\to\\Bionic-Hand

# Create virtual environment (recommended)
python -m venv venv
venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
        """, language="bash")
    
    with tab_mac:
        st.code("""
# Open Terminal
cd path/to/Bionic-Hand

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
        """, language="bash")
    
    with tab_linux:
        st.code("""
# Open Terminal
cd path/to/Bionic-Hand

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
        """, language="bash")

with tab3:
    st.header("⚙️ Configuration & Usage")
    
    st.subheader("Step 1: Find Your COM Port")
    
    st.markdown("""
    First, find which COM port your robot is connected to:
    """)
    
    st.code("""
# List available serial ports
python local_client.py --list-ports
    """, language="bash")
    
    st.info("📝 **Example output:**  \n`COM14` (Windows) or `/dev/ttyUSB0` (Linux) or `/dev/cu.usbserial` (Mac)")
    
    st.divider()
    
    st.subheader("Step 2: Run the Controller")
    
    st.markdown("""
    Run the local client with your COM port:
    """)
    
    port_input = st.text_input("Enter your COM port:", placeholder="e.g., COM14 or /dev/ttyUSB0")
    enable_serial = st.checkbox("Enable Serial Communication", value=True)
    serial_fps = st.slider("Serial FPS", 1, 60, 20)
    lpf_value = st.slider("Low Pass Filter", 0.0, 1.0, 0.25, help="Lower = smoother, Higher = more responsive")
    use_webcam = st.checkbox("Force Webcam (disable OAK-D)", value=False)
    
    if port_input:
        command = f"python local_client.py --serial-port {port_input}"
        if enable_serial:
            command += " --enable-serial"
        if serial_fps != 20:
            command += f" --serial-fps {serial_fps}"
        if lpf_value != 0.25:
            command += f" --lpf-value {lpf_value}"
        if use_webcam:
            command += " --force-webcam"
        
        st.code(command, language="bash")
        
        st.success("✅ Copy and run this command in your terminal!")
    else:
        st.warning("⚠️ Enter your COM port above to generate the command")
    
    st.divider()
    
    st.subheader("Alternative: Use Original Controller")
    
    st.markdown("""
    You can also use the original controller with more features:
    """)
    
    st.code("""
python controller.py --enable-serial --serial-port COM14 --serial-fps 20
    """, language="bash")

with tab4:
    st.header("❓ Troubleshooting")
    
    with st.expander("🔴 Camera not working"):
        st.markdown("""
        **Solutions:**
        1. Check if camera is properly connected
        2. Close other applications using the camera (Zoom, Skype, etc.)
        3. Grant camera permissions to Python
        4. Try `--force-webcam` flag
        5. Check camera in other apps first
        
        **Test camera:**
        ```python
        python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAILED'); cap.release()"
        ```
        """)
    
    with st.expander("🔴 Serial port not found"):
        st.markdown("""
        **Solutions:**
        1. Connect robot via USB
        2. Install USB drivers (check robot manufacturer website)
        3. Check Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac)
        4. Try different USB ports
        5. Restart computer
        
        **Windows - Check Device Manager:**
        - Open Device Manager
        - Look under "Ports (COM & LPT)"
        - Note the COM number
        
        **List ports:**
        ```bash
        python local_client.py --list-ports
        ```
        """)
    
    with st.expander("🔴 Import errors / Module not found"):
        st.markdown("""
        **Solutions:**
        1. Make sure you installed dependencies:
           ```bash
           pip install -r requirements.txt
           ```
        
        2. Check Python version (3.8+ required):
           ```bash
           python --version
           ```
        
        3. Make sure all files are in the same directory:
           - `local_client.py`
           - `opencv_cam.py`
           - `depthai_cam.py`
           - `requirements.txt`
        
        4. Try reinstalling MediaPipe:
           ```bash
           pip uninstall mediapipe
           pip install mediapipe==0.10.30
           ```
        """)
    
    with st.expander("🔴 Low FPS / Laggy"):
        st.markdown("""
        **Solutions:**
        1. Lower camera resolution (use `--force-webcam`)
        2. Close other applications
        3. Increase `--lpf-value` (less smoothing, faster response)
        4. Reduce `--serial-fps`
        5. Use a more powerful computer
        6. Update graphics drivers
        """)
    
    with st.expander("🔴 Robot not responding"):
        st.markdown("""
        **Solutions:**
        1. Make sure `--enable-serial` flag is used
        2. Check correct COM port
        3. Verify robot is powered on
        4. Check USB cable connection
        5. Verify baud rate (115200 default)
        6. Test with Arduino Serial Monitor first
        7. Check robot firmware is uploaded
        """)
    
    with st.expander("🔴 Hand not detected"):
        st.markdown("""
        **Solutions:**
        1. Ensure good lighting
        2. Show your **right hand** to the camera
        3. Keep hand in frame
        4. Remove gloves or coverings
        5. Move hand slowly initially
        6. Stand further from camera if too close
        7. Check MediaPipe detection confidence (in code)
        """)
    
    st.divider()
    
    st.subheader("Still Having Issues?")
    st.markdown("""
    - 📖 Check the full documentation: [GitHub README](https://github.com/swarupecenits/Bionic-Hand)
    - 🐛 Report bugs: [GitHub Issues](https://github.com/swarupecenits/Bionic-Hand/issues)
    - 💬 Ask questions in the repository discussions
    """)

# Footer
st.divider()

st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <h3>📚 Additional Resources</h3>
    <p>
        <a href="https://github.com/swarupecenits/Bionic-Hand" target="_blank">GitHub Repository</a> • 
        <a href="https://github.com/swarupecenits/Bionic-Hand/blob/main/README.md" target="_blank">Documentation</a> • 
        <a href="https://github.com/swarupecenits/Bionic-Hand/issues" target="_blank">Support</a>
    </p>
    <p style='margin-top: 1rem; font-size: 0.9rem;'>
        Made with ❤️ using MediaPipe, OpenCV, and Streamlit
    </p>
</div>
""", unsafe_allow_html=True)

"""
Streamlit Web App for Robot Hand Controller
Allows wireless control and monitoring of the robot hand via web browser
"""

import streamlit as st
import cv2
import numpy as np
import threading
import time
import serial.tools.list_ports
from robot_controller import RobotHandController, MEDIAPIPE_AVAILABLE

# Try importing camera modules
try:
    import opencv_cam
    OPENCV_CAM_AVAILABLE = True
except ImportError:
    OPENCV_CAM_AVAILABLE = False
    opencv_cam = None

try:
    import depthai_cam
    DEPTHAI_CAM_AVAILABLE = True
except ImportError:
    DEPTHAI_CAM_AVAILABLE = False
    depthai_cam = None

# Page configuration
st.set_page_config(
    page_title="Robot Hand Controller",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .status-active {
        background-color: #4CAF50;
        color: white;
    }
    .status-inactive {
        background-color: #F44336;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'controller' not in st.session_state:
    st.session_state.controller = None
if 'running' not in st.session_state:
    st.session_state.running = False
if 'controller_thread' not in st.session_state:
    st.session_state.controller_thread = None
if 'selected_port' not in st.session_state:
    st.session_state.selected_port = None

def get_available_ports():
    """Get list of available serial ports"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def start_controller():
    """Initialize and start the controller"""
    try:
        # Initialize camera
        if st.session_state.use_oakd and not st.session_state.force_webcam:
            camera = depthai_cam.DepthAICam(
                width=st.session_state.oakd_width,
                height=st.session_state.oakd_height
            )
            if not camera.is_depthai_device_available():
                st.warning("OAK-D camera not found, falling back to webcam")
                camera = opencv_cam.OpenCVCam(
                    width=st.session_state.webcam_width,
                    height=st.session_state.webcam_height
                )
        else:
            camera = opencv_cam.OpenCVCam(
                width=st.session_state.webcam_width,
                height=st.session_state.webcam_height
            )
        
        # Initialize controller
        st.session_state.controller = RobotHandController(
            camera_source=camera,
            serial_port=st.session_state.selected_port,
            serial_fps=st.session_state.serial_fps,
            lpf_value=st.session_state.lpf_value,
            enable_serial=st.session_state.enable_serial,
            preview_width=st.session_state.preview_width,
            preview_height=st.session_state.preview_height
        )
        
        # Start controller
        if st.session_state.controller.start():
            st.session_state.running = True
            
            # Start processing thread
            st.session_state.controller_thread = threading.Thread(
                target=st.session_state.controller.run_loop,
                daemon=True
            )
            st.session_state.controller_thread.start()
            
            st.success("✅ Controller started successfully!")
            return True
        else:
            st.error("❌ Failed to start controller")
            return False
            
    except Exception as e:
        st.error(f"❌ Error starting controller: {e}")
        return False

def stop_controller():
    """Stop the controller"""
    if st.session_state.controller:
        st.session_state.controller.stop()
        st.session_state.running = False
        st.session_state.controller = None
        st.session_state.controller_thread = None
        st.success("⏹️ Controller stopped")

# Header
st.markdown('<h1 class="main-header">🤖 Robot Hand Controller</h1>', unsafe_allow_html=True)

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Serial Port Settings
    st.subheader("Serial Port")
    available_ports = get_available_ports()
    
    if available_ports:
        st.session_state.selected_port = st.selectbox(
            "Select COM Port",
            options=available_ports,
            index=0 if st.session_state.selected_port is None else 
                  (available_ports.index(st.session_state.selected_port) 
                   if st.session_state.selected_port in available_ports else 0)
        )
    else:
        st.warning("⚠️ No serial ports detected")
        st.session_state.selected_port = st.text_input("Enter COM Port manually", value="COM14")
    
    st.session_state.enable_serial = st.checkbox("Enable Serial Communication", value=False)
    st.session_state.serial_fps = st.slider("Serial FPS", min_value=1, max_value=60, value=20)
    
    st.divider()
    
    # Camera Settings
    st.subheader("Camera Settings")
    st.session_state.use_oakd = st.checkbox("Use OAK-D Camera", value=True)
    st.session_state.force_webcam = st.checkbox("Force Webcam", value=False)
    
    with st.expander("OAK-D Settings"):
        st.session_state.oakd_width = st.number_input("Width", value=3840, step=160)
        st.session_state.oakd_height = st.number_input("Height", value=2160, step=90)
    
    with st.expander("Webcam Settings"):
        st.session_state.webcam_width = st.number_input("Width", value=1920, step=160, key="webcam_w")
        st.session_state.webcam_height = st.number_input("Height", value=1080, step=90, key="webcam_h")
    
    st.session_state.preview_width = st.slider("Preview Width", 640, 1920, 1280, step=160)
    st.session_state.preview_height = st.slider("Preview Height", 360, 1080, 720, step=90)
    
    st.divider()
    
    # Processing Settings
    st.subheader("Processing Settings")
    st.session_state.lpf_value = st.slider(
        "Low Pass Filter", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.25,
        help="1.0 = no filtering, lower values = more smoothing"
    )
    
    st.divider()
    
    # Control Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start", disabled=st.session_state.running, use_container_width=True):
            start_controller()
    with col2:
        if st.button("⏹️ Stop", disabled=not st.session_state.running, use_container_width=True):
            stop_controller()
    
    if st.button("🔄 Refresh Ports", use_container_width=True):
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📹 Live Video Feed")
    video_placeholder = st.empty()
    
    if st.session_state.running and st.session_state.controller:
        # Display video stream
        while st.session_state.running:
            frame = st.session_state.controller.get_frame()
            if frame is not None:
                # Convert BGR to RGB for Streamlit
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            time.sleep(0.033)  # ~30 FPS display update
    else:
        video_placeholder.info("👆 Click 'Start' to begin video stream")

with col2:
    st.subheader("📊 Status & Metrics")
    
    # Connection Status
    status_placeholder = st.empty()
    if st.session_state.running:
        status_placeholder.markdown(
            '<div class="status-box status-active">🟢 System Active</div>',
            unsafe_allow_html=True
        )
    else:
        status_placeholder.markdown(
            '<div class="status-box status-inactive">🔴 System Inactive</div>',
            unsafe_allow_html=True
        )
    
    # Real-time metrics
    if st.session_state.running and st.session_state.controller:
        st.divider()
        
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            st.metric("Frame Rate", f"{st.session_state.controller.frame_rate:.1f} FPS")
            st.metric("Elbow Angle", f"{st.session_state.controller.right_elbow_angle:.1f}°")
        
        with metrics_col2:
            st.metric("Serial Port", st.session_state.selected_port or "N/A")
            st.metric("Wrist Rotation", f"{st.session_state.controller.wrist_rotation:.1f}°")
        
        st.divider()
        
        # Joint angles display
        with st.expander("📐 Joint Angles (0-255)", expanded=False):
            if st.session_state.controller.joint_angles is not None:
                angles = np.clip(st.session_state.controller.joint_angles, 0, 255).astype(int)
                
                # Display in groups
                st.write("**Fingers (0-15):**")
                st.text(f"Index:  {angles[0]:3d} {angles[1]:3d} {angles[2]:3d}")
                st.text(f"Middle: {angles[3]:3d} {angles[4]:3d} {angles[5]:3d}")
                st.text(f"Ring:   {angles[6]:3d} {angles[7]:3d} {angles[8]:3d}")
                st.text(f"Pinky:  {angles[9]:3d} {angles[10]:3d} {angles[11]:3d}")
                st.text(f"Thumb:  {angles[12]:3d} {angles[13]:3d} {angles[14]:3d} {angles[15]:3d}")
                
                st.write("**Wrist & Arm (16-22):**")
                st.text(f"Wrist:    {angles[16]:3d} {angles[17]:3d} {angles[18]:3d}")
                st.text(f"Shoulder: {angles[19]:3d} {angles[20]:3d} {angles[21]:3d}")
                st.text(f"Elbow:    {angles[22]:3d}")
    
    st.divider()
    
    # Information
    with st.expander("ℹ️ Information"):
        st.markdown("""
        ### How to Use:
        1. **Connect Hardware**: Plug in your camera and robot hand
        2. **Configure**: Select COM port and adjust settings
        3. **Start**: Click the Start button to begin
        4. **Control**: Move your hand in front of the camera
        
        ### Features:
        - Real-time hand and pose tracking
        - Wireless control via web browser
        - Adjustable processing parameters
        - Serial communication to robot
        
        ### Access from Other Devices:
        Find your computer's IP address and access this app from any device on your network:
        ```
        http://<your-ip>:8501
        ```
        
        To find your IP:
        - Windows: `ipconfig` in Command Prompt
        - Look for "IPv4 Address"
        """)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Robot Hand Controller | Powered by MediaPipe & Streamlit</p>
        <p>Access this interface from any device on your network</p>
    </div>
""", unsafe_allow_html=True)

# Auto-refresh for metrics when running
if st.session_state.running:
    time.sleep(0.1)
    st.rerun()

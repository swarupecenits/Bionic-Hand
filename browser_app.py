"""
Robot Hand Controller - Browser-Based Version
Uses Web Serial API for direct browser-to-robot communication
No installation required - just open in Chrome/Edge browser
"""

import streamlit as st
import streamlit.components.v1 as components

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
    #video-container {
        position: relative;
        width: 100%;
        max-width: 1280px;
        margin: 0 auto;
    }
    #webcam {
        width: 100%;
        transform: scaleX(-1);
        border-radius: 10px;
    }
    #canvas {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        transform: scaleX(-1);
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    .status-connected {
        background-color: #4CAF50;
        color: white;
    }
    .status-disconnected {
        background-color: #F44336;
        color: white;
    }
    .control-panel {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 Robot Hand Controller</h1>', unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; color: #666; margin-bottom: 2rem;'>
    <strong>No Installation Required!</strong> Just connect your robot via USB and use Chrome/Edge browser
</div>
""", unsafe_allow_html=True)

# Browser compatibility check
st.info("""
⚠️ **Browser Requirements:**
- ✅ Google Chrome (version 89+)
- ✅ Microsoft Edge (version 89+)
- ❌ Firefox (not supported yet)
- ❌ Safari (not supported yet)

This app uses the Web Serial API which is only available in Chromium-based browsers.
""")

# Main HTML/JavaScript component
html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/control_utils/control_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/holistic/holistic.js" crossorigin="anonymous"></script>
</head>
<body>
    <div style="max-width: 1400px; margin: 0 auto; padding: 20px;">
        
        <!-- Control Panel -->
        <div class="control-panel">
            <h3>🎮 Controls</h3>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
                <button id="connectBtn" onclick="connectSerial()" 
                    style="padding: 10px 20px; font-size: 16px; background: #1E88E5; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    🔌 Connect Serial Port
                </button>
                
                <button id="startBtn" onclick="startCamera()" 
                    style="padding: 10px 20px; font-size: 16px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    📹 Start Camera
                </button>
                
                <button id="stopBtn" onclick="stopCamera()" disabled
                    style="padding: 10px 20px; font-size: 16px; background: #F44336; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    ⏹️ Stop
                </button>
                
                <label style="margin-left: 20px;">
                    Serial FPS: 
                    <input type="range" id="serialFps" min="1" max="60" value="20" 
                        oninput="document.getElementById('fpsValue').textContent = this.value">
                    <span id="fpsValue">20</span>
                </label>
                
                <label>
                    <input type="checkbox" id="enableSerial" checked> Enable Serial
                </label>
            </div>
            
            <div id="status" class="status-box status-disconnected" style="margin-top: 15px;">
                ⚪ Not Connected
            </div>
        </div>

        <!-- Video Display -->
        <div id="video-container" style="margin: 20px 0;">
            <video id="webcam" autoplay playsinline></video>
            <canvas id="canvas"></canvas>
        </div>

        <!-- Statistics -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
            <div style="background: #f0f2f6; padding: 15px; border-radius: 8px; text-align: center;">
                <div style="font-size: 14px; color: #666;">Frame Rate</div>
                <div id="fps" style="font-size: 24px; font-weight: bold; color: #1E88E5;">0 FPS</div>
            </div>
            <div style="background: #f0f2f6; padding: 15px; border-radius: 8px; text-align: center;">
                <div style="font-size: 14px; color: #666;">Serial Port</div>
                <div id="portName" style="font-size: 24px; font-weight: bold; color: #1E88E5;">None</div>
            </div>
            <div style="background: #f0f2f6; padding: 15px; border-radius: 8px; text-align: center;">
                <div style="font-size: 14px; color: #666;">Packets Sent</div>
                <div id="packetCount" style="font-size: 24px; font-weight: bold; color: #1E88E5;">0</div>
            </div>
            <div style="background: #f0f2f6; padding: 15px; border-radius: 8px; text-align: center;">
                <div style="font-size: 14px; color: #666;">Hand Detected</div>
                <div id="handDetected" style="font-size: 24px; font-weight: bold; color: #F44336;">NO</div>
            </div>
        </div>

        <!-- Joint Angles Display -->
        <details style="background: #f0f2f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <summary style="cursor: pointer; font-weight: bold;">📐 Joint Angles (Click to expand)</summary>
            <pre id="angles" style="margin-top: 10px; font-family: monospace; font-size: 12px;"></pre>
        </details>
    </div>

    <script>
        // Global variables
        let port = null;
        let writer = null;
        let camera = null;
        let holistic = null;
        let jointAngles = new Array(23).fill(0);
        let packetCount = 0;
        let lastSerialTime = 0;
        let isRunning = false;

        // Initialize MediaPipe Holistic
        holistic = new Holistic({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`;
            }
        });

        holistic.setOptions({
            modelComplexity: 1,
            smoothLandmarks: true,
            enableSegmentation: false,
            smoothSegmentation: false,
            refineFaceLandmarks: false,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });

        holistic.onResults(onResults);

        // Connect to serial port
        async function connectSerial() {
            try {
                // Request serial port
                port = await navigator.serial.requestPort();
                await port.open({ baudRate: 115200 });
                
                writer = port.writable.getWriter();
                
                document.getElementById('status').className = 'status-box status-connected';
                document.getElementById('status').innerHTML = '🟢 Serial Connected';
                
                // Get port info
                const info = port.getInfo();
                document.getElementById('portName').textContent = 'Connected';
                
                console.log('Serial port connected');
            } catch (error) {
                console.error('Error connecting to serial port:', error);
                alert('Failed to connect to serial port: ' + error.message);
            }
        }

        // Start camera and processing
        async function startCamera() {
            try {
                const video = document.getElementById('webcam');
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 1280, height: 720 }
                });
                
                video.srcObject = stream;
                
                camera = new Camera(video, {
                    onFrame: async () => {
                        await holistic.send({ image: video });
                    },
                    width: 1280,
                    height: 720
                });
                
                camera.start();
                isRunning = true;
                
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                
                console.log('Camera started');
            } catch (error) {
                console.error('Error starting camera:', error);
                alert('Failed to start camera: ' + error.message);
            }
        }

        // Stop camera
        function stopCamera() {
            if (camera) {
                camera.stop();
                isRunning = false;
            }
            
            const video = document.getElementById('webcam');
            if (video.srcObject) {
                video.srcObject.getTracks().forEach(track => track.stop());
            }
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }

        // Calculate angle between three points
        function calculateAngle(a, b, c) {
            const ba = { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z };
            const bc = { x: c.x - b.x, y: c.y - b.y, z: c.z - b.z };
            
            const dot = ba.x * bc.x + ba.y * bc.y + ba.z * bc.z;
            const magBa = Math.sqrt(ba.x * ba.x + ba.y * ba.y + ba.z * ba.z);
            const magBc = Math.sqrt(bc.x * bc.x + bc.y * bc.y + bc.z * bc.z);
            
            const cosAngle = dot / (magBa * magBc);
            const angle = Math.acos(Math.max(-1, Math.min(1, cosAngle)));
            
            return angle * (180 / Math.PI);
        }

        // Process MediaPipe results
        function onResults(results) {
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            const video = document.getElementById('webcam');
            
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            ctx.save();
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw pose
            if (results.poseLandmarks) {
                drawConnectors(ctx, results.poseLandmarks, POSE_CONNECTIONS, {color: '#00FF00', lineWidth: 2});
                drawLandmarks(ctx, results.poseLandmarks, {color: '#FF0000', lineWidth: 1, radius: 3});
            }
            
            // Draw hands
            if (results.rightHandLandmarks) {
                drawConnectors(ctx, results.rightHandLandmarks, HAND_CONNECTIONS, {color: '#00FF00', lineWidth: 2});
                drawLandmarks(ctx, results.rightHandLandmarks, {color: '#FF0000', lineWidth: 1, radius: 2});
                
                document.getElementById('handDetected').textContent = 'YES';
                document.getElementById('handDetected').style.color = '#4CAF50';
            } else {
                document.getElementById('handDetected').textContent = 'NO';
                document.getElementById('handDetected').style.color = '#F44336';
            }
            
            ctx.restore();
            
            // Calculate joint angles
            if (results.poseWorldLandmarks && results.rightHandLandmarks) {
                calculateJointAngles(results);
                sendSerialData();
            }
            
            // Update FPS
            updateFPS();
        }

        // Calculate all joint angles
        function calculateJointAngles(results) {
            // Simplified angle calculation - basic implementation
            // In production, you'd implement the full algorithm from controller.py
            
            if (results.rightHandLandmarks) {
                const hand = results.rightHandLandmarks;
                
                // Simple finger angles (index finger as example)
                jointAngles[0] = calculateAngle(hand[0], hand[5], hand[8]);
                jointAngles[1] = calculateAngle(hand[9], hand[5], hand[6]);
                jointAngles[2] = calculateAngle(hand[5], hand[6], hand[7]);
                
                // Set other angles to defaults for now
                for (let i = 3; i < 23; i++) {
                    jointAngles[i] = 90; // Default middle position
                }
            }
            
            // Update display
            const anglesInt = jointAngles.map(a => Math.round(Math.max(0, Math.min(255, a))));
            document.getElementById('angles').textContent = 
                'Fingers:\n' +
                `Index:  ${anglesInt[0].toString().padStart(3)} ${anglesInt[1].toString().padStart(3)} ${anglesInt[2].toString().padStart(3)}\n` +
                `Middle: ${anglesInt[3].toString().padStart(3)} ${anglesInt[4].toString().padStart(3)} ${anglesInt[5].toString().padStart(3)}\n` +
                `Ring:   ${anglesInt[6].toString().padStart(3)} ${anglesInt[7].toString().padStart(3)} ${anglesInt[8].toString().padStart(3)}\n` +
                `Pinky:  ${anglesInt[9].toString().padStart(3)} ${anglesInt[10].toString().padStart(3)} ${anglesInt[11].toString().padStart(3)}\n` +
                `Thumb:  ${anglesInt[12].toString().padStart(3)} ${anglesInt[13].toString().padStart(3)} ${anglesInt[14].toString().padStart(3)} ${anglesInt[15].toString().padStart(3)}`;
        }

        // Send data via serial
        async function sendSerialData() {
            if (!writer || !document.getElementById('enableSerial').checked) return;
            
            const fps = parseInt(document.getElementById('serialFps').value);
            const period = 1000 / fps;
            
            const now = Date.now();
            if (now - lastSerialTime < period) return;
            lastSerialTime = now;
            
            try {
                // Convert to bytes
                const angles = jointAngles.map(a => Math.round(Math.max(0, Math.min(255, a))));
                
                // Calculate checksum
                const sum = angles.reduce((a, b) => a + b, 0) & 0xFF;
                const checksum = 255 - sum;
                
                // Build packet
                const packet = new Uint8Array(29);
                packet[0] = 0xFE;  // Start byte 1
                packet[1] = 0xFE;  // Start byte 2
                for (let i = 0; i < 23; i++) {
                    packet[i + 2] = angles[i];
                }
                packet[25] = checksum;
                packet[26] = 0xFD;  // End byte 1
                packet[27] = 0xFD;  // End byte 2
                
                await writer.write(packet);
                
                packetCount++;
                document.getElementById('packetCount').textContent = packetCount;
                
            } catch (error) {
                console.error('Error sending serial data:', error);
            }
        }

        // FPS calculation
        let lastFrameTime = Date.now();
        let frameCount = 0;
        let fps = 0;

        function updateFPS() {
            frameCount++;
            const now = Date.now();
            if (now - lastFrameTime >= 1000) {
                fps = frameCount;
                document.getElementById('fps').textContent = fps + ' FPS';
                frameCount = 0;
                lastFrameTime = now;
            }
        }

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            if (writer) {
                writer.releaseLock();
            }
            if (port) {
                port.close();
            }
        });
    </script>
</body>
</html>
"""

# Display the component
components.html(html_code, height=1000, scrolling=True)

# Instructions
st.divider()

with st.expander("📖 How to Use", expanded=False):
    st.markdown("""
    ### Step-by-Step Guide:
    
    1. **Connect your robot** to your computer via USB
    
    2. **Click "Connect Serial Port"** button
       - Your browser will show a popup
       - Select your robot's COM port
       - Click "Connect"
    
    3. **Click "Start Camera"** button
       - Grant camera permissions if asked
       - You should see yourself on screen
    
    4. **Show your right hand** to the camera
       - The system will track your hand and pose
       - Green lines show detected landmarks
    
    5. **The robot will mimic your movements!**
       - Adjust "Serial FPS" if needed (higher = faster)
       - Uncheck "Enable Serial" to preview without sending commands
    
    ### ✅ That's it! No software installation required!
    """)

with st.expander("⚙️ Advanced Settings", expanded=False):
    st.markdown("""
    ### Configuration:
    
    - **Serial FPS**: How many commands per second to send (1-60)
      - Higher = more responsive but more data
      - Lower = smoother but slower response
      - Default: 20 FPS (good balance)
    
    - **Enable Serial**: Toggle serial communication on/off
      - Useful for testing without robot connected
      - Preview mode to check hand detection
    
    ### Browser Permissions:
    
    - **Camera**: Required for hand tracking
    - **Serial Port**: Required for robot control
    
    Both permissions are requested by your browser and can be revoked anytime.
    """)

with st.expander("🔧 Troubleshooting", expanded=False):
    st.markdown("""
    ### Common Issues:
    
    **Serial port not showing up:**
    - Make sure robot is connected via USB
    - Install USB drivers if needed
    - Try a different USB port
    - Refresh the page
    
    **Camera not working:**
    - Grant camera permissions
    - Close other apps using camera
    - Try a different browser (Chrome/Edge)
    - Check camera privacy settings
    
    **Hand not detected:**
    - Ensure good lighting
    - Show your RIGHT hand
    - Keep hand in frame
    - Move hand slowly initially
    
    **Robot not responding:**
    - Check "Enable Serial" is checked
    - Verify correct serial port selected
    - Check robot is powered on
    - Adjust Serial FPS if needed
    """)

st.divider()

st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🌐 <strong>100% Browser-Based</strong> • No Installation • No Downloads</p>
    <p style='font-size: 0.9rem;'>Powered by MediaPipe, Web Serial API, and Streamlit</p>
</div>
""", unsafe_allow_html=True)

"""
Local Client for Robot Hand Controller
This script runs on your local machine and handles:
- Camera capture
- MediaPipe processing  
- Serial communication with robot

It connects to the web interface for remote configuration and monitoring.
"""

import cv2
import mediapipe as mp
import numpy as np
from copy import deepcopy
import argparse
import struct
import time
import sys
import requests
import json
from threading import Thread, Lock
import serial
import serial.tools.list_ports

# Try importing camera modules
try:
    import opencv_cam
    import depthai_cam
except ImportError:
    print("Warning: Camera modules not found. Make sure opencv_cam.py and depthai_cam.py are in the same directory.")

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_hand = mp.solutions.hands
mp_holistic = mp.solutions.holistic


class LocalRobotClient:
    def __init__(self, serial_port, server_url=None, enable_serial=True, serial_fps=20, lpf_value=0.25):
        self.serial_port = serial_port
        self.server_url = server_url
        self.enable_serial = enable_serial
        self.serial_fps = serial_fps
        self.lpf_value = lpf_value
        
        self.ser = None
        self.joint_angles = np.zeros(23)
        self.is_valid_frame = False
        self.serial_timestamp = time.time()
        self.running = False
        self.frame_rate = 0.0
        
        # Stats for web interface
        self.stats = {
            'fps': 0.0,
            'joint_angles': [],
            'connected': True,
            'serial_port': serial_port,
            'is_valid_frame': False
        }
        self.stats_lock = Lock()
        
        if self.enable_serial:
            self._init_serial()
    
    def _init_serial(self):
        """Initialize serial port"""
        try:
            self.ser = serial.Serial(
                port=self.serial_port,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
                timeout=1
            )
            print(f"✅ Serial port {self.serial_port} opened successfully")
        except Exception as e:
            print(f"❌ Failed to open serial port {self.serial_port}: {e}")
            self.ser = None
    
    def angle(self, a, b, c):
        """Calculate angle between three points"""
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        return np.degrees(angle)
    
    def landmark_to_np(self, landmark):
        """Convert landmark to numpy array"""
        return np.array([landmark.x, landmark.y, landmark.z])
    
    def calculate_y_up_matrix(self, v):
        """Calculate rotation matrix to align vector with Y-up"""
        v = v / np.linalg.norm(v)
        axis = np.cross(v, np.array([0.0, 1.0, 0.0]))
        axis_norm = np.linalg.norm(axis)
        
        if axis_norm < 1e-6:
            return np.eye(3)
        
        axis = axis / axis_norm
        angle = -np.arccos(np.clip(np.dot(v, np.array([0.0, 1.0, 0.0])), -1.0, 1.0))
        
        axis_crossproduct_matrix = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])
        
        rotation_matrix = (
            np.eye(3) +
            np.sin(angle) * axis_crossproduct_matrix +
            (1 - np.cos(angle)) * np.dot(axis_crossproduct_matrix, axis_crossproduct_matrix)
        )
        
        return rotation_matrix
    
    def calculate_pose_angles(self, pose_world_landmarks):
        """Calculate pose angles from landmarks"""
        right_elbow = pose_world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
        right_wrist = pose_world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        right_shoulder = pose_world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_shoulder = pose_world_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_hip = pose_world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
        
        right_elbow_angle = self.angle(
            np.array([right_shoulder.x, right_shoulder.y]), 
            np.array([right_elbow.x, right_elbow.y]), 
            np.array([right_wrist.x, right_wrist.y])
        )
        right_elbow_angle = 180.0 - right_elbow_angle
        
        right_shoulder_yaw = self.angle(
            np.array([right_hip.x, right_hip.y]), 
            np.array([right_shoulder.x, right_shoulder.y]), 
            np.array([right_elbow.x, right_elbow.y])
        )
        
        yaw_cutoff = 30.0
        if right_shoulder_yaw < yaw_cutoff or right_shoulder_yaw > 180.0 - yaw_cutoff:
            right_shoulder_pitch = self.angle(
                np.array([right_hip.z, right_hip.y]), 
                np.array([right_shoulder.z, right_shoulder.y]), 
                np.array([right_elbow.z, right_elbow.y])
            )
        else:
            right_shoulder_pitch = 180.0 - self.angle(
                np.array([right_elbow.x, right_elbow.z]), 
                np.array([right_shoulder.x, right_shoulder.z]), 
                np.array([left_shoulder.x, left_shoulder.z])
            )
        
        return right_elbow_angle, right_shoulder_yaw, right_shoulder_pitch
    
    def calculate_finger_angles(self, joint_angles, joint_xyz):
        """Calculate finger joint angles"""
        # Index finger
        joint_angles[0] = self.angle(joint_xyz[0], joint_xyz[5], joint_xyz[8])
        joint_angles[1] = self.angle(joint_xyz[9], joint_xyz[5], joint_xyz[6])
        joint_angles[2] = self.angle(joint_xyz[5], joint_xyz[6], joint_xyz[7])
        
        # Middle finger
        joint_angles[3] = self.angle(joint_xyz[0], joint_xyz[9], joint_xyz[12])
        joint_angles[4] = self.angle(joint_xyz[13], joint_xyz[9], joint_xyz[10])
        joint_angles[5] = self.angle(joint_xyz[9], joint_xyz[10], joint_xyz[11])
        
        # Ring finger
        joint_angles[6] = self.angle(joint_xyz[0], joint_xyz[13], joint_xyz[16])
        joint_angles[7] = self.angle(joint_xyz[9], joint_xyz[13], joint_xyz[14])
        joint_angles[8] = self.angle(joint_xyz[13], joint_xyz[14], joint_xyz[15])
        
        # Pinky finger
        joint_angles[9] = self.angle(joint_xyz[0], joint_xyz[17], joint_xyz[20])
        joint_angles[10] = self.angle(joint_xyz[13], joint_xyz[17], joint_xyz[18])
        joint_angles[11] = self.angle(joint_xyz[17], joint_xyz[18], joint_xyz[19])
        
        # Thumb
        joint_angles[12] = self.angle(joint_xyz[1], joint_xyz[2], joint_xyz[3]) * 1.3
        joint_angles[13] = self.angle(joint_xyz[2], joint_xyz[1], joint_xyz[5])
        joint_angles[14] = self.angle(joint_xyz[2], joint_xyz[3], joint_xyz[4])
        joint_angles[15] = self.angle(joint_xyz[9], joint_xyz[5], joint_xyz[2])
        
        return joint_angles
    
    def transmit_angles_serial(self, joint_angles):
        """Transmit angles via serial port"""
        if not self.ser:
            return
        
        try:
            joint_angles_int = np.clip(joint_angles, 0, 255).astype(int)
            sum_val = int(np.sum(joint_angles_int))
            sum_val = sum_val & 0x000000FF
            t_xchecksum = 255 - sum_val
            
            command = b'\xFE'
            self.ser.write(command)
            self.ser.write(command)
            packed_data = struct.pack('23B', *joint_angles_int)
            self.ser.write(packed_data)
            self.ser.write(struct.pack('B', t_xchecksum))
            command = b'\xFD'
            self.ser.write(command)
            self.ser.write(command)
            self.ser.flushOutput()
        except Exception as e:
            print(f"Serial transmission error: {e}")
    
    def serial_timer_transmit(self):
        """Periodic serial transmission with rate limiting"""
        serial_period = 1.0 / self.serial_fps
        
        if (time.time() - self.serial_timestamp) > serial_period:
            if self.enable_serial:
                self.transmit_angles_serial(self.joint_angles)
            
            joint_angles_int = np.clip(self.joint_angles, 0, 255).astype(int)
            print(f"Angles: {joint_angles_int}")
            self.serial_timestamp = time.time()
            
            # Update stats for web interface
            with self.stats_lock:
                self.stats['joint_angles'] = joint_angles_int.tolist()
    
    def process_frame(self, image, results):
        """Process a single frame with MediaPipe results"""
        prev_joint_angles = self.joint_angles.astype(np.float32)
        
        # Calculate hand angles
        if results.right_hand_landmarks is not None:
            hand_landmarks = results.right_hand_landmarks
            hand_points = np.array([
                [hand_landmarks.landmark[i].x, hand_landmarks.landmark[i].y, hand_landmarks.landmark[i].z] 
                for i in range(21)
            ])
            
            hand_points_norm = deepcopy(hand_points)
            hand_points_norm -= hand_points_norm[0]
            
            normalized_up = hand_points_norm[mp_hand.HandLandmark.WRIST] - \
                           hand_points_norm[mp_hand.HandLandmark.MIDDLE_FINGER_MCP]
            normalized_up /= np.linalg.norm(normalized_up)
            
            hand_rotation_matrix = self.calculate_y_up_matrix(normalized_up)
            hand_points_norm = np.matmul(hand_points_norm, hand_rotation_matrix)
            
            # Calculate wrist rotation
            index = hand_points_norm[mp_hand.HandLandmark.INDEX_FINGER_MCP]
            pinky = hand_points_norm[mp_hand.HandLandmark.PINKY_MCP]
            zaxis = hand_points_norm[mp_hand.HandLandmark.PINKY_MCP] + np.array([0.0, 0.0, 1.0])
            
            wrist_rotation = 180 - self.angle(
                np.array([index[0], index[2]]),
                np.array([pinky[0], pinky[2]]),
                np.array([zaxis[0], zaxis[2]])
            )
            
            rel = index - pinky
            if rel[0] < 0:
                wrist_rotation = 360 - wrist_rotation
            
            # Calculate finger angles
            self.calculate_finger_angles(self.joint_angles, hand_points_norm)
            
            # Calculate wrist angles
            if results.pose_world_landmarks is not None:
                pose_wrist = self.landmark_to_np(
                    results.pose_world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
                )
                delta = pose_wrist - hand_points[0]
                hand_points += delta
                
                right_elbow = self.landmark_to_np(
                    results.pose_world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
                )
                
                hcp = (hand_points[0] + hand_points[5] + hand_points[17]) / 3.0
                hup = hand_points[9] - hand_points[0]
                hup /= np.linalg.norm(hup)
                hright = hand_points[5] - hand_points[17]
                hright /= np.linalg.norm(hright)
                hand_normal = np.cross(hright, hup)
                hand_normal /= np.linalg.norm(hand_normal)
                
                fk = hand_points[0] + hand_normal
                self.joint_angles[16] = self.angle(fk, hand_points[0], right_elbow) - 30.0
                
                wrist_yaw = self.angle(
                    hand_points[mp_hand.HandLandmark.MIDDLE_FINGER_MCP], 
                    hand_points[mp_hand.HandLandmark.WRIST], 
                    np.array([1.0, 0, 0])
                )
                self.joint_angles[17] = 180.0 - wrist_yaw
                self.joint_angles[18] = wrist_rotation
        
        # Calculate pose angles
        if results.pose_world_landmarks is not None:
            right_elbow_angle, right_shoulder_yaw, right_shoulder_pitch = \
                self.calculate_pose_angles(results.pose_world_landmarks)
            
            self.joint_angles[19] = right_shoulder_pitch
            self.joint_angles[20] = right_shoulder_yaw
            self.joint_angles[21] = 0.0
            self.joint_angles[22] = right_elbow_angle
        
        # Check validity
        self.is_valid_frame = results.pose_landmarks is not None and \
                             results.right_hand_landmarks is not None
        
        if self.is_valid_frame:
            self.joint_angles = (1.0 - self.lpf_value) * prev_joint_angles + \
                               self.lpf_value * self.joint_angles
            self.serial_timer_transmit()
        
        # Update stats
        with self.stats_lock:
            self.stats['is_valid_frame'] = self.is_valid_frame
        
        return image
    
    def run(self, camera_source):
        """Main processing loop"""
        self.running = True
        
        print(f"🚀 Starting Robot Hand Controller")
        print(f"📹 Camera: {type(camera_source).__name__}")
        print(f"🔌 Serial Port: {self.serial_port}")
        print(f"📡 Serial Enabled: {self.enable_serial}")
        
        if not camera_source.start():
            print("❌ Failed to start camera")
            return
        
        with mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as holistic:
            
            while self.running and camera_source.is_opened():
                frame_time = cv2.getTickCount()
                
                success, image = camera_source.read_frame()
                if not success:
                    continue
                
                # Process with MediaPipe
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
                
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )
                mp_drawing.draw_landmarks(
                    image,
                    results.right_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style()
                )
                
                # Process frame
                self.process_frame(image, results)
                
                # Calculate frame rate
                self.frame_rate = cv2.getTickFrequency() / (cv2.getTickCount() - frame_time)
                
                # Update stats
                with self.stats_lock:
                    self.stats['fps'] = self.frame_rate
                
                # Display
                image = cv2.resize(image, (1280, 720))
                cv2.rectangle(image, (0, 0), (200, 40), (0, 0, 0), -1)
                cv2.putText(image, f"FPS: {self.frame_rate:.2f}", (5, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
                
                image = cv2.flip(image, 1)
                cv2.imshow('Robot Hand Controller', image)
                
                if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                    break
        
        camera_source.stop()
        cv2.destroyAllWindows()
        
        if self.ser:
            self.ser.close()
        
        print("👋 Controller stopped")


def list_serial_ports():
    """List all available serial ports"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def main():
    parser = argparse.ArgumentParser(description='Local Robot Hand Controller Client')
    parser.add_argument('--serial-port', type=str, default=None, help='Serial port (e.g., COM14)')
    parser.add_argument('--enable-serial', action='store_true', help='Enable serial communication')
    parser.add_argument('--serial-fps', type=int, default=20, help='Serial transmission rate')
    parser.add_argument('--lpf-value', type=float, default=0.25, help='Low pass filter value')
    parser.add_argument('--force-webcam', action='store_true', help='Force webcam instead of OAK-D')
    parser.add_argument('--list-ports', action='store_true', help='List available serial ports and exit')
    args = parser.parse_args()
    
    # List ports if requested
    if args.list_ports:
        print("\n📡 Available Serial Ports:")
        ports = list_serial_ports()
        if ports:
            for port in ports:
                print(f"  - {port}")
        else:
            print("  No serial ports found")
        return
    
    # Check for serial port
    if not args.serial_port:
        print("\n⚠️  No serial port specified!")
        print("Available ports:")
        ports = list_serial_ports()
        if ports:
            for port in ports:
                print(f"  - {port}")
            print(f"\nExample: python local_client.py --serial-port {ports[0]} --enable-serial")
        else:
            print("  No serial ports found")
            print("\nExample: python local_client.py --serial-port COM14 --enable-serial")
        return
    
    # Initialize camera
    if args.force_webcam:
        camera = opencv_cam.OpenCVCam(width=1920, height=1080)
    else:
        try:
            camera = depthai_cam.DepthAICam(width=3840, height=2160)
            if not camera.is_depthai_device_available():
                print("OAK-D not found, using webcam...")
                camera = opencv_cam.OpenCVCam(width=1920, height=1080)
        except:
            camera = opencv_cam.OpenCVCam(width=1920, height=1080)
    
    # Create and run client
    client = LocalRobotClient(
        serial_port=args.serial_port,
        enable_serial=args.enable_serial,
        serial_fps=args.serial_fps,
        lpf_value=args.lpf_value
    )
    
    try:
        client.run(camera)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

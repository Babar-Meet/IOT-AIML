import cv2
import math
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

class HandDetector:
    def __init__(self, min_detection_conf=0.3, min_tracking_conf=0.5):
        # MediaPipe Tasks API setup
        model_path = 'models/hand_landmarker.task'
        base_options = BaseOptions(model_asset_path=model_path)
        options = HandLandmarkerOptions(
            base_options=base_options,
            running_mode=RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=min_detection_conf,
            min_hand_presence_confidence=min_detection_conf,
            min_tracking_confidence=min_tracking_conf
        )
        self.hand_landmarker = HandLandmarker.create_from_options(options)

        # Drawing Utils
        self.HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (0, 17),
            (17, 18), (18, 19), (19, 20),
        ]
        
    def detect(self, frame):
        """
        Runs mediapipe over frame. Returns the raw result and processed finger counts.
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        results = self.hand_landmarker.detect(mp_image)
        
        fingers_up_total = 0
        hand_details = []
        
        if results.hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.hand_landmarks):
                # Retrieve handedness (Left or Right)
                hand_type = "Left"
                if results.handedness:
                    hand_type = results.handedness[hand_idx][0].category_name
                
                # Count fingers for this hand
                count = self._count_fingers(hand_landmarks, hand_type)
                fingers_up_total += count
                
                hand_details.append({
                    "landmarks": hand_landmarks,
                    "type": hand_type,
                    "count": count
                })
        
        return results, fingers_up_total, hand_details

    def draw(self, frame, results):
        """
        Helper to overlay skeleton on frame using basic cv2 geometry.
        """
        if not results.hand_landmarks:
             return
             
        h, w = frame.shape[:2]
             
        for hand_landmarks in results.hand_landmarks:
            points = []
            for lm in hand_landmarks:
                points.append((int(lm.x * w), int(lm.y * h)))
                
            for connection in self.HAND_CONNECTIONS:
                pt1 = points[connection[0]]
                pt2 = points[connection[1]]
                cv2.line(frame, pt1, pt2, (0, 255, 0), 2, cv2.LINE_AA)
                
            for pt in points:
                cv2.circle(frame, pt, 4, (0, 0, 255), -1, cv2.LINE_AA)

    def _count_fingers(self, hand_landmarks, hand_type):
        """
        Calculates how many fingers are extended using orientation-independent 
        straightness ratios. This works regardless of hand rotation or mirroring.
        """
        def get_dist(p1, p2):
            return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
            
        fingers_extended = []
        
        # 1. Thumb (Points 2, 3, 4)
        # Straightness: Tip(4) to MCP(2) vs total length through IP(3)
        d_tip_mcp = get_dist(hand_landmarks[4], hand_landmarks[2])
        d_path = get_dist(hand_landmarks[4], hand_landmarks[3]) + get_dist(hand_landmarks[3], hand_landmarks[2])
        s_thumb = d_tip_mcp / d_path if d_path > 0 else 0
        
        # In addition to being straight, thumb must be away from the palm.
        # We compare tip distance to pinky base (17) vs IP distance to pinky base.
        d_tip_pinky = get_dist(hand_landmarks[4], hand_landmarks[17])
        d_ip_pinky = get_dist(hand_landmarks[3], hand_landmarks[17])
        
        # A threshold of ~0.85-0.9 indicates a reasonably 'straight' line.
        if s_thumb > 0.85 and d_tip_pinky > d_ip_pinky:
            fingers_extended.append(1)
        else:
            fingers_extended.append(0)
                
        # 2. Other 4 Fingers (Index, Middle, Ring, Pinky)
        # Check if the tip-to-MCP line is nearly the same length as the joint segments.
        for tip_id, pip_id, mcp_id in [(8, 6, 5), (12, 10, 9), (16, 14, 13), (20, 18, 17)]:
            d_direct = get_dist(hand_landmarks[tip_id], hand_landmarks[mcp_id])
            d_joint_path = get_dist(hand_landmarks[tip_id], hand_landmarks[pip_id]) + \
                           get_dist(hand_landmarks[pip_id], hand_landmarks[mcp_id])
            
            s_ratio = d_direct / d_joint_path if d_joint_path > 0 else 0
            
            # Using 0.85 to allow for slight natural curvature of extended fingers.
            if s_ratio > 0.85:
                # Also ensure tip is further from wrist than PIP is to handle 
                # weird perspective cases where a curled finger looks 'straight' 
                # but is pointing towards the palm.
                if get_dist(hand_landmarks[tip_id], hand_landmarks[0]) > get_dist(hand_landmarks[pip_id], hand_landmarks[0]):
                    fingers_extended.append(1)
                else:
                    fingers_extended.append(0)
            else:
                fingers_extended.append(0)
                
        return sum(fingers_extended)

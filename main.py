import sys
import time
import cv2
import threading
import tkinter as tk
from tkinter import filedialog
import argparse

import config
from core.config_manager import ConfigManager
from core.iot_manager import IOTManager
from detector.hand_detector import HandDetector
from ui.renderer import Renderer

# Global flag to signal the main loop to open file dialog safely
OPEN_CONFIG_DIALOG = False

def mouse_callback(event, x, y, flags, param):
    global OPEN_CONFIG_DIALOG
    if event == cv2.EVENT_LBUTTONDOWN:
        frame_w = param.get('width', 1920)
        if frame_w - 120 <= x <= frame_w and 0 <= y <= 48:
            OPEN_CONFIG_DIALOG = True

def main():
    global OPEN_CONFIG_DIALOG
    
    parser = argparse.ArgumentParser(description="IOT-AIML Hand Tracker")
    parser.add_argument("--video", type=str, help="Path to video file for testing")
    parser.add_argument("--camera", type=int, default=config.CAMERA_INDEX, help="Camera index")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  IOT-AIML")
    print("=" * 60)
    
    # Initialize Core
    config_mgr = ConfigManager(config_path="config.json")
    iot_mgr = IOTManager(debounce_duration=1.0)
    hand_detector = HandDetector(min_detection_conf=0.3)
    renderer = Renderer()

    # Open Source (Video or Camera)
    source = args.video if args.video else args.camera
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"[ERROR] Could not open source: {source}")
        sys.exit(1)
        
    if not args.video:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
    
    ret, init_frame = cap.read()
    if not ret:
        print("[ERROR] Failed to read from source.")
        sys.exit(1)
        
    actual_h, actual_w = init_frame.shape[:2]
    
    cv2.namedWindow(config.WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(config.WINDOW_NAME, actual_w, actual_h)
    cv2.setMouseCallback(config.WINDOW_NAME, mouse_callback, param={'width': actual_w})
    
    # Hide tkinter root for file dialog
    root = tk.Tk()
    root.withdraw()
    
    fps = 0.0
    frame_times = []
    last_fps_update = time.time()
    
    print(f"[Main] Source: {source}. Press 'Q' to quit.")
    
    try:
        while True:
            if OPEN_CONFIG_DIALOG:
                filepath = filedialog.askopenfilename(
                    title="Select Config JSON",
                    filetypes=[("JSON Files", "*.json")]
                )
                if filepath:
                    config_mgr.reload(filepath)
                OPEN_CONFIG_DIALOG = False

            frame_start = time.time()
            ret, frame = cap.read()
            if not ret:
                if args.video:
                    print("[Main] Video finished.")
                    break
                time.sleep(0.01)
                continue
                
            # Mirror frame ONLY if it's from personal camera (usually better for user feel)
            # Video files probably shouldn't be mirrored by default
            if not args.video:
                frame = cv2.flip(frame, 1)
            
            # Detect Hands
            results, total_fingers, details = hand_detector.detect(frame)
            
            # IOT Trigger Logic
            triggered_count = iot_mgr.update_count(total_fingers, config_mgr.mode, config_mgr.iot_endpoints)
            if triggered_count is not None:
                renderer.set_trigger_flash(triggered_count)
            
            # Render Overlay
            hand_detector.draw(frame, results)
            renderer.draw_top_bar(frame, config_mgr.mode, fps, current_count=total_fingers, hand_details=details)
            renderer.draw_large_count(frame, total_fingers)
            
            # FPS Calculation
            frame_end = time.time()
            frame_times.append(frame_end - frame_start)
            if frame_end - last_fps_update >= 0.5:
                if frame_times:
                    avg = sum(frame_times) / len(frame_times)
                    fps = 1.0 / avg if avg > 0 else 0
                frame_times.clear()
                last_fps_update = frame_end
                
            cv2.imshow(config.WINDOW_NAME, frame)
            
            # If playing video, wait for real-time speed if possible
            wait_time = 1
            if args.video:
                # Basic sync for 30fps
                elapsed = (time.time() - frame_start) * 1000
                wait_time = max(1, int(33 - elapsed))

            key = cv2.waitKey(wait_time) & 0xFF
            if key in [ord("q"), ord("Q"), 27]:
                break

            # Handle case where user clicks 'X' on window
            if cv2.getWindowProperty(config.WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        print("[Main] Releasing resources...")
        cap.release()
        cv2.destroyAllWindows()
        root.destroy()
        print("[Main] Done.")

if __name__ == "__main__":
    main()

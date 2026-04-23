import cv2
import config

class Renderer:
    """Renders the minimal Finger IOT Tracker UI."""

    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_alt = cv2.FONT_HERSHEY_DUPLEX
        self.trigger_flash_count = 0
        self.trigger_value = None

    def set_trigger_flash(self, value):
        self.trigger_flash_count = 15  # Show for 15 frames
        self.trigger_value = value

    def draw_top_bar(self, frame, mode, fps=0, current_count=None, hand_details=None):
        h, w = frame.shape[:2]
        bar_h = 48

        # Transparent bar background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, bar_h), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

        # Mode Text
        mode_text = f"Mode: {mode}"
        mode_color = (0, 255, 100) if mode == "IOT" else (0, 220, 255)
        cv2.putText(
            frame, mode_text, (15, 32),
            self.font_alt, 0.7, mode_color, 2, cv2.LINE_AA
        )

        # Config button
        cv2.putText(
            frame, "CONFIG", (w - 100, 32),
            self.font_alt, 0.7, (255, 255, 255), 2, cv2.LINE_AA
        )
        cv2.rectangle(frame, (w - 120, 0), (w, bar_h), (100, 100, 100), 2)

        # Display counts
        if hand_details and len(hand_details) > 1:
            # Multi-hand display
            detail_str = " | ".join([f"{d['type']}: {d['count']}" for d in hand_details])
            text = f"Total: {current_count} ({detail_str})"
        elif current_count is not None:
            text = f"Fingers Detected: {current_count}"
        else:
            text = ""

        if text:
            (tw, _), _ = cv2.getTextSize(text, self.font_alt, 0.7, 2)
            tx = (w - tw) // 2
            cv2.putText(
                frame, text, (tx, 32),
                self.font_alt, 0.7, (255, 255, 255), 2, cv2.LINE_AA
            )

        # Handle Trigger Flash
        if self.trigger_flash_count > 0:
            msg = f"LOCKED: {self.trigger_value}" if mode == "Counting" else f"TRIGGERED: {self.trigger_value}"
            (mw, mh), _ = cv2.getTextSize(msg, self.font_alt, 1.2, 3)
            mx = (w - mw) // 2
            my = bar_h + 60
            
            # Simple pulsating color
            color = (0, 255, 255) if mode == "Counting" else (0, 255, 0)
            cv2.putText(frame, msg, (mx, my), self.font_alt, 1.2, color, 3, cv2.LINE_AA)
            self.trigger_flash_count -= 1

    def draw_large_count(self, frame, current_count):
        if current_count == 0:
            return
            
        h, w = frame.shape[:2]
        
        # Display the big number
        text = str(current_count)
        font_scale = 10
        thickness = 25
        (tw, th), _ = cv2.getTextSize(text, self.font_alt, font_scale, thickness)
        
        tx = (w - tw) // 2
        ty = (h + th) // 2
        
        overlay = frame.copy()
        cv2.putText(overlay, text, (tx, ty), self.font_alt, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)
        cv2.putText(overlay, text, (tx, ty), self.font_alt, font_scale, (255, 255, 255), thickness - 10, cv2.LINE_AA)
        
        # Pulse effect transparency
        alpha = 0.3 if self.trigger_flash_count <= 0 else 0.7
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


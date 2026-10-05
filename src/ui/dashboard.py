import cv2
import numpy as np

class DarkDashboard:
    def __init__(self, frame_size=(640, 640), panel_width=350):
        self.frame_w, self.frame_h = frame_size
        self.panel_w = panel_width
        
        # Color Palette (OpenCV BGR Format)
        self.bg_color = (15, 15, 15)         
        self.card_bg = (25, 25, 25)          
        self.border_color = (60, 60, 60)     
        self.text_color = (180, 180, 180)    
        self.teal_accent = (180, 150, 80)    
        self.alert_bg = (20, 20, 100)       
        self.alert_border = (30, 30, 220)    
        self.green_safe = (50, 200, 50)     
        

    def draw_rounded_card(self, img, pt1, pt2, border_color, bg_color=None, r=8, thickness=1):
        """Draws a rounded rectangle using lines and ellipses for smooth corners."""
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Draw Background Fill
        if bg_color:
            cv2.rectangle(img, (x1 + r, y1), (x2 - r, y2), bg_color, -1)
            cv2.rectangle(img, (x1, y1 + r), (x2, y2 - r), bg_color, -1)
            cv2.circle(img, (x1 + r, y1 + r), r, bg_color, -1)
            cv2.circle(img, (x2 - r, y1 + r), r, bg_color, -1)
            cv2.circle(img, (x1 + r, y2 - r), r, bg_color, -1)
            cv2.circle(img, (x2 - r, y2 - r), r, bg_color, -1)
            
        # Draw Borders
        cv2.line(img, (x1 + r, y1), (x2 - r, y1), border_color, thickness)
        cv2.line(img, (x1 + r, y2), (x2 - r, y2), border_color, thickness)
        cv2.line(img, (x1, y1 + r), (x1, y2 - r), border_color, thickness)
        cv2.line(img, (x2, y1 + r), (x2, y2 - r), border_color, thickness)
        
        # Draw Corner Arcs
        cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 0, 180, 270, border_color, thickness)
        cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 0, 270, 360, border_color, thickness)
        cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, border_color, thickness)
        cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 0, 90, 180, border_color, thickness)

    def render(self, frame, telemetry, logs, is_alert=False):
        # 1. Panel Base
        panel = np.full((self.frame_h, self.panel_w, 3), self.bg_color, dtype=np.uint8)
        
        # 2. Top Right Status
        cv2.circle(panel, (self.panel_w - 130, 30), 4, self.green_safe, -1)
        cv2.putText(panel, "SYSTEM ACTIVE", (self.panel_w - 115, 34), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.green_safe, 1)

        # 3. Main Alert Box
        if is_alert:
            self.draw_rounded_card(panel, (20, 60), (self.panel_w - 20, 110), self.alert_border, self.alert_bg)
            cv2.circle(panel, (40, 85), 5, self.alert_border, -1)
            cv2.putText(panel, "FIRE ALERT", (60, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            self.draw_rounded_card(panel, (20, 60), (self.panel_w - 20, 110), self.border_color, self.card_bg)
            cv2.circle(panel, (40, 85), 5, self.green_safe, -1)
            cv2.putText(panel, "MONITORING...", (60, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.text_color, 1)

        # 4. Telemetry Box (RAM and Temperature)
        self.draw_rounded_card(panel, (20, 130), (self.panel_w - 20, 200), self.border_color, self.card_bg)
        ram_used, ram_total, ram_pct = telemetry.get('ram', (0,0,0))
        temp = telemetry.get('temp', 0.0)
        
        cv2.putText(panel, "RAM Memory", (35, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.text_color, 1)
        cv2.putText(panel, f"{ram_used:.1f} / {ram_total:.1f} GB", (self.panel_w - 140, 160), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1)
                    
        cv2.putText(panel, "Temperature", (35, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.text_color, 1)
        cv2.putText(panel, f"{temp:.0f} C", (self.panel_w - 75, 185), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1)

        # 5. Event History Box
        cv2.putText(panel, "EVENT HISTORY", (20, 300), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.teal_accent, 1)
        self.draw_rounded_card(panel, (20, 315), (self.panel_w - 20, self.frame_h - 20), self.border_color, self.card_bg)
        
        y_offset = 345
        for log in logs:
            cv2.line(panel, (35, y_offset - 10), (35, y_offset + 5), self.teal_accent, 2)
            cv2.putText(panel, log, (45, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.text_color, 1)
            y_offset += 35

        # 6. Prepare the Video Frame with camera markings
        frame_resized = cv2.resize(frame, (self.frame_w, self.frame_h))
        
        cv2.putText(frame_resized, "MAIN VIDEO FEED", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.teal_accent, 1)
        cv2.putText(frame_resized, "CAM-01 [NORTH]", (20, self.frame_h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.text_color, 1)
        cv2.putText(frame_resized, "1920x1080 @ 30fps", (self.frame_w - 180, self.frame_h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, self.text_color, 1)
        
        # Combine video and lateral panel
        combined_view = cv2.hconcat([frame_resized, panel])
        
        return combined_view

    def check_button_click(self, x, y):
        bx1, by1, bx2, by2 = self.roi_btn_area
        x_in_panel = x - self.frame_w 
        return bx1 <= x_in_panel <= bx2 and by1 <= y <= by2
import cv2
import time
import os
from datetime import datetime

from detector import detect_people
from firebase_notifier import send_push_notification


class CCTVSystem:
    def __init__(
        self,
        camera_index=0,
        alert_cooldown=10,
        stream_timeout=10,
        capture_dir="captures"
    ):
        self.cap = cv2.VideoCapture(camera_index)

        self.alert_cooldown = alert_cooldown
        self.stream_timeout = stream_timeout
        self.capture_dir = capture_dir

        self.last_alert_time = 0
        self.last_detect_time = time.time()

        self.last_capture_file = None
        self.last_capture_time = None

        self.alert_count = 0
        self.streaming_active = True

        os.makedirs(self.capture_dir, exist_ok=True)

    def save_capture(self, frame):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"person_{now}.jpg"
        filepath = os.path.join(self.capture_dir, filename)

        cv2.imwrite(filepath, frame)

        return filename

    def handle_person_detected(self, frame):
        current_time = time.time()

        self.last_detect_time = current_time
        self.streaming_active = True

        if current_time - self.last_alert_time < self.alert_cooldown:
            return

        self.last_alert_time = current_time

        filename = self.save_capture(frame)

        self.last_capture_file = filename
        self.last_capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.alert_count += 1

        print(f"[ALERT] Person detected! Saved: {filename}")

        send_push_notification(
            "CCTV Alert",
            "사람이 감지되었습니다!"
        )

    def draw_people_boxes(self, frame, people):
        for x1, y1, x2, y2, confidence in people:
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            label = f"Person {confidence:.2f}"

            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    def update_streaming_state(self):
        if time.time() - self.last_detect_time > self.stream_timeout:
            self.streaming_active = False

    def generate_frames(self):
        while True:
            self.update_streaming_state()

            success, frame = self.cap.read()

            if not success:
                break

            people = detect_people(frame)

            if len(people) > 0:
                self.handle_person_detected(frame)

            self.draw_people_boxes(frame, people)

            if self.streaming_active:
                _, buffer = cv2.imencode(".jpg", frame)
                frame_bytes = buffer.tobytes()

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" +
                    frame_bytes +
                    b"\r\n"
                )
            else:
                time.sleep(0.1)

    def get_status(self):
        return {
            "last_capture": self.last_capture_file,
            "time": self.last_capture_time,
            "alert_count": self.alert_count,
            "streaming": self.streaming_active
        }

    def release(self):
        self.cap.release()
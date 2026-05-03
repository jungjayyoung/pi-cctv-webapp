from flask import Flask, render_template, Response
import cv2
import time
import os
from datetime import datetime
from detector import detect_people
from flask import send_from_directory
from flask import request
from firebase_notifier import save_token, send_push_notification

app = Flask(__name__)

cap = cv2.VideoCapture(0)

last_alert_time = 0
ALERT_COOLDOWN = 10  # 10초에 한 번만 이벤트 발생
alert_count = 0

last_capture_file = None
last_capture_time = None

def save_capture(frame):
    os.makedirs("captures", exist_ok=True)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captures/person_{now}.jpg"

    cv2.imwrite(filename, frame)
    return filename


def handle_person_detected(frame):
    global last_alert_time

    global last_capture_file, last_capture_time

    global alert_count

    current_time = time.time()

    if current_time - last_alert_time < ALERT_COOLDOWN:
        return

    last_alert_time = current_time

    filename = save_capture(frame)

    last_capture_file = filename
    last_capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    alert_count += 1

    print(f"[ALERT] Person detected! Saved: {filename}")

   
    send_push_notification(
        "CCTV Alert",
        "사람이 감지되었습니다!"
    )


def generate_frames():
    while True:
        success, frame = cap.read()

        if not success:
            break

        people = detect_people(frame)

        for x1, y1, x2, y2, confidence in people:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

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

        if len(people) > 0:
            handle_person_detected(frame)

        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video")
def video():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/status")
def status():
    return {
        "last_capture": last_capture_file,
        "time": last_capture_time,
        "alert_count": alert_count
    }


@app.route('/captures/<path:filename>')
def serve_capture(filename):
    return send_from_directory('../captures', filename)


@app.route("/save-token", methods=["POST"])
def save_fcm_token():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return {"success": False, "message": "No token"}, 400

    save_token(token)

    return {"success": True}


@app.route("/test-push")
def test_push():
    send_push_notification(
        "CCTV Test",
        "Firebase 푸시 테스트입니다."
    )
    return {"success": True}

if __name__ == "__main__":
    app.run(debug=True)
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURE_DIR = os.path.join(BASE_DIR, "captures")

cap = cv2.VideoCapture(0)

last_alert_time = 0
ALERT_COOLDOWN = 10  # 10초에 한 번만 이벤트 발생
alert_count = 0

last_detect_time = time.time()

last_capture_file = None
last_capture_time = None


streaming_active = True

def save_capture(frame):
    os.makedirs(CAPTURE_DIR, exist_ok=True)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"person_{now}.jpg"

    filepath = os.path.join(CAPTURE_DIR, filename)
    cv2.imwrite(filepath, frame)

    return filename


def handle_person_detected(frame):
    global last_alert_time

    global last_capture_file, last_capture_time

    global alert_count

    global streaming_active

    global last_detect_time

    current_time = time.time()

    

    if current_time - last_alert_time < ALERT_COOLDOWN:
        return

    last_alert_time = current_time
    last_detect_time = current_time
    streaming_active = True

    filename = save_capture(frame)

    last_capture_file = filename
    last_capture_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    alert_count += 1

    streaming_active = True

    print(f"[ALERT] Person detected! Saved: {filename}")


    send_push_notification(
        "CCTV Alert",
        "사람이 감지되었습니다!"
    )


def generate_frames():
    global streaming_active, last_detect_time

    

    while True:
        if time.time() - last_detect_time > 10:
            streaming_active = False
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

        if streaming_active:
            _, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        else:
            time.sleep(0.1)  # CPU 낭비 방지


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
        "alert_count": alert_count,
        "streaming": streaming_active
    }


@app.route('/captures/<path:filename>')
def serve_capture(filename):
    return send_from_directory(CAPTURE_DIR, filename)


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
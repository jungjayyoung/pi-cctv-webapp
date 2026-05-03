import os
from flask import Flask, render_template, Response, send_from_directory, request

from cctv_system import CCTVSystem
from firebase_notifier import save_token, send_push_notification
from datetime import datetime

app = Flask(__name__)

LOG_DIR = "logs"
ACCESS_LOG_FILE = os.path.join(LOG_DIR, "access.log")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURE_DIR = os.path.join(BASE_DIR, "captures")

cctv = CCTVSystem(
    camera_index=0,
    alert_cooldown=10,
    stream_timeout=10,
    capture_dir=CAPTURE_DIR
)


os.makedirs(LOG_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video")
def video():
    return Response(
        cctv.generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/status")
def status():
    return cctv.get_status()


@app.route("/captures/<path:filename>")
def serve_capture(filename):
    return send_from_directory(cctv.capture_dir, filename)


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


@app.before_request
def log_access():

    # status는 로그 제외
    if request.path == "/status":
        return

    real_ip = request.headers.get("CF-Connecting-IP", request.remote_addr)
    path = request.path
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_line = f"[{now}] IP={real_ip} PATH={path}\n"

    with open(ACCESS_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

if __name__ == "__main__":
    app.run(debug=True)
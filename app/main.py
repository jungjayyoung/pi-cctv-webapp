import os
from flask import Flask, render_template, Response, send_from_directory, request

from cctv_system import CCTVSystem
from firebase_notifier import save_token, send_push_notification

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURE_DIR = os.path.join(BASE_DIR, "captures")

cctv = CCTVSystem(
    camera_index=0,
    alert_cooldown=10,
    stream_timeout=10,
    capture_dir=CAPTURE_DIR
)


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


if __name__ == "__main__":
    app.run(debug=True)
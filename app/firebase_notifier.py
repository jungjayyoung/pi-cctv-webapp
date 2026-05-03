import json
import os
import firebase_admin
from firebase_admin import credentials, messaging

SERVICE_ACCOUNT_PATH = "firebase-service-account.json"
TOKEN_FILE = "fcm_tokens.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)


def save_token(token):
    tokens = load_tokens()

    if token not in tokens:
        tokens.append(token)

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)


def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return []

    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def send_push_notification(title, body):
    tokens = load_tokens()

    if not tokens:
        print("[FCM] No tokens saved.")
        return

    # 저장된 모든 기기에 알림 전송
    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )

        try:
            response = messaging.send(message)
            print("[FCM] Sent:", response)
        except Exception as e:
            print("[FCM] Send failed:", e)
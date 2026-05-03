# 🛡️ Pi CCTV Web App

라즈베리파이를 기반으로 한 **실시간 CCTV 감지 시스템**입니다.  
YOLO 기반 사람 감지 + 웹 스트리밍 + Firebase 푸시 알림 + 접속 로그 기능까지 포함되어 있습니다.

---

## 🚀 주요 기능

- 🎥 실시간 카메라 스트리밍 (Flask)
- 🧠 YOLO 기반 사람 감지
- 📸 감지 시 이미지 자동 저장
- 🔔 Firebase Push 알림 (멀티 디바이스 지원)
- 🌐 Cloudflare Tunnel을 통한 외부 접속
- 📊 접속자 IP + 시간 로그 기록

---

## 🏗️ 시스템 구조

```bash
[ Raspberry Pi ]
├─ Camera (USB)
├─ YOLO Detection
├─ Flask Server
├─ Firebase Push
└─ Access Log
    ↓ (Cloudflare Tunnel)

[ Client Devices ]
├─ PC
├─ Mobile
└─ Tablet
```

---

## 🧰 사용 기술

- Python
- Flask
- OpenCV
- YOLO
- Firebase Cloud Messaging (FCM)
- Cloudflare Tunnel

---

## ⚙️ 설치 방법

### 1. 프로젝트 클론

```bash
git clone https://github.com/jungjayyoung/pi-cctv-webapp.git
cd pi-cctv-webapp
```

### 2. 가상환경 생성 및 실행
```bash
python -m venv venv
source venv/bin/activate
```
### 3. 패키지 설치
```bash
pip install -r requirements.txt
```
### 4. 실행
```bash
python app/main.py
```
### 5. 접속
```bash
http://localhost:5000
```
또는
```bash
http://<라즈베리파이_IP>:5000
```
## 🌍 외부 접속 (Cloudflare Tunnel)
```bash
cloudflared tunnel --url http://localhost:5000
```
## 🔔 Firebase 설정

- Firebase 프로젝트 생성
- 서비스 계정 JSON 파일 추가
- VAPID 키 설정
- 토큰 저장 후 푸시 알림 전송

## 📁 프로젝트 구조

```bash
pi-cctv-webapp/
├─ app/
│  ├─ main.py
│  ├─ cctv_system.py
│  ├─ firebase_notifier.py
│  └─ templates/
│     └─ index.html
├─ captures/
├─ logs/
├─ requirements.txt
└─ README.md
```

## 📊 로그 기능

- 접속자 IP 기록 (Cloudflare 실제 IP 포함)
- 접속 시간 기록
- logs/access.log 파일에 저장

## 💡 향후 개선

- 🎞️ 영상 클립 저장 기능
- 📊 웹 기반 로그 대시보드
- 👤 사용자 인증 기능
- ☁️ AWS + S3 연동

## 📌 한 줄 요약

라즈베리파이 기반 실시간 CCTV 시스템 + 웹 + 푸시 알림 + 로그까지 구현한 IoT 프로젝트
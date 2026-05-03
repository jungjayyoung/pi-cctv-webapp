from ultralytics import YOLO

# 가벼운 모델. 처음 실행할 때 자동 다운로드됨
model = YOLO("yolov8n.pt")

def detect_people(frame):
    results = model(frame, verbose=False)

    people = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            # COCO 데이터셋에서 person 클래스 id는 0
            if class_id == 0 and confidence >= 0.5:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                people.append((x1, y1, x2, y2, confidence))

    return people
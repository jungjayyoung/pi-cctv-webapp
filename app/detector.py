from ultralytics import YOLO

# 가벼운 모델. 처음 실행할 때 자동 다운로드됨
model = YOLO("yolov8s.pt")

def detect_objects(frame):
    results = model(frame, verbose=False)

    people = []
    dogs = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if confidence < 0.5:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if class_id == 0:
                people.append((x1, y1, x2, y2, confidence))

            elif class_id == 16:
                dogs.append((x1, y1, x2, y2, confidence))

    return people, dogs
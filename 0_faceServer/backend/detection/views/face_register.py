import os
import json
import cv2
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import torch
from insightface.app import FaceAnalysis

# 🔹 YOLOv5 모델 로드
model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)

# 🔹 ArcFace 모델 로드
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=-1)  # CPU 사용

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EMBEDDING_DIR = os.path.join(BASE_DIR, "embeddings")
os.makedirs(EMBEDDING_DIR, exist_ok=True)

MAX_CAPTURE = 5  # 5장 평균

def adjust_bbox_for_retina(yolo_bbox, scale_factor=1.2):
    """ YOLO의 바운딩 박스를 20% 확대하여 RetinaFace와 유사한 크기로 변환 """
    x, y, w, h = yolo_bbox
    cx, cy = x + w / 2, y + h / 2
    new_w, new_h = w * scale_factor, h * scale_factor
    return [max(0, cx - new_w / 2), max(0, cy - new_h / 2), new_w, new_h]

@csrf_exempt
def register_face(request):
    """ 사용자의 얼굴을 YOLO로 검출 후 임베딩 저장 (바운딩 박스 20% 확대) """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "잘못된 요청입니다."}, status=405)

    user_id = request.POST.get("user_id", "unknown")
    images = request.FILES.getlist("face_images")

    if not images:
        return JsonResponse({"status": "error", "message": "이미지가 감지되지 않았습니다."}, status=400)

    embeddings_list = []

    for image_file in images:
        image_bytes = image_file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # YOLO 얼굴 검출
        results = model(image)

        if results is None or len(results.pred[0]) == 0:
            continue  # 얼굴이 감지되지 않으면 무시

        # 가장 큰 얼굴 선택
        detected_faces = sorted(results.pred[0].cpu().numpy(), key=lambda x: (x[2] - x[0]) * (x[3] - x[1]), reverse=True)
        x, y, w, h, conf, cls = detected_faces[0]  # YOLO 결과 형식에 맞게 값 가져오기
        x, y, w, h = adjust_bbox_for_retina([x, y, w - x, h - y])  # 20% 확대

        # 얼굴 크롭
        face_crop = image[int(y):int(y + h), int(x):int(x + w)]

        # ArcFace 임베딩 추출
        face_data = app.get(face_crop)
        if face_data:
            embeddings_list.append(face_data[0].normed_embedding)

        if len(embeddings_list) >= MAX_CAPTURE:
            break

    if len(embeddings_list) == 0:
        return JsonResponse({"status": "error", "message": "얼굴을 감지하지 못했습니다."}, status=400)

    # 🔹 PCA 제거: 128D 원본 임베딩 그대로 사용
    avg_embedding = np.mean(embeddings_list, axis=0).tolist()

    embedding_path = os.path.join(EMBEDDING_DIR, f"{user_id}_embedding.json")
    with open(embedding_path, "w") as f:
        json.dump(avg_embedding, f, indent=4)

    return JsonResponse({"message": f"{user_id}님 얼굴 등록 완료!", "embedding_path": embedding_path})

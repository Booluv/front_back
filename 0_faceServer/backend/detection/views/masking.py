import os
import cv2
import json
import numpy as np
import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time
from insightface.app import FaceAnalysis


# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DETECTED_PATH = os.path.join(BASE_DIR, "detection", "masked_image")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings")
EMOJI_PATH = os.path.join(BASE_DIR, "emojis")
os.makedirs(DETECTED_PATH, exist_ok=True)

# YOLO 모델 로드
print("YOLO 모델 로드 중...")
model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
print("YOLO 모델 로드 완료.")

# ArcFace 모델 로드
face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0, det_size=(640, 640))

# 이모지 로드 함수
def load_emoji(filename):
    path = os.path.join(EMOJI_PATH, filename)
    return cv2.imread(path, cv2.IMREAD_COLOR) if os.path.exists(path) else None

# 이모지 파일명 매핑
emojis = {
    "bear": load_emoji("emoji_bear.png"),
    "tiger": load_emoji("emoji_tiger.png"),
    "koala": load_emoji("emoji_koala.png"),
}

@csrf_exempt
def masking_face(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "잘못된 요청입니다."}, status=405)

    user_id = request.POST.get("user_id", "").strip()
    mask_type = request.POST.get("mask_type", "black")
    image_file = request.FILES.get("image")

    if not user_id or not image_file:
        return JsonResponse({"status": "error", "message": "아이디와 이미지를 입력하세요."}, status=400)

    try:
        # 사용자 임베딩 로드
        user_embedding_path = os.path.join(EMBEDDINGS_PATH, f"{user_id}_embedding.json")
        if not os.path.exists(user_embedding_path):
            return JsonResponse({"message": "해당 사용자 ID의 얼굴 데이터가 없습니다."}, status=400)

        with open(user_embedding_path, "r") as f:
            user_embedding = np.array(json.load(f))

        user_embedding = user_embedding / np.linalg.norm(user_embedding)

        # 이미지 로드
        image_bytes = image_file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return JsonResponse({"message": "이미지 파일이 잘못되었습니다."}, status=400)

        # 얼굴 감지
        faces = face_app.get(image)
        if len(faces) == 0:
            return JsonResponse({"message": "얼굴을 감지하지 못했습니다."}, status=400)

        # 유사도 비교 (코사인 유사도)
        threshold = 0.7
        target_face = None

        for face in faces:
            if "embedding" not in face:
                continue

            face_embedding = np.array(face["embedding"])
            face_embedding = face_embedding / np.linalg.norm(face_embedding)

            if face_embedding.shape != user_embedding.shape:
                continue

            sim = np.dot(user_embedding, face_embedding)
            if sim > threshold:
                target_face = face
                break

        if target_face is None:
            return JsonResponse({"message": "사용자 ID와 일치하는 얼굴이 없습니다."}, status=400)

        # 마스킹 적용
        x_min, y_min, x_max, y_max = map(int, target_face["bbox"])
        w, h = x_max - x_min, y_max - y_min

        if mask_type == "black":
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
        elif mask_type == "blur":
            face_roi = image[y_min:y_max, x_min:x_max]
            face_roi = cv2.GaussianBlur(face_roi, (55, 55), 30)
            image[y_min:y_max, x_min:x_max] = face_roi
        elif mask_type in emojis and emojis[mask_type] is not None:
            emoji = cv2.resize(emojis[mask_type], (w, h))
            image[y_min:y_max, x_min:x_max] = emoji

        # 마스킹된 이미지 저장
        timestamp = int(time.time())
        result_filename = f"masked_result_{timestamp}.png"
        result_path = os.path.join(DETECTED_PATH, result_filename)
        success = cv2.imwrite(result_path, image)

        if not success:
            return JsonResponse({"message": "이미지 저장 실패!"}, status=500)

        return JsonResponse({"message": "마스킹 완료", "image_url": f"/media/{result_filename}"})

    except Exception as e:
        return JsonResponse({"message": "서버 내부 오류 발생", "error": str(e)}, status=500)

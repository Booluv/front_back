import os
import json
import cv2
import numpy as np
import tempfile
import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from insightface.app import FaceAnalysis

# ArcFace & RetinaFace 모델 로드
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=-1)  # CPU 사용

# YOLOv5 모델 로드
model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EMBEDDING_DIR = os.path.join(BASE_DIR, "embeddings")

THRESHOLD_SIMILARITY = 0.7  # 유사도 기준 (0.7 이상: 정확, 0.6~0.7: 애매, 0.6 미만: 감지 실패)

def adjust_bbox_for_retina(yolo_bbox, scale_factor=1.2):
    """ YOLO의 바운딩 박스를 20% 확대하여 RetinaFace와 일관되도록 조정 """
    x, y, w, h = yolo_bbox
    cx, cy = x + w / 2, y + h / 2
    new_w, new_h = w * scale_factor, h * scale_factor
    return [max(0, cx - new_w / 2), max(0, cy - new_h / 2), new_w, new_h]

@csrf_exempt
def verify_face(request):
    """ 업로드된 얼굴을 등록된 얼굴과 비교하여 아이디 출력 """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "잘못된 요청입니다."}, status=405)

    user_id = request.POST.get("user_id", "").strip()
    image_file = request.FILES.get("face_image")

    if not image_file:
        return JsonResponse({"status": "error", "message": "이미지가 없습니다."}, status=400)
    if not user_id:
        return JsonResponse({"status": "error", "message": "아이디를 입력하세요."}, status=400)

    # 사용자 임베딩 로드
    user_embedding_path = os.path.join(EMBEDDING_DIR, f"{user_id}_embedding.json")
    if not os.path.exists(user_embedding_path):
        return JsonResponse({"status": "error", "message": f"{user_id}님의 얼굴 데이터가 등록되지 않았습니다."}, status=400)

    with open(user_embedding_path, "r") as f:
        user_embedding = np.array(json.load(f))

    # 이미지 로드 및 YOLO 얼굴 감지
    image_bytes = image_file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # YOLO 실행
    results = model(image)

    if results is None or len(results.pred[0]) == 0:
        return JsonResponse({"status": "error", "message": "이미지에서 얼굴을 감지하지 못했습니다."}, status=400)

    # YOLO가 감지한 모든 얼굴 처리
    detected_faces = sorted(results.pred[0].cpu().numpy(), key=lambda x: (x[2] - x[0]) * (x[3] - x[1]), reverse=True)

    best_match = None
    highest_similarity = -1

    for face in detected_faces:
        x, y, w, h, conf, cls = face  # YOLO 결과 형식에 맞춰서 값 가져오기
        x, y, w, h = adjust_bbox_for_retina([x, y, w - x, h - y])  # 바운딩 박스 크기 맞추기

        # 얼굴 크롭
        face_crop = image[int(y):int(y + h), int(x):int(x + w)]

        # RetinaFace로 정밀 분석
        face_data = app.get(face_crop)
        if not face_data:
            continue

        # ArcFace 임베딩 추출
        detected_embedding = face_data[0].normed_embedding

        # 코사인 유사도 계산 (PCA 미적용, 원본 128D 사용)
        similarity = np.dot(detected_embedding, user_embedding) / (
            np.linalg.norm(detected_embedding) * np.linalg.norm(user_embedding)
        )

        # 가장 높은 유사도를 가진 얼굴 선택
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = user_id  # 입력한 아이디와 비교하는 방식 유지

    # 결과 메시지 생성
    if highest_similarity >= THRESHOLD_SIMILARITY:
        confidence_label = "정확"
    elif highest_similarity >= 0.6:
        confidence_label = "애매"
    else:
        confidence_label = "감지되지 않음"

    if confidence_label == "감지되지 않음":
        return JsonResponse({"status": "fail", "message": f"{user_id}님이 감지되지 않았습니다! (유사도: {highest_similarity:.2f})"})

    return JsonResponse({
        "status": "success",
        "message": f"{best_match}님이 감지되었습니다! (유사도: {highest_similarity:.2f}) 동일인물: {confidence_label}"
    })
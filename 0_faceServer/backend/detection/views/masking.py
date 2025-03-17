import os
import cv2
import numpy as np
import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time

# ✅ BASE_DIR 설정 및 경로 정의
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend 경로
DETECTED_PATH = os.path.join(BASE_DIR, "masked_image")  # ✅ 저장할 폴더를 backend/detected/로 설정
EMOJI_PATH = os.path.join(BASE_DIR, "emojis")
os.makedirs(DETECTED_PATH, exist_ok=True)  # ✅ 폴더 없으면 생성

# ✅ 이모티콘 로드 함수
def load_emoji(filename):
    path = os.path.join(EMOJI_PATH, filename)
    return cv2.imread(path, cv2.IMREAD_UNCHANGED) if os.path.exists(path) else None

# ✅ 이모티콘 파일명 수정 적용
emojis = {
    "bear": load_emoji("emoji_bear.png"),
    "tiger": load_emoji("emoji_tiger.png"),
    "koala": load_emoji("emoji_koala.png"),
}

# ✅ YOLO 모델 로드
print("📌 YOLO 모델 로드 중...")
model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
print("✅ YOLO 모델 로드 완료!")

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
        # ✅ 이미지 로드
        image_bytes = image_file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return JsonResponse({"message": "이미지 파일이 잘못되었습니다."}, status=400)

        # ✅ YOLO로 얼굴 감지 (RGB 변환 필요할 수도 있음)
        results = model(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        detected_faces = results.xyxy[0].cpu().numpy()

        if len(detected_faces) == 0:
            return JsonResponse({"message": "얼굴을 감지하지 못했습니다."}, status=400)

        # ✅ 얼굴 마스킹
        for face in detected_faces:
            x, y, w, h = map(int, face[:4])  # YOLO 좌표 변환

            if mask_type == "black":
                cv2.rectangle(image, (x, y), (w, h), (0, 0, 0), -1)
            elif mask_type == "blur":
                face_roi = image[y:h, x:w]
                face_roi = cv2.GaussianBlur(face_roi, (99, 99), 30)
                image[y:h, x:w] = face_roi
            elif mask_type in emojis and emojis[mask_type] is not None:
                emoji = cv2.resize(emojis[mask_type], (w - x, h - y))
                image[y:h, x:w] = emoji

        # ✅ 마스킹된 이미지 저장 (올바른 `backend/detected/` 폴더로 설정)
        timestamp = int(time.time())
        result_filename = f"masked_result_{timestamp}.png"
        result_path = os.path.join(DETECTED_PATH, result_filename)
        print(f"📌 [DEBUG] 저장할 이미지 경로: {result_path}")
        success = cv2.imwrite(result_path, image)
        if not success:
            print("🚨 [ERROR] 이미지 저장 실패! 경로:", result_path)
            return JsonResponse({"message": "이미지 저장 실패!"}, status=500)

        print(f"📌 [DEBUG] 반환할 image_url: /media/{result_filename}")
        return JsonResponse({"message": "마스킹 완료", "image_url": f"/media/{result_filename}"})

    except Exception as e:
        return JsonResponse({"message": "서버 내부 오류 발생", "error": str(e)}, status=500)

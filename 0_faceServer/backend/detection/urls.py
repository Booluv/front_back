from django.urls import path
from detection.views.face_register import register_face
from detection.views.face_verify import verify_face
from detection.views.masking import masking_face


urlpatterns = [
    path("face-register/realtime/", register_face, name="face_register"),
    path("face-verify/", verify_face, name="face_verify"),
    path("face-masking/",masking_face, name="face_masking"),
]
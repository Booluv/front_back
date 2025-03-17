from django.urls import path
from .views import register_face, verify_face

urlpatterns = [
    path("face-register/realtime/", register_face, name="face_register"),
    path("face-verify/", verify_face, name="face_verify"),
]
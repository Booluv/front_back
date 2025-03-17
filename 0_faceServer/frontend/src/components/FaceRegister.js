import React, { useRef, useState } from "react";

const FaceRegister = () => {
    const [message, setMessage] = useState("");
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [isCameraOn, setIsCameraOn] = useState(false);
    const [isCapturing, setIsCapturing] = useState(false);
    const [userId, setUserId] = useState("");
    const [captureCount, setCaptureCount] = useState(0);  // 진행 상황 표시

    const CAPTURE_COUNT = 8;  // 8장의 사진 촬영
    const CAPTURE_INTERVAL = 500; // 0.5초 간격

    // ✅ 웹캠 켜기
    const startWebcam = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoRef.current.srcObject = stream;
            setIsCameraOn(true);
        } catch (error) {
            console.error("웹캠 접근 오류:", error);
            setMessage("웹캠을 사용할 수 없습니다. 브라우저 설정을 확인하세요.");
        }
    };

    // ✅ 웹캠 끄기
    const stopWebcam = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            let tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            videoRef.current.srcObject = null;
        }
        setIsCameraOn(false);
    };

    // ✅ 0.5초 간격으로 8장 촬영 후 서버로 전송
    const captureMultipleImages = async () => {
        if (!videoRef.current || !videoRef.current.srcObject) {
            alert("웹캠을 먼저 켜주세요!");
            return;
        }

        if (!userId.trim()) {
            alert("사용자 ID를 입력해주세요.");
            return;
        }

        setIsCapturing(true);
        setCaptureCount(0);
        setMessage("📸 얼굴 이미지를 촬영 중...");

        let images = [];

        for (let i = 0; i < CAPTURE_COUNT; i++) {
            await new Promise((resolve) => setTimeout(resolve, CAPTURE_INTERVAL));

            const canvas = canvasRef.current;
            const context = canvas.getContext("2d");
            context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

            images.push(new Promise((resolve) => {
                canvas.toBlob((blob) => {
                    setCaptureCount(prevCount => prevCount + 1);
                    resolve(blob);
                }, "image/jpeg");
            }));
        }

        const capturedBlobs = await Promise.all(images);
        sendImagesToServer(capturedBlobs);
    };

    // ✅ Django로 8장의 이미지를 전송
    const sendImagesToServer = async (images) => {
        const formData = new FormData();
        formData.append("user_id", userId.trim());

        images.forEach((image, index) => {
            formData.append("face_images", image, `face_${index}.jpg`);
        });

        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/detection/face-register/realtime/`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            setIsCapturing(false);

            if (response.ok) {
                setMessage("✅ 얼굴 등록이 완료되었습니다!");
            } else {
                setMessage(data.message || "⚠ 실시간 등록에 실패했습니다.");
            }
        } catch (error) {
            console.error("API 호출 오류:", error);
            setMessage("⚠ 서버와 연결할 수 없습니다. 다시 시도해주세요.");
            setIsCapturing(false);
        }
    };

    return (
        <div>
            <h1>실시간 얼굴 등록</h1>
            <input 
                type="text" 
                placeholder="사용자 ID 입력" 
                value={userId} 
                onChange={(e) => setUserId(e.target.value)} 
                disabled={isCapturing}
            />
            <video ref={videoRef} autoPlay width="400" height="300" style={{ display: isCameraOn ? "block" : "none" }} />
            <canvas ref={canvasRef} width="400" height="300" style={{ display: "none" }} />

            <button onClick={isCameraOn ? stopWebcam : startWebcam} disabled={isCapturing}>
                {isCameraOn ? "웹캠 끄기" : "웹캠 켜기"}
            </button>

            <button onClick={captureMultipleImages} disabled={!isCameraOn || isCapturing}>
                {isCapturing ? `📸 촬영 중... (${captureCount}/${CAPTURE_COUNT})` : "8장 캡처 & 전송"}
            </button>

            <p>{message}</p>
        </div>
    );
};

export default FaceRegister;
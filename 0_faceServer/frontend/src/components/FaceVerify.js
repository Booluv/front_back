import React, { useState } from "react";

const FaceVerify = () => {
    const [selectedImage, setSelectedImage] = useState(null);
    const [userId, setUserId] = useState(""); // 사용자 ID 입력 추가
    const [verificationResult, setVerificationResult] = useState(null);
    const [loading, setLoading] = useState(false);

    // 환경 변수에서 백엔드 URL 가져오기
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

    // 이미지 선택 핸들러
    const handleImageChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedImage(file);
        }
    };

    // 서버로 이미지 전송 후 얼굴 검증 요청 (fetch 사용)
    const handleVerify = async () => {
        if (!selectedImage) {
            alert("이미지를 먼저 선택해주세요.");
            return;
        }
        if (!userId.trim()) {
            alert("사용자 ID를 입력해주세요.");
            return;
        }

        const formData = new FormData();
        formData.append("face_image", selectedImage);
        formData.append("user_id", userId); // 사용자 ID 추가

        setLoading(true);
        setVerificationResult(null);

        try {
            const response = await fetch(`${BACKEND_URL}/detection/face-verify/`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`서버 오류: ${response.status}`);
            }

            const data = await response.json();
            setVerificationResult(data);
        } catch (error) {
            console.error("Error verifying face:", error);
            setVerificationResult({ status: "error", message: "얼굴 검증 실패" });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h2>얼굴 인증</h2>

            <label>
                사용자 ID:
                <input
                    type="text"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="ID를 입력하세요"
                />
            </label>

            <input type="file" accept="image/*" onChange={handleImageChange} />
            <button onClick={handleVerify} disabled={loading}>
                {loading ? "검증 중..." : "얼굴 검증"}
            </button>

            {selectedImage && (
                <div>
                    <h3>선택된 이미지:</h3>
                    <img
                        src={URL.createObjectURL(selectedImage)}
                        alt="Selected"
                        style={{ width: "300px", marginTop: "10px" }}
                    />
                </div>
            )}

            {verificationResult && (
                <div>
                    <h3>검증 결과:</h3>
                    {verificationResult.status === "success" ? (
                        <p style={{ color: "green" }}>{verificationResult.message}</p>
                    ) : (
                        <p style={{ color: "red" }}>{verificationResult.message}</p>
                    )}
                </div>
            )}
        </div>
    );
};

export default FaceVerify;
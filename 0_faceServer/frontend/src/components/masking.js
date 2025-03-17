import React, { useState } from "react";

function Masking() {
    const [userId, setUserId] = useState("");
    const [image, setImage] = useState(null);
    const [maskType, setMaskType] = useState("black");
    const [maskedImageUrl, setMaskedImageUrl] = useState("");

    const handleFileChange = (e) => {
        setImage(e.target.files[0]);
    };

    const handleMasking = async () => {
        if (!userId || !image) {
            alert("사용자 ID와 이미지를 업로드하세요.");
            return;
        }
    
        const formData = new FormData();
        formData.append("user_id", userId);
        formData.append("mask_type", maskType);
        formData.append("image", image);
    
        try {
            const response = await fetch("http://127.0.0.1:8000/detection/face-masking/", {
                method: "POST",
                body: formData
            });
    
            const data = await response.json();
            if (data.image_url) {
                // ✅ 새로운 파일명 반영하여 최신 이미지 표시
                const imgURL = `http://127.0.0.1:8000${data.image_url}`;
                console.log("✅ 백엔드에서 받은 이미지 URL:", imgURL);
                setMaskedImageUrl(imgURL);
            } else {
                alert("마스킹 실패: " + data.message);
            }
        } catch (error) {
            console.error("마스킹 오류:", error);
            alert("서버 오류 발생");
        }
    };
    

    return (
        <div style={{ textAlign: "center", marginTop: "20px" }}>
            <h2>얼굴 마스킹</h2>
            <input
                type="text"
                placeholder="사용자 ID 입력"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                style={{ display: "block", margin: "10px auto", padding: "10px" }}
            />
            <input 
                type="file" 
                accept="image/*" 
                onChange={handleFileChange} 
                style={{ display: "block", margin: "10px auto" }}
            />
            <select 
                value={maskType} 
                onChange={(e) => setMaskType(e.target.value)}
                style={{ display: "block", margin: "10px auto", padding: "5px" }}
            >
                <option value="black">기본(검은 사각형)</option>
                <option value="bear">이모티콘 곰</option>
                <option value="tiger">이모티콘 호랑이</option>
                <option value="koala">이모티콘 코알라</option>
                <option value="blur">블러</option>
            </select>
            <button 
                onClick={handleMasking} 
                style={{
                    display: "block",
                    margin: "10px auto",
                    padding: "10px",
                    backgroundColor: "#007BFF",
                    color: "white",
                    border: "none",
                    cursor: "pointer"
                }}
            >
                마스킹 적용
            </button>

            {/* 결과 이미지 출력 */}
            {maskedImageUrl && (
                <div style={{ marginTop: "20px" }}>
                    <h3>마스킹된 이미지</h3>
                    <img 
                        src={maskedImageUrl} 
                        alt="Masked" 
                        style={{ maxWidth: "100%", border: "2px solid black", padding: "5px" }} 
                    />
                    <br />
                    <a href={maskedImageUrl} download="masked_image.png">
                        <button style={{ marginTop: "10px", padding: "10px", backgroundColor: "#28A745", color: "white", border: "none", cursor: "pointer" }}>
                            이미지 다운로드
                        </button>
                    </a>
                </div>
            )}
        </div>
    );
}

export default Masking;

// server/index.js
const express = require("express");
const fs = require("fs");
const path = require("path");
const cors = require("cors");

const app = express();
const PORT = 5050;

// CORS 허용 (React 클라이언트가 localhost:3000에서 요청 가능)
app.use(cors());

// recordings 디렉토리 경로 설정
const RECORDINGS_DIR = "/Users/jeong-yujin/Desktop/Veteran/recordings";

// 세션 폴더 리스트 반환
app.get("/api/sessions", (req, res) => {
  try {
    const dirs = fs
      .readdirSync(RECORDINGS_DIR)
      .filter((file) =>
        fs.statSync(path.join(RECORDINGS_DIR, file)).isDirectory()
      )
      .sort();
    res.json(dirs);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "디렉토리를 읽을 수 없습니다." });
  }
});

// 특정 세션의 metadata.json 반환
app.get("/api/sessions/:sessionId/metadata", (req, res) => {
  const { sessionId } = req.params;
  const filePath = path.join(RECORDINGS_DIR, sessionId, "metadata.json");

  if (fs.existsSync(filePath)) {
    const data = fs.readFileSync(filePath, "utf-8");
    res.json(JSON.parse(data));
  } else {
    res.status(404).json({ error: "metadata.json 없음" });
  }
});

// 특정 세션의 transcript.txt 반환
app.get("/api/sessions/:sessionId/transcript", (req, res) => {
  const { sessionId } = req.params;
  const filePath = path.join(RECORDINGS_DIR, sessionId, "transcript.txt");

  if (fs.existsSync(filePath)) {
    const text = fs.readFileSync(filePath, "utf-8");
    res.send(text);
  } else {
    res.status(404).send("transcript.txt 없음");
  }
});

// 특정 세션의 오디오 파일 리스트 반환
app.get("/api/sessions/:sessionId/audios", (req, res) => {
  const { sessionId } = req.params;
  const dirPath = path.join(RECORDINGS_DIR, sessionId);

  try {
    const files = fs
      .readdirSync(dirPath)
      .filter((f) => f.endsWith(".wav"))
      .sort();
    res.json(files);
  } catch (err) {
    res.status(500).json({ error: "오디오 파일을 읽을 수 없음" });
  }
});

// 정적 파일 서빙 (오디오)
app.use("/recordings", express.static(RECORDINGS_DIR));

// 서버 실행
app.listen(PORT, () => {
  console.log(`🚀 Server listening on http://localhost:${PORT}`);
});

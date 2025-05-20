from fastapi import FastAPI, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from typing import List
from app.s3_utils import upload_file_to_s3, upload_text_to_s3
from app.models import Video
from app.video_chunker import split_video_into_chunks 
import datetime, tempfile, shutil, requests, os
from app.redis_client import redis_client
from fastapi import Form
import uuid
import whisper
from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Whisper 모델 로딩 (기본 base 모델)
model = whisper.load_model("base")
 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 영상 업로드 + S3 저장 + RDS 기록 + 청크 분할 + Redis 저장
@app.post("/upload-and-chunk")
async def upload_and_chunk(file: UploadFile = File(...), db: Session = Depends(get_db)):
   # 1. 업로드된 파일을 임시 파일로 저장
    tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.mp4")
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 2. S3에 원본 영상 업로드
    with open(tmp_path, "rb") as f:
        s3_url = upload_file_to_s3(f, file.filename)

    # 3. DB 저장
    video = Video(
        filename=file.filename,
        url=s3_url,
        uploaded_at=datetime.datetime.utcnow(),
        status="uploaded"
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    # 4. ffmpeg로 청크 분할
    chunk_paths = split_video_into_chunks(tmp_path)

    # 5. Redis에 청크 저장
    for idx, chunk_path in enumerate(chunk_paths):
        with open(chunk_path, "rb") as chunk_file:
            chunk_data = chunk_file.read()
            await redis_client.set(f"chunk:{video.id}:{idx}", chunk_data, ex=900)

    # 6. 상태 변경
    video.status = "chunked"
    db.commit()

    # 7. 임시 파일 및 청크 삭제 (선택)
    try:
        os.remove(tmp_path)
        for path in chunk_paths:
            os.remove(path)
    except Exception as cleanup_err:
        print(f"⚠️ 임시 파일 정리에 실패했습니다: {cleanup_err}")

    return {
        "video_id": video.id,
        "chunk_count": len(chunk_paths),
        "message": "S3 업로드 및 ffmpeg 청크 분할 완료"
    }
# 청크별 음성 → 텍스트 변환 & Redis 저장
@app.post("/run-transcribe/{video_id}")
async def run_transcribe(video_id: int):
    index = 0
    total = 0

    while True:
        key = f"chunk:{video_id}:{index}"
        chunk = await redis_client.get(key)
        if not chunk:
            break

        try:
            # 1. 임시로 mp4 저장
            tmp_mp4 = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            tmp_mp4.write(chunk)
            tmp_mp4.close()

            # 2. ffmpeg로 mp4 → wav 변환
            tmp_wav_path = tmp_mp4.name.replace(".mp4", ".wav")
            os.system(f"ffmpeg -y -i {tmp_mp4.name} -ar 16000 -ac 1 -f wav {tmp_wav_path}")

            # 3. Whisper로 텍스트 추출
            result = model.transcribe(tmp_wav_path)
            transcript = result.get("text", "").strip()

            # 4. Redis에 텍스트 저장
            await redis_client.set(f"transcript:{video_id}:{index}", transcript, ex=1800)

            total += 1
            print(f"✅ 청크 {index} 변환 완료")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"청크 {index} 처리 실패: {str(e)}")

        finally:
            os.remove(tmp_mp4.name)
            if os.path.exists(tmp_wav_path):
                os.remove(tmp_wav_path)

        index += 1

    return {
        "video_id": video_id,
        "transcribed_chunks": total,
        "message": "Whisper 인퍼런스 완료"
    }
# 텍스트 병합 + S3 업로드 + RDS 저장
@app.post("/merge-transcript/{video_id}")
async def merge_transcript(video_id: int, db: Session = Depends(get_db)):
    transcripts = []
    index = 0

    while True:
        key = f"transcript:{video_id}:{index}"
        value = await redis_client.get(key)
        if not value:
            break
        transcripts.append(value.decode("utf-8"))
        index += 1

    if not transcripts:
        raise HTTPException(status_code=404, detail="Transcript not found in Redis")

    full_text = "\n".join(transcripts)

    # 텍스트를 S3에 저장
    filename = f"{video_id}_transcript.txt"
    transcript_url = upload_text_to_s3(full_text, filename)

    # DB에 저장
    video = db.query(Video).filter(Video.id == video_id).first()
    if video:
        video.transcript_url = transcript_url
        db.commit()
        db.refresh(video)

    return {
        "video_id": video_id,
        "lines": len(transcripts),
        "transcript_url": transcript_url,
        "message": "Transcript 병합 및 S3 저장 완료"
    }

@app.post("/summarize-transcript/{video_id}")
async def summarize_transcript(video_id: int, db: Session = Depends(get_db)):
    # 1. DB에서 transcript_url 가져오기
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or not video.transcript_url:
        raise HTTPException(status_code=404, detail="Transcript URL not found")

    # 2. S3에서 텍스트 가져오기
    response = requests.get(video.transcript_url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch transcript from S3")

    full_text = response.text.strip()

    # 3. 요약 프롬프트 생성
    prompt = (
        "다음은 음성에서 추출된 전체 자막입니다. 이 내용을 간결하고 자연스럽게 요약해 주세요.\n\n"
        f"{full_text}\n\n요약:"
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 한국어 텍스트를 요약해주는 어시스턴트입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        summary = completion.choices[0].message.content.strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 실패: {str(e)}")

    return {
        "video_id": video_id,
        "summary": summary,
        "message": "요약 성공"
    }

#  AI Video Summarization Pipeline
### Whisper & GPT 기반 영상 요약 백엔드 파이프라인

> 대용량 영상 파일을 업로드하면  
> 음성을 추출·분할·텍스트화하고,  
> AI를 활용해 핵심 내용을 자동 요약하는  
> **AI 영상 요약 파이프라인 프로젝트**

---

##  Project Overview

- **Project Type**: Personal / Backend Project  
- **Topic**: AI-based Video Summarization Pipeline  
- **Core Tech**: FastAPI, Whisper, GPT, ffmpeg  
- **Focus**: 대용량 영상 처리, 비동기 파이프라인, AI 추론 자동화  

---

##  Project Goal

- 대용량 영상 업로드 및 안정적인 처리
- 음성 인식(ASR)과 요약을 분리한 **단계별 AI 파이프라인 구축**
- 영상 → 텍스트 → 요약으로 이어지는 자동화 흐름 구현
- 실제 서비스 적용을 고려한 백엔드 아키텍처 설계

---

##  Key Features

- **Video Upload API**
  - FastAPI 기반 영상 업로드
  - 대용량 파일 처리 지원
- **Audio Extraction & Chunking**
  - ffmpeg를 활용한 영상 음성 추출
  - 일정 길이 단위로 오디오 분할
- **Speech-to-Text (ASR)**
  - OpenAI Whisper 기반 음성 인식
  - 청크 단위 추론 후 결과 병합
- **AI Summarization**
  - GPT API를 활용한 텍스트 요약
  - 전체 영상 내용을 핵심 위주로 요약
- **Pipeline Orchestration**
  - 단계별 처리 상태 관리
  - 실패 시 재처리 고려

---

## System Architecture

```text
Client
  ↓
FastAPI (Upload API)
  ↓
Video File (S3)
  ↓
ffmpeg (Audio Extraction & Chunking)
  ↓
Redis (Chunk Task Storage)
  ↓
Whisper Inference (Chunk-based)
  ↓
Transcript Merge
  ↓
GPT Summarization
  ↓
Summary Result (S3 / DB)

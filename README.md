# AI Video Summarization Pipeline
### Whisper & GPT ベースの映像要約バックエンドパイプライン

> 大容量の動画ファイルをアップロードすると、  
> 音声の抽出・分割・テキスト化を行い、  
> AI を活用して重要な内容を自動的に要約する  
> **AI 映像要約パイプラインプロジェクト**

---

## Project Overview

- **Project Type**: 個人開発 / バックエンドプロジェクト  
- **Topic**: AI ベース映像要約パイプライン  
- **Core Tech**: FastAPI, Whisper, GPT, ffmpeg  
- **Focus**: 大容量動画処理、非同期パイプライン、AI 推論の自動化  

---

## Project Goal

- 大容量動画アップロードおよび安定した処理の実現  
- 音声認識（ASR）と要約処理を分離した **段階的 AI パイプラインの構築**  
- 動画 → テキスト → 要約までの自動化フロー実装  
- 実サービス適用を想定したバックエンドアーキテクチャ設計  

---

## Key Features

- **Video Upload API**
  - FastAPI ベースの動画アップロード API  
  - 大容量ファイル処理に対応
- **Audio Extraction & Chunking**
  - ffmpeg を用いた動画からの音声抽出  
  - 一定長ごとのオーディオ分割
- **Speech-to-Text（ASR）**
  - OpenAI Whisper を用いた音声認識  
  - チャンク単位での推論および結果の統合
- **AI Summarization**
  - GPT API を利用したテキスト要約  
  - 映像全体の内容を要点中心に要約
- **Pipeline Orchestration**
  - 各処理段階のステータス管理  
  - 処理失敗時の再実行を考慮した設計

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

# AI Video Summarization Pipeline

### Whisper & GPTを活用した動画要約バックエンドパイプライン

> 大容量の動画ファイルをアップロードすると、
> 音声の抽出・分割・文字起こしを行い、
> AIを活用して動画の要点を自動的に要約する
> **AI動画要約パイプラインプロジェクト**

---

## Project Overview

* **Project Type**: Personal / Backend Project
* **Topic**: AI-based Video Summarization Pipeline
* **Core Tech**: FastAPI, Whisper, GPT, ffmpeg
* **Focus**: 大容量動画処理、非同期パイプライン、AI推論の自動化

---

## Project Goal

* 大容量動画の安定したアップロード・処理を実現
* 音声認識（ASR）と要約処理を分離した**段階的なAIパイプライン**の構築
* 「動画 → テキスト → 要約」までの自動処理フローを実装
* 実サービスへの適用を想定したバックエンドアーキテクチャの設計

---

## Key Features

### Video Upload API

* FastAPIを用いた動画アップロードAPI
* 大容量ファイルのアップロードに対応

### Audio Extraction & Chunking

* ffmpegによる音声抽出
* 一定時間ごとに音声をチャンクへ分割

### Speech-to-Text (ASR)

* OpenAI Whisperを用いた音声認識
* チャンク単位で推論を実行し、認識結果を統合

### AI Summarization

* GPT APIを用いたテキスト要約
* 動画全体の内容を要点中心に要約

### Pipeline Orchestration

* 各処理ステージの状態管理
* エラー発生時の再実行を考慮した設計

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
```
## My Role

- FastAPIを用いたREST APIの設計・実装
- S3を利用した動画ファイル管理
- ffmpegによる音声抽出・チャンク分割処理の実装
- Redisを利用したチャンク単位の処理状態管理
- OpenAI Whisperによる音声認識パイプラインの構築
- GPT APIを利用した動画要約機能の実装
- AIパイプライン全体の設計およびバックエンドアーキテクチャの構築
- AWS（EC2・S3・RDS）を利用したデプロイ・運用

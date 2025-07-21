# 🤖 QuickMeet: AI-Powered Meeting Insights

**QuickMeet** is an AI-powered platform that extracts meaningful insights from recorded Google Meet sessions. From generating summaries to action items, PDFs, presentations, and even AI-narrated videos — QuickMeet helps turn conversations into clear outcomes.

---

## 🚀 Features

- 🎙️ Upload meeting audio (Google Meet recordings)
- ☁️ Store audio files securely in AWS S3
- 🧠 Transcribe speech to text using AWS Transcribe
- ✂️ Generate smart summaries with a BART-based model
- ✅ Extract clear action items using NLP + Regex
- 🎥 Generate AI avatar videos (HeyGen) to narrate summaries
- 📄 Export summary and action items to PDF & PPT
- 📧 Email outputs via AWS SES
- 🔍 Semantic search to instantly find key points from the meeting

---

## 🛠️ Tech Stack & Tools

| Tool | Purpose |
|------|---------|
| **AWS S3** | Audio file storage |
| **AWS Transcribe** | Speech-to-text transcription |
| **HuggingFace BART** | Adaptive text summarization |
| **Regex NLP Rules** | Extracting action items (tasks, dates, responsibilities) |
| **HeyGen API** | AI avatar video narration |
| **All-MiniLM-L6-v2** | Fast semantic search over transcript |
| **PDFKit / wkhtmltopdf** | Generate PDF reports |
| **python-pptx** | Generate PPT presentations |
| **AWS SES** | Sending summary/action item emails |

---
## ⚙️ How It Works

1. **Upload Audio** → User uploads a `.mp3` or `.wav` file.
2. **Transcription** → AWS Transcribe converts speech to text.
3. **Summarization** → BART summarizer condenses long text.
4. **Action Items** → Regex identifies tasks, deadlines, persons.
5. **Video Narration** → HeyGen generates an avatar video summary.
6. **Export Docs** → Summary + Action Items → PDF and PPT.
7. **Email Delivery** → Everything sent to your inbox via AWS SES.
8. **Search** → Find key insights using semantic search.

---

# 🎬 Smart Subtitle & Audio Pipeline (CapCut Style)

Công cụ Python **All-in-One** tự động hóa quy trình chuyển đổi file SRT thô thành file Audio đọc tự nhiên bằng AI (`edge-tts`) và đồng bộ phụ đề chuẩn xác đến từng từ bằng `faster-whisper`.

Pipeline hỗ trợ **Smart Chunking** — ngắt dòng phụ đề thông minh theo phong cách CapCut — và xuất phụ đề **Word-by-Word** với timestamp riêng cho từng từ, phù hợp cho các hiệu ứng pop-up, đổi màu hoặc animation.

---

## ✨ Tính năng chính

### 📝 Trích xuất văn bản tự động

* Đọc toàn bộ nội dung từ file SRT đầu vào.
* Tự động loại bỏ các thẻ HTML.
* Làm sạch các định dạng hoặc nội dung rác trước khi đưa vào TTS.

### 🎙️ Tổng hợp giọng đọc AI — Edge-TTS

* Sử dụng `edge-tts` để tạo giọng đọc AI.
* Tạo file audio liền mạch từ toàn bộ nội dung.
* Hỗ trợ tùy chỉnh:

  * Giọng đọc.
  * Tốc độ đọc.
  * Âm lượng.
  * Độ cao giọng đọc.

### ✂️ Smart Chunking — Cắt câu kiểu CapCut

Sử dụng timestamp cấp độ từ (**word-level timestamps**) do Whisper cung cấp để tự động gom nhóm các từ thành những đoạn phụ đề cân đối.

Mặc định:

```text
--max-chars 40
```

Ví dụ:

```text
Quê hương là nơi mỗi người
được sinh ra và lớn lên.
```

Thay vì giữ nguyên các câu hoặc đoạn SRT ban đầu, hệ thống có thể phân chia lại subtitle dựa trên:

* Timestamp thực tế của từng từ.
* Độ dài tối đa của mỗi dòng.
* Ranh giới từ.
* Tính liên tục của nội dung.

### 💬 Word-by-Word SRT Export

Xuất thêm một file SRT riêng trong đó mỗi subtitle tương ứng với **một từ**.

Ví dụ:

```text
1
00:00:00,000 --> 00:00:00,420
Quê

2
00:00:00,420 --> 00:00:00,760
hương

3
00:00:00,760 --> 00:00:01,120
là
```

Định dạng này phù hợp với:

* Hiệu ứng từng từ xuất hiện.
* Word pop-up.
* Karaoke.
* Đổi màu từng từ.
* Animation subtitle.
* Video TikTok / Reels / Shorts.

### 🖥️ Giao diện dòng lệnh — CLI

CLI cho phép tùy chỉnh toàn bộ pipeline mà không cần sửa mã nguồn:

* File SRT đầu vào.
* File audio đầu ra.
* File SRT đồng bộ.
* File Word-by-Word SRT.
* Voice Edge-TTS.
* Rate.
* Volume.
* Pitch.
* Whisper model.
* Prompt.
* Giới hạn ký tự subtitle.

---

## 📦 Yêu cầu hệ thống

### Python

Yêu cầu:

```text
Python 3.8+
```

### FFmpeg

`FFmpeg` cần được cài đặt trên hệ thống và thêm vào biến môi trường `PATH`.

FFmpeg được sử dụng trong quá trình xử lý audio phục vụ cho Whisper.

Kiểm tra:

```bash
ffmpeg -version
```

Nếu lệnh trên trả về thông tin phiên bản FFmpeg thì hệ thống đã nhận diện được FFmpeg.

### Python packages

Các thư viện chính:

```text
faster-whisper
edge-tts
pysrt
```

Cài đặt:

```bash
pip install faster-whisper edge-tts pysrt
```

---

## ⚙️ Hướng dẫn cài đặt nhanh

### 1. Chuẩn bị mã nguồn

Đặt hai file:

```text
app.py
run.sh
```

vào cùng một thư mục.

Cấu trúc tối thiểu:

```text
smart-subtitle-pipeline/
├── app.py
├── run.sh
└── input.srt
```

### 2. Chuẩn bị file SRT

Đặt file SRT cần xử lý vào cùng thư mục.

Ví dụ:

```text
input.srt
```

Nội dung:

```srt
1
00:00:00,000 --> 00:00:03,000
Quê hương là nơi mỗi người được sinh ra.

2
00:00:03,000 --> 00:00:06,000
Là nơi lưu giữ những ký ức tuổi thơ.
```

---

# 🚀 Hướng dẫn sử dụng

## Cách 1 — Sử dụng Bash Script

Trên Linux/macOS, cấp quyền thực thi:

```bash
chmod +x run.sh
```

Sau đó chạy:

```bash
./run.sh input.srt
```

Script có thể được sử dụng để tự động hóa toàn bộ quá trình xử lý.

---

## Cách 2 — Chạy trực tiếp bằng Python

Cài đặt dependencies:

```bash
pip install faster-whisper edge-tts pysrt
```

Sau đó chạy:

```bash
python app.py input.srt \
  -o output.mp3 \
  -s synced_output.srt \
  -w word_by_word.srt \
  --whisper-model medium \
  --max-chars 40
```

Pipeline sẽ thực hiện:

```text
input.srt
    │
    ▼
Extract & Clean Text
    │
    ▼
Edge-TTS
    │
    ▼
output.mp3
    │
    ▼
faster-whisper
    │
    ▼
Word-level Timestamps
    │
    ├───────────────┐
    ▼               ▼
Smart Chunking    Word-by-Word
    │               │
    ▼               ▼
synced_output.srt  word_by_word.srt
```

---

# 🎬 Smart Subtitle & Audio Pipeline — CLI Reference

## 🚀 Câu lệnh Bash đầy đủ

Có thể sử dụng câu lệnh sau để cấu hình toàn bộ các tham số:

```bash
python app.py input.srt \
  -o output.mp3 \
  -s synced_output.srt \
  -w word_by_word.srt \
  -v vi-VN-HoaiMyNeural \
  -r "+0%" \
  --volume "+0%" \
  --pitch "+0Hz" \
  --whisper-model medium \
  --prompt "Đoạn văn bản mẫu định hướng từ vựng cho Whisper..." \
  --max-chars 40
```

---

## 📋 Bảng tham số CLI

| Tham số / Cờ       | Giá trị mặc định     | Mô tả                                    |
| ------------------ | -------------------- | ---------------------------------------- |
| `input`            | **Bắt buộc**         | Đường dẫn file SRT đầu vào               |
| `-o`, `--output`   | `output.mp3`         | File audio đầu ra                        |
| `-s`, `--sync-srt` | `synced_output.srt`  | File SRT đồng bộ mới bằng Smart Chunking |
| `-w`, `--word-srt` | Trống                | Tên file SRT Word-by-Word đầu ra         |
| `-v`, `--voice`    | `vi-VN-HoaiMyNeural` | Giọng đọc Edge-TTS                       |
| `-r`, `--rate`     | `+0%`                | Tốc độ đọc                               |
| `--volume`         | `+0%`                | Âm lượng                                 |
| `--pitch`          | `+0Hz`               | Độ cao giọng đọc                         |
| `--whisper-model`  | `medium`             | Model Whisper sử dụng để nhận dạng       |
| `--prompt`         | `""`                 | Prompt định hướng từ vựng cho Whisper    |
| `--max-chars`      | `40`                 | Số ký tự tối đa cho mỗi đoạn phụ đề      |

---

# 🧩 Ví dụ sử dụng

## Ví dụ 1 — Cấu hình cơ bản

```bash
python app.py input.srt
```

Sử dụng các giá trị mặc định của chương trình.

---

## Ví dụ 2 — Tạo audio và subtitle đồng bộ

```bash
python app.py input.srt \
  -o output.mp3 \
  -s synced_output.srt
```

Kết quả:

```text
output.mp3
synced_output.srt
```

---

## Ví dụ 3 — Xuất Word-by-Word

```bash
python app.py input.srt \
  -o output.mp3 \
  -s synced_output.srt \
  -w word_by_word.srt
```

Kết quả:

```text
output.mp3
synced_output.srt
word_by_word.srt
```

---

## Ví dụ 4 — Giới hạn subtitle 30 ký tự

```bash
python app.py input.srt \
  --max-chars 30
```

Điều này yêu cầu Smart Chunking cố gắng giới hạn mỗi đoạn subtitle ở mức tối đa khoảng 30 ký tự.

---

## Ví dụ 5 — Thay đổi giọng đọc

```bash
python app.py input.srt \
  -v vi-VN-HoaiMyNeural
```

Có thể thay đổi voice theo voice mà Edge-TTS hỗ trợ.

---

## Ví dụ 6 — Điều chỉnh tốc độ, âm lượng và pitch

```bash
python app.py input.srt \
  -r "+10%" \
  --volume "+0%" \
  --pitch "+2Hz"
```

---

# 📁 Cấu trúc đầu ra

Sau khi chạy pipeline, thư mục có thể có dạng:

```text
smart-subtitle-pipeline/
│
├── app.py
├── run.sh
├── input.srt
│
├── output.mp3
├── synced_output.srt
└── word_by_word.srt
```

### `output.mp3`

File audio được tạo bởi Edge-TTS.

### `synced_output.srt`

File subtitle được tạo lại dựa trên timestamp thực tế từ Whisper và thuật toán Smart Chunking.

### `word_by_word.srt`

File subtitle trong đó mỗi từ có timestamp riêng.

---

# 🔄 Pipeline xử lý

Toàn bộ quy trình:

```text
┌──────────────────────┐
│      input.srt       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Extract SRT Text     │
│ Remove HTML / Noise  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Edge-TTS       │
│   Generate Audio     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      output.mp3      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   faster-whisper     │
│ Word-level Timestamp │
└──────────┬───────────┘
           │
           ▼
      ┌────┴─────┐
      │          │
      ▼          ▼
┌───────────┐ ┌───────────────┐
│   Smart   │ │ Word-by-Word  │
│ Chunking  │ │    Export     │
└─────┬─────┘ └───────┬───────┘
      │               │
      ▼               ▼
synced_output.srt  word_by_word.srt
```

---

# 🎯 Mục tiêu thiết kế

Pipeline được thiết kế theo hướng **Script → Audio → Word Timestamp → Subtitle**, thay vì phụ thuộc hoàn toàn vào timestamp của SRT gốc.

Điều này giúp subtitle bám sát hơn với **audio thực tế**, đặc biệt khi:

* Tốc độ đọc thay đổi.
* Nội dung SRT có timestamp không chính xác.
* Một câu được đọc nhanh hoặc chậm hơn dự kiến.
* Cần tạo subtitle animation theo từng từ.
* Cần chia subtitle thành các đoạn ngắn phù hợp với video dạng short-form.

---

# 📌 Use Cases

Pipeline phù hợp cho:

* 🎬 TikTok.
* 📱 YouTube Shorts.
* 📸 Instagram Reels.
* 🎙️ Video voice-over.
* 📰 Video tin tức.
* 📚 Video giáo dục.
* 📖 Audiobook ngắn.
* 🧠 Video quote / philosophy.
* 🎵 Karaoke và subtitle animation.
* ✨ Caption từng từ kiểu pop-up.

---

# 🛠️ Công nghệ

| Thành phần           | Công nghệ      |
| -------------------- | -------------- |
| Programming Language | Python         |
| Text-to-Speech       | Edge-TTS       |
| Speech-to-Text       | faster-whisper |
| Subtitle Input       | SRT            |
| Subtitle Output      | SRT            |
| Audio Processing     | FFmpeg         |
| Subtitle Parsing     | pysrt          |
| Interface            | CLI            |

---

# 📄 License

Tùy thuộc vào license được lựa chọn cho dự án.

> **Lưu ý:** Việc sử dụng Edge-TTS, faster-whisper, FFmpeg và các model liên quan cần tuân thủ license và điều khoản sử dụng tương ứng của từng dự án.
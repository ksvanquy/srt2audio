# SRT to Audio

Công cụ dòng lệnh chuyển nội dung tiếng Việt trong file SRT thành audio đọc liên tục bằng [Edge-TTS](https://github.com/rany2/edge-tts), sau đó dùng [faster-whisper](https://github.com/SYSTRAN/faster-whisper) để nhận dạng audio và tạo timestamp theo từ.

Kết quả phù hợp để tạo subtitle bám theo audio TTS, subtitle chia đoạn ngắn hoặc hiệu ứng hiển thị từng từ. Đây là **word-level transcription/timestamping**, không phải forced alignment chính xác với văn bản SRT gốc.

## Tính năng

- Đọc và gom nội dung từ toàn bộ file SRT.
- Xóa HTML tag và chuẩn hóa xuống dòng trong nội dung subtitle.
- Tạo một file audio liền mạch với Edge-TTS.
- Tạo SRT chia thành các chunk dựa trên timestamp của Whisper.
- Tạo SRT word-by-word, mỗi mục tương ứng với một từ.
- Tùy chỉnh voice, tốc độ, âm lượng, cao độ, model Whisper và độ dài chunk.

## Yêu cầu

- Python 3.8 trở lên.
- Kết nối Internet khi chạy Edge-TTS; lần đầu dùng model Whisper có thể cần tải model.
- faster-whisper hiện được cấu hình chạy trên CPU với `compute_type="int8"`. Model mặc định `medium` có thể cần nhiều RAM và chạy lâu.

Mã nguồn không gọi FFmpeg trực tiếp. Nếu môi trường hoặc phiên bản backend audio của bạn yêu cầu FFmpeg, hãy cài riêng và thêm vào `PATH`.

## Cài đặt

Từ thư mục dự án, tạo virtual environment và cài dependency:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Dependency trực tiếp được khai báo trong `requirements.txt`:

- `edge-tts>=6.1.9`
- `pysrt>=1.1.2`
- `faster-whisper>=1.0.3`

## Sử dụng nhanh

Đặt file SRT UTF-8 vào thư mục dự án rồi chạy:

```bash
python main.py input.srt
```

Lệnh trên tạo:

```text
output.mp3
synced_output.srt
synced_output_word_by_word.srt
```

Tên file word-by-word mặc định được tạo bằng cách thay `.srt` trong giá trị `--sync-srt` bằng `_word_by_word.srt`.

Ví dụ chỉ định toàn bộ các tùy chọn:

```bash
python main.py input.srt \
  -o output.mp3 \
  -s synced_output.srt \
  -w word_by_word.srt \
  -v vi-VN-HoaiMyNeural \
  -r "+10%" \
  --volume "+0%" \
  --pitch "+2Hz" \
  --whisper-model small \
  --prompt "Đoạn văn bản mẫu định hướng từ vựng cho Whisper" \
  --max-chars 40
```

Trên PowerShell, cú pháp nhiều dòng tương đương dùng dấu backtick:

```powershell
python main.py input.srt `
  -o output.mp3 `
  -s synced_output.srt `
  -w word_by_word.srt `
  --whisper-model small `
  --max-chars 40
```

## CLI reference

| Tham số | Mặc định | Mô tả |
| --- | --- | --- |
| `input` | Bắt buộc | Đường dẫn file SRT đầu vào. |
| `-o`, `--output` | `output.mp3` | File audio đầu ra. |
| `-s`, `--sync-srt` | `synced_output.srt` | SRT được tạo từ timestamp của Whisper và thuật toán chia chunk. |
| `-w`, `--word-srt` | Trống | Tên SRT word-by-word; để trống thì tự động đặt tên theo `--sync-srt`. |
| `-v`, `--voice` | `vi-VN-HoaiMyNeural` | Voice Edge-TTS. |
| `-r`, `--rate` | `+0%` | Tốc độ đọc theo định dạng Edge-TTS, ví dụ `+10%` hoặc `-10%`. |
| `--volume` | `+0%` | Âm lượng theo định dạng Edge-TTS. |
| `--pitch` | `+0Hz` | Cao độ theo định dạng Edge-TTS. |
| `--whisper-model` | `medium` | Tên model faster-whisper, ví dụ `small` hoặc `medium`. |
| `--prompt` | Trống | Prompt định hướng từ vựng cho Whisper. Nếu bỏ trống, chương trình dùng 200 ký tự đầu của văn bản. |
| `--max-chars` | `40` | Số ký tự mục tiêu tối đa cho mỗi chunk trong từng Whisper segment. Đây là giới hạn xấp xỉ. |

Xem các tham số trực tiếp từ terminal:

```bash
python main.py --help
```

## Pipeline

1. `srt_parser.py` đọc SRT bằng `pysrt`, xóa HTML tag, thay newline bằng khoảng trắng và nối các subtitle thành một chuỗi.
2. `tts_engine.py` gửi toàn bộ chuỗi cho Edge-TTS để tạo audio liên tục.
3. `aligner.py` chạy faster-whisper trên audio với `language="vi"`, word timestamps, CPU và `int8`.
4. Các từ trong mỗi Whisper segment được gom tuần tự thành các chunk theo `--max-chars`, rồi ghi vào `--sync-srt`.
5. Whisper được chạy thêm một lần để ghi từng từ vào `--word-srt`.

## Input và output

Input là file SRT UTF-8, ví dụ:

```srt
1
00:00:01,000 --> 00:00:04,000
Quê hương là nơi mỗi người được sinh ra.

2
00:00:04,500 --> 00:00:08,000
Là nơi lưu giữ những ký ức tuổi thơ.
```

Các timestamp và khoảng nghỉ của SRT đầu vào **không được giữ lại**. Chương trình chỉ lấy text, đọc thành một audio liên tục, rồi tạo timestamp mới từ kết quả Whisper. Vì Whisper là mô hình nhận dạng giọng nói, text output có thể khác input về dấu câu, cách viết hoặc từ ngữ.

`output.mp3` là audio do Edge-TTS tạo. `synced_output.srt` chứa các chunk có timestamp. File word-by-word chứa một từ trên mỗi mục SRT. Các file đầu ra có thể bị ghi đè; thư mục cha của chúng phải tồn tại trước khi chạy.

## Cấu trúc dự án

```text
srt2audio/
├── main.py          # CLI và điều phối pipeline
├── srt_parser.py    # Đọc, làm sạch và gom text SRT
├── tts_engine.py    # Tạo audio bằng Edge-TTS
├── aligner.py       # Whisper timestamp và xuất SRT
├── requirements.txt
├── input.srt        # File mẫu
└── README.md
```

## Giới hạn đã biết

- Ngôn ngữ Whisper đang cố định là tiếng Việt (`vi`); CLI chưa có tùy chọn đổi ngôn ngữ.
- Đây không phải forced alignment với transcript gốc. Kết quả phụ thuộc vào khả năng nhận dạng của Whisper.
- `--max-chars` được áp dụng trong từng Whisper segment, không phải trên toàn bộ audio; một từ dài hơn giới hạn vẫn được giữ nguyên.
- Model được khởi tạo và audio được nhận dạng hai lần khi xuất cả hai loại SRT, nên có thể tốn thêm thời gian và bộ nhớ.
- Nội dung rỗng có thể khiến bước Edge-TTS thất bại.
- Tên word-by-word tự động dùng phép thay thế chuỗi `.srt`, vì vậy nên dùng tên `--sync-srt` có phần mở rộng `.srt` viết thường khi muốn dùng quy tắc mặc định.

## License

Repository này hiện chưa khai báo một license cụ thể. Việc sử dụng Edge-TTS, faster-whisper, model Whisper và các dịch vụ liên quan phải tuân thủ license và điều khoản tương ứng của từng dự án.

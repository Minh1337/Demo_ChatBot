# PyBạn — Demo ChatBot

> Chatbot hỏi đáp tiếng Việt với bộ nhớ hội thoại, hỗ trợ học Python và tra cứu kiến thức cục bộ.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-6E56CF)](https://openrouter.ai/)
[![License](https://img.shields.io/badge/license-educational-lightgrey)](#gi%E1%BA%A5y-ph%C3%A9p)

**PyBạn** là một ứng dụng chatbot chạy cục bộ trên Windows, được xây dựng để trình diễn cách kết hợp giao diện web, API FastAPI, truy xuất tài liệu (retrieval) và mô hình ngôn ngữ qua OpenRouter. Chatbot có thể trả lời câu hỏi tổng quát bằng tiếng Việt, giữ ngữ cảnh trong cuộc trò chuyện và cung cấp các đoạn tài liệu tham khảo khi câu hỏi liên quan đến Python.

## Mục lục

- [Tính năng](#tính-năng)
- [Kiến trúc](#kiến-trúc)
- [Yêu cầu](#yêu-cầu)
- [Cài đặt và chạy nhanh](#cài-đặt-và-chạy-nhanh)
- [Cấu hình OpenRouter](#cấu-hình-openrouter)
- [Sử dụng](#sử-dụng)
- [Kiểm thử](#kiểm-thử)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Bảo mật và quyền riêng tư](#bảo-mật-và-quyền-riêng-tư)
- [Giới hạn hiện tại](#giới-hạn-hiện-tại)
- [Tài liệu dự án](#tài-liệu-dự-án)
- [Giấy phép](#giấy-phép)

## Tính năng

- **Hỏi đáp đa chủ đề:** trả lời các câu hỏi thông thường bằng tiếng Việt và sử dụng ngữ cảnh các lượt trước.
- **Hỗ trợ học Python:** nhận diện chủ đề, xếp hạng và đưa vào prompt các đoạn tài liệu liên quan.
- **Giải bài lập trình:** hỏi thêm đề bài khi yêu cầu chưa đủ thông tin; với đề bài cụ thể, hỗ trợ ý tưởng, mã chạy được và cách kiểm tra.
- **Lịch sử nhiều cuộc trò chuyện:** lưu, đổi tên và mở lại hội thoại trực tiếp trong trình duyệt.
- **Thiết kế responsive:** sử dụng được trên màn hình desktop và mobile.
- **Chế độ dự phòng:** khi LLM không khả dụng, câu hỏi Python vẫn có thể nhận nội dung từ corpus cục bộ.
- **Kiểm soát chi phí:** chỉ cho phép endpoint OpenRouter chính thức và model `openrouter/free` hoặc model có hậu tố `:free`.
- **Thông báo lỗi an toàn:** phân biệt lỗi xác thực, hạn mức, kết nối, timeout, model không khả dụng và phản hồi trống mà không lộ API key.

## Kiến trúc

```text
Trình duyệt
    │
    ▼
FastAPI (app.py)
    ├── Xác thực request và giới hạn ngữ cảnh
    ├── Nhận diện câu hỏi Python
    ├── Retrieval từ rag/corpus.jsonl
    └── Generation qua OpenRouter / OpenAI SDK
```

- **Frontend:** HTML, CSS và JavaScript thuần; không cần bundler.
- **Backend:** FastAPI chạy bằng Uvicorn.
- **Retrieval:** tìm kiếm từ vựng và xếp hạng trên corpus JSONL nhỏ.
- **Generation:** API tương thích OpenAI, mặc định dùng router miễn phí của OpenRouter.
- **Lưu trữ:** lịch sử được lưu trong `localStorage` của trình duyệt; máy chủ không lưu hội thoại.

## Yêu cầu

- Windows 10/11
- Python **3.10 trở lên**
- Kết nối Internet để cài dependency và gọi OpenRouter
- API key OpenRouter nếu muốn dùng trả lời AI tổng quát

## Cài đặt và chạy nhanh

### Cách 1: dùng file batch trên Windows

1. Clone repository và mở thư mục project:

   ```powershell
   git clone https://github.com/Minh1337/Demo_ChatBot.git
   cd Demo_ChatBot
   ```

2. Nhấp đúp `setup.bat` để tạo `.venv` và cài dependency.
3. Mở `.env`, điền API key theo phần [Cấu hình OpenRouter](#cấu-hình-openrouter).
4. Nhấp đúp `run.bat`.
5. Mở <http://127.0.0.1:8765/> trong trình duyệt.

Giữ cửa sổ terminal đang chạy server. Nhấn `Ctrl+C` để dừng.

### Cách 2: dùng PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765
```

### Chạy và debug bằng VS Code

1. Mở thư mục project trong VS Code.
2. Chọn interpreter `.venv\Scripts\python.exe`.
3. Mở **Run and Debug** và chọn cấu hình **PyBan (FastAPI)**.
4. Nhấn `F5`, sau đó mở <http://127.0.0.1:8765/>.

Project đã có sẵn cấu hình trong `.vscode/launch.json` và `.vscode/tasks.json`.

## Cấu hình OpenRouter

Tạo file `.env` từ `.env.example` hoặc mở file `.env` cục bộ:

```dotenv
LLM_API_KEY=your_openrouter_key_here
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openrouter/free
```

Lấy API key tại [OpenRouter API Keys](https://openrouter.ai/settings/keys). Không đưa key vào mã nguồn, README, ảnh chụp màn hình hoặc commit Git.

`openrouter/free` cho phép OpenRouter tự chọn một model miễn phí tương thích. Nếu muốn cố định model, chỉ sử dụng model ID có hậu tố `:free` trong [danh sách model OpenRouter](https://openrouter.ai/models). Ứng dụng sẽ chặn model trả phí hoặc endpoint khác trước khi gửi request.

Sau khi chỉnh `.env`, hãy khởi động lại server. Khi chưa có key hoặc API gặp lỗi, câu hỏi Python có thể được trả lời bằng tài liệu cục bộ; các câu hỏi tổng quát cần LLM sẽ hiển thị thông báo lỗi phù hợp.

## Sử dụng

Một số câu hỏi mẫu:

- `Giải thích vòng lặp for trong Python bằng ví dụ đơn giản.`
- `Hàm trong Python khai báo và gọi như thế nào?`
- `Giúp tôi lập kế hoạch học Python cho người mới trong một tuần.`
- `Giúp tôi giải bài toán tính tổng các số chẵn trong danh sách.`

Mỗi cuộc trò chuyện có tối đa 20 tin nhắn gần đây và 12.000 ký tự ngữ cảnh được gửi tới API. Toàn bộ nội dung hội thoại vẫn được giữ trong trình duyệt cho đến khi người dùng xóa dữ liệu trang web.

## Kiểm thử

Chạy các kiểm thử Python:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Chạy kiểm thử JavaScript và kiểm tra cú pháp:

```powershell
node --test tests\conversations.cjs
node --check web\app.js
node --check web\conversations.js
```

Các kiểm thử không gửi hội thoại thật hoặc API key tới OpenRouter. Chẩn đoán request độc lập, nếu cần, có thể chạy bằng:

```powershell
.\.venv\Scripts\python.exe tools\check_openrouter.py
```

Lệnh trên chỉ gửi câu `Reply with OK.` và che thông tin nhạy cảm trong output.

## Cấu trúc thư mục

```text
app.py                    FastAPI app, routing và API /api/chat
rag/
  corpus.jsonl             Corpus kiến thức Python cục bộ
  retrieval.py             Nhận diện chủ đề và xếp hạng tài liệu
  generation.py            Tích hợp OpenRouter và xử lý lỗi
web/
  index.html               Khung giao diện
  style.css                Thiết kế responsive
  app.js                   Luồng chat và tương tác UI
  conversations.js         Lưu và quản lý nhiều hội thoại
tests/
  test_generation_errors.py Kiểm thử generation không gọi mạng
  conversations.cjs         Kiểm thử localStorage và chuyển chat
tools/
  check_openrouter.py       Kiểm tra cấu hình/request mẫu an toàn
docs/                      Báo cáo, kịch bản và tài liệu dự án
```

## Bảo mật và quyền riêng tư

- `.env` nằm trong `.gitignore` và không được commit.
- API key chỉ được đọc từ biến môi trường; log ứng dụng không ghi raw response hoặc key.
- Lịch sử hội thoại được lưu trong trình duyệt hiện tại, không lưu trên backend.
- Khi sử dụng OpenRouter, nội dung câu hỏi và một phần ngữ cảnh gần đây được gửi tới nhà cung cấp để tạo câu trả lời.
- Không nhập thông tin cá nhân, mật khẩu, token hoặc dữ liệu nhạy cảm vào bản demo.

## Giới hạn hiện tại

- Retrieval hiện là tìm kiếm từ vựng trên corpus nhỏ, nên có thể bỏ sót câu hỏi diễn đạt quá khác tài liệu.
- Chất lượng và khả năng đáp ứng phụ thuộc model miễn phí, hạn mức và tình trạng OpenRouter.
- Chế độ không có API key chỉ hỗ trợ fallback cho nội dung có trong corpus Python.
- Lịch sử `localStorage` không đồng bộ giữa thiết bị hoặc các trình duyệt khác nhau.
- Corpus hiện phục vụ mục tiêu demo/học tập, không thay thế tài liệu Python đầy đủ.

## Tài liệu dự án

- [Báo cáo sản phẩm](docs/PROJECT_REPORT_VI.md)
- [Nhật ký phát triển](docs/DEVELOPMENT_LOG_VI.md)
- [Bảng tình huống kiểm thử](docs/TEST_CASES_VI.md)
- [Kịch bản video demo](docs/DEMO_SCRIPT_VI.md)
- [Thiết kế giao diện](docs/UI_LAYOUT_VI.md)

## Giấy phép

Đây là project demo phục vụ mục đích học tập và trình diễn. Nội dung trong corpus cần được đối chiếu với tài liệu chính thức trước khi sử dụng cho mục đích sản xuất.

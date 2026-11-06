# PyBạn — chatbot hỏi đáp tiếng Việt

PyBạn là chatbot hỏi đáp tiếng Việt đa chủ đề, sử dụng OpenRouter để trả lời và theo dõi tối đa 20 tin nhắn gần đây trong cuộc trò chuyện hiện tại. Với câu hỏi Python, chatbot có thể tìm trong bộ tài liệu cục bộ và hiển thị nguồn tham khảo. Với lời nhờ code nhưng chưa có đề bài, PyBạn hỏi thêm; với đề bài cụ thể, chatbot có thể trình bày ý tưởng, mã Python và cách kiểm tra.

## Lưu và mở lại hội thoại

Tin nhắn được tự động lưu trong `localStorage` trên trình duyệt. Nhấn **Trò chuyện mới** ở thanh bên hoặc nút **＋** trên đầu trang để tạo chat mới ngay tại chỗ; chat cũ vẫn nằm trong danh sách lịch sử. Nhấp vào tên một hội thoại để mở lại và tiếp tục hỏi. Trên màn hình nhỏ, chọn hội thoại bằng danh sách ở đầu trang.

Toàn bộ nội dung được giữ lại, kể cả khi đóng rồi mở lại trình duyệt ở cùng địa chỉ ứng dụng. Mỗi chat có ngữ cảnh riêng; chỉ tối đa 20 tin nhắn gần đây (12.000 ký tự) được gửi tới AI. Dữ liệu nằm ở trình duyệt hiện tại, chưa đồng bộ giữa máy hoặc giữa các tab đang mở. Chat từ phiên cũ được nhập tự động nếu còn trong tab.

## Chạy trên Windows

Yêu cầu Python 3.10 trở lên và kết nối Internet trong lần cài thư viện đầu tiên.

1. Mở thư mục `ChatbotAI` trong File Explorer.
2. Nhấp đúp `setup.bat` và đợi cài đặt hoàn tất.
3. Nhấp đúp `run.bat`.
4. Mở <http://127.0.0.1:8765/> trong trình duyệt. Giữ cửa sổ máy chủ mở trong khi sử dụng; nhấn `Ctrl+C` để dừng.

## Chạy và debug bằng VS Code

1. Trong VS Code, chọn **File → Open Folder...** và mở thư mục `ChatbotAI`.
2. Chạy `setup.bat` một lần để tạo `.venv` và cài thư viện.
3. Nhấn `Ctrl+Shift+P`, chạy **Python: Select Interpreter**, chọn `.venv\Scripts\python.exe`.
4. Mở **Run and Debug** ở thanh bên, chọn **PyBan (FastAPI)** rồi nhấn `F5`.
5. Mở <http://127.0.0.1:8765/> trong trình duyệt. Dừng server bằng nút Stop trong VS Code.

Project có `.vscode/launch.json` và `.vscode/tasks.json`. Nếu VS Code hỏi extension Python, cài **Python** của Microsoft; debugger được cung cấp bởi Python Debugger.

Có thể mở terminal tích hợp (`Ctrl+``) và chạy:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765 --reload
```

Hoặc dùng PowerShell trong thư mục project:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8765
```

## Cấu hình OpenRouter

Project đã có file `.env` cục bộ với endpoint OpenRouter và model `openrouter/free`. Tạo hoặc lấy key tại [OpenRouter API Keys](https://openrouter.ai/settings/keys), mở `.env`, dán key sau `LLM_API_KEY=` rồi lưu. Không có khoảng trắng quanh dấu `=`. Khởi động lại server sau khi thay đổi.

```dotenv
LLM_API_KEY=your_openrouter_key_here
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openrouter/free
```

Không gửi hoặc đưa `.env` vào Git, ảnh chụp màn hình hay video báo cáo. `.env` đã được thêm vào `.gitignore`. Khi chưa có key hoặc OpenRouter lỗi, chatbot tổng quát chưa thể sinh câu trả lời; câu hỏi Python có tài liệu phù hợp sẽ được trả về bằng nội dung tra cứu cục bộ.

`openrouter/free` tự chọn một model miễn phí tương thích; model và giới hạn miễn phí có thể thay đổi. Nếu muốn cố định model miễn phí, thay `LLM_MODEL` bằng model ID có hậu tố `:free` trong [OpenRouter Models](https://openrouter.ai/models). Ứng dụng sẽ từ chối model trả phí hoặc endpoint khác trước khi gửi request.

## Cấu trúc

```text
app.py                 FastAPI, định tuyến câu hỏi và endpoint giao diện
rag/retrieval.py       Chuẩn hóa từ khóa, nhận diện phạm vi, xếp hạng tài liệu
rag/generation.py      Tạo câu trả lời tùy chọn qua OpenRouter (OpenAI SDK)
rag/corpus.jsonl       Mẩu kiến thức và metadata nguồn
web/                   Giao diện hội thoại HTML, CSS, JavaScript
docs/                  Báo cáo, nhật ký phát triển, kịch bản demo và kiểm thử
setup.bat, run.bat     Cài đặt và chạy trên Windows
.vscode/               Cấu hình chạy/debug và task cho VS Code
```

## Hồ sơ dự án

- [Bản nháp báo cáo sản phẩm](docs/PROJECT_REPORT_VI.md)
- [Nhật ký phát triển và quyết định thiết kế](docs/DEVELOPMENT_LOG_VI.md)
- [Bảng tình huống kiểm thử](docs/TEST_CASES_VI.md)
- [Kịch bản video minh họa 2–3 phút](docs/DEMO_SCRIPT_VI.md)
- [Thiết kế giao diện và kiểm tra cuộn](docs/UI_LAYOUT_VI.md)

## Hạn chế hiện biết

- Tra cứu hiện dùng khớp từ vựng BM25 đơn giản trên corpus nhỏ; câu hỏi diễn đạt quá khác tài liệu có thể không tìm đúng đoạn.
- Lời giải code được sinh khi OpenRouter cấu hình và hoạt động; nếu API lỗi, chatbot dự phòng bằng các đoạn kiến thức truy xuất nên có thể không tạo mã hoàn chỉnh.
- Hỏi đáp tổng quát và hiểu ngữ cảnh cần OpenRouter hoạt động; chế độ không có API chỉ trả nội dung Python đã tra cứu.
- Lịch sử lưu trong `localStorage`; xóa dữ liệu trang web của trình duyệt sẽ xóa lịch sử. Lịch sử không được lưu trên máy chủ.
- Tài liệu là bản tóm lược phục vụ bài tập, không thay thế tài liệu học phần hoặc tài liệu Python đầy đủ.
- Kết quả kiểm thử cần được nhóm chạy và ghi lại trước khi đưa vào báo cáo cuối cùng.

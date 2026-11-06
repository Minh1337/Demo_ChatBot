# Nhật ký phát triển PyBạn

Tài liệu này ghi lại các quyết định và thay đổi để dùng làm tư liệu báo cáo, thuyết trình và bàn giao.

## Bối cảnh

- **Đề tài:** chatbot hướng dẫn Python cơ bản cho sinh viên mới học.
- **Project tham khảo về tổ chức:** BONESCOPE trong thư mục `MainProject/BONESCOPE`.
- **Project thực hiện:** thư mục `ChatbotAI`.
- **Trạng thái ban đầu:** thư mục ChatbotAI trống, không có mã nguồn để nối tiếp.

## Nhật ký quyết định

| Ngày | Quyết định / thay đổi | Lý do | Ý nghĩa khi báo cáo |
|---|---|---|---|
| 06/11/2026 | Chọn tên làm việc PyBạn và giới hạn 5 chủ đề Python nhập môn | Phạm vi nhỏ, dễ chuẩn bị dữ liệu và trình diễn | Mô tả rõ người dùng, mục tiêu và giới hạn |
| 06/11/2026 | Tổ chức theo frontend web + FastAPI + thư mục `rag/` | Tham khảo cách BONESCOPE tách UI, API, retrieval và generation | Giải thích được các thành phần và luồng xử lý |
| 06/11/2026 | Dùng retrieval từ vựng cục bộ, không bắt buộc mô hình hoặc API key | Dễ khởi chạy, dễ kiểm soát tài liệu và có phương án demo offline | Đây là xử lý ngôn ngữ/truy xuất; không phải tự huấn luyện LLM |
| 06/11/2026 | Thêm LLM tùy chọn qua API tương thích OpenAI và fallback về corpus | Cho phép diễn đạt tự nhiên hơn nhưng giữ được demo khi thiếu API | Báo cáo cần nêu nhà cung cấp/cấu hình chỉ khi thực sự đã dùng |
| 06/11/2026 | Bổ sung tài liệu kiến thức, README, báo cáo nháp, nhật ký, kiểm thử và kịch bản video | Lưu bằng chứng quá trình và giảm việc tổng hợp sát hạn nộp | Dùng làm hồ sơ và kịch bản trình bày |
| 06/11/2026 | Chuyển cấu hình LLM sang OpenRouter (`https://openrouter.ai/api/v1`, `openrouter/free`) và thêm cấu hình F5/debug cho VS Code | Người dùng đã chọn OpenRouter và VS Code | Có thể demo sinh câu trả lời qua API; key được giữ trong `.env` cục bộ |
| 06/11/2026 | Mở rộng chatbot để nhận lời nhờ code bài Python cơ bản; câu hỏi chung sẽ xin đề bài, bài cụ thể sẽ được xử lý theo biến/điều kiện/vòng lặp/hàm | Người dùng muốn chatbot trả lời được lời nhờ giúp code như ảnh minh họa | Ghi lại phạm vi mới, hành vi hỏi làm rõ và cách tạo lời giải trong báo cáo |
| 06/11/2026 | Chuyển sang chatbot hỏi đáp tổng quát, bỏ chặn câu hỏi ngoài chủ đề Python, gửi lịch sử hội thoại gần đây tới OpenRouter và giữ lịch sử trong sessionStorage của tab | Người dùng muốn chatbot hiểu ngữ cảnh cá nhân/câu hỏi nối tiếp như chatbot thông thường | Mô tả rõ luồng đa lượt, giới hạn ngữ cảnh và phần RAG dùng riêng cho câu hỏi Python |

## Kiến trúc hiện tại

**Cập nhật lưu hội thoại (06/11/2026):** thêm `web/conversations.js` quản lý nhiều hội thoại trong localStorage, nhập lịch sử sessionStorage cũ, tự đặt tên theo tin nhắn đầu, chọn lại chat và tạo chat mới tại chỗ. Tin nhắn người dùng được lưu ngay khi gửi; phản hồi AI được gắn với ID chat gốc dù người dùng đã chuyển sang chat khác. Lưu đầy đủ bản hội thoại, chỉ giới hạn phần ngữ cảnh gửi API. Khi lưu trữ bị từ chối hoặc hết dung lượng, giao diện hiện thông báo.

- `web/index.html`, `web/style.css`, `web/app.js`: giao diện hội thoại tiếng Việt.
- `app.py`: FastAPI, xác thực kích thước lịch sử, chọn ngữ cảnh Python cho retrieval và trả kết quả JSON.
- `rag/corpus.jsonl`: 17 mẩu kiến thức có metadata và liên kết tham khảo, gồm thêm toán tử chia lấy dư và cách phân tích bài tập nhập môn.
- `rag/retrieval.py`: chuẩn hóa văn bản, phát hiện chủ đề và xếp hạng BM25 giản lược.
- `rag/generation.py`: tích hợp OpenRouter cho hỏi đáp tổng quát, ngữ cảnh hội thoại và diễn đạt grounded với RAG.
- `setup.bat`, `run.bat`: cài dependency và khởi chạy trên Windows.
- `.env`: cấu hình OpenRouter cục bộ; API key cần được người dùng tự thêm, không lưu trong repository.
- `.vscode/launch.json`, `.vscode/tasks.json`: chạy/debug FastAPI từ VS Code.
- `docs/`: báo cáo sản phẩm, bảng thử nghiệm và kịch bản demo.

## Trạng thái xác minh

**Chẩn đoán OpenRouter (06/11/2026):** cấu hình `.env` thực tế trả HTTP 200 và nội dung với request mẫu; luồng chatbot cho câu “Bạn có thể làm được những gì?” trả `answered/ai`. Chưa biết nguyên nhân request lỗi cũ. Đã phân biệt lỗi xác thực, hạn mức, kết nối, thời gian chờ, dịch vụ và phản hồi trống bằng `GenerationError`, đồng thời bỏ log raw exception. Chín kiểm tra Python dùng API giả lập đạt, gồm cả việc chặn cấu hình trả phí; bốn kiểm tra hội thoại Node đạt. Xem [hồ sơ chẩn đoán](OPENROUTER_TROUBLESHOOTING_VI.md).

**Giao diện ngày 06/11/2026:** viết lại CSS theo khung cố định 100dvh, header và composer ngoài vùng chat cuộn độc lập; sidebar ưu tiên lịch sử, tài liệu Python thu gọn. Đã kiểm tra trực quan bằng trình duyệt trên desktop và mobile với hội thoại giả dài, xác nhận header `top=0` và trang ngoài `scrollTop=0` sau khi cuộn nhiều trang. Bốn kiểm tra tự động lưu hội thoại vẫn đạt. Xem [bằng chứng bố cục](UI_LAYOUT_VI.md).

Kiểm tra tự động cho chức năng lưu hội thoại: `node --test tests/conversations.cjs` đạt **4/4**. Các tình huống gồm lưu/khôi phục nhiều chat, giữ toàn bộ nội dung khi giới hạn ngữ cảnh, nhập phiên cũ và báo lỗi lưu trữ, chuyển chat/tạo chat mới trong lúc có request rồi lưu phản hồi đúng chat gốc. `node --check` đạt cho cả hai file JavaScript. Kiểm tra dùng dữ liệu giả và mô phỏng DOM/fetch, chưa kiểm tra trực quan trên trình duyệt và không gọi OpenRouter.

Các file cấu hình và mã nguồn đã được tạo trong workspace. Chưa chạy cài dependency, chưa khởi động server và chưa ghi nhận kết quả kiểm thử tương tác. Cần cập nhật mục này sau khi người dùng chạy `setup.bat`, `run.bat` và thực hiện các tình huống trong `TEST_CASES_VI.md`.

OpenRouter được cấu hình bằng endpoint `https://openrouter.ai/api/v1` và model router `openrouter/free`. Key giữ cục bộ và không ghi vào tài liệu. Kết nối được xác nhận ở lần chẩn đoán nêu trên; khả năng sử dụng về sau vẫn phụ thuộc model và hạn mức dịch vụ.

## Việc cần hoàn thiện trước khi nộp

1. Chạy ứng dụng trên máy trình diễn, sửa lỗi nếu phát hiện.
2. Chạy ít nhất năm trường hợp và ghi kết quả thực tế vào bảng kiểm thử.
3. Điền tên thành viên, lớp, ngày và phân công vào báo cáo.
4. Đối chiếu nội dung corpus với nguồn tài liệu và tài liệu môn học.
5. Quay video 2–3 phút theo kịch bản, thay các placeholder bằng ảnh/chụp màn hình thực.
6. Ghi rõ có dùng LLM/API hay chỉ dùng retrieval trong lần demo và báo cáo.

# Chẩn đoán OpenRouter

## Kết quả ngày 06/11/2026

Ảnh Activity của người dùng hiển thị `Tokens (Total) by API Key`, key Chatbot có khoảng 7,99 nghìn token và `100% of Total`. Đây là tỷ trọng token của key trong khoảng thời gian đã chọn, không phải phần trăm hạn mức đã dùng.

Đã kiểm tra trực tiếp bằng cấu hình `.env`: request mẫu trả HTTP 200, model được router chọn là `google/gemma-4-31b-it:free`, có nội dung phản hồi. Luồng `app.chat` với câu “Bạn có thể làm được những gì?” trả `status=answered`, `mode=ai`. Kết quả cho thấy cấu hình/key sử dụng được ở thời điểm kiểm tra; chưa xác định được nguyên nhân của request lỗi trước ảnh chụp. Không có API key hoặc nội dung hội thoại thật được ghi vào tài liệu.

Request đầu tiên trong môi trường công cụ bị hạn chế mạng gặp WinError 10013. Kiểm tra lại bằng quyền mạng được phê duyệt đã thành công; lỗi hạn chế đó không chứng minh mạng ứng dụng VS Code của người dùng bị chặn.

## Thay đổi để lỗi rõ hơn

Trước đây `draft()` trả None cho mọi lỗi, bao gồm phản hồi trống, dẫn tới thông báo chung “chưa kết nối”. Bây giờ backend trả mã lỗi an toàn và hướng dẫn tương ứng, không đưa raw response, header hoặc key ra log/giao diện.

| Mã | Ý nghĩa thông báo |
|---|---|
| authentication / 401 | Key không được chấp nhận |
| credits / 402 | Số dư hoặc hạn mức chi tiêu |
| permission / 403 | Bị từ chối quyền truy cập |
| model_unavailable / 404 | Model không khả dụng |
| rate_limit / 429 | Bị giới hạn lượt gọi |
| connection | Lỗi kết nối mạng/HTTPS tới dịch vụ |
| timeout | Vượt thời gian chờ |
| provider_unavailable / 5xx | Dịch vụ/model lỗi |
| empty_response / output_limit | Request hoàn tất nhưng chưa có nội dung trả lời hoặc hết ngân sách đầu ra |

Tham khảo [Chat Completions API của OpenRouter](https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request?explorer=true) và [mô hình miễn phí](https://openrouter.ai/collections/free-models/).

## Cách kiểm tra tại VS Code

Dừng server và chạy lại F5 sau khi cập nhật code hoặc `.env`. Gửi một tin nhắn mới; các thông báo lỗi cũ đã lưu trong lịch sử sẽ không thay đổi.

Có thể chạy một request mẫu độc lập trong terminal:

```powershell
.\.venv\Scripts\python.exe tools\check_openrouter.py
```

Lệnh gửi “Reply with OK.” tới model trong `.env`, in trạng thái HTTP và chi tiết lỗi đã che key. Nó không gửi hội thoại cũ.

## Kiểm tra tự động

`python -m unittest discover -s tests -p test_generation_errors.py -v`: 9/9 đạt với API giả lập, gồm phân loại HTTP, thiếu cấu hình, phản hồi trống/hết token, giữ ngữ cảnh, không ghi bí mật trong log và chặn model trả phí/endpoint ngoài trước khi kết nối. Bộ lưu hội thoại Node vẫn đạt 4/4. Các kết quả không xác nhận mọi model miễn phí sẽ luôn sẵn sàng.

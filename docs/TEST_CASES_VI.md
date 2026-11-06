# Bảng tình huống kiểm thử PyBạn

> Chạy từng câu hỏi qua giao diện hoặc `POST /api/chat`. Cột “Kết quả thực tế” đang để chờ kiểm thử trên máy; không sao chép kết quả mong đợi vào cột này nếu chưa chạy.

| # | Loại tình huống | Đầu vào | Kết quả mong đợi | Kết quả thực tế | Nhận xét |
|---|---|---|---|---|---|
| 1 | Bình thường — vòng lặp | `Vòng lặp for dùng để làm gì?` | Giải thích for duyệt phần tử/dãy, kèm ví dụ hoặc tài liệu liên quan và nguồn. | Chưa chạy | Điền sau khi chạy. |
| 2 | Bình thường — hàm | `Hàm trong Python khai báo và gọi như thế nào?` | Nêu `def`, dấu `:`, thụt lề, cách gọi hàm; dẫn tài liệu hàm. | Chưa chạy | Điền sau khi chạy. |
| 3 | Bình thường — kiểu dữ liệu | `input() trả về kiểu dữ liệu gì?` | Nêu `input()` trả về `str`, cần ép kiểu khi tính số. | Chưa chạy | Điền sau khi chạy. |
| 4 | Thiếu thông tin | `Code của em bị lỗi` | Hỏi thêm thông báo lỗi hoặc đoạn mã liên quan, không tự đoán nguyên nhân. | Chưa chạy | Điền sau khi chạy. |
| 5 | Mơ hồ | `Hàm?` | Hỏi người dùng cần biết cách định nghĩa, truyền tham số hay dùng `return`. | Chưa chạy | Điền sau khi chạy. |
| 6 | Hỏi đáp tổng quát | `Vì sao bầu trời có màu xanh?` | Trả lời trực tiếp, dễ hiểu bằng tiếng Việt; không báo ngoài phạm vi Python. | Chưa chạy | Kiểm tra chế độ OpenRouter tổng quát. |
| 7 | Tài liệu chưa đủ / thuật ngữ lỗi | `NameError xuất hiện khi nào?` | Giải thích nguyên nhân thường gặp và cách kiểm tra tên biến, có nguồn. | Chưa chạy | Điền sau khi chạy. |
| 8 | Lỗi công cụ AI (OpenRouter) | Cấu hình sai endpoint hoặc ngắt kết nối, sau đó hỏi `Hàm trong Python khai báo và gọi như thế nào?` | Ứng dụng vẫn trả lời bằng retrieval cục bộ; lỗi chi tiết xuất hiện ở terminal VS Code, không hiện API key trong giao diện. | Chưa chạy | Chỉ thực hiện nếu đã bật API; không chụp key/headers. |
| 9 | Nhờ hỗ trợ nhưng chưa gửi đề | `Bạn có thể giúp tôi code một bài toán không?` | Chatbot xác nhận có thể giúp và hỏi đề bài, đầu vào/đầu ra, ràng buộc hoặc ví dụ; không báo ngoài phạm vi. | Chưa chạy | Tình huống từ yêu cầu người dùng. |
| 10 | Bài tập nhập môn cụ thể | `Giúp em viết chương trình nhập một số nguyên n rồi kiểm tra n chẵn hay lẻ.` | Chatbot nêu ý tưởng dùng `%` và `if/else`, đưa code Python ngắn chạy được, giải thích và ví dụ; kèm nguồn đã truy xuất. | Chưa chạy | Cần OpenRouter hoạt động để nhận code sinh; nếu không thì ghi rõ chế độ fallback. |
| 11 | Hiểu ngữ cảnh nhiều lượt | Lượt 1: `Tôi đang học Python list. List là gì?` Lượt 2: `Cho ví dụ tạo một cái gồm ba tên.` | Ở lượt 2, chatbot hiểu “một cái” là Python list, đưa ví dụ list gồm ba tên và không hỏi lại chủ đề. | Chưa chạy | Giữ cùng tab; có thể tải lại tab để kiểm tra khôi phục lịch sử phiên. |
| 12 | Không biết thông tin cá nhân chưa được cung cấp | `Tên đầy đủ của tôi là gì?` khi chưa từng nói tên trong hội thoại | Chatbot nói chưa biết thay vì tự đoán; có thể hỏi người dùng muốn cung cấp tên không. | Chưa chạy | Kiểm tra khả năng thừa nhận thiếu ngữ cảnh. |
| 13 | Câu nối tiếp theo ví dụ người dùng | Lượt 1: `Code giúp mình 1 bài toán.` Lượt 2: `Code giúp mình bài toán số đối xứng.` Lượt 3: `Tìm số nguyên.` | Lượt 1 hỏi đề bài; các lượt sau hiểu đang nói về số nguyên đối xứng, hỏi thêm khoảng cần tìm nếu chưa được cung cấp, không báo ngoài phạm vi. | Chưa chạy | Giữ nguyên cùng hội thoại để kiểm tra lịch sử được gửi tới mô hình. |

## Cách ghi kết quả

Các ca kiểm tra chức năng lưu hội thoại được thực thi bằng `node --test tests/conversations.cjs`: **4/4 đạt** với dữ liệu giả (khôi phục nhiều chat; giới hạn ngữ cảnh không cắt lịch sử; nhập phiên cũ và xử lý lỗi lưu trữ; phản hồi đang chờ được lưu đúng chat khi đổi hội thoại). Cần kiểm tra trực quan thêm: gửi tin nhắn → tạo chat mới → mở lại chat cũ → đóng/mở lại trang, rồi kiểm tra cả màn hình nhỏ bằng hộp chọn hội thoại.

1. Chạy `run.bat`, mở `http://127.0.0.1:8765/`.
2. Gửi nguyên văn từng đầu vào; giữ lại ảnh chụp màn hình nếu cần làm minh chứng.
3. Ghi câu trả lời thực tế ngắn gọn hoặc mô tả hành vi quan sát được; đánh giá đúng một phần/đúng/chưa đạt.
4. Nếu câu trả lời lệch kỳ vọng, ghi nguyên nhân và sửa corpus, ngưỡng truy xuất hoặc xử lý câu hỏi; chạy lại và lưu kết quả mới.
5. Không ghi rằng LLM đã được sử dụng nếu lần chạy kiểm thử không có cấu hình LLM.

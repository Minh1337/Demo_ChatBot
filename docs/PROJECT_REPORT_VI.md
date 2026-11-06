# Báo cáo sản phẩm: PyBạn — chatbot hỏi đáp tiếng Việt

> Bản nháp báo cáo 3–5 trang. Thay các trường trong ngoặc vuông, cập nhật bảng kết quả sau khi chạy ứng dụng và kiểm thử trên máy nộp bài.

## 1. Thông tin sản phẩm

- **Tên:** PyBạn — chatbot hỏi đáp tiếng Việt
- **Thành viên:** [Họ tên, lớp/mã sinh viên của từng thành viên]
- **Phiên bản:** 0.2.0
- **Ngày cập nhật báo cáo:** [ngày/tháng/năm]

## 2. Bài toán và người dùng

PyBạn hướng tới người dùng cần hỏi đáp bằng tiếng Việt qua hội thoại nhiều lượt. Chatbot trả lời các chủ đề thông thường bằng OpenRouter và dùng những lượt trước trong cùng cuộc trò chuyện để hiểu câu hỏi nối tiếp. Trọng tâm minh họa của sản phẩm là hỗ trợ học Python: tra cứu tài liệu có nguồn, giải thích lỗi và hướng dẫn bài tập nhập môn. Chatbot chỉ biết thông tin cá nhân người dùng đã chia sẻ trong ngữ cảnh được gửi; đây không phải bộ nhớ hồ sơ lâu dài và hội thoại không được lưu phía máy chủ.

Phần kiến thức có tài liệu nguồn được giới hạn ở các nhóm: (1) biến, kiểu dữ liệu và nhập/xuất cơ bản, (2) điều kiện `if/elif/else` và toán tử số học, (3) vòng lặp `for`, `while`, (4) hàm, tham số và `return`, (5) một số lỗi phổ biến, và (6) bài tập nhập môn. Câu hỏi ngoài các nhóm này vẫn có thể được OpenRouter trả lời theo kiến thức mô hình, nhưng không có trích dẫn từ corpus của dự án.

## 3. Chức năng chính

Người dùng nhập câu hỏi vào giao diện web hoặc chọn gợi ý. Các hội thoại được lưu đầy đủ trong `localStorage`, có tên lấy từ tin nhắn đầu tiên và có thể mở lại từ danh sách lịch sử. Nút “Trò chuyện mới” tạo hội thoại riêng mà không tải lại trang. Với mỗi lượt mới, trình duyệt chỉ gửi tối đa 20 tin nhắn gần đây, giới hạn 12.000 ký tự của đúng hội thoại đang dùng lên backend; lịch sử hiển thị không bị cắt. Backend chuyển câu hỏi và lịch sử hợp lệ tới OpenRouter. Với các chủ đề Python được nhận diện, backend kèm đoạn tài liệu phù hợp; với các chủ đề khác, mô hình trả lời trực tiếp.

Giao diện hiển thị hội thoại, câu hỏi gợi ý, nguồn trích dẫn, trạng thái hoạt động, nút làm mới và bố cục thích ứng màn hình nhỏ. Ứng dụng chạy cục bộ tại `127.0.0.1`; không yêu cầu triển khai lên Internet.

## 4. Dữ liệu và tài liệu

Bộ kiến thức ở `rag/corpus.jsonl` gồm 17 đoạn do nhóm biên soạn/tóm lược cho người mới học, bao gồm hướng dẫn phân tích bài toán, nhập/xuất, vòng lặp, điều kiện và phép chia lấy dư. Mỗi đoạn có mã định danh, chủ đề, tiêu đề, đường dẫn nguồn, mục tài liệu và nội dung. Các chủ đề trong corpus phản ánh phạm vi sản phẩm; có thể mở rộng bằng tài liệu học phần sau khi kiểm tra quyền sử dụng và độ chính xác.

Nguồn tham khảo chính là tài liệu chính thức của Python Software Foundation:

- [Python Tutorial: An Informal Introduction](https://docs.python.org/3/tutorial/introduction.html)
- [Python Tutorial: More Control Flow Tools](https://docs.python.org/3/tutorial/controlflow.html)
- [Built-in Types](https://docs.python.org/3/library/stdtypes.html)
- [Built-in Functions](https://docs.python.org/3/library/functions.html)
- [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
- [Compound statements reference](https://docs.python.org/3/reference/compound_stmts.html)

Đây là các liên kết tham khảo gắn với từng mục trong corpus. Nhóm cần đọc và đối chiếu lại nội dung nguồn khi cập nhật tài liệu.

## 5. Quy trình và công cụ AI

Ứng dụng dùng Python, FastAPI và giao diện HTML/CSS/JavaScript. `rag/retrieval.py` chuẩn hóa tiếng Việt bằng cách bỏ dấu để so khớp, thay một số từ đồng nghĩa tiếng Anh và xếp hạng đoạn bằng công thức BM25 giản lược trên corpus Python.

`rag/generation.py` gửi câu hỏi, tối đa 20 tin nhắn lịch sử và (khi liên quan Python) các đoạn tài liệu tới OpenRouter qua OpenAI SDK. Cấu hình mặc định dùng endpoint `https://openrouter.ai/api/v1` và model router `openrouter/free`; model miễn phí có thể thay đổi hoặc bị giới hạn lượt gọi. Prompt yêu cầu mô hình dùng lịch sử để giải quyết tham chiếu và câu hỏi nối tiếp. Không đưa API key vào mã nguồn hoặc hồ sơ nộp.

Luồng xử lý:

```text
Câu hỏi mới + lịch sử gần đây → OpenRouter
              ├─ câu hỏi Python → truy xuất corpus → câu trả lời + nguồn
              └─ chủ đề khác → câu trả lời tổng quát
Lời nhờ code thiếu đề → hỏi thông tin cần thiết
```

## 6. Kết quả thử nghiệm và hạn chế

Điền kết quả chạy thực tế vào [bảng kiểm thử](TEST_CASES_VI.md). Chưa ghi nhận số liệu đạt/không đạt trong bản nháp này. Sau khi kiểm thử, báo cáo cần nêu máy/môi trường chạy, cấu hình AI (nếu dùng), kết quả mong đợi và thực tế, cùng các lỗi cần sửa.

Hạn chế chính: corpus chỉ bao phủ Python cơ bản; phương pháp khớp từ vựng có thể không tìm đúng đoạn khi diễn đạt khác biệt; ngữ cảnh được giới hạn ở 20 tin nhắn gần đây và không đồng bộ giữa các tab; câu trả lời tổng quát phụ thuộc OpenRouter. Câu trả lời do LLM tạo vẫn có thể sai hoặc thiếu nên người dùng cần kiểm tra thông tin và tự chạy mã.

## 7. Hướng mở rộng

Có thể bổ sung tài liệu học phần được phép sử dụng, thêm bộ câu hỏi đánh giá có nhãn, cải thiện tìm kiếm bằng embedding tiếng Việt và thêm bài tập tương tác. Mỗi thay đổi cần được đánh giá với câu hỏi tổng quát, câu nối tiếp cần ngữ cảnh, câu mơ hồ, yêu cầu code thiếu đề và câu Python có nguồn.

## 8. Phân công và thành phần kế thừa

- **[Thành viên 1]:** [giao diện / nội dung / kiểm thử]
- **[Thành viên 2]:** [backend / truy xuất / tích hợp API]
- **[Thành viên 3]:** [báo cáo / video / kiểm thử]
- **Thành phần tự xây dựng:** mã nguồn ứng dụng, corpus tóm lược, giao diện và chính sách phạm vi.
- **Thành phần bên thứ ba:** FastAPI, Uvicorn, python-dotenv, OpenAI Python SDK (chỉ dùng nếu cấu hình LLM); tài liệu tham khảo chính thức Python.org.

## 9. Hướng dẫn cài đặt và khởi chạy

Thực hiện theo mục “Chạy trên Windows” trong [README](../README.md). Máy cần Python 3.10 trở lên; trình duyệt truy cập `http://127.0.0.1:8765/`. Chế độ hỏi đáp tổng quát cần cấu hình OpenRouter trong `.env`; nếu API không khả dụng, câu hỏi Python có thể dùng nội dung corpus làm phương án dự phòng.

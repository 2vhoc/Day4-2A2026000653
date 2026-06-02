# Quy tắc chấm điểm (Rubric)

## Trình chấm điểm sẽ kiểm tra những gì

Trình chấm điểm kết hợp việc kiểm tra hành vi xác định (deterministic behavior) với giám khảo LLM (LLM judge).

Nó sẽ đánh giá:

- tính chính xác của file JSON được lưu
- tính chính xác khi sử dụng các công cụ
- chất lượng câu trả lời cuối cùng

## Các trường hợp lưu đơn hàng (Save Cases)

Đối với các trường hợp tạo đơn hàng thông thường, trình chấm điểm kiểm tra:

- đối tượng `saved_order` được trả về
- tệp được lưu trong thư mục `artifacts/orders/`
- nội dung JSON so với thư mục `data/expected_orders/`
- trình tự công cụ bắt buộc
- câu trả lời cuối cùng dựa trên rubric

Trọng số thông thường:

- `json_output`: 70
- `tools`: 20
- `llm_judge`: 10

Trường `created_at` bị bỏ qua khi so sánh JSON.

## Các trường hợp không lưu đơn hàng (Non-Save Cases)

Đối với các trường hợp yêu cầu làm rõ, từ chối và lỗi do hết hàng, trình chấm điểm kiểm tra:

- không có đơn hàng nào được lưu
- lịch sử công cụ (tool trace) khớp với hành vi dự kiến
- câu trả lời cuối cùng phù hợp với rubric của từng trường hợp

Trọng số thông thường:

- `json_output`: 55
- `tools`: 25
- `llm_judge`: 20

## Kỳ vọng đối với công cụ (Tool Expectations)

Với các đơn hàng hợp lệ, quy trình công cụ dự kiến là:

1. `list_products`
2. `get_product_details`
3. `get_discount`
4. `calculate_order_totals`
5. `save_order`

Với các trường hợp làm rõ và từ chối, công cụ dự kiến sử dụng thường là không dùng công cụ nào.

## Học viên bị trừ điểm trong trường hợp nào

- prompt (câu lệnh) quá mơ hồ, dẫn đến việc model hành động quá sớm
- lược đồ công cụ (tool schema) quá lỏng lẻo, dẫn đến việc thiếu hoặc sai tham số
- rào chắn bảo vệ (guardrails) yếu, dẫn đến việc model chấp nhận các yêu cầu không hợp lệ
- việc căn cứ vào dữ liệu (grounding) kém, dẫn đến JSON được lưu bị sai
- câu trả lời làm rõ/từ chối có chất lượng thấp, dẫn đến việc giám khảo LLM trừ điểm

## Diễn giải điểm số

- `90-100`: kiểm soát tốt hành vi
- `80-89`: đa phần chính xác, gặp một số lỗi nhỏ về chất lượng trả lời hoặc quy trình làm việc
- `65-79`: kiểm soát được một phần, nhưng vẫn còn quá lỏng lẻo
- `0-64`: thiết kế prompt/lược đồ công cụ/rào chắn quá yếu

## Lưu ý quan trọng

Bài thực hành này không chỉ nói về logic nghiệp vụ (business logic). Điểm thấp thường xuất phát từ kỹ năng viết prompt yếu (weak prompt engineering):

- hướng dẫn không rõ ràng
- mô tả công cụ không đầy đủ (underspecified tools)
- quy trình xác thực không tốt
- quy tắc từ chối yếu

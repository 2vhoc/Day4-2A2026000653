# Hướng dẫn

## 1. Bắt đầu với giải pháp cơ bản (Baseline)

Chạy giải pháp cơ bản yếu (weak baseline) trước tiên:

```bash
python grade/scoring.py --module simple_solution.agent.graph --provider google
```

Bạn sẽ nhận được điểm xuất phát. Nhiệm vụ của bạn là cải thiện thư mục `src/` và đạt điểm cao hơn.

## 2. Hiểu yêu cầu bài toán

Agent cần xử lý 4 hành vi sau:

- tạo đơn hàng hợp lệ
- làm rõ thông tin khi thiếu dữ liệu khách hàng
- từ chối khi yêu cầu vi phạm chính sách
- xác nhận chính xác dựa trên dữ liệu (grounded confirmation) sau khi lưu thành công

Đối với một đơn hàng hợp lệ, luồng công cụ (tool) dự kiến là:

1. `list_products`
2. `get_product_details`
3. `get_discount`
4. `calculate_order_totals`
5. `save_order`

## 3. Nơi làm việc

Tập trung vào:

- `src/agent/graph.py`
- `src/utils/data_store.py`

Tài liệu tham khảo hữu ích:

- `data/graded_cases.json`
- `data/expected_orders/`
- `simple_solution/`

## 4. Cần cải thiện những gì

### Prompt (Câu lệnh)

System prompt (câu lệnh hệ thống) của bạn cần phải làm rõ các quy tắc sau:

- trả lời bằng tiếng Việt
- không bịa đặt thông tin sản phẩm, mã giảm giá, tổng tiền hoặc đường dẫn file
- yêu cầu các trường thông tin khách hàng còn thiếu trước khi gọi bất kỳ công cụ nào
- từ chối các yêu cầu không an toàn mà không gọi công cụ
- tuân thủ thứ tự công cụ dự kiến
- chỉ lưu sau khi xác thực thành công

### Lược đồ công cụ (Tool Schema)

Một lược đồ công cụ tốt sẽ giảm thiểu sai sót của agent. Ưu tiên:

- tên công cụ rõ ràng
- docstrings (chuỗi tài liệu) rõ ràng
- quy định rõ các tham số bắt buộc (explicit required arguments)
- đầu vào có cấu trúc phù hợp với quy trình làm việc

### Rào chắn bảo vệ (Guardrails)

Agent phải từ chối các yêu cầu muốn:

- bỏ qua kiểm tra số lượng tồn kho (stock)
- ép buộc áp dụng mã giảm giá giả mạo
- tạo hóa đơn giả mạo
- phớt lờ danh mục sản phẩm hoặc chính sách

### Làm rõ thông tin (Clarification)

Trước khi dùng công cụ, agent cần có:

- tên khách hàng
- số điện thoại
- email
- địa chỉ giao hàng
- ít nhất một mặt hàng và số lượng

Nếu thiếu bất kỳ thông tin nào, nó phải hỏi lại và dừng lại.

## 5. Cách gỡ lỗi (Debug)

Khi một trường hợp bị lỗi (fails), hãy kiểm tra:

- lịch sử sử dụng công cụ (tool trace): model đã gọi các công cụ quá sớm hay sai thứ tự?
- JSON đã lưu: nó lưu sai payload (dữ liệu tải trọng) hay lưu khi không nên lưu?
- câu trả lời cuối cùng: việc làm rõ thông tin, từ chối hay xác nhận có chính xác dựa trên dữ liệu (grounded) và súc tích không?

## 6. Vòng lặp cải tiến

Sử dụng vòng lặp này:

1. chạy `simple_solution`
2. chạy `src`
3. kiểm tra các trường hợp bị lỗi
4. thắt chặt prompt (làm rõ và nghiêm ngặt hơn)
5. thắt chặt lược đồ công cụ (tool schema)
6. chạy lại trình chấm điểm (grader)

Chạy bản triển khai của bạn với:

```bash
python grade/scoring.py --module src.agent.graph --provider google
```

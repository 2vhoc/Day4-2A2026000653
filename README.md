# Bài thực hành Prompt Engineering OrderDesk

Xây dựng một agent quản lý đơn hàng bằng LLM cho một cửa hàng bán lẻ đồ điện tử và cải thiện điểm số của nó thông qua prompt engineering.

Trong bài thực hành này, agent phải:

- hiểu các yêu cầu đặt hàng bằng tiếng Việt và đa ngôn ngữ (mixed-language)
- sử dụng các công cụ (tools) theo đúng thứ tự
- yêu cầu cung cấp thông tin còn thiếu trước khi hành động
- từ chối các yêu cầu không an toàn hoặc vi phạm chính sách
- lưu đơn hàng cuối cùng dưới dạng JSON chính xác dựa trên dữ liệu (grounded JSON)

Mục tiêu chính không chỉ là làm cho mã code chạy được. Mục tiêu là cải thiện hành vi của agent bằng cách thắt chặt prompt, lược đồ công cụ (tool schema) và rào chắn (guardrails).

## Bạn sẽ thực hành những gì

- viết system prompt (câu lệnh hệ thống) mạnh mẽ hơn
- thiết kế lược đồ công cụ rõ ràng hơn
- bắt buộc làm rõ thông tin trước khi sử dụng công cụ
- thêm các rào chắn (guardrails) cho các yêu cầu không an toàn
- căn cứ (grounding) câu trả lời cuối cùng vào kết quả của công cụ
- gỡ lỗi (debug) từ lịch sử sử dụng công cụ và các tệp kết quả đã lưu

## Sơ đồ Repository (Kho lưu trữ)

- `src/`: bản triển khai của bạn
- `simple_solution/`: giải pháp cơ bản yếu (weak baseline)
- `data/products.json`: danh mục sản phẩm
- `data/graded_cases.json`: các kịch bản dùng để chấm điểm
- `data/expected_orders/`: cấu trúc JSON dự kiến cho các trường hợp lưu đơn hàng
- `grade/scoring.py`: trình chấm điểm (grader)
- `guide.md`: quy trình làm việc từng bước
- `rubric.md`: quy tắc chấm điểm

## Quy trình làm việc được đề xuất

1. Chạy giải pháp cơ bản yếu trước tiên.
2. Ghi lại điểm số của nó.
3. Cải thiện thư mục `src/`.
4. Chạy trình chấm điểm với `src/`.
5. Lặp lại cho đến khi điểm số của bạn vượt qua giải pháp cơ bản một cách rõ rệt.

## Cài đặt (Setup)

Tạo một file `.env`:

```bash
GOOGLE_API_KEY=...
LLM_MODEL=gemini-2.5-flash
```

Tùy chọn mô hình local (chạy trên máy cá nhân):

```bash
OLLAMA_MODEL=qwen3.5:3b
OLLAMA_BASE_URL=http://localhost:11434
```

## Các câu lệnh (Commands)

Chạy giải pháp cơ bản yếu:

```bash
python grade/scoring.py --module simple_solution.agent.graph --provider google
```

Chạy bản triển khai của bạn:

```bash
python grade/scoring.py --module src.agent.graph --provider google
```

Chạy unit tests (kiểm thử):

```bash
pytest -q
```

## Một bài làm tốt sẽ đạt được những gì

- làm rõ thông tin trước khi sử dụng công cụ nếu thiếu các trường thông tin bắt buộc
- từ chối các yêu cầu không hợp lệ mà không gọi các công cụ
- tuân thủ đúng trình tự công cụ dự kiến với các đơn hàng hợp lệ
- lưu kết quả tệp JSON chính xác
- đưa ra câu trả lời cuối cùng bằng tiếng Việt ngắn gọn, súc tích và dựa trên dữ liệu (grounded answer)

Hãy đọc [guide.md](/Users/duongnh59.al1/Documents/Project/Vin20K/Cohort2/Day-4-Lab/labs_update/guide.md) trước khi chỉnh sửa trong thư mục `src/`.


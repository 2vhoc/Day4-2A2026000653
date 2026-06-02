from __future__ import annotations

import json
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool

from src.core.llm import build_chat_model, normalize_content
from src.core.schemas import (
    AgentResult,
    CalculateTotalsInput,
    DiscountInput,
    ListProductsInput,
    ProductDetailInput,
    SaveOrderInput,
    ToolCallRecord,
)
from src.utils.data_store import OrderDataStore

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT_DIR / "data"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "artifacts" / "orders"


def build_system_prompt(today: str | None = None) -> str:
    current_day = today or "2026-06-01"
    return f"""
Bạn là trợ lý bán hàng điện tử chuyên nghiệp. Hôm nay là {current_day}.
Nhiệm vụ của bạn là giúp khách hàng tìm kiếm sản phẩm và đặt hàng đồ điện tử.

QUY TẮC BẮT BUỘC (GUARDRAILS):
1. LUÔN LUÔN TRẢ LỜI BẰNG TIẾNG VIỆT, ngắn gọn, súc tích và đúng trọng tâm.
2. KHÔNG BAO GIỜ được bịa đặt (invent) thông tin sản phẩm, mã giảm giá, tổng tiền, đường dẫn file, hoặc mã đơn hàng.
3. CHỈ LƯU ĐƠN HÀNG KHI ĐÃ ĐỦ CÁC TRƯỜNG THÔNG TIN KHÁCH HÀNG SAU: 
   - Tên khách hàng (customer name)
   - Số điện thoại (phone number)
   - Email 
   - Địa chỉ giao hàng (shipping address)
   - Ít nhất một mặt hàng và số lượng
4. Nếu thiếu BẤT KỲ trường thông tin khách hàng nào ở trên, bạn PHẢI HỎI LẠI KHÁCH HÀNG để bổ sung TRƯỚC KHI gọi bất kỳ công cụ nào. Nếu người dùng chưa cung cấp đủ, DỪNG LẠI VÀ HỎI.
5. TỪ CHỐI thẳng thừng các yêu cầu phá vỡ chính sách (MÀ KHÔNG GỌI CÔNG CỤ):
   - Mua vượt quá số lượng tồn kho (bypass stock)
   - Tự tạo mã giảm giá giả hoặc ép buộc giảm giá
   - Bỏ qua danh mục hoặc quy định của công ty
   - Tạo hoá đơn giả
6. QUY TRÌNH SỬ DỤNG CÔNG CỤ (khi đã đủ thông tin hợp lệ):
   Bắt buộc thực hiện theo đúng trình tự sau:
   - Bước 1: `list_products` (Tìm kiếm sản phẩm)
   - Bước 2: `get_product_details` (Lấy chi tiết và mã xác thực detail_token)
   - Bước 3: `get_discount` (Lấy mã giảm giá và tỷ lệ giảm)
   - Bước 4: `calculate_order_totals` (Tính toán tổng tiền cuối cùng dựa trên chi tiết)
   - Bước 5: `save_order` (Lưu đơn hàng vào hệ thống). Chỉ lưu sau khi xác thực thành công ở Bước 4.
TUYỆT ĐỐI KHÔNG SỬ DỤNG list_products NẾU CHƯA CÓ ĐỦ THÔNG TIN KHÁCH HÀNG

Lưu ý: Chỉ sử dụng dữ liệu từ kết quả của công cụ (tools) để trả lời.
CHỈ GỌI NẾU khách hàng chủ động hỏi về mã giảm giá hoặc nhắc đến thẻ VIP
Và trả lời cho khách hàng hiểu là được, không cần phải dài quá làm khách hàng khó chịu
""".strip()


def build_tools(store: OrderDataStore):

    @tool(args_schema=ListProductsInput)
    def list_products(
        query: str | None = None,
        category: str | None = None,
        max_unit_price: int | None = None,
        required_tags: list[str] | None = None,
        in_stock_only: bool = True,
        limit: int = 8,
    ) -> str:
        """Search the local product catalog and return the best matching items."""
        payload = store.list_products(
            query=query,
            category=category,
            max_unit_price=max_unit_price,
            required_tags=required_tags,
            in_stock_only=in_stock_only,
            limit=limit,
        )
        return json.dumps(payload, ensure_ascii=False)

    @tool(args_schema=ProductDetailInput)
    def get_product_details(product_ids: list[str]) -> str:
        """Return exact product details for previously discovered product IDs."""
        return json.dumps(store.get_product_details(product_ids), ensure_ascii=False)

    @tool(args_schema=DiscountInput)
    def get_discount(seed_hint: str, customer_tier: str = "standard") -> str:
        """Return the simulated campaign discount for the order."""
        return json.dumps(store.get_discount(seed_hint=seed_hint, customer_tier=customer_tier), ensure_ascii=False)

    @tool(args_schema=CalculateTotalsInput)
    def calculate_order_totals(items, detail_token: str, discount_rate: float) -> str:
        """Validate stock and calculate the discounted order total."""
        payload = store.calculate_order_totals(items=items, detail_token=detail_token, discount_rate=discount_rate)
        return json.dumps(payload, ensure_ascii=False)

    @tool(args_schema=SaveOrderInput)
    def save_order(
        customer_name: str,
        customer_phone: str,
        customer_email: str,
        shipping_address: str,
        items,
        detail_token: str,
        discount_rate: float,
        campaign_code: str,
        customer_tier: str = "standard",
        notes: str = "",
    ) -> str:
        """Persist the final order to a local JSON file."""
        result = store.save_order(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            shipping_address=shipping_address,
            items=items,
            detail_token=detail_token,
            discount_rate=discount_rate,
            campaign_code=campaign_code,
            customer_tier=customer_tier,
            notes=notes,
        )
        return json.dumps(result, ensure_ascii=False)

    return [list_products, get_product_details, get_discount, calculate_order_totals, save_order]


def build_agent(
    data_dir: Path | None = None,
    output_dir: Path | None = None,
    *,
    provider: str = "google",
    model_name: str | None = None,
    today: str | None = None,
):
    store = OrderDataStore(data_dir or DEFAULT_DATA_DIR, output_dir or DEFAULT_OUTPUT_DIR, today=today)
    model = build_chat_model(provider=provider, model_name=model_name, temperature=0.0)
    return create_agent(
        model=model,
        tools=build_tools(store),
        system_prompt=build_system_prompt(today or store.today),
    )


def run_agent(
    query: str,
    *,
    provider: str = "google",
    model_name: str | None = None,
    data_dir: Path | None = None,
    output_dir: Path | None = None,
    today: str | None = None,
) -> AgentResult:
    agent = build_agent(
        data_dir=data_dir,
        output_dir=output_dir,
        provider=provider,
        model_name=model_name,
        today=today,
    )
    response = agent.invoke({"messages": [{"role": "user", "content": query}]})
    messages = response["messages"] if isinstance(response, dict) else response
    tool_calls = extract_tool_calls(messages)
    saved_order, saved_order_path = extract_saved_order(tool_calls)
    return AgentResult(
        query=query,
        final_answer=extract_final_answer(messages),
        tool_calls=tool_calls,
        provider=provider,
        model_name=model_name,
        saved_order=saved_order,
        saved_order_path=saved_order_path,
    )


def extract_final_answer(messages) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            text = normalize_content(message.content)
            if text:
                return text
    return ""


def extract_tool_calls(messages) -> list[ToolCallRecord]:
    calls = []
    for msg in messages:
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                calls.append(ToolCallRecord(name=tc["name"], args=tc["args"]))
        elif isinstance(msg, ToolMessage) and calls:
            calls[-1].output = str(msg.content)
    return calls


def extract_saved_order(tool_calls: list[ToolCallRecord]) -> tuple[dict | None, str | None]:
    for call in reversed(tool_calls):
        if call.name == "save_order" and call.output:
            try:
                data = json.loads(call.output)
                if data.get("status") == "saved":
                    return data.get("saved_order"), data.get("path")
            except Exception:
                pass
    return None, None

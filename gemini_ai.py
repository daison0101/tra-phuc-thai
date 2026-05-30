import google.generativeai as genai
import json
import re
import os

# =========================
# GEMINI API KEY (FIX)
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "temperature": 0.2,
        "top_p": 0.9,
        "response_mime_type": "application/json"
    }
)

# =========================
# SAFE JSON PARSER
# =========================
def safe_json_load(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
    return None


# =========================
# MAIN AI FUNCTION
# =========================
def recommend_with_gemini(user_input, products):

    product_text = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description or "",
            "short_description": getattr(p, "short_description", "") or ""
        }
        for p in products
    ]

    # =========================
    # PROMPT VIP (KHÓA NGÔN NGỮ + JSON)
    # =========================
    prompt = f"""
Bạn là AI tư vấn sức khỏe và bán hàng chuyên nghiệp tại Việt Nam.

QUY TẮC BẮT BUỘC:
- CHỈ trả lời tiếng Việt 100%
- KHÔNG dùng tiếng Anh
- KHÔNG markdown
- KHÔNG giải thích ngoài JSON
- CHỈ chọn sản phẩm có trong danh sách
- KHÔNG bịa sản phẩm mới

NHIỆM VỤ:
- Phân tích vấn đề người dùng
- Gợi ý tối đa 5 sản phẩm phù hợp
- Giải thích lý do theo triệu chứng
- Đưa ra cách dùng và thời điểm uống

DANH SÁCH SẢN PHẨM:
{json.dumps(product_text, ensure_ascii=False)}

NGƯỜI DÙNG:
{user_input}

TRẢ VỀ JSON CHUẨN:

{{
  "user_problem": "string",
  "summary": "string (tiếng Việt)",
  "recommendations": [
    {{
      "id": 0,
      "name": "string",
      "match_score": 0,
      "reasons": ["string"],
      "benefits": ["string"],
      "how_to_use": "string",
      "best_time": "string",
      "warning": "string"
    }}
  ],
  "extra_suggestions": ["string"]
}}
"""

    response = model.generate_content(prompt)

    data = safe_json_load(response.text)

    # =========================
    # FALLBACK AN TOÀN
    # =========================
    if not data:
        return {
            "user_problem": user_input,
            "summary": "Không thể phân tích dữ liệu từ AI",
            "recommendations": [
                {
                    "id": 0,
                    "name": "Trà Xanh",
                    "match_score": 50,
                    "reasons": ["Hỗ trợ thanh lọc cơ thể"],
                    "benefits": ["Tăng sức khỏe tổng thể"],
                    "how_to_use": "Uống 1-2 lần mỗi ngày",
                    "best_time": "Buổi sáng",
                    "warning": ""
                }
            ],
            "extra_suggestions": ["Ngủ đủ giấc", "Giảm căng thẳng"]
        }

    return data

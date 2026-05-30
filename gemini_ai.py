import google.generativeai as genai
import json
import re
import os
genai.configure(api_key=os.environ.get("AQ.Ab8RN6LkDW6DOgyM8KgH8oSc0vn_EmxDXP1Q8ipxlbROcLzMyA"))

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={
        "temperature": 0.2,
        "top_p": 0.9,
        "response_mime_type": "application/json"
    }
)

# =========================
# SAFE PARSE JSON
# =========================
def safe_json_load(text):
    try:
        return json.loads(text)
    except:
        # bóc JSON từ trong text nếu Gemini lỡ thêm chữ
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

    product_text = []

    for p in products:
        product_text.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "short_description": getattr(p, "short_description", "")
        })

    # =========================
    # PROMPT FIX (KHÓA CỨNG JSON)
    # =========================
    prompt = f"""
You are a STRICT JSON API SYSTEM.

RULES (VERY IMPORTANT):
- Output ONLY valid JSON
- NO markdown
- NO explanation
- NO text before or after JSON
- If you fail -> response will be rejected

TASK:
- Analyze user health problem
- Recommend products ONLY from list
- Explain reasons clearly

PRODUCTS:
{json.dumps(product_text, ensure_ascii=False)}

USER INPUT:
{user_input}

RETURN JSON FORMAT EXACTLY:

{{
  "user_problem": "string",
  "summary": "string",
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
            "summary": "AI không trả về JSON hợp lệ",
            "recommendations": [
                {
                    "id": 0,
                    "name": "Trà Xanh",
                    "match_score": 50,
                    "reasons": ["Hỗ trợ sức khỏe tổng thể"],
                    "benefits": ["Thanh lọc cơ thể"],
                    "how_to_use": "Uống hằng ngày",
                    "best_time": "sáng",
                    "warning": ""
                }
            ],
            "extra_suggestions": []
        }

    return data

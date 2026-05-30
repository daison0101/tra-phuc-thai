import re
import unicodedata

# ======================
# MAP TRIỆU CHỨNG → NHU CẦU
# ======================
INTENT_MAP = {
    "stress": ["stress", "căng thẳng", "áp lực", "lo âu"],
    "mất ngủ": ["mất ngủ", "khó ngủ", "insomnia"],
    "mệt": ["mệt", "thiếu năng lượng", "uể oải"],
    "giảm cân": ["giảm cân", "detox", "béo"],
}


# ======================
# CHUẨN HOÁ TEXT
# ======================
def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


# ======================
# AI PRO
# ======================
def recommend_tea(user_input, products):

    query = normalize(user_input)

    # ======================
    # 1. XÁC ĐỊNH INTENT
    # ======================
    detected_intents = []

    for intent, keywords in INTENT_MAP.items():
        for k in keywords:
            if k in query:
                detected_intents.append(intent)
                break

    results = []

    # ======================
    # 2. MATCH SẢN PHẨM + GIẢI THÍCH
    # ======================
    for p in products:

        text = normalize(
            f"{p.name} {p.short_description or ''} {p.description or ''}"
        )

        score = 0
        reasons = []

        # MATCH INTENT → PRODUCT
        for intent in detected_intents:

            if intent in ["stress", "mất ngủ"]:

                if any(x in text for x in ["cúc", "tâm sen", "an thần", "thư giãn"]):
                    score += 5
                    reasons.append("Giúp giảm stress, thư giãn thần kinh, hỗ trợ giấc ngủ")

            if intent == "mệt":

                if any(x in text for x in ["matcha", "năng lượng"]):
                    score += 5
                    reasons.append("Tăng năng lượng, giúp tỉnh táo")

            if intent == "giảm cân":

                if any(x in text for x in ["ô long", "detox"]):
                    score += 5
                    reasons.append("Hỗ trợ giảm cân, thanh lọc cơ thể")

        # MATCH TEXT DIRECT
        if query in text:
            score += 2

        if score > 0:
            results.append({
                "name": p.name,
                "image": p.image,
                "price": p.price,
                "description": p.short_description or p.description,
                "score": score,
                "reasons": list(set(reasons))
            })

    # ======================
    # SORT
    # ======================
    results.sort(key=lambda x: x["score"], reverse=True)

    # fallback
    if not results:
        results = [{
            "name": "Trà Xanh",
            "description": "Thanh lọc cơ thể, hỗ trợ sức khỏe tổng thể",
            "reasons": ["Tốt cho sức khỏe", "Dễ uống hằng ngày"],
            "price": 0
        }]

    # ======================
    # HTML OUTPUT
    # ======================
    html = """
    <div class="alert alert-success">
        <h4>🤖 AI Tư Vấn Sức Khỏe</h4>
        <p>Dựa trên triệu chứng bạn nhập, hệ thống đã phân tích và gợi ý:</p>
    </div>
    """

    for r in results:

        html += f"""
        <div class="card mb-3 shadow-sm">
            <div class="card-body">

                <h4 class="text-success">{r['name']}</h4>

                <p><b>Vì sao nên dùng:</b></p>
                <ul>
        """

        for reason in r["reasons"]:
            html += f"<li>{reason}</li>"

        html += f"""
                </ul>

                <p class="text-muted">{r['description']}</p>

                <b class="text-success">Giá: {r['price']}đ</b>

            </div>
        </div>
        """

    return html
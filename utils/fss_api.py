"""금융감독원 금융상품 비교공시 API 연동 모듈 (finlife.fss.or.kr)"""
import requests

BASE_URL = "https://finlife.fss.or.kr/finlifeapi"
BANK_GROUP = "020000"   # 은행권 코드

ENDPOINTS = {
    "정기예금":    "/depositProductsSearch.json",
    "적금":       "/savingProductsSearch.json",
    "전세자금대출": "/rentHouseLoanProductsSearch.json",
    "주택담보대출": "/mortgageLoanProductsSearch.json",
    "개인신용대출": "/creditLoanProductsSearch.json",
}

# 카테고리별 관련 금융상품 (카테고리 이름은 각 페이지의 CATEGORY 변수와 동일해야 함)
CATEGORY_PRODUCTS = {
    "사회초년생":   ["정기예금", "적금", "전세자금대출", "개인신용대출"],
    "대학생":      ["정기예금", "적금"],
    "군 전역 예정자": ["정기예금", "적금", "전세자금대출"],
    "취업 준비생":  ["정기예금", "적금"],
}


def _fetch_raw(api_key: str, product_type: str) -> dict:
    endpoint = ENDPOINTS.get(product_type)
    if not endpoint:
        return {}
    params = {"auth": api_key, "topFinGrpNo": BANK_GROUP, "pageNo": 1}
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("result", {})
    except Exception:
        return {}


def format_for_context(api_key: str, category: str) -> str:
    """카테고리에 맞는 금융상품 정보를 GPT 컨텍스트용 텍스트로 반환합니다."""
    product_types = CATEGORY_PRODUCTS.get(category, ["정기예금", "적금"])
    sections = ["[금융감독원 금융상품 비교공시]"]

    for ptype in product_types:
        result = _fetch_raw(api_key, ptype)
        base_list   = result.get("baseList", [])[:10]
        option_list = result.get("optionList", [])

        if not base_list:
            continue

        sections.append(f"\n▶ {ptype}")
        for b in base_list:
            code     = b.get("fin_prdt_cd", "")
            name     = b.get("fin_prdt_nm", "")
            company  = b.get("kor_co_nm", "")
            join_way = b.get("join_way", "")
            join_mem = b.get("join_member", "")
            spcl_cnd = b.get("spcl_cnd", "")

            opts = [o for o in option_list if o.get("fin_prdt_cd") == code]
            rates = []
            for o in opts:
                r = o.get("intr_rate2") or o.get("intr_rate")
                if r:
                    try:
                        rates.append(float(r))
                    except (ValueError, TypeError):
                        pass
            max_rate = f"{max(rates):.2f}%" if rates else "정보없음"

            sections.append(
                f"  - {company} 《{name}》\n"
                f"    최고금리: {max_rate} | 가입방법: {join_way} | 가입대상: {join_mem}\n"
                f"    우대조건: {spcl_cnd}"
            )

    return "\n".join(sections) if len(sections) > 1 else ""

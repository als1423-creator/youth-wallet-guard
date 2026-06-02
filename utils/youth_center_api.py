"""온통청년 청년정책 API 연동 모듈 (공공데이터포털)"""
import requests

BASE_URL = "https://www.youthcenter.go.kr/openapi/getYouthPolicyList.do"

# 카테고리별 API 정책 분야 코드 (srchPolyBizSecd)
# 023: 일자리, 024: 주거, 025: 교육, 026: 복지·문화, 027: 참여·권리
CATEGORY_AREA_CODES = {
    "사회초년생":   ["023", "024", "026"],
    "대학생":      ["025", "026", "027"],
    "군 전역 예정자": ["023", "024", "026"],
    "취업 준비생":  ["023", "026"],
}


def fetch_policies(api_key: str, category: str = "", display: int = 100) -> list:
    """온통청년 API에서 청년정책 목록을 가져옵니다."""
    codes = CATEGORY_AREA_CODES.get(category, [])

    # 분야 코드가 있으면 코드별로 가져와서 합침, 없으면 전체 조회
    if codes:
        all_policies = []
        seen_ids = set()
        for code in codes:
            params = {
                "openApiVlak": api_key,
                "display": 50,
                "pageIndex": 1,
                "srchPolyBizSecd": code,
            }
            try:
                resp = requests.get(BASE_URL, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()
                items = data.get("youthPolicy", {}).get("list", [])
                for item in items:
                    biz_id = item.get("bizId", "")
                    if biz_id and biz_id not in seen_ids:
                        seen_ids.add(biz_id)
                        all_policies.append(item)
            except Exception:
                continue
        return all_policies
    else:
        params = {
            "openApiVlak": api_key,
            "display": display,
            "pageIndex": 1,
        }
        try:
            resp = requests.get(BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return data.get("youthPolicy", {}).get("list", [])
        except Exception:
            return []


def format_for_context(policies: list) -> str:
    """정책 목록을 GPT 컨텍스트용 텍스트로 변환합니다."""
    if not policies:
        return ""

    lines = ["[온통청년 청년정책 목록]"]
    for i, p in enumerate(policies, 1):
        name    = p.get("polyBizSjNm", "")
        org     = p.get("cnsgNmor", "")
        target  = p.get("sporTrgtCn", "")
        age     = p.get("ageInfo", "")
        content = p.get("sporCn", "")
        method  = p.get("aplySc", "")
        period  = p.get("rqutPrdCn", "")
        url     = p.get("pohstPprsUrl", "")

        entry = (
            f"\n{i}. {name}\n"
            f"   · 운영기관: {org}\n"
            f"   · 지원대상: {target} / 나이: {age}\n"
            f"   · 지원내용: {content}\n"
            f"   · 신청방법: {method}\n"
            f"   · 신청기간: {period}\n"
            f"   · 신청URL: {url}"
        )
        lines.append(entry)

    return "\n".join(lines)

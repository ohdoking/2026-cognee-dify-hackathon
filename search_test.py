import requests
import os
import json
from dotenv import load_dotenv

# ==========================================
# 1. 환경 설정
# ==========================================
load_dotenv()
COGNEE_API_KEY = os.environ.get("COGNEE_API_KEY")
BASE_URL = os.environ.get("BASE_URL")
SEARCH_ENDPOINT = f"{BASE_URL}/api/search"

headers = {
    "X-Api-Key": COGNEE_API_KEY,
    "Content-Type": "application/json"
}

# ==========================================
# 2. 검색 실행 함수
# ==========================================
def test_search(query_text):
    print(f"🔎 Searching for: '{query_text}'...")

    # API 명세의 Example Value와 Schema를 반영한 페이로드
    payload = {
        "searchType": "GRAPH_COMPLETION", # 그래프 기반 완성형 검색
        "datasets": ["Project_Aurora_Knowledge"],
        "query": query_text,
        "topK": 5,
        "onlyContext": False # True로 하면 LLM 답변 대신 원본 컨텍스트만 받음
    }

    try:
        response = requests.post(SEARCH_ENDPOINT, headers=headers, json=payload)
        
        if response.status_code == 200:
            results = response.json()
            print("\n✅ Search Results:")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return results
        else:
            print(f"❌ Search Failed ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during request: {e}")
        return None

if __name__ == "__main__":
    # 테스트 1: 데이터베이스 표준 확인
    test_search("What is our standard database for the ledger?")
    
    # 테스트 2: 데이터 저장 위치 규정 확인
    # test_search("Where should we store customer PII data for Project Aurora?")
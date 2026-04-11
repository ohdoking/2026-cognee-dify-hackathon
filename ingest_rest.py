import requests
import os
from dotenv import load_dotenv

# ==========================================
# 1. 환경 설정
# ==========================================
load_dotenv()
COGNEE_API_KEY = os.environ.get("COGNEE_API_KEY")
BASE_URL = os.environ.get("BASE_URL")

# 💡 문서에 명시된 정확한 경로로 수정
ADD_TEXT_ENDPOINT = f"{BASE_URL}/api/add_text"
COGNIFY_ENDPOINT = f"{BASE_URL}/api/cognify"

# 💡 이전 캡처에서 확인된 커스텀 헤더 적용
headers = {
    "X-Api-Key": COGNEE_API_KEY,
    "Content-Type": "application/json"
}

# 우리가 사용할 데이터셋 이름 (원하시는 이름으로 수정 가능)
DATASET_NAME = "Project_Aurora_Knowledge"

# ==========================================
# 2. 주입할 데이터 (복잡한 컨텍스트)
# ==========================================
background_knowledge = """
    [Strategic Overview]
    Project Aurora is N26's high-priority initiative to expand into the Latin American market. 
    The internal project code is 'AUR-2026'. 
    Current Project Lead: Lena (Engineering) and Marcus (Compliance).

    [Data Governance & Legal]
    - GDPR+ Protocol: As a German-based fintech, we apply GDPR even for LATAM users. 
    - Regional Locking: All primary user PII (Personally Identifiable Information) must be physically hosted in Frankfurt (eu-central-1).
    - EXCEPTION: Analytics metadata can be stored in US-East-1, but ONLY if anonymized through the 'Anonymizer-V3' service managed by the DevOps team.
    - Compliance Rule 402: Any change in data residency requires a signed waiver from Marcus and the Legal Head, Sarah.

    [Technical Infrastructure]
    - Database Standard: Our core ledger must use a distributed PostgreSQL (Aurora Flavor) to ensure ACID compliance. 
    - No-Go Tech: MongoDB and other NoSQL databases are strictly prohibited for financial ledger transactions due to consistency concerns.
    - Security Patch: All serverless functions (AWS Lambda) must be updated to Node.js 20.x.

    [Budget & Resource Allocation]
    - Fixed Budget: €150,000 for the initial launch phase.
    - Cost Cutting: If budget exceeds 90%, the 'Marketing' spend is cut first, NOT the 'Infrastructure' or 'Security'.
    - Stakeholder Matrix: Lena has the final say on tech stack changes. Marcus has a 'Veto Power' over any architectural changes that affect data residency.

    [Timeline & Milestones]
    - Hard Deadline: November 1st, 2026.
    - Soft Launch: October 1st, 2026 (Internal employees only).
    - Rule of Delay: Any deadline extension beyond 14 days must be approved by the Board of Directors.
"""

def run_ingestion():
    print(f"🚀 Starting Ingestion to {BASE_URL}...")

    # ----------------------------------------
    # STEP 1: Add Text Data (/api/add_text)
    # ----------------------------------------
    # 💡 409 에러 해결: datasetName 추가 및 키값 수정 (textData)
    add_payload = {
        "textData": [background_knowledge], # 리스트 형식
        "datasetName": DATASET_NAME
    }

    print(f"📡 Step 1: Sending text to dataset '{DATASET_NAME}'...")
    add_res = requests.post(ADD_TEXT_ENDPOINT, headers=headers, json=add_payload)

    if add_res.status_code == 200:
        print("✅ Step 1 Success: Text added to dataset.")
    else:
        print(f"❌ Step 1 Failed ({add_res.status_code}): {add_res.text}")
        return

    # ----------------------------------------
    # STEP 2: Cognify (/api/cognify)
    # ----------------------------------------
    # 💡 문서에 따라 어떤 데이터셋을 그래프로 만들지 지정
    cognify_payload = {
        "datasets": [DATASET_NAME],
        "runInBackground": False  # 결과를 바로 보기 위해 False 설정
    }

    print(f"📡 Step 2: Triggering Cognify for '{DATASET_NAME}'...")
    cog_res = requests.post(COGNIFY_ENDPOINT, headers=headers, json=cognify_payload)

    if cog_res.status_code == 200:
        print("✅ Step 2 Success: Knowledge Graph construction complete!")
        print("🎉 Now you can use this in your Dify workflow.")
    else:
        print(f"❌ Step 2 Failed ({cog_res.status_code}): {cog_res.text}")

if __name__ == "__main__":
    run_ingestion()
import asyncio
import cognee
import os
from dotenv import load_dotenv

load_dotenv()

# 1. API 키 설정
# .env 파일에서 COGNEE_API_KEY를 자동으로 가져옵니다.

async def ingest_knowledge():
    print("🚀 Connecting to cognee and preparing knowledge base...")

    # 2. 주입할 배경 지식 데이터 (앞서 만든 시나리오 내용)
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

    try:
        # 3. 데이터 추가 (Add)
        # cognee는 텍스트를 분석하여 엔티티(인물, 장소, 기술 등) 간의 관계를 생성합니다.
        await cognee.add(background_knowledge)
        
        # 4. 지식 그래프 생성 (Cognify)
        # 이 과정에서 LLM이 텍스트를 이해하고 그래프 구조로 변환합니다.
        await cognee.cognify()
        
        print("✅ Success: Knowledge 'Project Aurora' has been graphed!")
        
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")

async def check_data():
    # 데이터가 잘 들어갔는지 간단히 확인하는 쿼리 (선택 사항)
    search_results = await cognee.search("What is the security protocol for Project Aurora?")
    print(f"🔍 Test Search Result: {search_results}")

if __name__ == "__main__":
    # 스크립트 실행
    asyncio.run(ingest_knowledge())
    # asyncio.run(check_data()) # 확인하고 싶을 때 주석 해제
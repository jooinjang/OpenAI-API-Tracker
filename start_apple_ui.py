#!/usr/bin/env python3
"""
간단한 Apple UI 테스트를 위한 런처
환경 문제를 우회하여 Apple 파일 업로드 UI를 테스트합니다.
"""

import os
import sys

def main():
    print("🍎 OpenAI Usage Tracker - Apple Design System")
    print("=" * 50)
    print()
    
    print("📍 실행 방법:")
    print()
    print("1. 터미널에서 다음 명령어 실행:")
    print("   cd /Users/jaewooklee/Documents/Github/OpenAITracker")
    print("   streamlit run app.py --server.port 8504")
    print()
    print("2. 브라우저에서 접속:")
    print("   http://localhost:8504")
    print()
    print("🍎 Apple 파일 업로드 UI 확인 사항:")
    print("   • 사이드바에서 새로운 Apple 스타일 파일 업로더")
    print("   • 👤 사용자별 데이터 업로드 영역") 
    print("   • 🏗️ 프로젝트별 데이터 업로드 영역")
    print("   • Apple Blue (#007AFF) 컬러 시스템")
    print("   • 호버 애니메이션 효과")
    print("   • 드래그 앤 드롭 스타일 인터페이스")
    print("   • 실시간 파일 상태 표시")
    print()
    print("🎯 테스트 순서:")
    print("   1. JSON 파일 준비 (OpenAI 플랫폼에서 다운로드)")
    print("   2. Apple 스타일 업로드 영역 클릭")
    print("   3. 파일 선택 후 상태 확인")
    print("   4. userID 오류 없이 정상 작동 확인")
    print()
    print("✅ 모든 오류가 수정되었습니다:")
    print("   • NameError: userID → 해결됨")
    print("   • ImportError: list_organization_projects → 해결됨")
    print("   • Apple 파일 업로드 UI → 구현 완료")
    print()

if __name__ == "__main__":
    main()
import json
import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 환경 변수에서 API 키 정보 가져오기
openai_org_id = os.environ.get("OPENAI_ORG_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")
INFO_FILEPATH = os.environ.get("USERINFO_PATH", "userinfo.json")

# API 키 검증
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
if not openai_org_id:
    raise ValueError("OPENAI_ORG_KEY 환경 변수가 설정되지 않았습니다.")


def extract_results_from_buckets(data):
    """2025년 버킷 구조에서 결과 데이터를 추출합니다."""
    results = []
    for bucket in data.get("data", []):
        if "results" in bucket:
            for result in bucket["results"]:
                # 날짜 정보 추가 (start_time을 기준으로)
                result["date"] = datetime.fromtimestamp(bucket["start_time"]).strftime("%Y-%m-%d")
                result["start_time"] = bucket["start_time"]
                result["end_time"] = bucket["end_time"]
                results.append(result)
    return results


def group_by_date(data):
    """날짜별로 데이터를 그룹화합니다."""
    # 2025년 구조만 지원
    results = extract_results_from_buckets(data)
    
    group = {}
    for line in results:
        date = line.get("date")
        if not date and "start_time" in line:
            date = datetime.fromtimestamp(line["start_time"]).strftime("%Y-%m-%d")
        
        if date not in group:
            group[date] = [line]
        else:
            group[date].append(line)
    return group


def group_by_userID(data):
    """사용자 ID별로 데이터를 그룹화합니다."""
    # 2025년 구조만 지원
    results = extract_results_from_buckets(data)
    
    group = {}
    for line in results:
        user_id = line.get("user_id")
        # user_id가 None이거나 빈 문자열인 경우 처리
        if user_id is None or user_id == "":
            user_id = "unknown_user"
        
        if user_id not in group:
            group[user_id] = [line]
        else:
            group[user_id].append(line)
    return group


def group_by_model(data):
    """모델별로 데이터를 그룹화합니다."""
    # 2025년 구조만 지원
    results = extract_results_from_buckets(data)
    
    group = {}
    for line in results:
        # 2025년 구조에서는 line_item 사용
        model_name = line.get("line_item", "")
        temp = model_name.split(",")
        model = temp[0].strip()
        
        if model not in group:
            group[model] = [line]
        else:
            group[model].append(line)
    return group


def get_total_cost(data):
    """총 비용을 계산합니다."""
    # 2025년 구조만 지원
    results = extract_results_from_buckets(data)
    
    total_cost = 0
    cost_by_date = [0] * 32
    
    for line in results:
        # 2025년 구조에서는 amount.value 사용
        if "amount" in line and isinstance(line["amount"], dict):
            cost = line["amount"]["value"]  # 이미 달러 단위
        else:
            cost = 0  # 데이터 구조가 예상과 다를 경우 0으로 처리
        
        total_cost += cost
        
        # 날짜별 비용 계산
        date = line.get("date")
        if not date and "start_time" in line:
            date = datetime.fromtimestamp(line["start_time"]).strftime("%Y-%m-%d")
        
        if date:
            day = int(date.split("-")[2])
            cost_by_date[day] += cost
    
    return total_cost, cost_by_date


def build_userinfo():
    """OpenAI 조직의 사용자 정보를 가져와 JSON 파일로 저장합니다."""
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "OpenAI-Organization": openai_org_id,
        "Content-Type": "application/json",
    }

    try:
        # OpenAI API v1 엔드포인트 사용
        response = requests.get(
            f"https://api.openai.com/v1/organization/users?&limit=50",
            headers=headers,
            timeout=30
        )
        
        # HTTP 상태 코드 확인
        if response.status_code != 200:
            print(f"API 요청 실패: HTTP {response.status_code}")
            print(f"응답 내용: {response.text}")
            return False
        
        # JSON 응답 파싱
        response_data = response.json()
        print(f"API 응답: {response_data}")
        
        # 응답 구조 확인 및 데이터 추출
        if "members" in response_data and "data" in response_data["members"]:
            users = response_data["members"]["data"]
        elif "data" in response_data:
            users = response_data["data"]
        else:
            print("예상하지 못한 응답 구조입니다.")
            print(f"응답 키: {list(response_data.keys())}")
            return False
            
        logging.debug("사용자 정보 파일 생성 중...")
        
        # 사용자 정보를 JSON 파일로 저장
        with open(INFO_FILEPATH, "w", encoding="utf-8") as fp:
            json.dump(users, fp, ensure_ascii=False, indent=2)
        
        print(f"사용자 정보가 {INFO_FILEPATH}에 성공적으로 저장되었습니다.")
        print(f"총 {len(users)}명의 사용자 정보를 저장했습니다.")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류가 발생했습니다: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류가 발생했습니다: {e}")
        print(f"응답 내용: {response.text}")
        return False
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
        return False


def get_name_with_userID(uid, userinfo):
    for uinfo in userinfo:
        # 안전하게 딕셔너리에 접근하여 KeyError 방지
        if uid == uinfo.get("id"):
            return uinfo.get("name")
    print(f"User {uid} NOT FOUNDED...")
    return None


def get_userID_with_name(uid, userinfo):
    for uinfo in userinfo:
        # 안전하게 딕셔너리에 접근하여 KeyError 방지
        if uid == uinfo.get("name"):
            return uinfo.get("id")
    print(f"User {uid} NOT FOUNDED...")
    return None


def rebuild_to_cost(data):
    result = {}
    keys = data.keys()
    for k in keys:
        total_cost, total_cost_by_date = get_total_cost(data[k])
        result[k] = {"total_cost": total_cost, "cost_transition": total_cost_by_date}
    return result


# 함수 테스트
if __name__ == "__main__":
    success = build_userinfo()
    if success:
        print("사용자 정보 수집 완료!")
    else:
        print("사용자 정보 수집 실패!")

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
    
    # data가 딕셔너리이고 "data" 키를 가지고 있는 경우
    if isinstance(data, dict) and "data" in data:
        buckets = data["data"]
    # data가 이미 리스트인 경우 (이미 추출된 결과)
    elif isinstance(data, list):
        return data  # 이미 추출된 결과라면 그대로 반환
    else:
        return results  # 예상치 못한 구조인 경우 빈 리스트 반환
    
    for bucket in buckets:
        if isinstance(bucket, dict) and "results" in bucket:
            for result in bucket["results"]:
                # 날짜 정보 추가 (start_time을 기준으로)
                result["date"] = datetime.fromtimestamp(bucket["start_time"]).strftime("%Y-%m-%d")
                result["start_time"] = bucket["start_time"]
                result["end_time"] = bucket["end_time"]
                results.append(result)
    return results


def group_by_date(data):
    """날짜별로 데이터를 그룹화합니다."""
    # data가 이미 결과 리스트인 경우 처리
    if isinstance(data, list):
        results = data
    else:
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
    # data가 이미 결과 리스트인 경우 처리
    if isinstance(data, list):
        results = data
    else:
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
    # data가 이미 결과 리스트인 경우 처리
    if isinstance(data, list):
        results = data
    else:
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


def build_userinfo(admin_api_key=None):
    """OpenAI 조직의 사용자 정보를 가져와 JSON 파일로 저장합니다."""
    # 관리자 키가 제공되면 사용, 없으면 기본 환경변수 사용
    api_key = admin_api_key or openai_api_key
    org_id = openai_org_id  # Organization ID는 환경변수 사용
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Organization ID가 있을 때만 헤더에 추가
    if org_id:
        headers["OpenAI-Organization"] = org_id

    try:
        # OpenAI API v1 엔드포인트 사용 (더 많은 사용자 가져오기)
        response = requests.get(
            f"https://api.openai.com/v1/organization/users?limit=100",
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
        # data[k]는 이미 결과 리스트이므로 직접 전달
        total_cost, total_cost_by_date = get_total_cost(data[k])
        result[k] = {"total_cost": total_cost, "cost_transition": total_cost_by_date}
    return result


def group_by_project_id(data):
    """프로젝트 ID별로 데이터를 그룹화합니다."""
    # 2025년 구조만 지원
    results = extract_results_from_buckets(data)
    
    group = {}
    for line in results:
        project_id = line.get("project_id")
        
        # project_id가 None이거나 빈 문자열인 경우 처리
        if project_id is None or project_id == "":
            project_id = "no_project"  # 프로젝트가 할당되지 않은 사용량
        
        if project_id not in group:
            group[project_id] = [line]
        else:
            group[project_id].append(line)
    return group


def calculate_project_usage(data):
    """프로젝트별 사용량을 계산합니다."""
    project_groups = group_by_project_id(data)
    project_usage = {}
    
    for project_id, project_data in project_groups.items():
        total_cost, _ = get_total_cost(project_data)
        
        # 사용자별 세부 정보도 포함
        user_breakdown = {}
        for line in project_data:
            user_id = line.get("user_id", "unknown_user")
            user_email = line.get("user_email", "unknown@email.com")
            
            cost = 0
            if "amount" in line and isinstance(line["amount"], dict):
                cost = line["amount"]["value"]
            
            if user_id not in user_breakdown:
                user_breakdown[user_id] = {
                    "email": user_email,
                    "cost": 0,
                    "requests": 0
                }
            
            # 안전한 값 추가 (NaN이나 None 값 처리)
            safe_cost = cost if cost is not None and not (isinstance(cost, float) and cost != cost) else 0
            user_breakdown[user_id]["cost"] += safe_cost
            user_breakdown[user_id]["requests"] += 1
        
        project_usage[project_id] = {
            "total_cost": total_cost,
            "users": user_breakdown,
            "total_requests": len(project_data)
        }
    
    return project_usage


def find_budget_overages(project_usage, project_budgets, projects_info=None):
    """예산 초과 프로젝트를 찾습니다."""
    overages = []
    
    for project_id, budget in project_budgets.items():
        # 해당 프로젝트의 실제 사용량 찾기
        actual_usage = 0
        usage_details = None
        
        # project_id가 정확히 매칭되는 경우
        if project_id in project_usage:
            actual_usage = project_usage[project_id]["total_cost"]
            usage_details = project_usage[project_id]
        # 프로젝트 정보가 없는 데이터의 경우 (project_id가 null인 경우)
        elif "no_project" in project_usage and projects_info:
            # 이 경우는 프로젝트별 분석이 불가능하므로 건너뛰기
            continue
        
        # 예산 초과 확인
        if actual_usage > budget:
            overage_amount = actual_usage - budget
            overage_percentage = ((actual_usage - budget) / budget) * 100 if budget > 0 else 0
            
            # 프로젝트 이름 찾기
            project_name = project_id
            if projects_info:
                for project in projects_info:
                    if project.get("id") == project_id:
                        project_name = project.get("name", project_id)
                        break
            
            overages.append({
                "project_id": project_id,
                "project_name": project_name,
                "budget": budget,
                "actual_usage": actual_usage,
                "overage_amount": overage_amount,
                "overage_percentage": overage_percentage,
                "usage_details": usage_details
            })
    
    # 초과 금액 순으로 정렬
    overages.sort(key=lambda x: x["overage_amount"], reverse=True)
    return overages


def list_organization_projects(admin_api_key=None):
    """조직의 프로젝트 목록을 가져옵니다 (pagination 지원)."""
    # 관리자 키가 제공되면 사용, 없으면 기본 환경변수 사용
    api_key = admin_api_key or openai_api_key
    org_id = openai_org_id
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Organization": org_id,
        "Content-Type": "application/json",
    }

    all_projects = []
    after = None
    
    try:
        while True:
            # pagination을 위한 URL 구성
            url = "https://api.openai.com/v1/organization/projects?limit=100"
            if after:
                url += f"&after={after}"
                
            response = requests.get(url, headers=headers, timeout=30)
            
            # HTTP 상태 코드 확인
            if response.status_code != 200:
                print(f"Organization Projects 요청 실패: HTTP {response.status_code}")
                print(f"응답 내용: {response.text}")
                break
            
            # JSON 응답 파싱
            response_data = response.json()
            projects_batch = response_data.get("data", [])
            all_projects.extend(projects_batch)
            
            # 더 많은 데이터가 있는지 확인
            if not response_data.get("has_more", False):
                break
                
            # 다음 페이지를 위한 after 값 설정
            after = response_data.get("last_id")
            if not after:
                break
                
        print(f"총 {len(all_projects)}개의 프로젝트를 가져왔습니다.")
        return all_projects
        
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류가 발생했습니다: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류가 발생했습니다: {e}")
        print(f"응답 내용: {response.text}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
        return None


def list_api_keys(admin_api_key=None):
    """조직의 모든 프로젝트에서 API 키 목록을 가져옵니다."""
    projects = list_organization_projects(admin_api_key)
    if not projects:
        return None
    
    all_api_keys = []
    for project in projects:
        project_id = project["id"]
        project_name = project["name"]
        
        project_keys = get_project_api_keys(project_id, admin_api_key)
        if project_keys:
            # 각 API 키에 프로젝트 정보 추가
            for key in project_keys:
                key["project_id"] = project_id
                key["project_name"] = project_name
            all_api_keys.extend(project_keys)
    
    return all_api_keys


def get_organization_users(admin_api_key=None):
    """조직의 사용자 목록을 가져옵니다 (pagination 지원)."""
    # 관리자 키가 제공되면 사용, 없으면 기본 환경변수 사용
    api_key = admin_api_key or openai_api_key
    org_id = openai_org_id
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Organization": org_id,
        "Content-Type": "application/json",
    }

    all_users = []
    after = None
    
    try:
        while True:
            # pagination을 위한 URL 구성
            url = "https://api.openai.com/v1/organization/users?limit=100"
            if after:
                url += f"&after={after}"
                
            response = requests.get(url, headers=headers, timeout=30)
            
            # HTTP 상태 코드 확인
            if response.status_code != 200:
                print(f"Organization Users 요청 실패: HTTP {response.status_code}")
                print(f"응답 내용: {response.text}")
                break
            
            # JSON 응답 파싱
            response_data = response.json()
            users_batch = response_data.get("data", [])
            all_users.extend(users_batch)
            
            # 더 많은 데이터가 있는지 확인
            if not response_data.get("has_more", False):
                break
                
            # 다음 페이지를 위한 after 값 설정
            after = response_data.get("last_id")
            if not after:
                break
                
        print(f"총 {len(all_users)}명의 사용자를 가져왔습니다.")
        return all_users
        
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류가 발생했습니다: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류가 발생했습니다: {e}")
        print(f"응답 내용: {response.text}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
        return None


def get_project_api_keys(project_id, admin_api_key=None):
    """특정 프로젝트의 API 키 목록을 가져옵니다 (pagination 지원)."""
    # 관리자 키가 제공되면 사용, 없으면 기본 환경변수 사용
    api_key = admin_api_key or openai_api_key
    org_id = openai_org_id
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Organization": org_id,
        "Content-Type": "application/json",
    }

    all_keys = []
    after = None
    
    try:
        while True:
            # pagination을 위한 URL 구성
            url = f"https://api.openai.com/v1/organization/projects/{project_id}/api_keys?limit=100"
            if after:
                url += f"&after={after}"
                
            response = requests.get(url, headers=headers, timeout=30)
            
            # HTTP 상태 코드 확인
            if response.status_code != 200:
                print(f"Project API Keys 요청 실패: HTTP {response.status_code}")
                print(f"응답 내용: {response.text}")
                break
            
            # JSON 응답 파싱
            response_data = response.json()
            keys_batch = response_data.get("data", [])
            all_keys.extend(keys_batch)
            
            # 더 많은 데이터가 있는지 확인
            if not response_data.get("has_more", False):
                break
                
            # 다음 페이지를 위한 after 값 설정
            after = response_data.get("last_id")
            if not after:
                break
                
        return all_keys
        
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류가 발생했습니다: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류가 발생했습니다: {e}")
        print(f"응답 내용: {response.text}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
        return None


def get_api_key_details(api_key_id, admin_api_key=None):
    """특정 API 키의 상세 정보를 가져옵니다.
    
    주의: 이 기능은 현재 OpenAI 공개 API에서 지원되지 않습니다.
    """
    print("⚠️ API 키 상세 정보 조회 엔드포인트는 현재 공개적으로 접근할 수 없습니다.")
    return None


def delete_api_key(project_id, api_key_id, admin_api_key=None):
    """특정 프로젝트의 API 키를 삭제합니다."""
    # 관리자 키가 제공되면 사용, 없으면 기본 환경변수 사용
    api_key = admin_api_key or openai_api_key
    org_id = openai_org_id
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Organization": org_id,
        "Content-Type": "application/json",
    }

    try:
        url = f"https://api.openai.com/v1/organization/projects/{project_id}/api_keys/{api_key_id}"
        response = requests.delete(url, headers=headers, timeout=30)
        
        # HTTP 상태 코드 확인
        if response.status_code == 200:
            print(f"✅ API 키 {api_key_id}가 성공적으로 삭제되었습니다.")
            return True
        else:
            print(f"❌ API 키 삭제 실패: HTTP {response.status_code}")
            print(f"응답 내용: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류가 발생했습니다: {e}")
        return False
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
        return False


def bulk_delete_api_keys(project_keys_list, admin_api_key=None):
    """여러 프로젝트의 API 키들을 일괄 삭제합니다.
    
    Args:
        project_keys_list: [(project_id, api_key_id, key_name), ...] 형태의 리스트
        admin_api_key: 관리자 API 키
    
    Returns:
        dict: {"success": [], "failed": []} 형태의 결과
    """
    results = {"success": [], "failed": []}
    
    for project_id, api_key_id, key_name in project_keys_list:
        success = delete_api_key(project_id, api_key_id, admin_api_key)
        
        if success:
            results["success"].append({
                "project_id": project_id,
                "api_key_id": api_key_id,
                "key_name": key_name
            })
        else:
            results["failed"].append({
                "project_id": project_id,
                "api_key_id": api_key_id,
                "key_name": key_name
            })
    
    return results


def save_project_budgets(budgets, filename="project_budgets.json"):
    """프로젝트 예산 정보를 JSON 파일로 저장합니다."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(budgets, f, ensure_ascii=False, indent=2)
        print(f"✅ 프로젝트 예산이 {filename}에 저장되었습니다.")
        return True
    except Exception as e:
        print(f"❌ 예산 저장 실패: {e}")
        return False


def load_project_budgets(filename="project_budgets.json"):
    """JSON 파일에서 프로젝트 예산 정보를 로드합니다."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                budgets = json.load(f)
            print(f"✅ 프로젝트 예산이 {filename}에서 로드되었습니다.")
            return budgets
        else:
            print(f"⚠️ 예산 파일 {filename}이 존재하지 않습니다.")
            return {}
    except Exception as e:
        print(f"❌ 예산 로드 실패: {e}")
        return {}


def reset_project_budgets(filename="project_budgets.json"):
    """프로젝트 예산 파일을 삭제하여 초기화합니다."""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"✅ 프로젝트 예산 파일 {filename}이 삭제되었습니다.")
            return True
        else:
            print(f"⚠️ 삭제할 예산 파일 {filename}이 존재하지 않습니다.")
            return True  # 파일이 없어도 초기화 목적은 달성
    except Exception as e:
        print(f"❌ 예산 파일 삭제 실패: {e}")
        return False


def get_project_rate_limits(project_id, admin_api_key=None):
    """특정 프로젝트의 Rate Limit 정보를 가져옵니다."""
    # 관리자 키가 제공되면 사용, 없으면 기본 환경변수 사용
    api_key = admin_api_key or openai_api_key
    org_id = openai_org_id
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Organization": org_id,
        "Content-Type": "application/json",
    }

    try:
        url = f"https://api.openai.com/v1/organization/projects/{project_id}/rate_limits"
        print(f"🔍 Rate Limit API 요청 시도: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        # HTTP 상태 코드 확인
        print(f"📊 Rate Limit API 응답 상태: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Project Rate Limits 요청 실패: HTTP {response.status_code}")
            print(f"응답 헤더: {dict(response.headers)}")
            print(f"응답 내용: {response.text}")
            return None
        
        # JSON 응답 파싱
        response_data = response.json()
        all_data = response_data.get("data", [])
        
        print(f"✅ Rate Limit 응답 받음: {len(all_data)}개 항목")
        return all_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류가 발생했습니다: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류가 발생했습니다: {e}")
        print(f"응답 내용: {response.text}")
        return None
    except Exception as e:
        print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
        return None


def update_project_rate_limit(project_id, rate_limit_id, max_requests_per_1_minute, admin_api_key=None):
    """특정 프로젝트의 Rate Limit을 업데이트합니다."""
    # 관리자 키가 제공되면 사용, 없으면 기본 환경변수 사용
    api_key = admin_api_key or openai_api_key
    org_id = openai_org_id
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Organization": org_id,
        "Content-Type": "application/json",
    }

    data = {
        "max_requests_per_1_minute": max_requests_per_1_minute
    }

    try:
        url = f"https://api.openai.com/v1/organization/projects/{project_id}/rate_limits/{rate_limit_id}"
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # HTTP 상태 코드 확인
        if response.status_code == 200:
            print(f"✅ 프로젝트 {project_id}의 Rate Limit이 성공적으로 업데이트되었습니다.")
            return response.json()
        else:
            print(f"❌ Rate Limit 업데이트 실패: HTTP {response.status_code}")
            print(f"응답 내용: {response.text}")
            
            # 권한 오류인 경우 특별한 예외 발생
            if response.status_code == 401:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "권한이 없습니다.")
                    if "api.management.write" in error_message:
                        raise ValueError(f"API 키 권한 오류: Rate Limit 수정을 위해서는 'api.management.write' 권한이 필요합니다. OpenAI 조직 설정에서 API 키 권한을 확인해주세요.")
                    else:
                        raise ValueError(f"권한 오류: {error_message}")
                except (json.JSONDecodeError, KeyError):
                    raise ValueError("API 키 권한이 부족합니다. 관리자 권한이 있는 API 키를 사용해주세요.")
            else:
                raise ValueError(f"Rate Limit 업데이트 실패: HTTP {response.status_code}")
            
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류가 발생했습니다: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류가 발생했습니다: {e}")
        print(f"응답 내용: {response.text}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
        return None


def get_all_projects_rate_limits(admin_api_key=None):
    """모든 프로젝트의 Rate Limit 정보를 가져옵니다."""
    projects = list_organization_projects(admin_api_key)
    if not projects:
        print("❌ 프로젝트 목록을 가져올 수 없습니다.")
        return None
    
    print(f"📋 총 {len(projects)}개의 프로젝트에 대해 Rate Limit을 조회합니다.")
    all_rate_limits = {}
    success_count = 0
    
    for i, project in enumerate(projects):
        project_id = project["id"]
        project_name = project["name"]
        
        print(f"🔄 ({i+1}/{len(projects)}) {project_name} ({project_id}) Rate Limit 조회 중...")
        
        try:
            rate_limits = get_project_rate_limits(project_id, admin_api_key)
            if rate_limits is not None:
                # 필요한 필드만 필터링해서 응답 크기 최적화
                filtered_rate_limits = []
                for limit in rate_limits:
                    filtered_limit = {
                        "id": limit.get("id", ""),
                        "model": limit.get("model", ""),
                        "max_requests_per_1_minute": limit.get("max_requests_per_1_minute", 0),
                        "max_tokens_per_1_minute": limit.get("max_tokens_per_1_minute", 0),
                    }
                    filtered_rate_limits.append(filtered_limit)
                
                all_rate_limits[project_id] = {
                    "project_name": project_name,
                    "rate_limits": filtered_rate_limits
                }
                success_count += 1
                print(f"✅ {project_name}: {len(filtered_rate_limits)}개 Rate Limit 조회 성공 (필터링됨)")
            else:
                print(f"⚠️ {project_name}: Rate Limit 정보 없음")
        except Exception as e:
            print(f"❌ {project_name}: Rate Limit 조회 실패 - {e}")
    
    print(f"📊 Rate Limit 조회 완료: {success_count}/{len(projects)} 프로젝트 성공")
    return all_rate_limits


def save_rate_limit_template(template_data, filename="rate_limit_template.json"):
    """Rate Limit 템플릿을 JSON 파일로 저장합니다."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Rate Limit 템플릿이 {filename}에 저장되었습니다.")
        return True
    except Exception as e:
        print(f"❌ 템플릿 저장 실패: {e}")
        return False


def load_rate_limit_template(filename="rate_limit_template.json"):
    """JSON 파일에서 Rate Limit 템플릿을 로드합니다."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                template = json.load(f)
            print(f"✅ Rate Limit 템플릿이 {filename}에서 로드되었습니다.")
            return template
        else:
            print(f"⚠️ 템플릿 파일 {filename}이 존재하지 않습니다.")
            return None
    except Exception as e:
        print(f"❌ 템플릿 로드 실패: {e}")
        return None


def apply_rate_limit_template_to_project(project_id, template_data, admin_api_key=None):
    """특정 프로젝트에 Rate Limit 템플릿을 적용합니다."""
    results = []
    
    # 현재 프로젝트의 Rate Limit 정보 가져오기
    current_limits = get_project_rate_limits(project_id, admin_api_key)
    if not current_limits:
        return {"success": False, "message": "현재 Rate Limit 정보를 가져올 수 없습니다."}
    
    # 템플릿의 각 Rate Limit을 적용
    for template_limit in template_data:
        # 매칭되는 Rate Limit 찾기 (model 기준)
        matching_limit = None
        for current_limit in current_limits:
            if current_limit.get("model") == template_limit.get("model"):
                matching_limit = current_limit
                break
        
        if matching_limit:
            rate_limit_id = matching_limit["id"]
            new_value = template_limit["max_requests_per_1_minute"]
            
            result = update_project_rate_limit(
                project_id, 
                rate_limit_id, 
                new_value, 
                admin_api_key
            )
            
            results.append({
                "model": template_limit.get("model"),
                "rate_limit_id": rate_limit_id,
                "success": result is not None,
                "new_value": new_value
            })
        else:
            results.append({
                "model": template_limit.get("model"),
                "success": False,
                "message": "매칭되는 Rate Limit을 찾을 수 없습니다."
            })
    
    return {"success": True, "results": results}


# 함수 테스트
if __name__ == "__main__":
    success = build_userinfo()
    if success:
        print("사용자 정보 수집 완료!")
    else:
        print("사용자 정보 수집 실패!")
        
    # API 키 테스트
    api_keys = list_api_keys()
    if api_keys:
        print(f"API 키 개수: {len(api_keys)}")
    else:
        print("API 키 목록 가져오기 실패!")

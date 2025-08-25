from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Import existing organization utils
from utils import (
    list_organization_projects,
    get_organization_users,
    get_project_api_keys,
    delete_api_key as utils_delete_api_key,
    bulk_delete_api_keys as utils_bulk_delete_api_keys,
    get_project_rate_limits,
    update_project_rate_limit,
    get_all_projects_rate_limits,
    save_rate_limit_template,
    load_rate_limit_template,
    apply_rate_limit_template_to_project,
    build_userinfo,
    extract_results_from_buckets,
    group_by_userID,
)

app = FastAPI(title="OpenAI Organization API Wrapper", version="1.0.0")

# CORS: allow local dev React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BulkDeleteItem(BaseModel):
    project_id: str
    api_key_id: str
    key_name: Optional[str] = None


class BulkDeleteRequest(BaseModel):
    keys: List[BulkDeleteItem]


class RateLimitUpdateRequest(BaseModel):
    max_requests_per_1_minute: int


class RateLimitTemplateRequest(BaseModel):
    template_data: List[Dict[str, Any]]
    template_name: Optional[str] = "default"


class ApplyTemplateRequest(BaseModel):
    project_id: str
    template_name: Optional[str] = "default"


class UserUsageAnalysisRequest(BaseModel):
    usage_data: Dict[str, Any]  # The uploaded user usage data


class GenerateUserinfoResponse(BaseModel):
    success: bool
    message: str
    userinfo_path: Optional[str] = None
    user_count: Optional[int] = None
    userinfo_data: Optional[List[Dict[str, Any]]] = None


def _extract_admin_key(
    x_admin_api_key: Optional[str], authorization: Optional[str]
) -> Optional[str]:
    # Prefer explicit header
    if x_admin_api_key:
        key = x_admin_api_key.strip()
        # Check if it's a real OpenAI key format
        if key.startswith(('sk-', 'sk-proj-')):
            return key
        else:
            print(f"⚠️ 올바르지 않은 API 키 형식입니다: {key[:10]}...")
            return key  # Still return it for testing purposes
    # Support Authorization: Bearer <token>
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return None


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/org/projects")
async def org_projects(
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    projects = list_organization_projects(admin_key)
    if projects is None:
        raise HTTPException(
            status_code=502, detail="Failed to fetch projects from OpenAI API"
        )
    return {"data": projects, "success": True}


@app.get("/org/users")
async def org_users(
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    users = get_organization_users(admin_key)
    if users is None:
        raise HTTPException(
            status_code=502, detail="Failed to fetch users from OpenAI API"
        )
    return {"data": users, "success": True}


@app.get("/projects/{project_id}/keys")
async def project_api_keys(
    project_id: str,
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    keys = get_project_api_keys(project_id, admin_key)
    if keys is None:
        raise HTTPException(
            status_code=502, detail="Failed to fetch project API keys from OpenAI API"
        )
    return {"data": keys, "success": True}


@app.delete("/projects/{project_id}/keys/{key_id}")
async def delete_key(
    project_id: str,
    key_id: str,
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    ok = utils_delete_api_key(project_id, key_id, admin_key)
    if not ok:
        raise HTTPException(status_code=502, detail="Failed to delete API key")
    return {"success": True}


@app.post("/keys/bulk-delete")
async def bulk_delete(
    body: BulkDeleteRequest,
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    tuples = [
        (item.project_id, item.api_key_id, item.key_name or "") for item in body.keys
    ]
    results = utils_bulk_delete_api_keys(tuples, admin_key)
    return {"success": True, "result": results}


# Rate Limit Management Endpoints

@app.get("/projects/{project_id}/rate_limits")
async def get_project_rate_limits_endpoint(
    project_id: str,
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """특정 프로젝트의 Rate Limit 정보를 가져옵니다."""
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    rate_limits = get_project_rate_limits(project_id, admin_key)
    if rate_limits is None:
        raise HTTPException(
            status_code=502, detail="Failed to fetch rate limits from OpenAI API"
        )
    return {"data": rate_limits, "success": True}


@app.post("/projects/{project_id}/rate_limits/{rate_limit_id}")
async def update_project_rate_limit_endpoint(
    project_id: str,
    rate_limit_id: str,
    body: RateLimitUpdateRequest,
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """특정 프로젝트의 Rate Limit을 업데이트합니다."""
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    
    try:
        result = update_project_rate_limit(
            project_id, rate_limit_id, body.max_requests_per_1_minute, admin_key
        )
        if result is None:
            raise HTTPException(status_code=502, detail="Failed to update rate limit")
        return {"success": True, "data": result}
    except ValueError as e:
        # 권한 오류나 기타 구체적인 오류 메시지를 그대로 전달
        error_message = str(e)
        if "권한" in error_message or "permission" in error_message.lower():
            raise HTTPException(status_code=403, detail=error_message)
        else:
            raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Unexpected error: {str(e)}")


@app.get("/org/rate_limits")
async def get_all_rate_limits(
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """모든 프로젝트의 Rate Limit 정보를 가져옵니다."""
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    all_rate_limits = get_all_projects_rate_limits(admin_key)
    if all_rate_limits is None:
        raise HTTPException(
            status_code=502, detail="Failed to fetch rate limits from OpenAI API"
        )
    return {"data": all_rate_limits, "success": True}


@app.post("/rate_limit_template/save")
async def save_template(
    body: RateLimitTemplateRequest,
) -> Dict[str, Any]:
    """Rate Limit 템플릿을 저장합니다."""
    filename = f"rate_limit_template_{body.template_name}.json"
    success = save_rate_limit_template(body.template_data, filename)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save template")
    return {"success": True, "message": f"Template '{body.template_name}' saved successfully"}


@app.get("/rate_limit_template/load/{template_name}")
async def load_template(
    template_name: str = "default",
) -> Dict[str, Any]:
    """저장된 Rate Limit 템플릿을 로드합니다."""
    filename = f"rate_limit_template_{template_name}.json"
    template_data = load_rate_limit_template(filename)
    if template_data is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"data": template_data, "success": True}


@app.post("/rate_limit_template/apply")
async def apply_template(
    body: ApplyTemplateRequest,
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """특정 프로젝트에 Rate Limit 템플릿을 적용합니다."""
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    
    # 템플릿 로드
    filename = f"rate_limit_template_{body.template_name}.json"
    template_data = load_rate_limit_template(filename)
    if template_data is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 템플릿 적용
    result = apply_rate_limit_template_to_project(
        body.project_id, template_data, admin_key
    )
    if not result.get("success"):
        raise HTTPException(status_code=502, detail=result.get("message", "Failed to apply template"))
    
    return result


@app.post("/generate-userinfo")
async def generate_userinfo_from_usage(
    body: UserUsageAnalysisRequest,
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> GenerateUserinfoResponse:
    """사용자별 사용량 데이터에서 user_id들을 추출하고 OpenAI API를 통해 userinfo.json을 생성합니다."""
    print("🚀 /generate-userinfo API 호출됨!")
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    
    try:
        # 사용량 데이터에서 사용자 ID들 추출
        usage_data = body.usage_data
        user_ids = set()
        
        # 버킷 구조에서 결과 추출
        results = extract_results_from_buckets(usage_data)
        
        # 모든 user_id 수집
        for result in results:
            user_id = result.get("user_id")
            if user_id and user_id != "unknown_user":
                user_ids.add(user_id)
        
        print(f"📊 사용량 데이터에서 {len(user_ids)}개의 고유한 사용자 ID를 발견했습니다: {list(user_ids)[:5]}{'...' if len(user_ids) > 5 else ''}")
        
        if not user_ids:
            return GenerateUserinfoResponse(
                success=False,
                message="사용량 데이터에서 사용자 ID를 찾을 수 없습니다."
            )
        
        # OpenAI API를 통해 조직 사용자 정보 가져오기
        print("🔍 OpenAI Organization API에서 사용자 정보를 가져오는 중...")
        success = build_userinfo(admin_key)
        
        if success:
            # 생성된 userinfo.json 파일을 읽어서 응답에 포함
            try:
                import json
                from utils import INFO_FILEPATH
                with open(INFO_FILEPATH, "r", encoding="utf-8") as f:
                    userinfo_data = json.load(f)
                
                return GenerateUserinfoResponse(
                    success=True,
                    message=f"사용자 정보 파일이 성공적으로 생성되었습니다. {len(user_ids)}개의 사용자 ID가 발견되었습니다.",
                    userinfo_path="userinfo.json",
                    user_count=len(user_ids),
                    userinfo_data=userinfo_data
                )
            except Exception as e:
                print(f"⚠️ 생성된 userinfo.json 파일 읽기 실패: {e}")
                return GenerateUserinfoResponse(
                    success=True,
                    message=f"사용자 정보 파일이 성공적으로 생성되었습니다. {len(user_ids)}개의 사용자 ID가 발견되었습니다. (파일 읽기 실패)",
                    userinfo_path="userinfo.json",
                    user_count=len(user_ids)
                )
        else:
            # API 키 권한 문제인 경우, mock userinfo 데이터를 생성해서 반환
            print("⚠️ OpenAI API 키 권한 문제로 인해 mock userinfo 데이터를 생성합니다.")
            mock_userinfo_data = {}
            
            # 발견된 user_id들에 대해 mock 사용자 정보 생성
            for i, user_id in enumerate(list(user_ids)[:10]):  # 최대 10개까지만
                mock_userinfo_data[user_id] = {
                    "name": f"테스트 사용자 {i+1}",
                    "email": f"user{i+1}@example.com"
                }
            
            return GenerateUserinfoResponse(
                success=True,
                message=f"API 키 권한 문제로 인해 mock 사용자 정보를 생성했습니다. {len(user_ids)}개의 사용자 ID가 발견되었습니다.",
                userinfo_path="mock_userinfo.json",
                user_count=len(user_ids),
                userinfo_data=mock_userinfo_data
            )
    
    except Exception as e:
        print(f"❌ userinfo 생성 중 오류 발생: {e}")
        return GenerateUserinfoResponse(
            success=False,
            message=f"userinfo 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.post("/build-userinfo")
async def build_userinfo_endpoint(
    x_admin_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> GenerateUserinfoResponse:
    """직접적으로 OpenAI Organization API를 통해 userinfo.json을 생성합니다."""
    admin_key = _extract_admin_key(x_admin_api_key, authorization)
    
    try:
        print("🔍 OpenAI Organization API에서 사용자 정보를 가져오는 중...")
        success = build_userinfo(admin_key)
        
        if success:
            return GenerateUserinfoResponse(
                success=True,
                message="사용자 정보 파일이 성공적으로 생성되었습니다.",
                userinfo_path="userinfo.json"
            )
        else:
            return GenerateUserinfoResponse(
                success=False,
                message="OpenAI API에서 사용자 정보를 가져오는데 실패했습니다. API 키와 권한을 확인해주세요."
            )
    
    except Exception as e:
        print(f"❌ userinfo 생성 중 오류 발생: {e}")
        return GenerateUserinfoResponse(
            success=False,
            message=f"userinfo 생성 중 오류가 발생했습니다: {str(e)}"
        )


# To run: uvicorn org_api_server:app --reload --port 8000

export const ORG_API_BASE =
  import.meta.env.VITE_ORG_API_BASE || "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit = {},
  adminKey?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (adminKey) headers["X-Admin-Api-Key"] = adminKey;

  // Add timeout for rate limit requests (120 seconds for large datasets)
  const timeout = path.includes('/rate_limits') ? 120000 : 10000;
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(`${ORG_API_BASE}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (!res.ok) {
      const text = await res.text();
      try {
        // JSON 에러 응답인 경우 detail 필드 추출
        const errorData = JSON.parse(text);
        const errorMessage = errorData.detail || errorData.message || text;
        throw new Error(errorMessage);
      } catch (parseError) {
        // JSON 파싱 실패시 원본 텍스트 사용
        throw new Error(text || `Request failed: ${res.status}`);
      }
    }
    return res.json();
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout/1000}s. The server is still processing the request.`);
    }
    throw error;
  }
}

export async function fetchProjects(adminKey?: string): Promise<any[]> {
  const json = await request<{ data: any[] }>(`/org/projects`, {}, adminKey);
  return json.data || [];
}

export async function fetchUsers(adminKey?: string): Promise<any[]> {
  const json = await request<{ data: any[] }>(`/org/users`, {}, adminKey);
  return json.data || [];
}

// Rate Limit Management APIs

export async function fetchProjectRateLimits(projectId: string, adminKey?: string): Promise<any[]> {
  const json = await request<{ data: any[] }>(`/projects/${projectId}/rate_limits`, {}, adminKey);
  return json.data || [];
}

export async function updateProjectRateLimit(
  projectId: string, 
  rateLimitId: string, 
  maxRequestsPerMinute: number, 
  adminKey?: string
): Promise<any> {
  console.log(`🔧 Rate Limit 업데이트 요청: ${projectId}/${rateLimitId} → max_requests_per_1_minute: ${maxRequestsPerMinute} (키: ${adminKey?.substring(0, 20)}...)`);
  return await request<any>(
    `/projects/${projectId}/rate_limits/${rateLimitId}`,
    {
      method: 'POST',
      body: JSON.stringify({ max_requests_per_1_minute: maxRequestsPerMinute }),
    },
    adminKey
  );
}

export async function fetchAllRateLimits(adminKey?: string): Promise<any> {
  const json = await request<{ data: any }>(`/org/rate_limits`, {}, adminKey);
  return json.data || {};
}

export async function saveRateLimitTemplate(templateData: any[], templateName: string = 'default'): Promise<any> {
  return await request<any>(
    `/rate_limit_template/save`,
    {
      method: 'POST',
      body: JSON.stringify({ template_data: templateData, template_name: templateName }),
    }
  );
}

export async function loadRateLimitTemplate(templateName: string = 'default'): Promise<any[]> {
  const json = await request<{ data: any[] }>(`/rate_limit_template/load/${templateName}`);
  return json.data || [];
}

export async function applyRateLimitTemplate(
  projectId: string, 
  templateName: string = 'default', 
  adminKey?: string
): Promise<any> {
  return await request<any>(
    `/rate_limit_template/apply`,
    {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, template_name: templateName }),
    },
    adminKey
  );
}

// Local Storage utilities for Rate Limit caching
const RATE_LIMITS_CACHE_KEY = 'openai_tracker_rate_limits_cache';
const RATE_LIMITS_TIMESTAMP_KEY = 'openai_tracker_rate_limits_timestamp';

export function saveRateLimitsToCache(rateLimitsData: any): void {
  try {
    localStorage.setItem(RATE_LIMITS_CACHE_KEY, JSON.stringify(rateLimitsData));
    localStorage.setItem(RATE_LIMITS_TIMESTAMP_KEY, Date.now().toString());
    console.log('📦 Rate Limit 데이터가 로컬 저장소에 저장되었습니다:', Object.keys(rateLimitsData).length, '개 프로젝트');
  } catch (error) {
    console.error('❌ Rate Limit 데이터 저장 실패:', error);
  }
}

export function loadRateLimitsFromCache(): any | null {
  try {
    const cachedData = localStorage.getItem(RATE_LIMITS_CACHE_KEY);
    const timestamp = localStorage.getItem(RATE_LIMITS_TIMESTAMP_KEY);
    
    if (cachedData && timestamp) {
      const data = JSON.parse(cachedData);
      const cacheAge = Date.now() - parseInt(timestamp);
      const cacheAgeHours = cacheAge / (1000 * 60 * 60);
      
      console.log('📁 저장된 Rate Limit 데이터 발견:', Object.keys(data).length, '개 프로젝트, 캐시 생성:', cacheAgeHours.toFixed(1), '시간 전');
      return data;
    }
    
    return null;
  } catch (error) {
    console.error('❌ Rate Limit 데이터 로드 실패:', error);
    return null;
  }
}

export function clearRateLimitsCache(): void {
  try {
    localStorage.removeItem(RATE_LIMITS_CACHE_KEY);
    localStorage.removeItem(RATE_LIMITS_TIMESTAMP_KEY);
    console.log('🗑️ Rate Limit 캐시가 삭제되었습니다.');
  } catch (error) {
    console.error('❌ Rate Limit 캐시 삭제 실패:', error);
  }
}

export function getCacheInfo(): { hasCache: boolean; cacheAge: number; projectCount: number } {
  try {
    const cachedData = localStorage.getItem(RATE_LIMITS_CACHE_KEY);
    const timestamp = localStorage.getItem(RATE_LIMITS_TIMESTAMP_KEY);
    
    if (cachedData && timestamp) {
      const data = JSON.parse(cachedData);
      const cacheAge = Date.now() - parseInt(timestamp);
      
      return {
        hasCache: true,
        cacheAge,
        projectCount: Object.keys(data).length
      };
    }
    
    return { hasCache: false, cacheAge: 0, projectCount: 0 };
  } catch (error) {
    console.error('❌ 캐시 정보 확인 실패:', error);
    return { hasCache: false, cacheAge: 0, projectCount: 0 };
  }
}


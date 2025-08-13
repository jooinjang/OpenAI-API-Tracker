import React, { useState } from "react";
import { useProjects, useBudgets, useProcessedData, useAdminApiKey, useAppActions } from "@/store/useAppStore";
import { AppleCard } from "@/components/ui/AppleCard";
import { AppleButton } from "@/components/ui/AppleButton";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import {
  fetchAllRateLimits,
  fetchProjectRateLimits,
  saveRateLimitTemplate,
  loadRateLimitTemplate,
  applyRateLimitTemplate,
  updateProjectRateLimit,
  saveRateLimitsToCache,
  loadRateLimitsFromCache,
  clearRateLimitsCache,
  getCacheInfo,
} from "@/utils/api";
import { ProjectRateLimits } from "@/types";

export const RateLimits: React.FC = () => {
  const projects = useProjects();
  const budgets = useBudgets();
  const processedData = useProcessedData();
  const adminApiKey = useAdminApiKey();
  const { setAdminApiKey } = useAppActions();

  // Admin API key state (use global state, fallback to local if needed)
  const [adminKey, setAdminKey] = useState<string>(adminApiKey || "");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Rate limits data
  const [allRateLimits, setAllRateLimits] = useState<Record<string, ProjectRateLimits>>({});
  const [hasTemplate, setHasTemplate] = useState<boolean>(false);

  // Cache state
  const [cacheInfo, setCacheInfo] = useState<{ hasCache: boolean; cacheAge: number; projectCount: number }>({ hasCache: false, cacheAge: 0, projectCount: 0 });

  // UI state
  const [showActions, setShowActions] = useState<boolean>(false);
  const [processingProjectId, setProcessingProjectId] = useState<string | null>(null);
  
  // New UI states for dropdown and filter
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [showOnlyOverBudget, setShowOnlyOverBudget] = useState<boolean>(false);
  
  // Modal state
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    type: 'disable' | 'restore' | 'save_template';
    projectId?: string;
    projectName?: string;
  }>({ isOpen: false, type: 'disable' });

  // Sync with global admin API key
  React.useEffect(() => {
    if (adminApiKey) {
      setAdminKey(adminApiKey);
    }
  }, [adminApiKey]);

  // Load cached data on component mount
  React.useEffect(() => {
    const cache = getCacheInfo();
    setCacheInfo(cache);
    
    if (cache.hasCache) {
      const cachedData = loadRateLimitsFromCache();
      if (cachedData && Object.keys(cachedData).length > 0) {
        setAllRateLimits(cachedData);
        setShowActions(true);
        
        // Check if template exists
        loadRateLimitTemplate('default')
          .then(() => setHasTemplate(true))
          .catch(() => setHasTemplate(false));
      }
    }
  }, []);

  // Load rate limits data
  const loadRateLimits = async () => {
    if (!adminKey.trim()) {
      setError("관리자 API 키를 입력해주세요.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      console.log("🔄 Rate Limit 데이터 요청 시작...");
      const rateLimitsData = await fetchAllRateLimits(adminKey);
      console.log("✅ Rate Limit 데이터 수신 완료:", Object.keys(rateLimitsData).length, "개 프로젝트");
      
      // Save to cache
      saveRateLimitsToCache(rateLimitsData);
      
      setAllRateLimits(rateLimitsData);
      setShowActions(true);
      
      // Update cache info
      const updatedCache = getCacheInfo();
      setCacheInfo(updatedCache);
      
      // Check if template exists and load it
      try {
        await loadRateLimitTemplate('default');
        setHasTemplate(true);
      } catch (e) {
        setHasTemplate(false);
      }
      
      setError(null);
    } catch (e) {
      console.error("❌ Rate Limit 데이터 로드 실패:", e);
      setError(
        e instanceof Error ? e.message : "Rate Limit 정보를 불러오지 못했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  // Save current rate limits as template
  const saveAsTemplate = async () => {
    try {
      // Find project with the most updatable rate limits to use as comprehensive template
      let bestProject = null;
      let maxUpdatableModels = 0;
      
      for (const project of Object.values(allRateLimits)) {
        // Count updatable models (excluding fine-tune and non-updatable models)
        const updatableCount = project.rate_limits.filter(rateLimit => 
          !rateLimit.id.startsWith("rl-ft:") && // Exclude fine-tune models
          rateLimit.id !== "rl-gpt-image-1"    // Exclude other non-updatable models
        ).length;
        
        if (updatableCount > maxUpdatableModels) {
          maxUpdatableModels = updatableCount;
          bestProject = project;
        }
      }
      
      if (!bestProject) {
        setError("템플릿으로 저장할 Rate Limit 정보가 없습니다.");
        return;
      }

      // Filter out fine-tune and non-updatable models for template
      const templateRateLimits = bestProject.rate_limits.filter(rateLimit => 
        !rateLimit.id.startsWith("rl-ft:") && // Exclude fine-tune models
        rateLimit.id !== "rl-gpt-image-1"    // Exclude other non-updatable models
      );

      console.log(`📋 템플릿 저장: ${bestProject.project_name} 프로젝트 기준 (${templateRateLimits.length}개 업데이트 가능 모델)`);
      console.log(`📝 템플릿에 포함된 모델들:`, templateRateLimits.map(rl => `${rl.model} (${rl.max_requests_per_1_minute})`));

      await saveRateLimitTemplate(templateRateLimits, 'default');
      setHasTemplate(true);
      setError(null);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "템플릿 저장에 실패했습니다."
      );
    }
  };

  // Disable rate limits (set to 0)
  const disableRateLimits = async (projectId: string) => {
    try {
      const projectRateLimits = allRateLimits[projectId];
      if (!projectRateLimits) return;

      // Check if admin key is provided
      if (!adminKey || !adminKey.trim()) {
        setError("관리자 API 키를 입력해주세요.");
        return;
      }

      setProcessingProjectId(projectId);
      console.log(`🔄 ${projectRateLimits.project_name}: ${projectRateLimits.rate_limits.length}개 Rate Limit 비활성화 시작...`);
      console.log(`🔑 사용 중인 API 키:`, adminKey?.substring(0, 20) + '...');

      // Filter out fine-tune models and non-updatable models before processing
      const updatableRateLimits = projectRateLimits.rate_limits.filter(rateLimit => 
        !rateLimit.id.startsWith("rl-ft:") && // Exclude fine-tune models
        rateLimit.id !== "rl-gpt-image-1"    // Exclude other non-updatable models
      );
      
      // Batch processing to avoid timeout issues - process in chunks of 5
      console.log(`📋 비활성화할 모델 목록 (총 ${updatableRateLimits.length}개):`, updatableRateLimits.map(rl => `${rl.id} (${rl.model}): ${rl.max_requests_per_1_minute} → 0`));
      console.log(`⚠️ 스킵된 모델 (업데이트 불가):`, projectRateLimits.rate_limits.filter(rl => rl.id.startsWith("rl-ft:") || rl.id === "rl-gpt-image-1").map(rl => `${rl.id} (${rl.model})`));
      
      const BATCH_SIZE = 20; // Process 20 models at a time to avoid timeout
      let processedCount = 0;
      
      for (let i = 0; i < updatableRateLimits.length; i += BATCH_SIZE) {
        const batch = updatableRateLimits.slice(i, i + BATCH_SIZE);
        console.log(`🔄 배치 ${Math.floor(i/BATCH_SIZE) + 1}/${Math.ceil(updatableRateLimits.length/BATCH_SIZE)} 처리 중... (${batch.length}개 모델)`);
        
        const batchPromises = batch.map(rateLimit => {
          console.log(`🔧 비활성화 중: ${rateLimit.id} (${rateLimit.model}) - max_requests_per_1_minute: ${rateLimit.max_requests_per_1_minute} → 0`);
          return updateProjectRateLimit(
            projectId,
            rateLimit.id,
            0, // Set max_requests_per_1_minute to 0 to disable ALL models
            adminKey
          );
        });

        await Promise.all(batchPromises);
        processedCount += batch.length;
        console.log(`✅ 배치 완료: ${processedCount}/${updatableRateLimits.length}개 모델 처리됨`);
        
        // Add small delay between batches to avoid overwhelming the API
        if (i + BATCH_SIZE < updatableRateLimits.length) {
          await new Promise(resolve => setTimeout(resolve, 100)); // 100ms delay
        }
      }
      
      console.log(`🎉 ${projectRateLimits.project_name}: ${processedCount}개 Rate Limit 비활성화 완료`);

      // Update only this project's data instead of reloading everything
      const updatedProjectData = await fetchProjectRateLimits(projectId, adminKey);
      
      // Update state and cache together
      setAllRateLimits(prev => {
        const updatedAllData = {
          ...prev,
          [projectId]: {
            ...projectRateLimits,
            rate_limits: updatedProjectData
          }
        };
        
        // Update cache with the new data
        saveRateLimitsToCache(updatedAllData);
        
        return updatedAllData;
      });

      setError(null);
    } catch (e) {
      console.error(`❌ Rate Limit 비활성화 실패:`, e);
      setError(
        e instanceof Error ? e.message : "Rate Limit 비활성화에 실패했습니다."
      );
    } finally {
      setProcessingProjectId(null);
    }
  };

  // Restore rate limits from template
  const restoreFromTemplate = async (projectId: string) => {
    try {
      const projectRateLimits = allRateLimits[projectId];
      if (!projectRateLimits) return;

      // Check if admin key is provided
      if (!adminKey || !adminKey.trim()) {
        setError("관리자 API 키를 입력해주세요.");
        return;
      }

      setProcessingProjectId(projectId);
      console.log(`🔄 ${projectRateLimits.project_name}: 템플릿에서 Rate Limit 복구 시작...`);
      
      // Load template data
      const templateData = await loadRateLimitTemplate('default');
      console.log(`📋 템플릿 데이터 로드 완료: ${templateData.length}개 Rate Limit`);
      
      // Create mapping of template data by model
      const templateMap = new Map(
        templateData.map(template => [template.model, template.max_requests_per_1_minute])
      );
      
      // Filter out fine-tune models and non-updatable models before processing
      const updatableRateLimits = projectRateLimits.rate_limits.filter(rateLimit => 
        !rateLimit.id.startsWith("rl-ft:") && // Exclude fine-tune models
        rateLimit.id !== "rl-gpt-image-1" && // Exclude other non-updatable models
        templateMap.has(rateLimit.model) // Only include models that exist in template
      );

      // Batch processing to avoid timeout issues - process in chunks of 5
      console.log(`📋 복구할 모델 목록 (총 ${updatableRateLimits.length}개):`, updatableRateLimits.map(rl => `${rl.id} (${rl.model}): ${rl.max_requests_per_1_minute} → ${templateMap.get(rl.model)}`));
      console.log(`⚠️ 스킵된 모델 (업데이트 불가):`, projectRateLimits.rate_limits.filter(rl => rl.id.startsWith("rl-ft:") || rl.id === "rl-gpt-image-1").map(rl => `${rl.id} (${rl.model})`));

      const BATCH_SIZE = 20; // Process 20 models at a time to avoid timeout
      let processedCount = 0;
      
      for (let i = 0; i < updatableRateLimits.length; i += BATCH_SIZE) {
        const batch = updatableRateLimits.slice(i, i + BATCH_SIZE);
        console.log(`🔄 배치 ${Math.floor(i/BATCH_SIZE) + 1}/${Math.ceil(updatableRateLimits.length/BATCH_SIZE)} 처리 중... (${batch.length}개 모델)`);
        
        const batchPromises = batch.map(rateLimit => {
          const templateValue = templateMap.get(rateLimit.model);
          console.log(`🔧 복구 중: ${rateLimit.id} (${rateLimit.model}) - ${rateLimit.max_requests_per_1_minute} → ${templateValue}`);
          return updateProjectRateLimit(
            projectId,
            rateLimit.id,
            templateValue,
            adminKey
          );
        });

        await Promise.all(batchPromises);
        processedCount += batch.length;
        console.log(`✅ 배치 완료: ${processedCount}/${updatableRateLimits.length}개 모델 처리됨`);
        
        // Add small delay between batches to avoid overwhelming the API
        if (i + BATCH_SIZE < updatableRateLimits.length) {
          await new Promise(resolve => setTimeout(resolve, 100)); // 100ms delay
        }
      }
      
      console.log(`🎉 ${projectRateLimits.project_name}: ${processedCount}개 Rate Limit 템플릿 복구 완료`);
      
      // Update only this project's data instead of reloading everything
      const updatedProjectData = await fetchProjectRateLimits(projectId, adminKey);
      console.log(`🔍 복구 후 데이터 확인:`, updatedProjectData.map(limit => `${limit.model}: ${limit.max_requests_per_1_minute}`));
      
      // Update state and cache together
      setAllRateLimits(prev => {
        const updatedAllData = {
          ...prev,
          [projectId]: {
            ...projectRateLimits,
            rate_limits: updatedProjectData
          }
        };
        
        // Update cache with the new data
        saveRateLimitsToCache(updatedAllData);
        
        return updatedAllData;
      });
      
      setError(null);
    } catch (e) {
      console.error(`❌ 템플릿 복구 실패:`, e);
      setError(
        e instanceof Error ? e.message : "템플릿 적용에 실패했습니다."
      );
    } finally {
      setProcessingProjectId(null);
    }
  };

  const executeAction = async () => {
    if (confirmModal.type === 'save_template') {
      await saveAsTemplate();
    } else if (confirmModal.type === 'disable' && confirmModal.projectId) {
      await disableRateLimits(confirmModal.projectId);
    } else if (confirmModal.type === 'restore' && confirmModal.projectId) {
      await restoreFromTemplate(confirmModal.projectId);
    }
    setConfirmModal({ isOpen: false, type: 'disable' });
  };

  // Clear cached rate limits data
  const clearCachedData = () => {
    clearRateLimitsCache();
    setAllRateLimits({});
    setShowActions(false);
    setHasTemplate(false);
    setCacheInfo({ hasCache: false, cacheAge: 0, projectCount: 0 });
    setError(null);
    console.log("🗑️ 저장된 Rate Limit 데이터가 모두 삭제되었습니다.");
  };

  // Check if project has any active rate limits
  const hasActiveRateLimits = (projectId: string): boolean => {
    const projectRateLimits = allRateLimits[projectId];
    console.log(`🔍 hasActiveRateLimits 호출: ${projectId}`, {
      hasProject: !!projectRateLimits,
      rateLimitsCount: projectRateLimits?.rate_limits?.length || 0,
      rateLimits: projectRateLimits?.rate_limits?.map(l => `${l.model}: ${l.max_requests_per_1_minute}`) || []
    });
    
    if (!projectRateLimits) {
      console.log(`❌ hasActiveRateLimits: 프로젝트 ${projectId}의 데이터가 없음`);
      return false;
    }
    
    if (!projectRateLimits.rate_limits) {
      console.log(`❌ hasActiveRateLimits: 프로젝트 ${projectId}의 rate_limits 속성이 없음`);
      return false;
    }
    
    const activeCount = projectRateLimits.rate_limits.filter(limit => limit.max_requests_per_1_minute > 0).length;
    console.log(`📊 hasActiveRateLimits: 프로젝트 ${projectId} - 활성화된 Rate Limit: ${activeCount}개`);
    
    return activeCount > 0;
  };

  // Check if project is over budget
  const isProjectOverBudget = (projectId: string): boolean => {
    const budget = budgets[projectId];
    if (!budget || !processedData || !processedData.usageByProject) return false;
    
    const projectUsage = processedData.usageByProject.find(p => p.projectId === projectId);
    if (!projectUsage) return false;
    
    return projectUsage.cost > budget.amount;
  };

  // Get filtered project list based on toggle
  const getFilteredProjects = (): Array<{id: string, name: string}> => {
    const projectsList = Object.values(projects);
    
    if (!showOnlyOverBudget) {
      return projectsList;
    }
    
    return projectsList.filter(project => isProjectOverBudget(project.id));
  };

  // Auto-select first project when filters change
  React.useEffect(() => {
    const filteredProjects = getFilteredProjects();
    if (filteredProjects.length > 0 && !selectedProjectId) {
      setSelectedProjectId(filteredProjects[0].id);
    } else if (filteredProjects.length === 0) {
      setSelectedProjectId("");
    } else if (selectedProjectId && !filteredProjects.find(p => p.id === selectedProjectId)) {
      setSelectedProjectId(filteredProjects[0].id);
    }
  }, [showOnlyOverBudget, projects, selectedProjectId]);

  // Check if we have projects from Organization API
  if (Object.keys(projects).length === 0) {
    return (
      <div className="p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-8 lg:mb-12 mt-4 lg:mt-6">
            <h1 className="mb-3 text-2xl font-bold text-text-primary sm:text-3xl">
              ⚙️ Rate Limit 관리
            </h1>
            <p className="text-lg text-text-secondary mb-6">
              프로젝트 정보가 없습니다. 먼저 예산 관리 탭에서 관리자 API 키로 프로젝트 목록을 불러와주세요.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8 lg:mb-12 mt-4 lg:mt-6 flex items-center justify-between">
          <div>
            <h1 className="mb-3 text-2xl font-bold text-text-primary sm:text-3xl">
              ⚙️ Rate Limit 관리
            </h1>
            <p className="text-text-secondary">
              프로젝트별 API Rate Limit 설정 및 템플릿 관리
            </p>
          </div>
        </div>

        {/* Cache Status Section */}
        {cacheInfo.hasCache && (
          <AppleCard className="mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="mb-2 text-lg font-semibold">💾 저장된 Rate Limit 데이터</h3>
                <div className="text-sm text-text-secondary">
                  <p>📊 {cacheInfo.projectCount}개 프로젝트 • 저장 시점: {Math.floor(cacheInfo.cacheAge / (1000 * 60 * 60))}시간 {Math.floor((cacheInfo.cacheAge % (1000 * 60 * 60)) / (1000 * 60))}분 전</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <AppleButton
                  variant="ghost"
                  size="sm"
                  onClick={clearCachedData}
                  className="text-apple-red hover:bg-red-50 dark:hover:bg-red-950/20"
                >
                  🗑️ 초기화
                </AppleButton>
              </div>
            </div>
          </AppleCard>
        )}

        {/* Admin Key Input Section */}
        {(!showActions || (showActions && (!adminKey || !adminKey.trim()))) && (
          <AppleCard className="mb-8">
            <h3 className="mb-4 text-lg font-semibold">
              🔑 {showActions ? "Rate Limit 수정을 위한 관리자 API 키 입력" : cacheInfo.hasCache ? "새로운 Rate Limit 수집" : "관리자 API 키 입력"}
            </h3>
            <div className="grid grid-cols-1 items-end gap-4 md:grid-cols-3">
              <div className="md:col-span-2">
                <label className="mb-2 block text-sm font-medium text-text-primary">
                  관리자 API 키 (Bearer)
                </label>
                <input
                  type="password"
                  value={adminKey}
                  onChange={(e) => setAdminKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full rounded-lg border border-border-primary px-3 py-2 focus:border-apple-blue focus:ring-2 focus:ring-apple-blue"
                />
                <p className="mt-1 text-xs text-text-tertiary">
                  {showActions ? "저장된 Rate Limit 데이터는 있지만, 설정을 변경하려면 관리자 API 키가 필요합니다." : "Rate Limit 정보를 불러오고 설정을 변경하기 위해 필요합니다."}
                </p>
                <div className="mt-2 rounded-md bg-apple-orange/10 p-2 border border-apple-orange/20">
                  <p className="text-xs text-apple-orange">
                    ⚠️ <strong>권한 요구사항:</strong> Rate Limit 수정을 위해서는 API 키에 <code>api.management.write</code> 권한이 필요합니다. 
                    OpenAI 조직 설정에서 "All" 권한 또는 "Rate Limit Management Write" 권한이 있는 API 키를 사용해주세요.
                  </p>
                </div>
              </div>
              <div className="flex space-x-2">
                <AppleButton variant="primary" onClick={loadRateLimits} disabled={loading}>
                  {loading ? "📊 데이터 수집 중... (최대 2분 소요)" : "Rate Limit 불러오기"}
                </AppleButton>
                {showActions && (!adminKey || !adminKey.trim()) && (
                  <AppleButton 
                    variant="secondary" 
                    onClick={() => {
                      if (adminKey && adminKey.trim()) {
                        setError(null);
                      } else {
                        setError("관리자 API 키를 입력해주세요.");
                      }
                    }}
                    disabled={!adminKey || !adminKey.trim()}
                  >
                    키 입력 확인
                  </AppleButton>
                )}
              </div>
            </div>
            {error && <div className="mt-3 text-sm text-apple-red">{error}</div>}
          </AppleCard>
        )}

        {/* Template Management */}
        {showActions && (
          <AppleCard className="mb-8">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold">📋 템플릿 관리</h3>
              <div className="flex space-x-2">
                {!hasTemplate && (
                  <AppleButton
                    variant="secondary"
                    onClick={() => setConfirmModal({ isOpen: true, type: 'save_template' })}
                  >
                    📥 현재 설정을 템플릿으로 저장
                  </AppleButton>
                )}
                <AppleButton
                  variant="ghost"
                  onClick={loadRateLimits}
                  disabled={loading}
                >
                  🔄 새로고침
                </AppleButton>
                <AppleButton
                  variant="ghost"
                  onClick={clearCachedData}
                  className="text-apple-red hover:bg-red-50 dark:hover:bg-red-950/20"
                >
                  🗑️ 초기화
                </AppleButton>
              </div>
            </div>
            
            {hasTemplate ? (
              <div className="rounded-lg bg-apple-green/10 p-4 border border-apple-green/20">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-apple-green">✅</span>
                  <span className="font-medium">템플릿이 저장되어 있습니다</span>
                </div>
                <p className="text-sm text-text-secondary">
                  비활성화된 프로젝트를 원래 설정으로 복구할 수 있습니다.
                </p>
              </div>
            ) : (
              <div className="rounded-lg bg-apple-orange/10 p-4 border border-apple-orange/20">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-apple-orange">⚠️</span>
                  <span className="font-medium">템플릿이 저장되지 않았습니다</span>
                </div>
                <p className="text-sm text-text-secondary">
                  현재 Rate Limit 설정을 템플릿으로 저장하여 나중에 복구할 수 있도록 하세요.
                </p>
              </div>
            )}
          </AppleCard>
        )}

        {/* Project Selection and Filter */}
        {showActions && Object.keys(allRateLimits).length > 0 && (
          <>
            <AppleCard className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">🚦 프로젝트 선택</h3>
                <div className="flex items-center space-x-2">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showOnlyOverBudget}
                      onChange={(e) => setShowOnlyOverBudget(e.target.checked)}
                      className="rounded border-border-primary text-apple-blue focus:ring-apple-blue"
                    />
                    <span className="text-sm text-text-secondary">예산을 초과한 프로젝트만 표시</span>
                  </label>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    프로젝트 선택
                  </label>
                  <select
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    className="w-full rounded-lg border border-border-primary px-3 py-2 focus:border-apple-blue focus:ring-2 focus:ring-apple-blue"
                  >
                    <option value="">프로젝트를 선택하세요</option>
                    {getFilteredProjects().map((project) => {
                      const isOverBudget = isProjectOverBudget(project.id);
                      const hasRateLimit = allRateLimits[project.id];
                      return (
                        <option key={project.id} value={project.id}>
                          {project.name}
                          {isOverBudget ? " (예산 초과)" : ""}
                          {!hasRateLimit ? " (Rate Limit 없음)" : ""}
                        </option>
                      );
                    })}
                  </select>
                </div>
                
                <div className="flex items-end">
                  <div className="text-sm text-text-secondary">
                    {showOnlyOverBudget ? (
                      <>
                        <span className="text-apple-red">⚠️ 예산 초과 프로젝트: {getFilteredProjects().length}개</span>
                      </>
                    ) : (
                      <>
                        <span>총 프로젝트: {getFilteredProjects().length}개</span>
                        {Object.values(projects).filter(p => isProjectOverBudget(p.id)).length > 0 && (
                          <span className="text-apple-red ml-2">
                            (예산 초과: {Object.values(projects).filter(p => isProjectOverBudget(p.id)).length}개)
                          </span>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            </AppleCard>

            {/* Selected Project Rate Limits */}
            {selectedProjectId && allRateLimits[selectedProjectId] && (
              <AppleCard>
                <h3 className="mb-6 text-lg font-semibold">🚦 Rate Limit 상태</h3>
                {(() => {
                  const projectRateLimits = allRateLimits[selectedProjectId];
                  console.log(`🔍 렌더링: ${selectedProjectId}`, {
                    hasData: !!projectRateLimits,
                    projectName: projectRateLimits?.project_name,
                    rateLimitsLength: projectRateLimits?.rate_limits?.length
                  });
                  
                  if (!projectRateLimits) {
                    console.log(`❌ 렌더링 오류: ${selectedProjectId} 데이터 없음`);
                    return <div className="text-center py-8 text-text-secondary">프로젝트 데이터를 불러올 수 없습니다.</div>;
                  }
                  
                  const isActive = hasActiveRateLimits(selectedProjectId);
                  const isOverBudget = isProjectOverBudget(selectedProjectId);
                  
                  return (
                    <div className="rounded-lg border border-border-primary p-4">
                      <div className="mb-4 flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold text-text-primary flex items-center space-x-2">
                            <span>{projectRateLimits.project_name}</span>
                            {isOverBudget && (
                              <span className="inline-flex px-2 py-1 rounded-full text-xs font-medium bg-apple-red/20 text-apple-red">
                                💰 예산 초과
                              </span>
                            )}
                          </h4>
                          <p className="text-sm text-text-secondary">
                            Project ID: {selectedProjectId}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          {processingProjectId === selectedProjectId ? (
                            <span className="inline-flex px-2 py-1 rounded-full text-xs font-medium bg-apple-blue/20 text-apple-blue">
                              🔄 처리 중...
                            </span>
                          ) : (
                            <span
                              className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                                isActive
                                  ? "bg-apple-green/20 text-apple-green"
                                  : "bg-apple-red/20 text-apple-red"
                              }`}
                            >
                              {isActive ? "✅ 활성화" : "⛔ 비활성화"}
                            </span>
                          )}
                          <div className="flex space-x-1">
                            {processingProjectId === selectedProjectId ? null : (
                              <>
                                <AppleButton
                                  variant="ghost"
                                  size="sm"
                                  onClick={() =>
                                    setConfirmModal({
                                      isOpen: true,
                                      type: 'disable',
                                      projectId: selectedProjectId,
                                      projectName: projectRateLimits.project_name,
                                    })
                                  }
                                  className="text-apple-red hover:bg-red-50 dark:hover:bg-red-950/20"
                                >
                                  ⛔ 비활성화
                                </AppleButton>
                                {hasTemplate && (
                                  <AppleButton
                                    variant="ghost"
                                    size="sm"
                                    onClick={() =>
                                      setConfirmModal({
                                        isOpen: true,
                                        type: 'restore',
                                        projectId: selectedProjectId,
                                        projectName: projectRateLimits.project_name,
                                      })
                                    }
                                    className="text-apple-green hover:bg-green-50 dark:hover:bg-green-950/20"
                                  >
                                    🔄 템플릿 적용
                                  </AppleButton>
                                )}
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {/* Rate Limits Details */}
                      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                        {projectRateLimits.rate_limits && projectRateLimits.rate_limits.length > 0 ? (
                          projectRateLimits.rate_limits.map((rateLimit) => {
                            const isFineTune = rateLimit.id.startsWith("rl-ft:");
                            const isNonUpdatable = rateLimit.id === "rl-gpt-image-1";
                            return (
                              <div
                                key={rateLimit.id}
                                className={`rounded-md p-3 ${
                                  isFineTune || isNonUpdatable 
                                    ? "bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800" 
                                    : "bg-bg-secondary"
                                }`}
                              >
                                <div className="font-medium text-sm flex items-center gap-2">
                                  {rateLimit.model || 'Unknown Model'}
                                  {(isFineTune || isNonUpdatable) && (
                                    <span className="text-xs px-2 py-1 bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 rounded-full">
                                      수정불가
                                    </span>
                                  )}
                                </div>
                                <div className="text-xs text-text-secondary mt-1">
                                  요청/분: {(rateLimit.max_requests_per_1_minute || 0).toLocaleString()}
                                </div>
                                <div className="text-xs text-text-secondary">
                                  토큰/분: {(rateLimit.max_tokens_per_1_minute || 0).toLocaleString()}
                                </div>
                              </div>
                            );
                          })
                        ) : (
                          <div className="col-span-full text-center py-4 text-text-secondary">
                            이 프로젝트에는 Rate Limit 정보가 없습니다.
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })()}
              </AppleCard>
            )}
            
            {/* No Project Selected Message */}
            {selectedProjectId && !allRateLimits[selectedProjectId] && (
              <AppleCard>
                <div className="text-center py-8">
                  <p className="text-text-secondary">
                    선택한 프로젝트의 Rate Limit 정보가 없습니다.
                  </p>
                </div>
              </AppleCard>
            )}
            
            {/* No Projects Available Message */}
            {getFilteredProjects().length === 0 && showOnlyOverBudget && (
              <AppleCard>
                <div className="text-center py-8">
                  <p className="text-text-secondary">
                    예산을 초과한 프로젝트가 없습니다.
                  </p>
                </div>
              </AppleCard>
            )}
          </>
        )}

        {/* Confirm Modal */}
        <ConfirmModal
          isOpen={confirmModal.isOpen}
          onClose={() => setConfirmModal({ isOpen: false, type: 'disable' })}
          onConfirm={executeAction}
          title={
            confirmModal.type === 'save_template' 
              ? 'Rate Limit 템플릿 저장' 
              : confirmModal.type === 'disable'
              ? 'Rate Limit 비활성화'
              : 'Rate Limit 템플릿 적용'
          }
          message={
            confirmModal.type === 'save_template'
              ? '현재 Rate Limit 설정을 템플릿으로 저장하시겠습니까?'
              : confirmModal.type === 'disable'
              ? `"${confirmModal.projectName}" 프로젝트의 모든 모델 (rl-xxx)의 max_requests_per_1_minute를 0으로 설정하여 완전히 비활성화하시겠습니까?`
              : `"${confirmModal.projectName}" 프로젝트에 저장된 템플릿을 적용하시겠습니까?`
          }
          details={
            confirmModal.type === 'save_template'
              ? [{ label: '저장될 템플릿', value: '모든 프로젝트 공통 템플릿' }]
              : confirmModal.type === 'disable'
              ? [
                  { label: '프로젝트', value: confirmModal.projectName || '' },
                  { label: '작업', value: '모든 모델의 max_requests_per_1_minute → 0 (완전 비활성화)' }
                ]
              : [
                  { label: '프로젝트', value: confirmModal.projectName || '' },
                  { label: '작업', value: '템플릿 Rate Limit 적용' }
                ]
          }
          confirmButtonText={
            confirmModal.type === 'save_template' 
              ? '템플릿 저장' 
              : confirmModal.type === 'disable'
              ? '비활성화'
              : '적용'
          }
          isDestructive={confirmModal.type === 'disable'}
        />
      </div>
    </div>
  );
};
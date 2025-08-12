import React, { useMemo, useState } from "react";
import {
  useProcessedData,
  useBudgets,
  useProjects,
  useAppActions,
} from "@/store/useAppStore";
import { AppleCard } from "@/components/ui/AppleCard";
import { AppleButton } from "@/components/ui/AppleButton";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import {
  formatCurrency,
} from "@/utils/dataProcessor";
import {
  fetchProjects,
} from "@/utils/api";

export const Budgets: React.FC = () => {
  const processedData = useProcessedData();
  const budgets = useBudgets();
  const projects = useProjects();
  const { setBudget, removeBudget, clearAllBudgets, setProjects: setStoreProjects } = useAppActions();
  
  // Admin API key state
  const [adminKey, setAdminKey] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Project loading function
  const loadProjects = async () => {
    if (!adminKey.trim()) {
      setError("관리자 API 키를 입력해주세요.");
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const list = await fetchProjects(adminKey);
      setStoreProjects(list);
      setError(null);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "프로젝트 목록을 불러오지 못했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResetAll = () => {
    setResetModal({ isOpen: true, type: 'all' });
  };

  const handleResetSingle = (projectId: string, projectName: string) => {
    setResetModal({ isOpen: true, type: 'single', projectId, projectName });
  };

  const executeReset = () => {
    if (resetModal.type === 'all') {
      clearAllBudgets();
    } else if (resetModal.type === 'single' && resetModal.projectId) {
      removeBudget(resetModal.projectId);
    }
    setResetModal({ isOpen: false, type: 'all' });
  };
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [bulkValue, setBulkValue] = useState<number>(100);
  const [selectedProjectForBudget, setSelectedProjectForBudget] = useState<string>("");
  const [individualBudgetValue, setIndividualBudgetValue] = useState<number>(100);
  const [resetModal, setResetModal] = useState<{
    isOpen: boolean;
    type: 'all' | 'single';
    projectId?: string;
    projectName?: string;
  }>({ isOpen: false, type: 'all' });
  
  // Sorting state
  const [sortConfig, setSortConfig] = useState<{
    key: 'project' | 'spent' | 'budget' | 'rate' | 'status';
    direction: 'asc' | 'desc';
  } | null>(null);

  // Sort handler
  const handleSort = (key: 'project' | 'spent' | 'budget' | 'rate' | 'status') => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  // Sort budget data
  const sortedBudgets = useMemo(() => {
    const budgetEntries = Object.entries(budgets).map(([projectId, budget]) => {
      const project = projects[projectId];
      if (!project || !budget) return null;

      const usageData = processedData?.usageByProject?.find(usage => usage.projectId === projectId);
      const spent = usageData?.cost || 0;
      const limit = budget.limit;
      const rate = limit > 0 ? (spent / limit) * 100 : 0;
      
      return {
        projectId,
        project,
        budget,
        spent,
        rate,
        status: spent > limit ? 4 : rate >= 90 ? 3 : rate >= 70 ? 2 : 1 // numeric for sorting
      };
    }).filter(Boolean);

    if (!sortConfig) {
      return budgetEntries;
    }

    return [...budgetEntries].sort((a, b) => {
      if (!a || !b) return 0;
      
      let aValue: any = a[sortConfig.key];
      let bValue: any = b[sortConfig.key];

      if (sortConfig.key === 'project') {
        aValue = a.project.name.toLowerCase();
        bValue = b.project.name.toLowerCase();
      }

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [budgets, projects, processedData, sortConfig]);

  // Get project list from Organization API (not from uploaded JSON)
  const projectList = useMemo(() => {
    return Object.values(projects).map(p => ({
      projectId: p.id,
      projectName: p.name,
      // Get usage data if available
      cost: processedData?.usageByProject?.find(usage => usage.projectId === p.id)?.cost || 0,
      requests: processedData?.usageByProject?.find(usage => usage.projectId === p.id)?.requests || 0,
      tokens: processedData?.usageByProject?.find(usage => usage.projectId === p.id)?.tokens || 0
    }));
  }, [projects, processedData]);

  const totalBudget = useMemo(() => {
    return Object.values(budgets).reduce((sum, b) => sum + (b?.limit || 0), 0);
  }, [budgets]);

  const totalSpent = useMemo(() => {
    return projectList.reduce((sum, p) => sum + p.cost, 0);
  }, [projectList]);

  const exceededBudgets = useMemo(() => {
    let count = 0;
    for (const [projectId, budget] of Object.entries(budgets)) {
      if (!budget) continue;
      
      // Get usage data if available
      const usageData = processedData?.usageByProject?.find(usage => usage.projectId === projectId);
      const spent = usageData?.cost || 0;
      const limit = budget.limit;
      
      if (spent > limit) count += 1;
    }
    return count;
  }, [budgets, processedData]);
  const warningBudgets = useMemo(() => {
    // 경고 기준: 90% 이상 사용(초과 제외)
    let count = 0;
    for (const [projectId, budget] of Object.entries(budgets)) {
      if (!budget) continue;
      
      // Get usage data if available
      const usageData = processedData?.usageByProject?.find(usage => usage.projectId === projectId);
      const spent = usageData?.cost || 0;
      const limit = budget.limit;
      
      if (spent > limit) continue; // 이미 초과한 경우 제외
      const rate = limit > 0 ? (spent / limit) * 100 : 0;
      if (rate >= 90) count += 1;
    }
    return count;
  }, [budgets, processedData]);

  // Check if we have projects from Organization API
  if (Object.keys(projects).length === 0) {
    return (
      <div className="p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-8 lg:mb-12 mt-4 lg:mt-6">
            <h1 className="mb-3 text-2xl font-bold text-text-primary sm:text-3xl">
              💰 예산 관리
            </h1>
            <p className="text-lg text-text-secondary mb-6">
              프로젝트 정보가 없습니다. 먼저 관리자 API 키로 프로젝트 목록을 불러와주세요.
            </p>
            
            {/* Admin Key Input */}
            <AppleCard>
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
                    키는 네트워크로 서버에 전달되며, 서버에서 OpenAI API로
                    요청합니다. 브라우저에 저장되지 않습니다.
                  </p>
                </div>
                <div className="flex space-x-2">
                  <AppleButton variant="primary" onClick={loadProjects} disabled={loading}>
                    {loading ? "불러오는 중..." : "프로젝트 불러오기"}
                  </AppleButton>
                </div>
              </div>
              {error && <div className="mt-3 text-sm text-apple-red">{error}</div>}
            </AppleCard>
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
              💰 예산 관리
            </h1>
            <p className="text-text-secondary">
              프로젝트별 예산 설정 및 사용량 모니터링
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <AppleButton
              variant="ghost"
              onClick={handleResetAll}
              className="text-apple-red hover:bg-red-50 dark:hover:bg-red-950/20"
              disabled={Object.keys(budgets).length === 0}
            >
              🗑️ 전체 초기화
            </AppleButton>
            <AppleButton
              variant="primary"
              onClick={() => setShowCreateForm(true)}
            >
              ➕ 새 예산
            </AppleButton>
          </div>
        </div>

        {/* Overview Cards */}
        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6 lg:grid-cols-4">
          <AppleCard className="text-center">
            <div className="text-2xl font-bold text-apple-blue">
              {formatCurrency(totalBudget)}
            </div>
            <div className="mt-1 text-sm text-text-secondary">총 예산</div>
          </AppleCard>
          <AppleCard className="text-center">
            <div className="text-2xl font-bold text-apple-green">
              {formatCurrency(totalSpent)}
            </div>
            <div className="mt-1 text-sm text-text-secondary">총 사용량</div>
            <div className="mt-1 text-xs text-text-tertiary">
              {totalBudget > 0
                ? ((totalSpent / totalBudget) * 100).toFixed(1)
                : 0}
              % 사용
            </div>
          </AppleCard>
          <AppleCard className="text-center">
            <div className="text-2xl font-bold text-apple-orange">
              {warningBudgets}
            </div>
            <div className="mt-1 text-sm text-text-secondary">경고 상태</div>
          </AppleCard>
          <AppleCard className="text-center">
            <div className="text-2xl font-bold text-apple-red">
              {exceededBudgets}
            </div>
            <div className="mt-1 text-sm text-text-secondary">초과 상태</div>
          </AppleCard>
        </div>

        {/* Create Budget Form */}
        {showCreateForm && (
          <AppleCard className="mb-8">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold">🆕 새 예산 설정</h3>
              <AppleButton
                variant="ghost"
                onClick={() => setShowCreateForm(false)}
              >
                ✕
              </AppleButton>
            </div>

            <div className="space-y-6">
              <div>
                <label className="mb-2 block text-sm font-medium text-text-primary">
                  프로젝트 선택
                </label>
                <div className="flex items-center space-x-3">
                  <select
                    value={selectedProjectForBudget}
                    onChange={(e) => setSelectedProjectForBudget(e.target.value)}
                    className="flex-1 rounded-lg border border-border-primary px-3 py-2 focus:border-apple-blue focus:ring-2 focus:ring-apple-blue"
                  >
                    <option value="">프로젝트를 선택하세요</option>
                    {projectList.map((p) => (
                      <option key={p.projectId} value={p.projectId}>
                        {p.projectName}
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min="0"
                    step="10"
                    value={individualBudgetValue}
                    onChange={(e) => setIndividualBudgetValue(parseFloat(e.target.value || "0"))}
                    className="w-1/5 min-w-24 rounded-lg border border-border-primary px-3 py-2 text-right focus:border-apple-blue focus:ring-2 focus:ring-apple-blue"
                    placeholder="100.00"
                  />
                  <AppleButton
                    variant="secondary"
                    onClick={() => {
                      if (!selectedProjectForBudget) return;
                      setBudget(selectedProjectForBudget, {
                        projectId: selectedProjectForBudget,
                        limit: individualBudgetValue,
                        spent: 0,
                        period: "monthly",
                        alerts: { enabled: true, thresholds: [50, 80, 100] },
                      });
                      setSelectedProjectForBudget("");
                      setIndividualBudgetValue(100);
                    }}
                    disabled={!selectedProjectForBudget}
                  >
                    적용
                  </AppleButton>
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-text-primary">
                  일괄 예산 한도 (USD)
                </label>
                <div className="flex items-center space-x-3">
                  <input
                    type="number"
                    min="0"
                    step="10"
                    value={bulkValue}
                    onChange={(e) =>
                      setBulkValue(parseFloat(e.target.value || "0"))
                    }
                    className="flex-1 min-w-0 rounded-lg border border-border-primary px-4 py-3 text-lg focus:border-apple-blue focus:ring-2 focus:ring-apple-blue"
                    placeholder="예: 100.00"
                  />
                  <AppleButton
                    variant="secondary"
                    onClick={() => {
                      projectList.forEach((p) => {
                        setBudget(p.projectId, {
                          projectId: p.projectId,
                          limit: bulkValue,
                          spent: 0,
                          period: "monthly",
                          alerts: {
                            enabled: true,
                            thresholds: [50, 80, 100],
                          },
                        });
                      });
                    }}
                  >
                    전체 적용
                  </AppleButton>
                </div>
              </div>

              <div className="rounded-lg bg-bg-secondary/30 p-4">
                <h4 className="mb-2 text-sm font-semibold text-text-primary">
                  ℹ️ 예산 설정 안내
                </h4>
                <div className="text-sm text-text-secondary space-y-1">
                  <div>• 프로젝트별 예산을 설정하면 로컬에 저장되어 유지됩니다</div>
                  <div>• 업로드한 프로젝트 사용량과 비교하여 사용률 및 초과 여부를 분석합니다</div>
                  <div>• Organization API에서 가져온 프로젝트 목록을 기준으로 합니다</div>
                </div>
              </div>
            </div>
          </AppleCard>
        )}


        {/* Monitoring */}
        <AppleCard className="mb-8">
          <h3 className="mb-6 text-lg font-semibold">📈 예산 모니터링</h3>
          {Object.keys(budgets).length === 0 ? (
            <div className="text-center py-8 text-text-secondary">
              예산이 설정된 프로젝트가 없습니다.
              <br />
              위에서 프로젝트별 예산을 설정해주세요.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-border-primary">
                  <tr>
                    <th 
                      className="px-2 py-3 text-left cursor-pointer hover:bg-bg-secondary/30 select-none"
                      onClick={() => handleSort('project')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>프로젝트</span>
                        {sortConfig?.key === 'project' && (
                          <span className="text-apple-blue">
                            {sortConfig.direction === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th 
                      className="px-2 py-3 text-right cursor-pointer hover:bg-bg-secondary/30 select-none"
                      onClick={() => handleSort('spent')}
                    >
                      <div className="flex items-center justify-end space-x-1">
                        <span>사용량</span>
                        {sortConfig?.key === 'spent' && (
                          <span className="text-apple-blue">
                            {sortConfig.direction === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th 
                      className="px-2 py-3 text-right cursor-pointer hover:bg-bg-secondary/30 select-none"
                      onClick={() => handleSort('budget')}
                    >
                      <div className="flex items-center justify-end space-x-1">
                        <span>예산</span>
                        {sortConfig?.key === 'budget' && (
                          <span className="text-apple-blue">
                            {sortConfig.direction === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th 
                      className="px-2 py-3 text-center cursor-pointer hover:bg-bg-secondary/30 select-none"
                      onClick={() => handleSort('rate')}
                    >
                      <div className="flex items-center justify-center space-x-1">
                        <span>사용률</span>
                        {sortConfig?.key === 'rate' && (
                          <span className="text-apple-blue">
                            {sortConfig.direction === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th 
                      className="px-2 py-3 text-center cursor-pointer hover:bg-bg-secondary/30 select-none"
                      onClick={() => handleSort('status')}
                    >
                      <div className="flex items-center justify-center space-x-1">
                        <span>상태</span>
                        {sortConfig?.key === 'status' && (
                          <span className="text-apple-blue">
                            {sortConfig.direction === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th className="px-2 py-3 text-center">작업</th>
                  </tr>
                </thead>
                <tbody>
                {sortedBudgets.map((item) => {
                  if (!item) return null;
                  
                  const { projectId, project, budget, spent, rate } = item;
                  const limit = budget.limit;
                  const status =
                    spent > limit
                      ? "🚨 초과"
                      : rate >= 90
                      ? "⚠️ 경고"
                      : rate >= 70
                      ? "🟡 주의"
                      : "✅ 안전";

                  return (
                    <tr
                      key={projectId}
                      className="border-border-secondary hover:bg-background-secondary/30 border-b"
                    >
                      <td className="px-2 py-3">
                        <div className="font-medium">{project.name}</div>
                        <div className="text-xs text-text-secondary">{projectId}</div>
                      </td>
                      <td className="px-2 py-3 text-right">
                        {formatCurrency(spent)}
                      </td>
                      <td className="px-2 py-3 text-right">
                        {formatCurrency(limit)}
                      </td>
                      <td className="px-2 py-3 text-center">
                        <div className="font-semibold">{rate.toFixed(1)}%</div>
                      </td>
                      <td className="px-2 py-3 text-center">{status}</td>
                      <td className="px-2 py-3 text-center">
                        <AppleButton
                          variant="ghost"
                          size="sm"
                          onClick={() => handleResetSingle(projectId, project.name)}
                          className="text-apple-red hover:bg-red-50 dark:hover:bg-red-950/20"
                        >
                          🗑️
                        </AppleButton>
                      </td>
                    </tr>
                  );
                })}
                </tbody>
              </table>
            </div>
          )}
        </AppleCard>


        {/* Reset Confirmation Modal */}
        <ConfirmModal
          isOpen={resetModal.isOpen}
          onClose={() => setResetModal({ isOpen: false, type: 'all' })}
          onConfirm={executeReset}
          title={resetModal.type === 'all' ? '모든 예산 초기화' : '예산 삭제'}
          message={
            resetModal.type === 'all'
              ? '모든 프로젝트의 예산 설정을 삭제하시겠습니까?'
              : `"${resetModal.projectName}" 프로젝트의 예산을 삭제하시겠습니까?`
          }
          details={[
            ...(resetModal.type === 'all'
              ? [
                  { label: '삭제될 예산 개수', value: `${Object.keys(budgets).length}개` },
                  { label: '총 예산 금액', value: formatCurrency(totalBudget) }
                ]
              : resetModal.projectId && budgets[resetModal.projectId]
              ? [
                  { label: '프로젝트명', value: resetModal.projectName || '' },
                  { label: '설정된 예산', value: formatCurrency(budgets[resetModal.projectId]?.limit || 0) }
                ]
              : []
            )
          ]}
          confirmButtonText={resetModal.type === 'all' ? '전체 초기화' : '삭제'}
          isDestructive={true}
        />
      </div>
    </div>
  );
};

import React from "react";
import {
  useProcessedData,
  useAppActions,
  useLoading,
  useError,
  useAdminApiKey,
} from "@/store/useAppStore";
import { MetricCard } from "@/components/ui/MetricCard";
import { AppleCard } from "@/components/ui/AppleCard";
import {
  formatCurrency,
  formatNumber,
  validateUsageDataStructure,
  generateTimeSeriesData,
} from "@/utils/dataProcessor";
import { UnifiedFileUpload } from "@/components/ui/UnifiedFileUpload";
import { TestDataButton } from "@/components/ui/TestDataButton";
import type { MetricCardData, UserData, ProjectData } from "@/types";
import Plot from "react-plotly.js";

export const Dashboard: React.FC = () => {
  const processedData = useProcessedData();
  const loading = useLoading();
  const error = useError();
  const adminApiKey = useAdminApiKey();
  const { setUserData, setProjectData, setUserInfoFromFile, setError, setLoading, setSelectedView, setAdminApiKey } = useAppActions();

  const handleFileUpload = async (file: File, detectedType: "user" | "project" | "userinfo") => {
    setLoading(true);
    setError(null);

    try {
      const text = await file.text();

      // Parse JSON
      let data;
      try {
        data = JSON.parse(text);
      } catch (parseError) {
        throw new Error(
          "JSON 형식이 올바르지 않습니다. 파일이 유효한 JSON인지 확인해주세요."
        );
      }

      // Validate the data structure with detailed logging (skip validation for userinfo)
      if (detectedType !== "userinfo") {
        const isValid = validateUsageDataStructure(data, detectedType);
        if (!isValid) {
          throw new Error(
            `올바른 ${
              detectedType === "user" ? "사용자별" : "프로젝트별"
            } 데이터 형식이 아닙니다. OpenAI에서 다운로드한 JSON 파일인지 확인해주세요.`
          );
        }
      }

      // Handle different data types
      if (detectedType === "userinfo") {
        // Process userinfo data without clearing existing usage data
        setUserInfoFromFile(data);
        console.log(`✅ 사용자 정보 데이터가 성공적으로 업로드되었습니다. 기존 사용량 데이터의 사용자 이름이 업데이트됩니다.`);
      } else {
        // Clear previous data and set new usage data
        setUserData(null);
        setProjectData(null);
        
        // If this is user data, automatically generate userinfo.json
        if (detectedType === "user") {
          try {
            console.log(`🔍 사용자별 데이터가 감지되어 자동으로 userinfo.json을 생성합니다...`);
            
            const headers: Record<string, string> = {
              'Content-Type': 'application/json',
            };

            // Add admin API key if available
            if (adminApiKey) {
              headers['X-Admin-API-Key'] = adminApiKey;
            }

            const response = await fetch('http://localhost:8000/generate-userinfo', {
              method: 'POST',
              headers,
              body: JSON.stringify({
                usage_data: data
              })
            });

            if (response.ok) {
              const result = await response.json();
              if (result.success) {
                console.log(`✅ ${result.message}`);
                
                // Use userinfo data directly from the API response
                if (result.userinfo_data) {
                  setUserInfoFromFile(result.userinfo_data);
                  
                  // Check if this is mock data or real data
                  if (result.message.includes("mock")) {
                    console.warn(`⚠️ Mock 사용자 정보가 로드되었습니다. 실제 사용자 정보를 원한다면 올바른 관리자 API 키를 설정하세요.`);
                  } else {
                    console.log(`✅ 실제 사용자 정보가 자동으로 로드되었습니다.`);
                  }
                } else {
                  console.warn(`⚠️ API 응답에 userinfo_data가 포함되지 않았습니다.`);
                }
              } else {
                console.warn(`⚠️ Userinfo 생성에 실패했지만 사용자 데이터는 정상적으로 로드됩니다: ${result.message}`);
              }
            } else {
              console.warn(`⚠️ Userinfo 생성 API 호출에 실패했지만 사용자 데이터는 정상적으로 로드됩니다.`);
            }
          } catch (userinfoError) {
            console.warn(`⚠️ Userinfo 자동 생성 중 오류가 발생했지만 사용자 데이터는 정상적으로 로드됩니다: ${userinfoError}`);
          }
        }
        
        // Set the data in the store and navigate to appropriate view
        if (detectedType === "user") {
          setUserData(data as UserData);
          setSelectedView("users");
        } else {
          setProjectData(data as ProjectData);
          setSelectedView("projects");
        }
        console.log(`✅ ${detectedType === "user" ? "사용자별" : "프로젝트별"} 데이터가 성공적으로 업로드되었습니다.`);
      }
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "파일 업로드 중 오류가 발생했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  // If no data, show upload interface
  if (!processedData) {
    return (
      <div className="p-4 sm:p-6 lg:p-8">
        <div className="mx-auto max-w-4xl">
          {/* Global Error Display */}
          {error && (
            <div className="mb-6">
              <AppleCard className="border-red-200 bg-red-50">
                <div className="flex items-center">
                  <span className="mr-3 text-xl text-red-500">⚠️</span>
                  <div>
                    <h3 className="font-semibold text-red-800">
                      파일 처리 오류
                    </h3>
                    <p className="mt-1 text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </AppleCard>
            </div>
          )}

          {/* Loading Overlay */}
          {loading && (
            <div className="mb-6">
              <AppleCard className="border-blue-200 bg-blue-50">
                <div className="flex items-center">
                  <div className="apple-spinner mr-3" />
                  <div>
                    <h3 className="font-semibold text-blue-800">
                      파일 처리 중...
                    </h3>
                    <p className="mt-1 text-sm text-blue-700">
                      JSON 파일을 분석하고 있습니다.
                    </p>
                  </div>
                </div>
              </AppleCard>
            </div>
          )}
          {/* Header */}
          <div className="mb-8 text-center sm:mb-12">
            <h1 className="mb-4 text-2xl font-bold text-text-primary sm:text-3xl lg:text-4xl">
              OpenAI API 사용량 추적
            </h1>
            <p className="mx-auto max-w-2xl px-4 text-lg text-text-secondary sm:text-xl">
              OpenAI API 사용량 데이터를 업로드하여 상세한 분석과 시각화를
              확인하세요
            </p>
          </div>

          {/* Admin API Key Input */}
          <div className="mb-6 mx-auto max-w-2xl">
            <AppleCard>
              <h3 className="mb-4 text-lg font-semibold">🔑 관리자 API 키 설정</h3>
              <p className="mb-4 text-sm text-text-secondary">
                사용자별 데이터 업로드 시 자동으로 실제 사용자 정보를 가져오려면 올바른 OpenAI 관리자 API 키를 입력하세요.
              </p>
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-700 font-medium mb-2">✋ 중요: API 키 요구사항</p>
                <ul className="text-xs text-blue-600 space-y-1">
                  <li>• <strong>api.management.read</strong> 스코프 권한 필요</li>
                  <li>• OpenAI 조직의 <strong>관리자(Admin)</strong> 또는 <strong>소유자(Owner)</strong> 역할</li>
                  <li>• 권한이 없으면 테스트용 mock 데이터가 표시됩니다</li>
                </ul>
              </div>
              <div className="flex gap-3">
                <input
                  type="password"
                  placeholder="sk-proj-... 또는 sk-..."
                  value={adminApiKey || ""}
                  onChange={(e) => setAdminApiKey(e.target.value || null)}
                  className="flex-1 px-3 py-2 border border-border-primary rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-apple-blue"
                />
                <button
                  onClick={() => setAdminApiKey(null)}
                  disabled={!adminApiKey}
                  className="px-4 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  삭제
                </button>
              </div>
              {adminApiKey && (
                <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-700">
                    ✅ API 키가 설정되었습니다. 사용자별 데이터 업로드 시 자동으로 사용자 정보를 가져옵니다.
                  </p>
                </div>
              )}
            </AppleCard>
          </div>

          {/* Unified Upload */}
          <div className="mb-8 mx-auto max-w-2xl">
            <UnifiedFileUpload onFileUpload={handleFileUpload} />
          </div>

          {/* Help Section */}
          <AppleCard className="mx-auto max-w-2xl text-center">
            <h3 className="mb-4 text-lg font-semibold">📋 사용 방법</h3>
            <div className="mb-6 space-y-3 text-text-secondary">
              <p>
                1. OpenAI 대시보드에서 사용량 데이터를 JSON 형식으로 다운로드
              </p>
              <p>2. 위 업로드 영역에 JSON 파일을 드래그하거나 선택</p>
              <p>3. 데이터 타입이 자동으로 감지되어 해당 분석 페이지로 이동</p>
              <p>4. 자동으로 생성되는 분석 결과와 차트를 확인</p>
            </div>
            
            <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="text-sm font-semibold text-blue-800 mb-2">🎯 스마트 데이터 인식</h4>
              <div className="text-xs text-blue-700 space-y-1">
                <p>• 사용자별 데이터 → 자동으로 "사용자별" 탭으로 이동</p>
                <p>• 프로젝트별 데이터 → 자동으로 "프로젝트별" 탭으로 이동</p>
                <p>• 하나의 업로드로 모든 분석 완료!</p>
              </div>
            </div>
            
            <div className="border-t border-border-primary pt-6">
              <p className="mb-4 text-sm text-text-tertiary">
                개발 및 테스트를 위한 샘플 데이터:
              </p>
              <TestDataButton />
            </div>
          </AppleCard>
        </div>
      </div>
    );
  }

  // Create metric cards data
  const metricCards: MetricCardData[] = [
    {
      value: formatCurrency(processedData.totalCost),
      label: "총 사용 비용",
      icon: "💰",
      changeType: "neutral",
    },
    {
      value: formatNumber(processedData.totalRequests),
      label: "총 API 요청",
      icon: "📊",
      changeType: "neutral",
    },
    {
      value: formatNumber(processedData.activeUsers),
      label: "활성 사용자",
      icon: "👥",
      changeType: "neutral",
    },
    {
      value: formatNumber(processedData.usageByModel.length),
      label: "사용된 모델",
      icon: "🤖",
      changeType: "neutral",
    },
  ];

  const timeSeries = generateTimeSeriesData(processedData.usageByDate, "cost");
  const modelSeries = processedData.usageByModel
    .sort((a, b) => b.cost - a.cost)
    .slice(0, 10);

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8 lg:mb-12 mt-4 lg:mt-6">
          <h1 className="mb-3 text-2xl font-bold text-text-primary sm:text-3xl">
            대시보드
          </h1>
          <p className="text-text-secondary">OpenAI API 사용량 종합 현황</p>
        </div>

        {/* Metrics Grid */}
        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 sm:gap-6 lg:mb-12 lg:grid-cols-4">
          {metricCards.map((data, index) => (
            <MetricCard key={index} data={data} size="md" showTrend={false} />
          ))}
        </div>

        {/* Charts Row */}
        <div className="mb-6 grid grid-cols-1 gap-6 lg:mb-8 lg:gap-8 xl:grid-cols-2">
          {/* Usage by Date */}
          <AppleCard>
            <h3 className="mb-6 text-lg font-semibold">📈 일별 사용 현황</h3>
            <Plot
              data={[
                {
                  x: timeSeries.map((d) => d.x),
                  y: timeSeries.map((d) => d.y),
                  type: "scatter",
                  mode: "lines+markers",
                  line: { color: "#007AFF", width: 2 },
                  fill: "tozeroy",
                  fillcolor: "rgba(0,122,255,0.15)",
                },
              ]}
              layout={{
                margin: { l: 40, r: 20, t: 10, b: 40 },
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent",
                font: {
                  family: "-apple-system, Inter, sans-serif",
                  color: "var(--text-primary)",
                },
                xaxis: { title: "날짜", type: "date" },
                yaxis: { title: "비용(USD)" },
              }}
              style={{ width: "100%", height: 320 }}
              config={{ displayModeBar: false, responsive: true }}
            />
          </AppleCard>

          {/* Usage by Model */}
          <AppleCard>
            <h3 className="mb-6 text-lg font-semibold">🤖 모델별 사용량</h3>
            <Plot
              data={[
                {
                  x: modelSeries.map((m) => m.cost),
                  y: modelSeries.map((m) => m.model),
                  type: "bar",
                  orientation: "h",
                  marker: {
                    color: modelSeries.map(
                      (_, i) => `hsl(${(i * 360) / modelSeries.length},70%,55%)`
                    ),
                  },
                },
              ]}
              layout={{
                margin: { l: 120, r: 20, t: 10, b: 40 },
                paper_bgcolor: "transparent",
                plot_bgcolor: "transparent",
                font: {
                  family: "-apple-system, Inter, sans-serif",
                  color: "var(--text-primary)",
                },
                xaxis: { title: "비용(USD)" },
                yaxis: { automargin: true },
              }}
              style={{ width: "100%", height: 320 }}
              config={{ displayModeBar: false, responsive: true }}
            />
          </AppleCard>
        </div>

        {/* Top Users/Projects */}
        <div className="grid grid-cols-1 gap-6 lg:gap-8 xl:grid-cols-2">
          {/* Top Users */}
          <AppleCard>
            <h3 className="mb-6 text-lg font-semibold">👑 주요 사용자</h3>
            <div className="space-y-4">
              {processedData.usageByUser?.slice(0, 5).map((user, index) => (
                <div
                  key={user.userId}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-r from-apple-blue to-apple-purple">
                      <span className="text-xs font-bold text-white">
                        {index + 1}
                      </span>
                    </div>
                    <div>
                      <div className="text-sm font-medium">{user.userName}</div>
                      <div className="text-xs text-text-secondary">
                        {formatNumber(user.requests)} 요청
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold">
                      {formatCurrency(user.cost)}
                    </div>
                    <div className="text-xs text-text-secondary">
                      {formatNumber(user.tokens)} 토큰
                    </div>
                  </div>
                </div>
              )) || (
                <div className="py-4 text-center text-text-secondary">
                  사용자 데이터가 없습니다
                </div>
              )}
            </div>
          </AppleCard>

          {/* Top Projects */}
          <AppleCard>
            <h3 className="mb-6 text-lg font-semibold">📁 주요 프로젝트</h3>
            <div className="space-y-4">
              {processedData.usageByProject
                ?.sort((a, b) => b.cost - a.cost)
                .slice(0, 5)
                .map((project, index) => (
                  <div
                    key={project.projectId}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-r from-apple-green to-apple-teal">
                        <span className="text-xs font-bold text-white">
                          {index + 1}
                        </span>
                      </div>
                      <div>
                        <div className="text-sm font-medium">
                          {project.projectName}
                        </div>
                        <div className="text-xs text-text-secondary">
                          {formatNumber(project.requests)} 일
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold">
                        {formatCurrency(project.cost)}
                      </div>
                      <div className="text-xs text-text-secondary">
                        {formatNumber(project.tokens)} 토큰
                      </div>
                    </div>
                  </div>
                )) || (
                <div className="py-4 text-center text-text-secondary">
                  프로젝트 데이터가 없습니다
                </div>
              )}
            </div>
          </AppleCard>
        </div>
      </div>
    </div>
  );
};

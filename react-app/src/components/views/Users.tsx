import React, { useState } from 'react';
import { useProcessedData, useAppStore } from '@/store/useAppStore';
import { AppleCard } from '@/components/ui/AppleCard';
import { MetricCard } from '@/components/ui/MetricCard';
import { formatCurrency, formatNumber, extractResultsFromBuckets, groupByUserId } from '@/utils/dataProcessor';
import type { MetricCardData } from '@/types';
import Plot from 'react-plotly.js';

export const Users: React.FC = () => {
  const processedData = useProcessedData();
  const { userData } = useAppStore();
  const [topUsersCount, setTopUsersCount] = useState<number>(5);
  const [sortBy, setSortBy] = useState<'cost' | 'requests' | 'percentage'>('cost');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [expandedUserId, setExpandedUserId] = useState<string | null>(null);

  if (!processedData || !processedData.usageByUser || processedData.usageByUser.length === 0) {
    return (
      <div className="p-4 sm:p-6 lg:p-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8 lg:mb-12 mt-4 lg:mt-6">
            <h1 className="text-2xl sm:text-3xl font-bold text-text-primary mb-3">
              👤 사용자별 분석
            </h1>
            <p className="text-lg text-text-secondary">
              사용자별 데이터가 없습니다. 먼저 사용자별 사용량 데이터를 업로드해주세요.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const topUsers = processedData.usageByUser
    .sort((a, b) => b.cost - a.cost)
    .slice(0, topUsersCount);

  const totalUserCost = processedData.usageByUser.reduce((sum, user) => sum + user.cost, 0);
  const totalUserRequests = processedData.usageByUser.reduce((sum, user) => sum + user.requests, 0);
  const totalUserTokens = processedData.usageByUser.reduce((sum, user) => sum + user.tokens, 0);

  const handleSort = (column: 'cost' | 'requests' | 'percentage') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const getSortedUsers = () => {
    return [...processedData.usageByUser].sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'cost':
          aValue = a.cost;
          bValue = b.cost;
          break;
        case 'requests':
          aValue = a.requests;
          bValue = b.requests;
          break;
        case 'percentage':
          aValue = (a.cost / totalUserCost) * 100;
          bValue = (b.cost / totalUserCost) * 100;
          break;
        default:
          return 0;
      }
      
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    });
  };

  const getUserDailyModelUsage = (userId: string) => {
    if (!userData) return { dates: [], models: [], chartData: [] };
    
    const results = extractResultsFromBuckets(userData);
    const userResults = results.filter(result => result.user_id === userId);
    
    // Group by date and model, combining input and output costs
    const dailyModelUsage: Record<string, Record<string, number>> = {};
    const allModels = new Set<string>();
    
    userResults.forEach(result => {
      const date = new Date(result.timestamp).toISOString().split('T')[0];
      let model = result.model || 'unknown';
      
      // Combine input and output costs for the same model
      // Remove input/output suffixes to group them together
      model = model.replace(/-(input|output)$/, '');
      
      if (!dailyModelUsage[date]) {
        dailyModelUsage[date] = {};
      }
      if (!dailyModelUsage[date][model]) {
        dailyModelUsage[date][model] = 0;
      }
      dailyModelUsage[date][model] += result.cost;
      allModels.add(model);
    });
    
    // Sort dates
    const sortedDates = Object.keys(dailyModelUsage).sort();
    const modelArray = Array.from(allModels).sort();
    
    // Create chart data for each model
    const chartData = modelArray.map((model, index) => ({
      x: sortedDates,
      y: sortedDates.map(date => dailyModelUsage[date][model] || 0),
      name: model,
      type: 'bar' as const,
      marker: {
        color: `hsl(${(index * 360) / modelArray.length}, 70%, 55%)`
      }
    }));
    
    return {
      dates: sortedDates,
      models: modelArray,
      chartData
    };
  };

  const handleRowClick = (userId: string) => {
    setExpandedUserId(expandedUserId === userId ? null : userId);
  };

  const metricCards: MetricCardData[] = [
    {
      value: formatNumber(processedData.activeUsers),
      label: '총 활성 사용자',
      icon: '👥',
      changeType: 'neutral'
    },
    {
      value: formatCurrency(totalUserCost),
      label: '총 사용자 비용',
      icon: '💰',
      changeType: 'neutral'
    },
    {
      value: formatNumber(totalUserRequests),
      label: '총 요청 수',
      icon: '📊',
      changeType: 'neutral'
    },
    {
      value: formatNumber(totalUserTokens),
      label: '총 토큰 수',
      icon: '🔤',
      changeType: 'neutral'
    }
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 lg:mb-12 mt-4 lg:mt-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-text-primary mb-3">👤 사용자별 분석</h1>
          <p className="text-text-secondary">개별 사용자의 OpenAI API 사용 패턴 및 비용 분석</p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8 lg:mb-12">
          {metricCards.map((data, index) => (
            <MetricCard
              key={index}
              data={data}
              size="md"
              showTrend={false}
            />
          ))}
        </div>

        {/* Top Users List */}
        <AppleCard className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">🏆 주요 사용자 순위</h3>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-text-secondary">표시 개수:</span>
              <select
                value={topUsersCount}
                onChange={(e) => setTopUsersCount(Number(e.target.value))}
                className="px-3 py-1 border border-border-primary rounded-lg focus:ring-2 focus:ring-apple-blue focus:border-apple-blue text-sm"
              >
                <option value={5}>5위까지</option>
                <option value={10}>10위까지</option>
                <option value={20}>20위까지</option>
              </select>
            </div>
          </div>
          <div className="space-y-4">
            {topUsers.map((user, index) => {
              const costPercentage = (user.cost / totalUserCost) * 100;
              const avgCostPerRequest = user.requests > 0 ? user.cost / user.requests : 0;
              
              return (
                <div key={user.userId} className="flex items-center justify-between p-4 bg-background-secondary/50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gradient-to-r from-apple-blue to-apple-purple rounded-full flex items-center justify-center">
                      <span className="text-white font-bold">{index + 1}</span>
                    </div>
                    <div>
                      <div className="font-semibold text-text-primary">{user.userName}</div>
                      <div className="text-sm text-text-secondary">
                        사용자 ID: {user.userId.slice(0, 12)}...
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="font-semibold text-lg">{formatCurrency(user.cost)}</div>
                    <div className="text-sm text-text-secondary">
                      {formatNumber(user.requests)} 요청 · {formatNumber(user.tokens)} 토큰
                    </div>
                    <div className="text-xs text-text-tertiary">
                      전체의 {costPercentage.toFixed(1)}% · 평균 {formatCurrency(avgCostPerRequest)}/요청
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </AppleCard>

        {/* Detailed User Table */}
        <AppleCard>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">📋 전체 사용자 목록</h3>
            <div className="text-sm text-text-secondary">
              총 {processedData.usageByUser.length}명의 사용자
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-border-primary">
                <tr>
                  <th className="text-left py-3 px-2 font-semibold text-text-primary">사용자</th>
                  <th className="text-right py-3 px-2 font-semibold text-text-primary cursor-pointer hover:bg-background-secondary/50" onClick={() => handleSort('cost')}>
                    비용 {sortBy === 'cost' && (sortOrder === 'desc' ? '↓' : '↑')}
                  </th>
                  <th className="text-right py-3 px-2 font-semibold text-text-primary cursor-pointer hover:bg-background-secondary/50" onClick={() => handleSort('requests')}>
                    요청 {sortBy === 'requests' && (sortOrder === 'desc' ? '↓' : '↑')}
                  </th>
                  <th className="text-right py-3 px-2 font-semibold text-text-primary">평균 비용/요청</th>
                  <th className="text-right py-3 px-2 font-semibold text-text-primary cursor-pointer hover:bg-background-secondary/50" onClick={() => handleSort('percentage')}>
                    점유율 {sortBy === 'percentage' && (sortOrder === 'desc' ? '↓' : '↑')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {getSortedUsers().map((user) => {
                    const costPercentage = (user.cost / totalUserCost) * 100;
                    const avgCostPerRequest = user.requests > 0 ? user.cost / user.requests : 0;
                    const isExpanded = expandedUserId === user.userId;
                    const dailyModelData = isExpanded ? getUserDailyModelUsage(user.userId) : { dates: [], models: [], chartData: [] };
                    
                    return (
                      <React.Fragment key={user.userId}>
                        <tr 
                          className="border-b border-border-secondary hover:bg-background-secondary/30 cursor-pointer transition-colors"
                          onClick={() => handleRowClick(user.userId)}
                        >
                          <td className="py-3 px-2">
                            <div className="flex items-center space-x-2">
                              <div className={`transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}>
                                <span className="text-text-secondary">▶</span>
                              </div>
                              <div>
                                <div className="font-medium text-text-primary">{user.userName}</div>
                                <div className="text-sm text-text-secondary">{user.userId.slice(0, 16)}...</div>
                              </div>
                            </div>
                          </td>
                          <td className="py-3 px-2 text-right font-semibold">{formatCurrency(user.cost)}</td>
                          <td className="py-3 px-2 text-right">{formatNumber(user.requests)}</td>
                          <td className="py-3 px-2 text-right">{formatCurrency(avgCostPerRequest)}</td>
                          <td className="py-3 px-2 text-right">
                            <div className="flex items-center justify-end space-x-2">
                              <div className="w-12 h-2 bg-border-primary rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-apple-blue rounded-full"
                                  style={{ width: `${Math.max(2, costPercentage)}%` }}
                                />
                              </div>
                              <span className="text-sm">{costPercentage.toFixed(1)}%</span>
                            </div>
                          </td>
                        </tr>
                        {isExpanded && (
                          <tr>
                            <td colSpan={5} className="py-0 px-2">
                              <div className="py-4 bg-background-secondary/20 rounded-lg">
                                <h4 className="text-md font-semibold mb-4 px-4">📈 {user.userName}의 날짜별 모델 사용량</h4>
                                <div className="px-4">
                                  <Plot
                                    data={dailyModelData.chartData}
                                    layout={{
                                      margin: { l: 50, r: 120, t: 20, b: 60 },
                                      paper_bgcolor: 'transparent',
                                      plot_bgcolor: 'transparent',
                                      font: {
                                        family: '-apple-system, Inter, sans-serif',
                                        color: 'var(--text-primary)',
                                      },
                                      xaxis: { 
                                        title: '날짜',
                                        showgrid: true,
                                        gridcolor: 'rgba(0,0,0,0.1)',
                                        type: 'date',
                                      },
                                      yaxis: { 
                                        title: '비용(USD)',
                                        showgrid: true,
                                        gridcolor: 'rgba(0,0,0,0.1)',
                                      },
                                      barmode: 'stack',
                                      showlegend: true,
                                      legend: {
                                        orientation: 'v',
                                        x: 1.02,
                                        y: 1,
                                        xanchor: 'left',
                                        yanchor: 'top',
                                      },
                                      height: 400,
                                      hovermode: 'x unified',
                                    }}
                                    style={{ width: '100%' }}
                                    config={{ displayModeBar: false, responsive: true }}
                                  />
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </AppleCard>
      </div>
    </div>
  );
};
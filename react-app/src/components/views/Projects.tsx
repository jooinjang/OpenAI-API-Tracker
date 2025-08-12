import React, { useState } from 'react';
import { useProcessedData } from '@/store/useAppStore';
import { AppleCard } from '@/components/ui/AppleCard';
import { MetricCard } from '@/components/ui/MetricCard';
import { formatCurrency, formatNumber } from '@/utils/dataProcessor';
import type { MetricCardData } from '@/types';

export const Projects: React.FC = () => {
  const processedData = useProcessedData();
  const [sortBy, setSortBy] = useState<'cost' | 'requests' | 'percentage'>('cost');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  if (!processedData || !processedData.usageByProject || processedData.usageByProject.length === 0) {
    return (
      <div className="p-4 sm:p-6 lg:p-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8 lg:mb-12 mt-4 lg:mt-6">
            <h1 className="text-2xl sm:text-3xl font-bold text-text-primary mb-3">
              📁 프로젝트별 분석
            </h1>
            <p className="text-lg text-text-secondary">
              프로젝트별 데이터가 없습니다. 먼저 프로젝트별 사용량 데이터를 업로드해주세요.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const topProjects = processedData.usageByProject
    .sort((a, b) => b.cost - a.cost)
    .slice(0, 10);

  const totalProjectCost = processedData.usageByProject.reduce((sum, project) => sum + project.cost, 0);
  const totalProjectRequests = processedData.usageByProject.reduce((sum, project) => sum + project.requests, 0);
  
  const handleSort = (column: 'cost' | 'requests' | 'percentage') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const getSortedProjects = () => {
    return [...processedData.usageByProject].sort((a, b) => {
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
          aValue = (a.cost / totalProjectCost) * 100;
          bValue = (b.cost / totalProjectCost) * 100;
          break;
        default:
          return 0;
      }
      
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    });
  };

  const metricCards: MetricCardData[] = [
    {
      value: formatNumber(processedData.usageByProject.length),
      label: '총 활성 프로젝트',
      icon: '📁',
      changeType: 'neutral'
    },
    {
      value: formatCurrency(totalProjectCost),
      label: '총 프로젝트 비용',
      icon: '💰',
      changeType: 'neutral'
    },
    {
      value: formatNumber(totalProjectRequests),
      label: '총 요청 수',
      icon: '📊',
      changeType: 'neutral'
    },
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 lg:mb-12 mt-4 lg:mt-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-text-primary mb-3">📁 프로젝트별 분석</h1>
          <p className="text-text-secondary">프로젝트 단위의 OpenAI API 사용 현황 및 비용 관리</p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-3 gap-4 sm:gap-6 mb-8 lg:mb-12">
          {metricCards.map((data, index) => (
            <MetricCard
              key={index}
              data={data}
              size="md"
              showTrend={false}
            />
          ))}
        </div>


        {/* Detailed Project Table */}
        <AppleCard>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">📋 전체 프로젝트 목록</h3>
            <div className="text-sm text-text-secondary">
              총 {processedData.usageByProject.length}개 프로젝트
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-border-primary">
                <tr>
                  <th className="text-left py-3 px-2 font-semibold text-text-primary">프로젝트</th>
                  <th className="text-right py-3 px-2 font-semibold text-text-primary cursor-pointer hover:bg-background-secondary/50" onClick={() => handleSort('cost')}>
                    비용 {sortBy === 'cost' && (sortOrder === 'desc' ? '↓' : '↑')}
                  </th>
                  <th className="text-right py-3 px-2 font-semibold text-text-primary cursor-pointer hover:bg-background-secondary/50" onClick={() => handleSort('requests')}>
                    사용일수 {sortBy === 'requests' && (sortOrder === 'desc' ? '↓' : '↑')}
                  </th>
                  <th className="text-right py-3 px-2 font-semibold text-text-primary cursor-pointer hover:bg-background-secondary/50" onClick={() => handleSort('percentage')}>
                    점유율 {sortBy === 'percentage' && (sortOrder === 'desc' ? '↓' : '↑')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {getSortedProjects().map((project) => {
                    const costPercentage = (project.cost / totalProjectCost) * 100;
                    
                    return (
                      <tr key={project.projectId} className="border-b border-border-secondary hover:bg-background-secondary/30">
                        <td className="py-3 px-2">
                          <div>
                            <div className="font-medium text-text-primary">{project.projectName}</div>
                            <div className="text-sm text-text-secondary">{project.projectId.slice(0, 16)}...</div>
                          </div>
                        </td>
                        <td className="py-3 px-2 text-right font-semibold">{formatCurrency(project.cost)}</td>
                        <td className="py-3 px-2 text-right">{formatNumber(project.requests)}</td>
                        <td className="py-3 px-2 text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <div className="w-12 h-2 bg-border-primary rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-apple-green rounded-full"
                                style={{ width: `${Math.max(2, costPercentage)}%` }}
                              />
                            </div>
                            <span className="text-sm">{costPercentage.toFixed(1)}%</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </AppleCard>

        {/* Project Performance Analysis */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 lg:gap-8 mt-8">
          {/* Cost Efficiency */}
          <AppleCard>
            <h3 className="text-lg font-semibold mb-6">⚡ 비용 효율성 분석</h3>
            <div className="space-y-4">
              {processedData.usageByProject
                .sort((a, b) => (a.cost / a.requests) - (b.cost / b.requests))
                .slice(0, 5)
                .map((project, index) => {
                  const costPerRequest = project.requests > 0 ? project.cost / project.requests : 0;
                  return (
                    <div key={project.projectId} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-apple-green rounded-full flex items-center justify-center">
                          <span className="text-white text-xs font-bold">{index + 1}</span>
                        </div>
                        <div>
                          <div className="font-medium text-sm">{project.projectName}</div>
                          <div className="text-xs text-text-secondary">{formatNumber(project.requests)} 요청</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-apple-green">{formatCurrency(costPerRequest)}</div>
                        <div className="text-xs text-text-secondary">요청당</div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </AppleCard>

          {/* High Usage Projects */}
          <AppleCard>
            <h3 className="text-lg font-semibold mb-6">📊 자주 사용한 프로젝트</h3>
            <div className="space-y-4">
              {processedData.usageByProject
                .sort((a, b) => b.requests - a.requests)
                .slice(0, 5)
                .map((project, index) => {
                  const tokensPerRequest = project.requests > 0 ? project.tokens / project.requests : 0;
                  return (
                    <div key={project.projectId} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-apple-orange rounded-full flex items-center justify-center">
                          <span className="text-white text-xs font-bold">{index + 1}</span>
                        </div>
                        <div>
                          <div className="font-medium text-sm">{project.projectName}</div>
                          <div className="text-xs text-text-secondary">{formatCurrency(project.cost)} 비용</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-apple-orange">{formatNumber(project.requests)}</div>
                        <div className="text-xs text-text-secondary">(일)</div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </AppleCard>
        </div>
      </div>
    </div>
  );
};
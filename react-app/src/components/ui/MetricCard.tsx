import React from 'react';
import { MetricCardProps } from '@/types';
import { AppleCard } from './AppleCard';

export const MetricCard: React.FC<MetricCardProps> = ({
  data,
  size = 'md',
  showTrend = false
}) => {
  const { value, label, icon, change, changeType, trend } = data;
  
  const sizeClasses = {
    sm: 'min-h-[120px]',
    md: 'min-h-[140px]',
    lg: 'min-h-[160px]'
  };
  
  const valueSize = {
    sm: 'text-2xl',
    md: 'text-3xl',
    lg: 'text-4xl'
  };
  
  const changeColorClasses = {
    positive: 'text-apple-green bg-green-50',
    negative: 'text-apple-red bg-red-50',
    neutral: 'text-text-secondary bg-bg-secondary'
  };

  return (
    <AppleCard className={`${sizeClasses[size]} relative overflow-hidden`} hoverable>
      <div className="flex flex-col h-full">
        {/* Header with icon */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-2xl">{icon}</span>
          {change && (
            <div className={`px-2 py-1 rounded-full text-xs font-semibold ${changeColorClasses[changeType]}`}>
              {changeType === 'positive' ? '+' : changeType === 'negative' ? '' : ''}{change}
            </div>
          )}
        </div>
        
        {/* Value */}
        <div className={`font-bold bg-gradient-to-r from-apple-blue to-apple-purple bg-clip-text text-transparent ${valueSize[size]} mb-2`}>
          {value}
        </div>
        
        {/* Label */}
        <div className="text-text-secondary text-sm font-medium mb-4">
          {label}
        </div>
        
        {/* Trend sparkline */}
        {showTrend && trend && trend.length > 0 && (
          <div className="flex-1 flex items-end">
            <div className="w-full h-8 flex items-end space-x-1">
              {trend.slice(-12).map((point, index) => {
                const maxValue = Math.max(...trend);
                const height = maxValue > 0 ? (point / maxValue) * 100 : 0;
                return (
                  <div
                    key={index}
                    className="flex-1 bg-gradient-to-t from-apple-blue to-apple-blue/40 rounded-sm"
                    style={{ height: `${Math.max(height, 2)}%` }}
                  />
                );
              })}
            </div>
          </div>
        )}
        
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-apple-blue/5 to-apple-purple/5 rounded-full -translate-y-8 translate-x-8" />
      </div>
    </AppleCard>
  );
};
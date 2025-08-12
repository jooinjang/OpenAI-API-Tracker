import React from 'react';
import { AppleCardProps } from '@/types';

export const AppleCard: React.FC<AppleCardProps> = ({
  children,
  className = '',
  hoverable = false,
  padding = 'md'
}) => {
  const baseClasses = 'bg-bg-tertiary border border-border-primary rounded-xl shadow-apple-md transition-all duration-300';
  
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };
  
  const hoverClasses = hoverable 
    ? 'hover:-translate-y-1 hover:shadow-apple-lg cursor-pointer' 
    : '';
  
  const cardClasses = `
    ${baseClasses}
    ${paddingClasses[padding]}
    ${hoverClasses}
    ${className}
  `.trim();

  return (
    <div className={cardClasses}>
      {children}
    </div>
  );
};
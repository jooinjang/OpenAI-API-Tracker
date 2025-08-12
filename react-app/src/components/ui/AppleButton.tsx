import React from 'react';
import { AppleButtonProps } from '@/types';

export const AppleButton: React.FC<AppleButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  className = ''
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-500/20';
  
  const variantClasses = {
    primary: 'bg-apple-blue text-white hover:bg-apple-blue-hover active:scale-95 shadow-apple-md',
    secondary: 'bg-bg-secondary text-text-primary border border-border-primary hover:bg-bg-tertiary active:scale-95',
    ghost: 'text-apple-blue hover:bg-blue-50 active:scale-95'
  };
  
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm min-h-[36px]',
    md: 'px-6 py-3 text-sm min-h-[44px]',
    lg: 'px-8 py-4 text-base min-h-[52px]'
  };
  
  const buttonClasses = `
    ${baseClasses}
    ${variantClasses[variant]}
    ${sizeClasses[size]}
    ${disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
    ${className}
  `.trim();

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading && (
        <div className="apple-spinner mr-2" />
      )}
      {children}
    </button>
  );
};
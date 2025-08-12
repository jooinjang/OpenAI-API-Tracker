import React from 'react';
import { AppleButton } from './AppleButton';

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  details?: Array<{ label: string; value: string }>;
  confirmButtonText?: string;
  confirmButtonVariant?: 'primary' | 'secondary' | 'ghost';
  isDestructive?: boolean;
  isLoading?: boolean;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  details = [],
  confirmButtonText = '확인',
  confirmButtonVariant = 'primary',
  isDestructive = false,
  isLoading = false
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/70 transition-opacity" onClick={onClose} />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 shadow-2xl transition-all border border-gray-200 dark:border-gray-700">
          {/* Header */}
          <div className={`px-6 py-4 ${isDestructive ? 'border-b border-apple-red/20 bg-red-50 dark:bg-red-950/20' : 'border-b border-border-primary'}`}>
            <div className="flex items-center">
              <div className={`mr-3 flex h-10 w-10 items-center justify-center rounded-full ${isDestructive ? 'bg-apple-red/20 text-apple-red' : 'bg-apple-blue/20 text-apple-blue'}`}>
                {isDestructive ? '⚠️' : 'ℹ️'}
              </div>
              <h3 className="text-lg font-semibold text-text-primary">
                {title}
              </h3>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-4">
            <p className="mb-4 text-text-secondary">
              {message}
            </p>

            {/* Details */}
            {details.length > 0 && (
              <div className="mb-4 rounded-lg bg-gray-50 dark:bg-gray-700 p-4 border border-gray-200 dark:border-gray-600">
                <h4 className="mb-2 text-sm font-semibold text-gray-900 dark:text-white">
                  세부 정보
                </h4>
                <div className="space-y-2">
                  {details.map((detail, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-300">{detail.label}:</span>
                      <span className="font-medium text-gray-900 dark:text-white">{detail.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {isDestructive && (
              <div className="mb-4 rounded-lg bg-red-50 dark:bg-red-900/30 p-4 border border-red-200 dark:border-red-800">
                <p className="text-sm text-red-600 dark:text-red-400">
                  ⚠️ 이 작업은 되돌릴 수 없습니다. 신중하게 진행해주세요.
                </p>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
            <AppleButton
              variant="ghost"
              onClick={onClose}
              disabled={isLoading}
            >
              취소
            </AppleButton>
            <AppleButton
              variant={isDestructive ? 'ghost' : confirmButtonVariant}
              onClick={onConfirm}
              disabled={isLoading}
              className={isDestructive ? 'text-apple-red hover:bg-red-50 dark:hover:bg-red-950/20' : ''}
            >
              {isLoading ? '처리 중...' : confirmButtonText}
            </AppleButton>
          </div>
        </div>
      </div>
    </div>
  );
};
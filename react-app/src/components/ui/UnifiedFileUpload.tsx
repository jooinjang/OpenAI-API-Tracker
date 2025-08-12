import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { AppleCard } from "./AppleCard";
import { AppleButton } from "./AppleButton";

interface UnifiedFileUploadProps {
  onFileUpload: (file: File, detectedType: 'user' | 'project' | 'userinfo') => void;
  className?: string;
  maxSize?: number;
}

export const UnifiedFileUpload: React.FC<UnifiedFileUploadProps> = ({
  onFileUpload,
  className = "",
  maxSize = 10 * 1024 * 1024, // 10MB
}) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if data looks like userinfo structure
  const isUserInfoData = (data: any): boolean => {
    if (!data || typeof data !== 'object') return false;
    
    // Check for userinfo array format
    if (Array.isArray(data)) {
      return data.length > 0 && data.every((item: any) => 
        item && typeof item === 'object' && 
        'id' in item && 
        'name' in item
      );
    }
    
    // Check for userinfo object format
    const values = Object.values(data);
    return values.length > 0 && values.every((item: any) =>
      item && typeof item === 'object' && 
      'name' in item
    );
  };

  // Detect data type from JSON structure
  const detectDataType = (data: any): 'user' | 'project' | 'userinfo' => {
    // First check if this looks like userinfo data
    if (isUserInfoData(data)) {
      return 'userinfo';
    }
    if (!data || typeof data !== 'object' || !data.data || !Array.isArray(data.data)) {
      throw new Error('올바른 OpenAI 사용량 데이터 형식이 아닙니다.');
    }

    // Check first few buckets for data type indicators
    const sampleBuckets = data.data.slice(0, 3);
    let userIndicators = 0;
    let projectIndicators = 0;

    for (const bucket of sampleBuckets) {
      const results = bucket.results || bucket.result || [];
      
      for (const item of results.slice(0, 5)) { // Check first 5 items per bucket
        if (item.user_id && typeof item.user_id === 'string') {
          userIndicators++;
        }
        if (item.project_id && typeof item.project_id === 'string') {
          projectIndicators++;
        }
      }
    }

    // If we found both, go with the more prevalent one
    if (projectIndicators > userIndicators) {
      return 'project';
    } else if (userIndicators > 0) {
      return 'user';
    }

    // Fallback: if no clear indicators, assume user data
    console.warn('Could not clearly detect data type, defaulting to user data');
    return 'user';
  };

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      setUploading(true);
      setError(null);

      try {
        // Validate file type
        if (!file.name.toLowerCase().endsWith(".json")) {
          throw new Error("JSON 파일만 업로드 가능합니다.");
        }

        // Validate file size
        if (file.size > maxSize) {
          throw new Error(
            `파일 크기는 ${Math.round(
              maxSize / 1024 / 1024
            )}MB를 초과할 수 없습니다.`
          );
        }

        // Parse and detect data type
        const text = await file.text();
        const data = JSON.parse(text);

        if (!data || typeof data !== "object") {
          throw new Error("올바른 JSON 파일이 아닙니다.");
        }

        // Detect whether this is user or project data
        const detectedType = detectDataType(data);

        console.log(`📊 Detected data type: ${detectedType}`);
        
        onFileUpload(file, detectedType);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "파일 업로드 중 오류가 발생했습니다."
        );
      } finally {
        setUploading(false);
      }
    },
    [onFileUpload, maxSize]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/json": [".json"],
    },
    maxSize,
    multiple: false,
    disabled: uploading,
  });

  return (
    <AppleCard className={className}>
      <div
        {...getRootProps()}
        className={`
          apple-file-upload
          ${isDragActive ? "dragover border-apple-green bg-green-50" : ""}
          ${uploading ? "cursor-not-allowed opacity-50" : "cursor-pointer"}
          ${error ? "border-apple-red bg-red-50" : ""}
        `}
      >
        <input {...getInputProps()} />

        <div className="text-center">
          {uploading ? (
            <div className="flex flex-col items-center">
              <div className="apple-spinner mb-4" />
              <p className="text-text-secondary">분석 중...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="mb-4 text-4xl">
                {isDragActive ? "📤" : "📊"}
              </div>

              <h3 className="mb-2 text-lg font-semibold text-text-primary">
                📊 OpenAI 사용량 데이터 업로드
              </h3>

              <p className="mb-6 max-w-sm text-text-secondary">
                {isDragActive 
                  ? "파일을 여기에 놓으세요" 
                  : "OpenAI에서 다운로드한 사용량 JSON 파일이나 사용자 정보(userinfo.json) 파일을 업로드하세요. 데이터 타입이 자동으로 감지됩니다."
                }
              </p>

              <AppleButton variant="primary">파일 선택</AppleButton>

              <p className="mt-3 text-xs text-text-tertiary">
                최대 {Math.round(maxSize / 1024 / 1024)}MB, JSON 형식만 지원
              </p>
              
              <div className="mt-4 text-xs text-text-tertiary">
                <p>💡 자동 감지 기능:</p>
                <p>• 사용자별 데이터 → 사용자별 분석</p>
                <p>• 프로젝트별 데이터 → 프로젝트별 분석</p>
                <p>• 사용자 정보 데이터 → 사용자 이름 매핑</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3">
          <div className="flex items-center">
            <span className="mr-2 text-red-500">⚠️</span>
            <span className="text-sm text-red-700">{error}</span>
          </div>
        </div>
      )}
    </AppleCard>
  );
};
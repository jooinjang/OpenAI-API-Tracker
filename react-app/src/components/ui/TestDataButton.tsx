import React from 'react';
import { AppleButton } from './AppleButton';
import { useAppActions } from '@/store/useAppStore';
import { generateSampleData } from '@/utils/dataProcessor';
import type { UserData, ProjectData } from '@/types';

export const TestDataButton: React.FC = () => {
  const { setUserData, setProjectData } = useAppActions();

  const loadSampleData = () => {
    const userData = generateSampleData('user', 50) as UserData;
    const projectData = generateSampleData('project', 30) as ProjectData;
    
    setUserData(userData);
    setProjectData(projectData);
  };

  return (
    <AppleButton
      variant="secondary"
      onClick={loadSampleData}
    >
      🧪 샘플 데이터 로드
    </AppleButton>
  );
};
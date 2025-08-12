import React from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Dashboard } from '@/components/views/Dashboard';
import { Users } from '@/components/views/Users';
import { Projects } from '@/components/views/Projects';
import { Budgets } from '@/components/views/Budgets';
import { RateLimits } from '@/components/views/RateLimits';
import { useSelectedView } from '@/store/useAppStore';

const App: React.FC = () => {
  const selectedView = useSelectedView();

  const renderView = () => {
    switch (selectedView) {
      case 'dashboard':
        return <Dashboard />;
      case 'users':
        return <Users />;
      case 'projects':
        return <Projects />;
      case 'budgets':
        return <Budgets />;
      case 'rate-limits':
        return <RateLimits />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <MainLayout>
      {renderView()}
    </MainLayout>
  );
};

export default App;
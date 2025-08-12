import React, { useEffect, useState } from 'react';
import { useTheme } from '@/store/useAppStore';
import { Sidebar } from './Sidebar';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { theme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile screen size
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 1024); // lg breakpoint
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // Apply theme to document element
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('light', 'dark');
    
    if (theme === 'system') {
      // Let CSS handle system preference
      return;
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  // Hide loading screen when layout mounts
  useEffect(() => {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
      loadingScreen.style.opacity = '0';
      setTimeout(() => {
        loadingScreen.remove();
      }, 500);
    }
  }, []);

  return (
    <div className="flex h-screen bg-bg-primary">
      {/* Mobile Overlay */}
      {isMobile && sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <Sidebar 
        className={`
          flex-shrink-0 
          ${isMobile ? 'fixed z-50 h-full' : 'relative'}
          ${isMobile && !sidebarOpen ? '-translate-x-full' : 'translate-x-0'}
          transition-transform duration-300 ease-in-out
        `}
      />
      
      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {/* Mobile Header */}
        {isMobile && (
          <div className="lg:hidden bg-bg-secondary border-b border-border-primary p-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="apple-button-secondary text-sm"
            >
              ☰ 메뉴
            </button>
          </div>
        )}
        
        <div className="h-full overflow-auto">
          {children}
        </div>
      </main>
    </div>
  );
};
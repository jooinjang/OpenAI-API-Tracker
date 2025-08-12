import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  useSelectedView,
  useAppActions,
  useProcessedData,
  useAppStore,
} from "@/store/useAppStore";
import { AppleButton } from "@/components/ui/AppleButton";

interface SidebarProps {
  className?: string;
}

const navigationItems = [
  { id: "dashboard", label: "대시보드", icon: "📊" },
  { id: "users", label: "사용자별", icon: "👥" },
  { id: "projects", label: "프로젝트별", icon: "📁" },
  { id: "budgets", label: "예산 관리", icon: "💰" },
  { id: "rate-limits", label: "Rate Limit 관리", icon: "⚙️" },
] as const;

export const Sidebar: React.FC<SidebarProps> = ({ className = "" }) => {
  const selectedView = useSelectedView();
  const processedData = useProcessedData();
  const { userData, projectData } = useAppStore();
  const {
    setSelectedView,
    clearAllData,
    exportData,
  } = useAppActions();

  // Local resizable width (default 320px)
  const [sidebarWidth, setSidebarWidth] = useState<number>(320);
  const [isResizing, setIsResizing] = useState<boolean>(false);
  const sidebarRef = useRef<HTMLDivElement>(null);

  // Load saved width from localStorage on mount
  useEffect(() => {
    const savedWidth = localStorage.getItem('sidebarWidth');
    if (savedWidth) {
      const width = parseInt(savedWidth, 10);
      if (width >= 260 && width <= 520) {
        setSidebarWidth(width);
      }
    }
  }, []);

  // Save width to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('sidebarWidth', sidebarWidth.toString());
  }, [sidebarWidth]);

  const onResizeMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  useEffect(() => {
    if (!isResizing) return;
    const handleMove = (e: MouseEvent) => {
      const min = 260;
      const max = 520;
      const newWidth = Math.min(Math.max(e.clientX, min), max);
      setSidebarWidth(newWidth);
    };
    const handleUp = () => {
      setIsResizing(false);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
    document.addEventListener("mousemove", handleMove);
    document.addEventListener("mouseup", handleUp);
    return () => {
      document.removeEventListener("mousemove", handleMove);
      document.removeEventListener("mouseup", handleUp);
    };
  }, [isResizing]);

  // Filter navigation items based on available data
  const getVisibleNavigationItems = useCallback(() => {
    // Always show dashboard
    const visibleItems = [navigationItems[0]]; // dashboard
    
    // Show users tab only if user data is available
    if (userData) {
      visibleItems.push(navigationItems[1]); // users
    }
    
    // Show projects tab only if project data is available
    if (projectData) {
      visibleItems.push(navigationItems[2]); // projects
    }
    
    // Always show budget and rate limits tabs (they don't depend on specific data type)
    visibleItems.push(navigationItems[3]); // budgets
    visibleItems.push(navigationItems[4]); // rate-limits
    
    return visibleItems;
  }, [userData, projectData]);

  // Auto-redirect to dashboard if current view is not available
  useEffect(() => {
    const visibleItems = getVisibleNavigationItems();
    const visibleIds = visibleItems.map(item => item.id);
    
    if (!visibleIds.includes(selectedView)) {
      setSelectedView("dashboard");
    }
  }, [getVisibleNavigationItems, selectedView, setSelectedView]);

  return (
    <aside
      ref={sidebarRef}
      className={`apple-sidebar relative flex h-full flex-col ${className}`}
      style={{ width: `${sidebarWidth}px` }}
    >
      {/* Header */}
      <div className="border-b border-border-primary p-6">
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-apple-blue to-apple-purple">
            <span className="text-lg font-bold text-white">O</span>
          </div>
          <div>
            <h1 className="font-bold text-text-primary">OpenAI Tracker</h1>
            <p className="text-xs text-text-secondary">API 사용량 분석</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          {getVisibleNavigationItems().map((item) => (
            <button
              key={item.id}
              onClick={() => setSelectedView(item.id as any)}
              className={`
                apple-nav-item w-full
                ${selectedView === item.id ? "active" : ""}
              `}
            >
              <span className="mr-3 text-base">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Data Status */}
      {processedData && (
        <div className="border-t border-border-primary p-4">
          <div className="bg-bg-secondary rounded-xl p-4">
            <h3 className="mb-3 text-sm font-semibold text-text-primary">
              📈 데이터 현황
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-text-secondary">총 비용</span>
                <span className="font-semibold text-apple-blue">
                  ${processedData.totalCost.toFixed(4)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">총 요청</span>
                <span className="font-semibold text-text-primary">
                  {processedData.totalRequests.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">활성 사용자</span>
                <span className="font-semibold text-text-primary">
                  {processedData.activeUsers}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="space-y-2 border-t border-border-primary p-4">
        {processedData && (
          <>
            <AppleButton
              variant="secondary"
              size="sm"
              onClick={() => exportData("json")}
              className="w-full justify-center text-xs"
            >
              📥 JSON 내보내기
            </AppleButton>
            <AppleButton
              variant="secondary"
              size="sm"
              onClick={() => exportData("csv")}
              className="w-full justify-center text-xs"
            >
              📊 CSV 내보내기
            </AppleButton>
            <AppleButton
              variant="ghost"
              size="sm"
              onClick={clearAllData}
              className="w-full justify-center text-xs text-apple-red hover:bg-red-50"
            >
              🗑️ 데이터 지우기
            </AppleButton>
          </>
        )}
      </div>

      {/* Resize handle */}
      <div
        className={`absolute right-0 top-0 h-full w-1 cursor-col-resize transition-colors ${
          isResizing
            ? "bg-apple-blue/40"
            : "bg-transparent hover:bg-apple-blue/30"
        }`}
        onMouseDown={onResizeMouseDown}
        title="드래그하여 사이드바 너비 조절"
      />

      {/* Footer */}
      <div className="border-t border-border-primary p-4">
        <p className="text-center text-xs text-text-tertiary">
          React + Apple Design System
        </p>
      </div>
    </aside>
  );
};

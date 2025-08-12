import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import {
  AppState,
  UserData,
  ProjectData,
  ProcessedUsageData,
  UserInfo,
  AppSettings,
  AppError,
  Budget,
} from "@/types";
import { processUsageData } from "@/utils/dataProcessor";

interface AppStore extends AppState {
  // Data Management
  setUserData: (data: UserData | null) => void;
  setProjectData: (data: ProjectData | null) => void;
  setUserInfo: (userInfo: UserInfo) => void;
  updateUserInfo: (
    userId: string,
    info: { name: string; email?: string; organization?: string }
  ) => void;
  setUserInfoFromFile: (json: unknown) => void;
  
  // Project Management
  projects: Record<string, { id: string; name: string }>;
  setProjects: (projects: Array<{ id: string; name: string }>) => void;

  // UI State
  setSelectedView: (view: AppState["selectedView"]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setTheme: (theme: AppState["theme"]) => void;

  // Settings
  settings: AppSettings;
  updateSettings: (settings: Partial<AppSettings>) => void;

  // Budgets
  budgets: Record<string, Budget>;
  setBudget: (projectId: string, budget: Budget) => void;
  removeBudget: (projectId: string) => void;
  clearAllBudgets: () => void;

  // File Upload
  uploadProgress: Record<string, number>;
  setUploadProgress: (fileId: string, progress: number) => void;

  // Computed values
  getProcessedData: () => ProcessedUsageData | null;
  getTotalCost: () => number;
  getTotalRequests: () => number;
  getActiveUsers: () => number;

  // Actions
  clearAllData: () => void;
  exportData: (format: "json" | "csv") => void;

  // Error handling
  errors: AppError[];
  addError: (error: AppError) => void;
  clearErrors: () => void;

  // Filters and sorting
  filters: {
    dateRange?: { start: string; end: string };
    models?: string[];
    users?: string[];
    projects?: string[];
  };
  setFilters: (filters: AppStore["filters"]) => void;

  // Search
  searchQuery: string;
  setSearchQuery: (query: string) => void;

  // Admin API Key Management
  adminApiKey: string | null;
  setAdminApiKey: (key: string | null) => void;
  clearAdminApiKey: () => void;
}

// Default settings
const defaultSettings: AppSettings = {
  theme: "system",
  language: "ko",
  dateFormat: "YYYY-MM-DD",
  currency: "USD",
  refreshInterval: 300000, // 5 minutes
  autoSave: true,
  notifications: {
    budgetAlerts: true,
    dataUpdates: true,
    errors: true,
  },
};

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Initial state
      userData: null,
      projectData: null,
      userInfo: {},
      processedData: null,
      selectedView: "dashboard",
      loading: false,
      error: null,
      theme: "system",
      settings: defaultSettings,
      budgets: {},
      uploadProgress: {},
      errors: [],
      filters: {},
      searchQuery: "",
      projects: {},
      adminApiKey: null,

      // Data management actions
      setUserData: (data) => {
        set((state) => {
          const newState = { ...state, userData: data };
          // Automatically reprocess data when user data changes
          const processedData = processUsageData(
            data,
            state.projectData,
            state.userInfo,
            state.projects
          );
          return { ...newState, processedData };
        });
      },

      setProjectData: (data) => {
        set((state) => {
          const newState = { ...state, projectData: data };
          // Automatically reprocess data when project data changes
          const processedData = processUsageData(
            state.userData,
            data,
            state.userInfo,
            state.projects
          );
          return { ...newState, processedData };
        });
      },

      setUserInfo: (userInfo) => {
        set((state) => {
          const newState = { ...state, userInfo };
          // Reprocess data with new user info
          const processedData = processUsageData(
            state.userData,
            state.projectData,
            userInfo,
            state.projects
          );
          return { ...newState, processedData };
        });
      },

      setUserInfoFromFile: (json) => {
        // Accept both array format (userinfo.json) and map format
        try {
          let userInfo: UserInfo = {};
          if (Array.isArray(json)) {
            for (const item of json as any[]) {
              if (item && item.id) {
                userInfo[item.id] = {
                  name: item.name || item.email || item.id,
                  email: item.email,
                  organization: (item as any).organization,
                };
              }
            }
          } else if (json && typeof json === "object") {
            // Already in map form
            userInfo = json as UserInfo;
          }
          set((state) => {
            const newState = { ...state, userInfo };
            const processedData = processUsageData(
              state.userData,
              state.projectData,
              userInfo,
              state.projects
            );
            return { ...newState, processedData };
          });
        } catch (e) {
          // No-op: validation should be done in caller
        }
      },

      updateUserInfo: (userId, info) => {
        set((state) => {
          const newUserInfo = {
            ...state.userInfo,
            [userId]: { ...state.userInfo[userId], ...info },
          };
          const processedData = processUsageData(
            state.userData,
            state.projectData,
            newUserInfo,
            state.projects
          );
          return { userInfo: newUserInfo, processedData };
        });
      },

      // UI state actions
      setSelectedView: (view) => set({ selectedView: view }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      setTheme: (theme) => {
        set({ theme });
        // Apply theme to document
        if (theme === "system") {
          document.documentElement.classList.remove("light", "dark");
        } else {
          document.documentElement.classList.remove("light", "dark");
          document.documentElement.classList.add(theme);
        }
      },

      // Settings actions
      updateSettings: (newSettings) => {
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        }));
      },

      // Budget management
      setBudget: (projectId, budget) => {
        set((state) => ({
          budgets: { ...state.budgets, [projectId]: budget },
        }));
      },

      removeBudget: (projectId) => {
        set((state) => {
          const newBudgets = { ...state.budgets };
          delete newBudgets[projectId];
          return { budgets: newBudgets };
        });
      },

      clearAllBudgets: () => {
        set({ budgets: {} });
      },

      // Project management
      setProjects: (projectsList) => {
        set((state) => {
          const projectsMap: Record<string, { id: string; name: string }> = {};
          projectsList.forEach(p => {
            projectsMap[p.id] = { id: p.id, name: p.name };
          });
          
          // Reprocess data with new project information
          const processedData = processUsageData(
            state.userData,
            state.projectData,
            state.userInfo,
            projectsMap
          );
          
          return { ...state, projects: projectsMap, processedData };
        });
      },

      // File upload progress
      setUploadProgress: (fileId, progress) => {
        set((state) => ({
          uploadProgress: { ...state.uploadProgress, [fileId]: progress },
        }));
      },

      // Computed values
      getProcessedData: () => {
        const state = get();
        return state.processedData;
      },

      getTotalCost: () => {
        const state = get();
        return state.processedData?.totalCost || 0;
      },

      getTotalRequests: () => {
        const state = get();
        return state.processedData?.totalRequests || 0;
      },

      getActiveUsers: () => {
        const state = get();
        return state.processedData?.activeUsers || 0;
      },

      // Utility actions
      clearAllData: () => {
        set({
          userData: null,
          projectData: null,
          processedData: null,
          error: null,
          uploadProgress: {},
        });
      },

      exportData: (format) => {
        const state = get();
        if (!state.processedData) return;

        if (format === "json") {
          const dataStr = JSON.stringify(state.processedData, null, 2);
          const blob = new Blob([dataStr], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = `usage_data_${
            new Date().toISOString().split("T")[0]
          }.json`;
          link.click();
          URL.revokeObjectURL(url);
        } else if (format === "csv") {
          // Implement CSV export using the utility function
          import("@/utils/dataProcessor").then(({ exportToCSV }) => {
            exportToCSV(
              state.processedData!,
              `usage_data_${new Date().toISOString().split("T")[0]}.csv`
            );
          });
        }
      },

      // Error handling
      addError: (error) => {
        set((state) => ({
          errors: [...state.errors, error].slice(-10), // Keep only last 10 errors
        }));
      },

      clearErrors: () => set({ errors: [] }),

      // Filters and search
      setFilters: (filters) => set({ filters }),
      setSearchQuery: (searchQuery) => set({ searchQuery }),

      // Admin API Key management
      setAdminApiKey: (key) => set({ adminApiKey: key }),
      clearAdminApiKey: () => set({ adminApiKey: null }),
    }),
    {
      name: "openai-usage-tracker-storage",
      storage: createJSONStorage(() => localStorage),
      // Only persist certain fields
      partialize: (state) => ({
        userInfo: state.userInfo,
        settings: state.settings,
        budgets: state.budgets,
        theme: state.theme,
        adminApiKey: state.adminApiKey, // persist admin API key securely in localStorage
      }),
    }
  )
);

// Simple theme selector hooks (useEffect should be handled in components)
export const useTheme = () => {
  const theme = useAppStore((state) => state.theme);
  const setTheme = useAppStore((state) => state.setTheme);
  return { theme, setTheme };
};

// Selector hooks for performance optimization
export const useUserData = () => useAppStore((state) => state.userData);
export const useProjectData = () => useAppStore((state) => state.projectData);
export const useProcessedData = () =>
  useAppStore((state) => state.processedData);
export const useSelectedView = () => useAppStore((state) => state.selectedView);
export const useLoading = () => useAppStore((state) => state.loading);
export const useError = () => useAppStore((state) => state.error);
export const useSettings = () => useAppStore((state) => state.settings);
export const useBudgets = () => useAppStore((state) => state.budgets);
export const useProjects = () => useAppStore((state) => state.projects);
export const useAdminApiKey = () => useAppStore((state) => state.adminApiKey);

// Action hooks
export const useAppActions = () => {
  return useAppStore((state) => ({
    setUserData: state.setUserData,
    setProjectData: state.setProjectData,
    setUserInfo: state.setUserInfo,
    updateUserInfo: state.updateUserInfo,
    setUserInfoFromFile: state.setUserInfoFromFile,
    setSelectedView: state.setSelectedView,
    setLoading: state.setLoading,
    setError: state.setError,
    updateSettings: state.updateSettings,
    setBudget: state.setBudget,
    removeBudget: state.removeBudget,
    clearAllBudgets: state.clearAllBudgets,
    setProjects: state.setProjects,
    clearAllData: state.clearAllData,
    exportData: state.exportData,
    addError: state.addError,
    clearErrors: state.clearErrors,
    setFilters: state.setFilters,
    setSearchQuery: state.setSearchQuery,
    setAdminApiKey: state.setAdminApiKey,
    clearAdminApiKey: state.clearAdminApiKey,
  }));
};

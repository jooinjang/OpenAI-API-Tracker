// OpenAI Usage Tracker Types
export interface UsageData {
  id: string;
  timestamp: string;
  model: string;
  user_id?: string;
  project_id?: string;
  operation: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  cost: number;
  n_requests: number; // Actual number of requests
  request_id: string;
}

// 2025 OpenAI Usage Data Structure (supports both 'results' and 'result' keys)
// Updated to match real OpenAI data format with amount.value structure
export interface UserData {
  data: Array<{
    start_time?: number; // Unix timestamp for bucket
    end_time?: number;
    results?: Array<{
      user_id: string;
      project_id?: string;
      start_time?: number; // Unix timestamp for individual record
      line_item?: string; // Model identifier in 2025 structure
      model?: string; // Legacy model field
      usage?: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
      };
      // Real OpenAI format uses amount.value
      amount?: {
        value: number;
        currency?: string;
      };
      // Legacy/sample format
      cost?: number;
      n_requests?: number; // Number of actual requests
      operation?: string;
    }>;
    result?: Array<{
      user_id: string;
      project_id?: string;
      start_time?: string | number;
      model?: string;
      line_item?: string;
      usage?: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
      };
      amount?: {
        value: number;
        currency?: string;
      };
      cost?: number;
      n_requests?: number; // Number of actual requests
      operation?: string;
    }>;
  }>;
}

export interface ProjectData {
  data: Array<{
    start_time?: number; // Unix timestamp for bucket
    end_time?: number;
    results?: Array<{
      project_id: string;
      start_time?: number; // Unix timestamp for individual record
      line_item?: string; // Model identifier in 2025 structure
      model?: string; // Legacy model field
      usage?: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
      };
      // Real OpenAI format uses amount.value
      amount?: {
        value: number;
        currency?: string;
      };
      // Legacy/sample format
      cost?: number;
      n_requests?: number; // Number of actual requests
      operation?: string;
    }>;
    result?: Array<{
      project_id: string;
      start_time?: string | number;
      model?: string;
      line_item?: string;
      usage?: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
      };
      amount?: {
        value: number;
        currency?: string;
      };
      cost?: number;
      n_requests?: number; // Number of actual requests
      operation?: string;
    }>;
  }>;
}

export interface UserInfo {
  [userId: string]: {
    name: string;
    email?: string;
    organization?: string;
  };
}

export interface ProcessedUsageData {
  totalCost: number;
  totalRequests: number;
  activeUsers: number;
  usageByDate: Array<{
    date: string;
    cost: number;
    requests: number;
  }>;
  usageByModel: Array<{
    model: string;
    cost: number;
    requests: number;
    tokens: number;
  }>;
  usageByUser: Array<{
    userId: string;
    userName: string;
    cost: number;
    requests: number;
    tokens: number;
  }>;
  usageByProject?: Array<{
    projectId: string;
    projectName: string;
    cost: number;
    requests: number;
    tokens: number;
  }>;
}

export interface MetricCardData {
  value: string;
  label: string;
  icon: string;
  change?: string;
  changeType: "positive" | "negative" | "neutral";
  trend?: number[];
}

export interface ChartData {
  x: string | number;
  y: number;
  label?: string;
  color?: string;
}

export interface ApiKey {
  id: string;
  name: string;
  created: string;
  last_used?: string;
  permissions: string[];
  redacted_key: string;
}

export interface Project {
  id: string;
  name: string;
  created: string;
  status: "active" | "archived";
  api_keys?: ApiKey[];
}

export interface RateLimit {
  id: string;
  model: string;
  max_requests_per_1_minute: number;
  max_tokens_per_1_minute: number;
  max_images_per_1_minute?: number;
  max_audio_megabytes_per_1_minute?: number;
  max_requests_per_1_day?: number;
  batch_1_day_max_input_tokens?: number;
}

export interface ProjectRateLimits {
  project_id: string;
  project_name: string;
  rate_limits: RateLimit[];
}

export interface RateLimitTemplate {
  id: string;
  model: string;
  max_requests_per_1_minute: number;
  max_tokens_per_1_minute: number;
  max_images_per_1_minute?: number;
  max_audio_megabytes_per_1_minute?: number;
  max_requests_per_1_day?: number;
  batch_1_day_max_input_tokens?: number;
}

export interface Budget {
  projectId: string;
  limit: number;
  spent: number;
  period: "monthly" | "yearly";
  alerts: {
    enabled: boolean;
    thresholds: number[];
  };
}

export interface BudgetOverage {
  projectId: string;
  projectName: string;
  budget: number;
  spent: number;
  overageAmount: number;
  overagePercentage: number;
}

// UI State Types
export interface AppState {
  userData: UserData | null;
  projectData: ProjectData | null;
  userInfo: UserInfo;
  processedData: ProcessedUsageData | null;
  selectedView: "dashboard" | "users" | "projects" | "budgets" | "rate-limits";
  loading: boolean;
  error: string | null;
  theme: "light" | "dark" | "system";
}


// Component Props Types
export interface AppleButtonProps {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  className?: string;
}

export interface AppleCardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  padding?: "sm" | "md" | "lg";
}

export interface MetricCardProps {
  data: MetricCardData;
  size?: "sm" | "md" | "lg";
  showTrend?: boolean;
}


export interface ChartProps {
  data: ChartData[];
  type: "line" | "bar" | "pie" | "area";
  title?: string;
  height?: number;
  color?: string;
  className?: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// OpenAI API Types
export interface OpenAIUsageResponse {
  data: Array<{
    aggregation_timestamp: number;
    n_requests: number;
    operation: string;
    snapshot_id: string;
    n_context_tokens_total: number;
    n_generated_tokens_total: number;
  }>;
  has_more: boolean;
  next_page?: string;
}

// Utility Types
export type LoadingState = "idle" | "loading" | "success" | "error";

export type SortDirection = "asc" | "desc";

export interface SortConfig {
  field: string;
  direction: SortDirection;
}

export interface FilterConfig {
  dateRange?: {
    start: string;
    end: string;
  };
  models?: string[];
  users?: string[];
  projects?: string[];
  minCost?: number;
  maxCost?: number;
}

// Form Types
export interface BudgetFormData {
  projectId: string;
  limit: number;
  period: "monthly" | "yearly";
  alertsEnabled: boolean;
  alertThresholds: number[];
}

export interface UserInfoFormData {
  userId: string;
  name: string;
  email?: string;
  organization?: string;
}

// Error Types
export interface AppError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

// Animation Types
export interface AnimationConfig {
  duration: number;
  easing: string;
  delay?: number;
}

export type ViewTransition = "slide" | "fade" | "scale" | "none";

// Theme Types
export interface ThemeConfig {
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
    border: string;
  };
  spacing: Record<string, string>;
  borderRadius: Record<string, string>;
  shadows: Record<string, string>;
}

// Settings Types
export interface AppSettings {
  theme: "light" | "dark" | "system";
  language: "ko" | "en";
  dateFormat: "YYYY-MM-DD" | "MM/DD/YYYY" | "DD/MM/YYYY";
  currency: "USD" | "KRW";
  refreshInterval: number;
  autoSave: boolean;
  notifications: {
    budgetAlerts: boolean;
    dataUpdates: boolean;
    errors: boolean;
  };
}

// Chart Configuration Types
export interface PlotlyConfig {
  displayModeBar: boolean;
  responsive: boolean;
  toImageButtonOptions: {
    format: "png" | "jpeg" | "webp" | "svg";
    filename: string;
    height: number;
    width: number;
    scale: number;
  };
}

export interface ChartLayout {
  title?: string;
  xaxis?: {
    title?: string;
    type?: "linear" | "log" | "date" | "category";
  };
  yaxis?: {
    title?: string;
    type?: "linear" | "log";
  };
  showlegend?: boolean;
  margin?: {
    l: number;
    r: number;
    t: number;
    b: number;
  };
  paper_bgcolor?: string;
  plot_bgcolor?: string;
  font?: {
    family: string;
    size: number;
    color: string;
  };
}

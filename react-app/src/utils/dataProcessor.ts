// Data Processing Utilities - Migrated from Python utils.py
import { 
  UsageData, 
  UserData, 
  ProjectData, 
  ProcessedUsageData, 
  UserInfo,
  ChartData,
  BudgetOverage 
} from '@/types';

/**
 * Extract results from 2025 bucket structure (matches Streamlit version exactly)
 */
export function extractResultsFromBuckets(data: UserData | ProjectData): UsageData[] {
  const results: UsageData[] = [];
  
  // Handle case where data is a dictionary with "data" key
  let buckets: any[] = [];
  if (data && typeof data === 'object') {
    if ('data' in data && Array.isArray(data.data)) {
      buckets = data.data;
    } else if (Array.isArray(data)) {
      // Already extracted results
      return data as UsageData[];
    }
  }
  
  buckets.forEach((bucket, bucketIndex) => {
    // Check for 'results' key (2025 structure) or fallback to 'result'
    const bucketResults = bucket.results || bucket.result;
    
    if (bucketResults && Array.isArray(bucketResults)) {
      bucketResults.forEach((item: any, itemIndex: number) => {
        // Extract timestamp from bucket or item
        const timestamp = item.start_time || bucket.start_time;
        const dateStr = timestamp ? new Date(timestamp * 1000).toISOString() : new Date().toISOString();
        
        // Extract cost - support both amount.value (real format) and cost (legacy)
        let cost = 0;
        if (item.amount && typeof item.amount === 'object' && 'value' in item.amount) {
          cost = item.amount.value; // Real OpenAI format
        } else if (typeof item.cost === 'number') {
          cost = item.cost; // Legacy/sample format
        }
        
        results.push({
          id: `${bucketIndex}-${itemIndex}`,
          timestamp: dateStr,
          model: item.line_item || item.model || 'unknown', // Use line_item for 2025 structure
          user_id: item.user_id,
          project_id: item.project_id,
          operation: item.operation || 'completion',
          usage: {
            prompt_tokens: item.usage?.prompt_tokens || 0,
            completion_tokens: item.usage?.completion_tokens || 0,
            total_tokens: item.usage?.total_tokens || 0
          },
          cost,
          n_requests: item.n_requests || 1, // Extract actual request count
          request_id: `req_${bucketIndex}_${itemIndex}`
        });
      });
    }
  });
  
  return results;
}

/**
 * Calculate total cost from usage data
 */
export function getTotalCost(data: UserData | ProjectData): [number, UsageData[]] {
  const results = extractResultsFromBuckets(data);
  const totalCost = results.reduce((sum, item) => sum + item.cost, 0);
  return [totalCost, results];
}

/**
 * Group usage data by date
 */
export function groupByDate(data: UserData | ProjectData): Record<string, UsageData[]> {
  const results = extractResultsFromBuckets(data);
  const grouped: Record<string, UsageData[]> = {};
  
  results.forEach(item => {
    const date = new Date(item.timestamp).toISOString().split('T')[0];
    if (!grouped[date]) {
      grouped[date] = [];
    }
    grouped[date].push(item);
  });
  
  return grouped;
}

/**
 * Group usage data by model
 */
export function groupByModel(data: UserData | ProjectData): Record<string, UsageData[]> {
  const results = extractResultsFromBuckets(data);
  const grouped: Record<string, UsageData[]> = {};
  
  results.forEach(item => {
    if (!grouped[item.model]) {
      grouped[item.model] = [];
    }
    grouped[item.model].push(item);
  });
  
  return grouped;
}

/**
 * Group usage data by user ID
 */
export function groupByUserId(data: UserData): Record<string, UsageData[]> {
  const results = extractResultsFromBuckets(data);
  const grouped: Record<string, UsageData[]> = {};
  
  results.forEach(item => {
    const userId = item.user_id || 'unknown';
    if (!grouped[userId]) {
      grouped[userId] = [];
    }
    grouped[userId].push(item);
  });
  
  return grouped;
}

/**
 * Group usage data by project ID
 */
export function groupByProjectId(data: ProjectData): Record<string, UsageData[]> {
  const results = extractResultsFromBuckets(data);
  const grouped: Record<string, UsageData[]> = {};
  
  results.forEach(item => {
    const projectId = item.project_id || 'unknown';
    if (!grouped[projectId]) {
      grouped[projectId] = [];
    }
    grouped[projectId].push(item);
  });
  
  return grouped;
}

/**
 * Get user name from user ID
 */
export function getNameWithUserId(userId: string, userInfo: UserInfo): string | null {
  return userInfo[userId]?.name || null;
}

/**
 * Get user ID from user name
 */
export function getUserIdWithName(name: string, userInfo: UserInfo): string | null {
  for (const [userId, info] of Object.entries(userInfo)) {
    if (info.name === name) {
      return userId;
    }
  }
  return null;
}

/**
 * Process raw usage data into structured format for visualization
 */
export function processUsageData(
  userData: UserData | null,
  projectData: ProjectData | null,
  userInfo: UserInfo,
  projects?: Record<string, { id: string; name: string }>
): ProcessedUsageData | null {
  if (!userData && !projectData) return null;
  
  const processedData: ProcessedUsageData = {
    totalCost: 0,
    totalRequests: 0,
    activeUsers: 0,
    usageByDate: [],
    usageByModel: [],
    usageByUser: [],
    usageByProject: []
  };
  
  // Process user data
  if (userData) {
    const [userTotalCost, userResults] = getTotalCost(userData);
    processedData.totalCost += userTotalCost;
    processedData.totalRequests += userResults.reduce((sum, item) => sum + (item.n_requests || 1), 0);
    
    // Group by user
    const groupedByUser = groupByUserId(userData);
    processedData.activeUsers = Object.keys(groupedByUser).filter(id => id !== 'unknown').length;
    
    processedData.usageByUser = Object.entries(groupedByUser).map(([userId, items]) => {
      const cost = items.reduce((sum, item) => sum + item.cost, 0);
      const tokens = items.reduce((sum, item) => sum + item.usage.total_tokens, 0);
      return {
        userId,
        userName: getNameWithUserId(userId, userInfo) || `Unknown (${userId.slice(0, 8)}...)`,
        cost,
        requests: items.reduce((sum, item) => sum + (item.n_requests || 1), 0),
        tokens
      };
    });
  }
  
  // Process project data
  if (projectData) {
    const [projectTotalCost, projectResults] = getTotalCost(projectData);
    processedData.totalCost += projectTotalCost;
    processedData.totalRequests += projectResults.reduce((sum, item) => sum + (item.n_requests || 1), 0);
    
    // Group by project
    const groupedByProject = groupByProjectId(projectData);
    processedData.usageByProject = Object.entries(groupedByProject).map(([projectId, items]) => {
      const cost = items.reduce((sum, item) => sum + item.cost, 0);
      const tokens = items.reduce((sum, item) => sum + item.usage.total_tokens, 0);
      
      // Use actual project name if available, otherwise show project ID as-is
      const projectName = projects?.[projectId]?.name || projectId;
      
      return {
        projectId,
        projectName,
        cost,
        requests: items.reduce((sum, item) => sum + (item.n_requests || 1), 0),
        tokens
      };
    });
  }
  
  // Process combined data for dates and models
  const allData = [
    ...(userData ? extractResultsFromBuckets(userData) : []),
    ...(projectData ? extractResultsFromBuckets(projectData) : [])
  ];
  
  // Group by date
  const dateGroups = allData.reduce((acc, item) => {
    const date = new Date(item.timestamp).toISOString().split('T')[0];
    if (!acc[date]) acc[date] = [];
    acc[date].push(item);
    return acc;
  }, {} as Record<string, UsageData[]>);
  
  processedData.usageByDate = Object.entries(dateGroups)
    .map(([date, items]) => ({
      date,
      cost: items.reduce((sum, item) => sum + item.cost, 0),
      requests: items.reduce((sum, item) => sum + (item.n_requests || 1), 0)
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
  
  // Group by model
  const modelGroups = allData.reduce((acc, item) => {
    if (!acc[item.model]) acc[item.model] = [];
    acc[item.model].push(item);
    return acc;
  }, {} as Record<string, UsageData[]>);
  
  processedData.usageByModel = Object.entries(modelGroups).map(([model, items]) => ({
    model,
    cost: items.reduce((sum, item) => sum + item.cost, 0),
    requests: items.length,
    tokens: items.reduce((sum, item) => sum + item.usage.total_tokens, 0)
  }));
  
  return processedData;
}

/**
 * Format currency value
 */
export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 4
  }).format(amount);
}

/**
 * Format number with locale
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Format bytes to human readable format
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Calculate percentage change
 */
export function calculatePercentageChange(current: number, previous: number): number {
  if (previous === 0) return current > 0 ? 100 : 0;
  return ((current - previous) / previous) * 100;
}

/**
 * Generate chart data for time series
 */
export function generateTimeSeriesData(
  usageByDate: Array<{ date: string; cost: number; requests: number }>,
  metric: 'cost' | 'requests' = 'cost'
): ChartData[] {
  return usageByDate.map(item => ({
    x: item.date,
    y: item[metric],
    label: `${item.date}: ${metric === 'cost' ? formatCurrency(item.cost) : formatNumber(item.requests)}`
  }));
}

/**
 * Generate chart data for pie/bar charts
 */
export function generateCategoryData<T extends Record<string, any>>(
  data: T[],
  labelKey: keyof T,
  valueKey: keyof T,
  limit = 10
): ChartData[] {
  return data
    .sort((a, b) => b[valueKey] - a[valueKey])
    .slice(0, limit)
    .map((item, index) => ({
      x: item[labelKey],
      y: item[valueKey],
      label: `${item[labelKey]}: ${typeof item[valueKey] === 'number' ? formatNumber(item[valueKey]) : item[valueKey]}`,
      color: `hsl(${(index * 360) / limit}, 70%, 60%)`
    }));
}

/**
 * Calculate moving average
 */
export function calculateMovingAverage(data: number[], window = 7): number[] {
  const result: number[] = [];
  
  for (let i = 0; i < data.length; i++) {
    const start = Math.max(0, i - window + 1);
    const subset = data.slice(start, i + 1);
    const average = subset.reduce((sum, val) => sum + val, 0) / subset.length;
    result.push(average);
  }
  
  return result;
}

/**
 * Find budget overages
 */
export function findBudgetOverages(
  projectData: ProcessedUsageData['usageByProject'] = [],
  budgets: Record<string, number>
): BudgetOverage[] {
  const overages: BudgetOverage[] = [];
  
  projectData.forEach(project => {
    const budget = budgets[project.projectId];
    if (budget && project.cost > budget) {
      const overageAmount = project.cost - budget;
      const overagePercentage = (overageAmount / budget) * 100;
      
      overages.push({
        projectId: project.projectId,
        projectName: project.projectName,
        budget,
        spent: project.cost,
        overageAmount,
        overagePercentage
      });
    }
  });
  
  // Sort by overage amount descending
  return overages.sort((a, b) => b.overageAmount - a.overageAmount);
}

/**
 * Validate JSON structure for user/project data (extremely permissive to handle all real OpenAI formats)
 */
export function validateUsageDataStructure(data: unknown, type: 'user' | 'project' | 'userinfo'): boolean {
  console.log('🔍 Starting validation:', { type, hasData: !!data, dataType: typeof data });
  
  if (!data || typeof data !== 'object') {
    console.log('❌ Validation failed: Invalid data type');
    return false;
  }
  
  const typedData = data as any;
  console.log('📊 Data structure overview:', {
    topLevelKeys: Object.keys(typedData),
    hasDataKey: 'data' in typedData,
    dataType: typeof typedData.data,
    dataIsArray: Array.isArray(typedData.data),
    dataLength: Array.isArray(typedData.data) ? typedData.data.length : 'N/A'
  });
  
  // Special case for userinfo - more flexible validation
  if (type === 'userinfo') {
    console.log('✅ Validation passed: userinfo type (flexible validation)');
    return true; // Allow any valid JSON object for userinfo
  }
  
  // Must have "data" key with array value for user/project data
  if (!typedData.data || !Array.isArray(typedData.data)) {
    console.log('❌ Validation failed: Missing or invalid "data" array');
    return false;
  }
  
  if (typedData.data.length === 0) {
    console.log('⚠️ Warning: Data array is empty, but considering it valid');
    return true;
  }
  
  // Very permissive validation - just check if we have some recognizable structure
  let foundValidItem = false;
  let totalItems = 0;
  
  for (let bucketIndex = 0; bucketIndex < typedData.data.length; bucketIndex++) {
    const bucket = typedData.data[bucketIndex];
    console.log(`🪣 Bucket ${bucketIndex}:`, {
      keys: Object.keys(bucket),
      hasResults: 'results' in bucket,
      hasResult: 'result' in bucket,
      hasStartTime: 'start_time' in bucket,
      hasEndTime: 'end_time' in bucket
    });
    
    // Try both 'results' and 'result' keys
    const bucketResults = bucket.results || bucket.result;
    
    if (bucketResults && Array.isArray(bucketResults) && bucketResults.length > 0) {
      console.log(`📝 Found ${bucketResults.length} items in bucket ${bucketIndex}`);
      totalItems += bucketResults.length;
      
      // Check a few items to see if they look reasonable
      for (let i = 0; i < Math.min(3, bucketResults.length); i++) {
        const item = bucketResults[i];
        console.log(`🔍 Sample item ${i}:`, {
          keys: Object.keys(item),
          hasUserId: 'user_id' in item,
          hasProjectId: 'project_id' in item,
          hasStartTime: 'start_time' in item,
          hasLineItem: 'line_item' in item,
          hasModel: 'model' in item,
          hasAmount: 'amount' in item,
          hasCost: 'cost' in item,
          hasUsage: 'usage' in item
        });
        
        // Very basic check - just need some identifiable fields
        const looksLikeUsageData = (
          (item.user_id || item.project_id) && // Has some kind of ID
          (item.line_item || item.model) && // Has some kind of model identifier
          (item.amount || item.cost !== undefined || item.usage) // Has some cost/usage data
        );
        
        if (looksLikeUsageData) {
          // Check type-specific requirements very loosely
          if (type === 'user' && item.user_id) {
            foundValidItem = true;
            console.log('✅ Found valid user data item');
          } else if (type === 'project' && item.project_id) {
            foundValidItem = true;
            console.log('✅ Found valid project data item');
          } else if (type === 'user' && !item.project_id) {
            // Sometimes user data might not have explicit user_id but also no project_id
            foundValidItem = true;
            console.log('✅ Found potential user data item (no project_id)');
          } else if (type === 'project' && !item.user_id) {
            // Sometimes project data might not have explicit project_id but also no user_id
            foundValidItem = true;
            console.log('✅ Found potential project data item (no user_id)');
          }
        }
      }
    }
  }
  
  console.log(`📊 Validation summary:`, {
    totalBuckets: typedData.data.length,
    totalItems,
    foundValidItem,
    type
  });
  
  // If we found any valid-looking item, accept it
  if (foundValidItem) {
    console.log('✅ Validation passed!');
    return true;
  }
  
  // Final fallback - if the structure looks right but we're being too strict
  if (totalItems > 0) {
    console.log('⚠️ Accepting based on basic structure (items exist)');
    return true;
  }
  
  console.log('❌ Validation failed: No valid items found');
  return false;
}

/**
 * Generate sample data for testing (matches 2025 structure)
 */
export function generateSampleData(type: 'user' | 'project', count = 100): UserData | ProjectData {
  const models = ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4-vision-preview'];
  const now = new Date();
  const buckets = [];
  
  // Create 5 buckets representing different time periods
  for (let bucketIndex = 0; bucketIndex < 5; bucketIndex++) {
    const bucketTime = Math.floor((now.getTime() - bucketIndex * 7 * 24 * 60 * 60 * 1000) / 1000);
    const results = [];
    
    const itemsInBucket = Math.floor(count / 5) + Math.floor(Math.random() * 10);
    
    for (let i = 0; i < itemsInBucket; i++) {
      const model = models[Math.floor(Math.random() * models.length)];
      const promptTokens = Math.floor(Math.random() * 1000) + 100;
      const completionTokens = Math.floor(Math.random() * 500) + 50;
      const totalTokens = promptTokens + completionTokens;
      const cost = Math.random() * 0.1 + 0.001;
      
      const baseItem = {
        start_time: bucketTime + Math.floor(Math.random() * 86400), // Random time within the day
        line_item: model, // Use line_item for 2025 structure
        model: model, // Keep legacy field for compatibility
        usage: {
          prompt_tokens: promptTokens,
          completion_tokens: completionTokens,
          total_tokens: totalTokens
        },
        // Use real OpenAI format with amount.value
        amount: {
          value: cost,
          currency: 'USD'
        },
        cost, // Keep legacy field for compatibility
        operation: 'completion'
      };
      
      if (type === 'user') {
        results.push({
          ...baseItem,
          user_id: `user_${Math.floor(Math.random() * 10) + 1}`
        });
      } else {
        results.push({
          ...baseItem,
          project_id: `proj_${Math.floor(Math.random() * 5) + 1}`
        });
      }
    }
    
    buckets.push({
      start_time: bucketTime,
      end_time: bucketTime + 86400,
      results: results
    });
  }
  
  return {
    data: buckets
  } as UserData | ProjectData;
}

/**
 * Export processed data to CSV
 */
export function exportToCSV(data: ProcessedUsageData, filename = 'usage_data.csv'): void {
  const csvData = [];
  
  // Add headers
  csvData.push(['Type', 'Name/ID', 'Cost', 'Requests', 'Tokens']);
  
  // Add user data
  data.usageByUser?.forEach(user => {
    csvData.push(['User', user.userName, user.cost.toFixed(4), user.requests, user.tokens]);
  });
  
  // Add project data
  data.usageByProject?.forEach(project => {
    csvData.push(['Project', project.projectName, project.cost.toFixed(4), project.requests, project.tokens]);
  });
  
  // Add model data
  data.usageByModel.forEach(model => {
    csvData.push(['Model', model.model, model.cost.toFixed(4), model.requests, model.tokens]);
  });
  
  // Convert to CSV string
  const csvString = csvData.map(row => row.join(',')).join('\n');
  
  // Download file
  const blob = new Blob([csvString], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
}
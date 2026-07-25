import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useDashboardData() {
  const summaryQuery = useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: async () => (await api.get('/api/dashboard/summary')).data,
  });

  const intelligenceQuery = useQuery({
    queryKey: ['dashboard', 'machine-intelligence'],
    queryFn: async () => (await api.get('/api/dashboard/machine-intelligence')).data,
  });

  const knowledgeGrowthQuery = useQuery({
    queryKey: ['dashboard', 'knowledge-growth'],
    queryFn: async () => (await api.get('/api/dashboard/knowledge-growth')).data,
  });

  const complianceQuery = useQuery({
    queryKey: ['dashboard', 'compliance'],
    queryFn: async () => (await api.get('/api/dashboard/compliance')).data,
  });

  const aiPerformanceQuery = useQuery({
    queryKey: ['dashboard', 'ai-performance'],
    queryFn: async () => (await api.get('/api/dashboard/ai-performance')).data,
  });

  const activityQuery = useQuery({
    queryKey: ['dashboard', 'activity'],
    queryFn: async () => (await api.get('/api/dashboard/activity')).data,
  });

  const isLoading = 
    summaryQuery.isLoading || 
    intelligenceQuery.isLoading || 
    knowledgeGrowthQuery.isLoading || 
    complianceQuery.isLoading || 
    aiPerformanceQuery.isLoading || 
    activityQuery.isLoading;

  const isError = 
    summaryQuery.isError || 
    intelligenceQuery.isError || 
    knowledgeGrowthQuery.isError || 
    complianceQuery.isError || 
    aiPerformanceQuery.isError || 
    activityQuery.isError;

  const refetchAll = () => {
    summaryQuery.refetch();
    intelligenceQuery.refetch();
    knowledgeGrowthQuery.refetch();
    complianceQuery.refetch();
    aiPerformanceQuery.refetch();
    activityQuery.refetch();
  };

  return {
    summary: summaryQuery.data,
    intelligence: intelligenceQuery.data,
    knowledgeGrowth: knowledgeGrowthQuery.data,
    compliance: complianceQuery.data,
    aiPerformance: aiPerformanceQuery.data,
    activity: activityQuery.data,
    isLoading,
    isError,
    refetchAll
  };
}

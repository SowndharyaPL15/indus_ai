import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useDecisionCases() {
  // Placeholder for the list endpoint that doesn't exist on the backend yet
  const listQuery = useQuery({
    queryKey: ['decision-cases'],
    queryFn: async () => {
      // Simulate network delay for realistic empty state loading
      await new Promise(resolve => setTimeout(resolve, 800));
      return [];
    },
  });

  const createInvestigation = useMutation({
    mutationFn: async (payload: { query: string; machine_id?: string; execution_context?: string }) => {
      const response = await api.post('/api/idie/investigate', payload);
      return response.data;
    },
  });

  return {
    cases: listQuery.data || [],
    isLoading: listQuery.isLoading,
    isError: listQuery.isError,
    refetch: listQuery.refetch,
    createInvestigation,
  };
}

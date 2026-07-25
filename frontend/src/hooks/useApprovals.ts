import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useApprovals() {
  const queryClient = useQueryClient();

  const pendingQuery = useQuery({
    queryKey: ['approvals', 'pending'],
    queryFn: async () => (await api.get('/api/approvals/pending')).data,
  });

  const approveMutation = useMutation({
    mutationFn: async ({ id, comments }: { id: string; comments: string }) => {
      return (await api.post(`/api/approvals/${id}/approve`, { comments })).data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['approvals'] }),
  });

  const rejectMutation = useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason: string }) => {
      return (await api.post(`/api/approvals/${id}/reject`, { reason })).data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['approvals'] }),
  });

  const escalateMutation = useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason: string }) => {
      return (await api.post(`/api/approvals/${id}/escalate`, { reason })).data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['approvals'] }),
  });

  return {
    approvals: pendingQuery.data || [],
    isLoading: pendingQuery.isLoading,
    isError: pendingQuery.isError,
    refetch: pendingQuery.refetch,
    approve: approveMutation,
    reject: rejectMutation,
    escalate: escalateMutation,
  };
}

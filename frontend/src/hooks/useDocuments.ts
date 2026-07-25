import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useDocuments() {
  const queryClient = useQueryClient();

  const listQuery = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await api.get('/api/documents');
      return response.data;
    },
  });

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      const response = await api.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    }
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await api.delete(`/api/documents/${id}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    }
  });

  return {
    documents: listQuery.data || [],
    isLoading: listQuery.isLoading,
    isError: listQuery.isError,
    refetch: listQuery.refetch,
    uploadDocument: uploadMutation,
    deleteDocument: deleteMutation,
  };
}

export function useDocumentDetails(id: string) {
  const detailsQuery = useQuery({
    queryKey: ['documents', id],
    queryFn: async () => {
      const response = await api.get(`/api/documents/${id}`);
      return response.data;
    },
    enabled: !!id,
  });

  const statusQuery = useQuery({
    queryKey: ['documents', 'status', id],
    queryFn: async () => {
      const response = await api.get(`/api/documents/status/${id}`);
      return response.data;
    },
    enabled: !!id,
    // Auto Refresh every 5 seconds while processing. Stop when READY or FAILED.
    refetchInterval: (query) => {
      const status = query.state?.data?.status;
      if (status === 'READY' || status === 'FAILED' || status === 'ERROR') {
        return false;
      }
      return 5000;
    },
  });

  return {
    details: detailsQuery.data,
    statusData: statusQuery.data,
    isLoading: detailsQuery.isLoading || statusQuery.isLoading,
    isError: detailsQuery.isError || statusQuery.isError,
  };
}

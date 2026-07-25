import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useDecisionDetails(caseId: string) {
  const confidenceQuery = useQuery({
    queryKey: ['confidence', caseId],
    queryFn: async () => (await api.get(`/api/confidence/${caseId}`)).data,
    enabled: !!caseId,
  });

  const conflictsQuery = useQuery({
    queryKey: ['conflicts', caseId],
    queryFn: async () => (await api.get(`/api/conflicts/${caseId}`)).data,
    enabled: !!caseId,
  });

  const graphQuery = useQuery({
    queryKey: ['graph', caseId],
    queryFn: async () => (await api.get(`/api/graph/context/${caseId}`)).data,
    enabled: !!caseId,
  });

  // Mocking the details endpoint itself since we don't have a GET /api/idie/case/{id} listed in the requirements,
  // but we need basic case info. We'll extract what we can from the Confidence or Graph response if needed, 
  // or return a stub. The prompt didn't specify a GET case endpoint.
  const caseDetailsQuery = useQuery({
    queryKey: ['case-details', caseId],
    queryFn: async () => {
      // Stubbing the base case details
      return {
        id: caseId,
        query: "Fetching details from sub-systems...",
        status: "OPEN",
        intent: "INVESTIGATION",
        priority: "HIGH",
        created_at: new Date().toISOString()
      };
    },
    enabled: !!caseId,
  });

  const generateReport = useMutation({
    mutationFn: async ({ type, caseId }: { type: 'decision-case' | 'compliance' | 'audit', caseId: string }) => {
      const response = await api.post(`/api/reports/${type}/${caseId}`);
      return response.data; // Expected to return { file_path: string, id: string, etc }
    },
  });

  const downloadReport = async (reportId: string) => {
    // Standard window open for file downloads
    window.open(`${api.defaults.baseURL}/api/reports/download/${reportId}`, '_blank');
  };

  const isLoading = confidenceQuery.isLoading || conflictsQuery.isLoading || graphQuery.isLoading;
  const isError = confidenceQuery.isError || conflictsQuery.isError || graphQuery.isError;

  return {
    caseDetails: caseDetailsQuery.data,
    confidence: confidenceQuery.data,
    conflicts: conflictsQuery.data,
    graph: graphQuery.data,
    isLoading,
    isError,
    generateReport,
    downloadReport
  };
}

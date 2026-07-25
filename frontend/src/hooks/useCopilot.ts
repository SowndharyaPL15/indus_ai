import { useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';

export interface CopilotResponse {
  answer: string;
  confidence: number;
  citations: Array<{
    document: string;
    score: number | string;
    chunk?: number;
    page?: number;
  }>;
  documents_used: string[];
  processing_time: string;
}

export function useCopilot() {
  const queryMutation = useMutation({
    mutationFn: async (query: string): Promise<CopilotResponse> => {
      const response = await api.post('/api/copilot/query', { query });
      return response.data;
    },
  });

  return {
    askCopilot: queryMutation,
  };
}

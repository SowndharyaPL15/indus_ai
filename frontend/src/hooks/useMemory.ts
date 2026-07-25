import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useFactoryMemorySearch(query: string) {
  return useQuery({
    queryKey: ['memory', 'search', query],
    queryFn: async () => (await api.get(`/api/memory/search?q=${encodeURIComponent(query)}`)).data,
    enabled: query.length > 0,
  });
}

export function useReasoningSearch(query: string) {
  return useQuery({
    queryKey: ['reasoning', 'search', query],
    queryFn: async () => (await api.get(`/api/reasoning/similar?q=${encodeURIComponent(query)}`)).data,
    enabled: query.length > 0,
  });
}

export function useGraphSearch(query: string) {
  return useQuery({
    queryKey: ['graph', 'search', query],
    queryFn: async () => (await api.get(`/api/graph/search?q=${encodeURIComponent(query)}`)).data,
    enabled: query.length > 0,
  });
}

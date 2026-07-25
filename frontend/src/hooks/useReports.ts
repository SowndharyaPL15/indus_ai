import { useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useReports() {
  const generateReport = useMutation({
    mutationFn: async ({ type, id }: { type: 'decision-case' | 'maintenance' | 'compliance' | 'executive-summary'; id?: string }) => {
      let url = `/api/reports/${type}`;
      if (id) {
        url += `/${id}`;
      }
      return (await api.get(url)).data;
    },
  });

  const downloadReport = (reportId: string) => {
    window.open(`${api.defaults.baseURL}/api/reports/download/${reportId}`, '_blank');
  };

  return { generateReport, downloadReport };
}

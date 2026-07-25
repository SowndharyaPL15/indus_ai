import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileText, Download, Loader2 } from 'lucide-react';

export function ReportActionsCard({ caseId, generateReport, downloadReport }: { caseId: string, generateReport: any, downloadReport: any }) {
  
  const handleGenerate = (type: 'decision-case' | 'compliance' | 'audit') => {
    generateReport.mutate({ type, caseId }, {
      onSuccess: (data: any) => {
        // If the API directly returns the report object with an ID, we trigger download
        if (data && data.id) {
           downloadReport(data.id);
        }
      }
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Evidence Reporting</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button 
          variant="outline" 
          className="w-full justify-start"
          onClick={() => handleGenerate('decision-case')}
          disabled={generateReport.isPending}
        >
          {generateReport.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileText className="mr-2 h-4 w-4" />}
          Generate Decision Case Report
        </Button>
        <Button 
          variant="outline" 
          className="w-full justify-start"
          onClick={() => handleGenerate('compliance')}
          disabled={generateReport.isPending}
        >
           {generateReport.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileText className="mr-2 h-4 w-4" />}
          Generate Compliance Report
        </Button>
        <Button 
          variant="outline" 
          className="w-full justify-start"
          onClick={() => handleGenerate('audit')}
          disabled={generateReport.isPending}
        >
           {generateReport.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
          Generate Audit Trail
        </Button>
      </CardContent>
    </Card>
  );
}

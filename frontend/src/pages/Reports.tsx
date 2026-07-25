import { useState } from 'react';
import { useReports } from '@/hooks/useReports';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { FileText, Download, Loader2, ShieldCheck, BarChart3 } from 'lucide-react';

export default function Reports() {
  const { generateReport, downloadReport } = useReports();
  const [caseId, setCaseId] = useState('');
  const [lastReport, setLastReport] = useState<any>(null);

  const handleGenerate = (type: 'decision-case' | 'compliance' | 'audit') => {
    if (!caseId.trim()) return;
    generateReport.mutate({ type, caseId }, {
      onSuccess: (responseData) => {
        setLastReport(responseData);
      }
    });
  };

  const reportTypes = [
    { type: 'decision-case' as const, title: 'Decision Case Report', description: 'Full investigation summary with AI analysis, evidence, and recommendations.', icon: <FileText className="h-6 w-6" /> },
    { type: 'compliance' as const, title: 'Compliance Report', description: 'Regulatory compliance assessment with identified gaps and risk ratings.', icon: <ShieldCheck className="h-6 w-6" /> },
    { type: 'audit' as const, title: 'Audit Trail Report', description: 'Complete timeline of system events, actions, and user decisions.', icon: <BarChart3 className="h-6 w-6" /> },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Report Generation Center</h1>
        <p className="text-muted-foreground">Generate audit-ready PDF reports from Decision Cases.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Case Reference</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <input
              type="text"
              className="flex-1 rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Enter Decision Case ID (UUID)..."
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        {reportTypes.map((rt) => (
          <Card key={rt.type} className="flex flex-col">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="text-primary">{rt.icon}</div>
                <CardTitle className="text-sm">{rt.title}</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col justify-between">
              <p className="text-sm text-muted-foreground mb-4">{rt.description}</p>
              <Button
                className="w-full"
                variant="outline"
                disabled={!caseId.trim() || generateReport.isPending}
                onClick={() => handleGenerate(rt.type)}
              >
                {generateReport.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileText className="mr-2 h-4 w-4" />}
                Generate
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {lastReport && (
        <Card className="border-primary">
          <CardContent className="p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Badge variant="success">GENERATED</Badge>
              <span className="text-sm font-medium">Report ready for download</span>
            </div>
            <Button size="sm" onClick={() => downloadReport(lastReport.id)}>
              <Download className="mr-2 h-4 w-4" /> Download PDF
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

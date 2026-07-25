import { useState } from 'react';
import type { CopilotResponse } from '@/hooks/useCopilot';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Copy, Check, Clock, FileText, Bot, ShieldCheck, ClipboardCheck } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  query: string;
  response: CopilotResponse;
}

export function CopilotResponsePanel({ query, response }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(response.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getConfidenceBadge = (conf: number) => {
    if (conf >= 0.9) return { label: "VERY HIGH", color: "text-green-600 dark:text-green-400", bg: "bg-green-100 dark:bg-green-900/30" };
    if (conf >= 0.7) return { label: "HIGH", color: "text-green-500", bg: "bg-green-100 dark:bg-green-900/30" };
    if (conf >= 0.5) return { label: "MODERATE", color: "text-orange-500", bg: "bg-orange-100 dark:bg-orange-900/30" };
    return { label: "NEEDS REVIEW", color: "text-red-500", bg: "bg-red-100 dark:bg-red-900/30" };
  };

  // Strip generic headers
  const cleanAnswer = response.answer
    .replace(/^(Based on the provided documents[,:]?|According to the documents[,:]?|The uploaded files say[,:]?|Based on the provided information[,:]?)\s*/i, '')
    .trim();

  const parseScore = (score: number | string | undefined | null): number => {
    if (score === undefined || score === null) return 0;
    if (typeof score === 'string') {
      const parsed = parseFloat(score.replace('%', ''));
      if (isNaN(parsed)) return 0;
      return score.includes('%') ? parsed / 100 : parsed > 1 ? parsed / 100 : parsed;
    }
    return score > 1 ? score / 100 : score;
  };

  const formatCitationMeta = (citation: { chunk?: number; page?: number; score?: number | string }) => {
    const parts = [];
    if (citation.page !== undefined && citation.page !== null && citation.page !== 0 && !isNaN(Number(citation.page))) {
      parts.push(`Page ${citation.page}`);
    }
    if (citation.chunk !== undefined && citation.chunk !== null && citation.chunk !== 0 && !isNaN(Number(citation.chunk))) {
      parts.push(`Chunk #${citation.chunk}`);
    }

    const numScore = parseScore(citation.score);
    const formattedScore = `${(numScore * 100).toFixed(0)}% Match`;

    return {
      location: parts.length > 0 ? parts.join(' · ') : null,
      scoreText: formattedScore,
      numScore,
    };
  };

  const getDocumentInfo = (filename: string) => {
    let title = filename.replace(/\.(pdf|txt|docx?|csv)$/i, '');
    let type = "Engineering Note";
    
    if (title.toUpperCase().includes('MLOG')) {
      type = "Maintenance Log";
      title = title.replace(/MLOG-\d+_?/i, '').replace(/_/g, ' ') + ' ' + type;
    } else if (title.toUpperCase().includes('SOP')) {
      type = "Standard Operating Procedure";
      title = title.replace(/SOP-\d+_?/i, '').replace(/_/g, ' ') + ' Maintenance SOP';
    } else if (title.toUpperCase().includes('REP')) {
      type = "Inspection Report";
      title = title.replace(/_/g, ' ');
    } else {
      title = title.replace(/_/g, ' ');
    }
    return { title: title.trim(), type };
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-8">
      {/* User Query Header */}
      <div className="border-b pb-4">
        <h3 className="text-xl font-bold tracking-tight text-foreground">{query}</h3>
      </div>

      {/* AI Answer Section */}
      <div className="flex space-x-4">
        <div className="flex-shrink-0 mt-1">
          <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center shadow-sm">
            <Bot className="h-5 w-5 text-primary-foreground" />
          </div>
        </div>
        <div className="flex-1 space-y-6">
          {/* Decision Summary Card */}
          <Card className="shadow-sm border-border bg-card">
            <CardContent className="p-5">
              <div className="flex items-center space-x-2 mb-4">
                <ClipboardCheck className="h-5 w-5 text-primary" />
                <h4 className="text-lg font-semibold tracking-tight text-foreground">Decision Summary</h4>
              </div>
              <div className="prose prose-sm md:prose-base dark:prose-invert max-w-none text-foreground leading-relaxed">
                {cleanAnswer.split('\n').map((paragraph, idx) => (
                  <p key={idx} className="mb-2 last:mb-0">{paragraph}</p>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Confidence Assessment Card */}
          <Card className="shadow-sm border-border bg-card">
            <CardContent className="p-5">
              <div className="flex items-center space-x-2 mb-4">
                <ShieldCheck className="h-5 w-5 text-primary" />
                <h4 className="text-base font-semibold text-foreground">Confidence Assessment</h4>
              </div>
              
              <div className="flex items-center space-x-6">
                <div className="flex flex-col items-center justify-center w-24 h-24 rounded-full border-4 border-muted relative">
                  <span className="text-xl font-bold">{(response.confidence * 100).toFixed(0)}%</span>
                  <div className={cn("absolute inset-0 rounded-full border-4 opacity-50", getConfidenceBadge(response.confidence).color)} style={{ clipPath: 'polygon(50% 0, 100% 0, 100% 100%, 0 100%, 0 0, 50% 0)' }}></div>
                </div>
                <div>
                  <div className={cn("text-lg font-bold tracking-wider", getConfidenceBadge(response.confidence).color)}>
                    {getConfidenceBadge(response.confidence).label}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1 max-w-md">
                    Confidence derived from document evidence, historical cases and validated engineering knowledge.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Metadata Footer */}
          <div className="flex items-center justify-between pt-2 text-xs text-muted-foreground">
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1.5" />
              Response Time: {response.processing_time.replace('s', ' seconds').replace(' processing time', '')}
            </div>
            <Button variant="outline" size="sm" onClick={handleCopy} className="h-8">
              {copied ? <Check className="h-4 w-4 mr-1.5 text-green-600" /> : <Copy className="h-4 w-4 mr-1.5" />}
              {copied ? 'Copied!' : 'Export Decision'}
            </Button>
          </div>

          {/* Sources Section */}
          {response.citations && response.citations.length > 0 && (
            <div className="pt-2">
              <h4 className="text-base font-semibold mb-4 flex items-center text-foreground">
                <FileText className="h-5 w-5 mr-2 text-primary" />
                Supporting Evidence
              </h4>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {response.citations.map((source, idx) => {
                  const meta = formatCitationMeta(source);
                  const docInfo = getDocumentInfo(source.document);
                  return (
                    <Card key={idx} className="bg-secondary/40 shadow-sm hover:shadow-md transition-shadow border-border">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex flex-col">
                            <p className="text-sm font-semibold truncate pr-2 text-foreground" title={source.document}>
                              📄 {docInfo.title}
                            </p>
                            <span className="text-xs text-muted-foreground mt-0.5">{docInfo.type}</span>
                          </div>
                          <div className="flex flex-col items-end">
                            <span className="text-xs text-muted-foreground mb-0.5">Similarity</span>
                            <span className="text-sm font-bold text-primary">
                              {meta.numScore > 0 ? `${(meta.numScore * 100).toFixed(0)}%` : 'N/A'}
                            </span>
                          </div>
                        </div>
                        {meta.location && (
                          <div className="mt-3 pt-3 border-t border-border/50">
                            <p className="text-xs text-muted-foreground font-medium">
                              {meta.location}
                            </p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

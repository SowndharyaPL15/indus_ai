import { useParams, useNavigate } from 'react-router-dom';
import { useDocumentDetails } from '@/hooks/useDocuments';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ErrorState } from '@/components/ui/ErrorState';
import { Skeleton } from '@/components/ui/Skeleton';
import { ArrowLeft, Clock, FileText, Database, GitMerge, FileType, HardDrive } from 'lucide-react';
import { DocumentPipeline } from '@/components/documents/DocumentPipeline';

export default function DocumentDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { details, statusData, isLoading, isError } = useDocumentDetails(id || '');

  if (isError) {
    return <ErrorState message="Failed to load document details. It may have been deleted or the engine is offline." />;
  }

  const currentStatus = statusData?.status || details?.status || 'UPLOADED';

  const formatSize = (bytes?: number) => bytes ? `${(bytes / 1024 / 1024).toFixed(2)} MB` : 'N/A';
  const formatDate = (date?: string) => date ? new Date(date).toLocaleString() : 'N/A';

  return (
    <div className="space-y-6 pb-10 max-w-6xl mx-auto">
      <div className="flex items-center space-x-4 mb-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/documents')} className="p-0 hover:bg-transparent">
          <ArrowLeft className="h-5 w-5 mr-1" /> Back to Documents
        </Button>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight">Document Intelligence</h1>
        <p className="text-muted-foreground">Monitor extraction and embedding pipeline status.</p>
      </div>

      {isLoading && !details ? (
        <div className="grid gap-6 md:grid-cols-3">
          <Skeleton className="col-span-2 h-[400px]" />
          <Skeleton className="h-[400px]" />
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-3">
          {/* Main Metadata */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="flex justify-between items-center">
                <span className="truncate max-w-sm" title={details?.file_name}>{details?.file_name || 'Document Details'}</span>
                <Badge variant={currentStatus === 'READY' ? 'success' : currentStatus === 'FAILED' ? 'destructive' : 'warning'}>
                  {currentStatus}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center p-3 border rounded-md bg-secondary/30">
                  <FileType className="h-5 w-5 text-muted-foreground mr-3" />
                  <div>
                    <p className="text-xs text-muted-foreground">File Type</p>
                    <p className="text-sm font-medium">{details?.file_type || 'Unknown'}</p>
                  </div>
                </div>
                <div className="flex items-center p-3 border rounded-md bg-secondary/30">
                  <HardDrive className="h-5 w-5 text-muted-foreground mr-3" />
                  <div>
                    <p className="text-xs text-muted-foreground">File Size</p>
                    <p className="text-sm font-medium">{formatSize(details?.file_size)}</p>
                  </div>
                </div>
                <div className="flex items-center p-3 border rounded-md bg-secondary/30">
                  <Clock className="h-5 w-5 text-muted-foreground mr-3" />
                  <div>
                    <p className="text-xs text-muted-foreground">Uploaded At</p>
                    <p className="text-sm font-medium">{formatDate(details?.created_at)}</p>
                  </div>
                </div>
                <div className="flex items-center p-3 border rounded-md bg-secondary/30">
                  <FileText className="h-5 w-5 text-muted-foreground mr-3" />
                  <div>
                    <p className="text-xs text-muted-foreground">OCR Status</p>
                    <p className="text-sm font-medium">{statusData?.ocr_status || 'Pending'}</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div className="flex items-center p-3">
                  <GitMerge className="h-5 w-5 text-primary mr-3" />
                  <div>
                    <p className="text-xs text-muted-foreground">Chunks Generated</p>
                    <p className="text-sm font-bold">{statusData?.chunk_count || 0}</p>
                  </div>
                </div>
                <div className="flex items-center p-3">
                  <Database className="h-5 w-5 text-primary mr-3" />
                  <div>
                    <p className="text-xs text-muted-foreground">Vector Store Status</p>
                    <p className="text-sm font-bold">{statusData?.vector_status || 'Pending'}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Animated Pipeline */}
          <Card>
            <CardHeader>
              <CardTitle>Processing Pipeline</CardTitle>
            </CardHeader>
            <CardContent>
              <DocumentPipeline currentStatus={currentStatus} />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDocuments } from '@/hooks/useDocuments';
import { EmptyState } from '@/components/ui/EmptyState';
import { ErrorState } from '@/components/ui/ErrorState';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { Search, UploadCloud, RefreshCw, Eye, Trash2, FileText } from 'lucide-react';

export default function Documents() {
  const navigate = useNavigate();
  const { documents, isLoading, isError, refetch, deleteDocument } = useDocuments();

  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('All');
  const [sortOrder, setSortOrder] = useState('Newest');

  // Check for uploading stuck docs
  useEffect(() => {
    if (!documents) return;
    const hasUploading = documents.some((d: any) => d.status === 'UPLOADING');
    if (hasUploading) {
      const interval = setInterval(() => {
        refetch();
      }, 10000); // Poll every 10s if something is uploading
      return () => clearInterval(interval);
    }
  }, [documents, refetch]);



  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this document?")) {
      deleteDocument.mutate(id);
    }
  };

  const getStatusBadge = (doc: any) => {
    let status = doc.status;
    if (status === 'UPLOADING') {
      const isTimeout = Date.now() - new Date(doc.created_at).getTime() > 120000;
      if (isTimeout) status = 'FAILED';
    }

    if (status === 'READY') return <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900/30 dark:text-green-400">🟢 Ready</span>;
    if (status === 'PROCESSING') return <span className="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">🟡 Processing</span>;
    if (status === 'FAILED' || status === 'ERROR') return <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900/30 dark:text-red-400">🔴 Failed</span>;
    if (status === 'UPLOADING') return <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">🔵 Uploading</span>;
    return <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800">⚪ {status}</span>;
  };

  const parseDocumentMeta = (filename: string) => {
    let title = filename.replace(/\.(pdf|txt|docx?|csv)$/i, '');
    let category = "Engineering Guideline";
    
    if (title.toUpperCase().includes('MLOG')) {
      category = "Maintenance Log";
      title = title.replace(/MLOG-\d+_?/i, '').replace(/_/g, ' ') + ' ' + category;
    } else if (title.toUpperCase().includes('SOP')) {
      category = "SOP";
      title = title.replace(/SOP-\d+_?/i, '').replace(/_/g, ' ') + ' Maintenance SOP';
    } else if (title.toUpperCase().includes('IR-')) {
      category = "Incident Report";
      title = title.replace(/IR-\d+_?/i, '').replace(/_/g, ' ') + ' Incident';
    } else if (title.toUpperCase().includes('MAN-')) {
      category = "OEM Manual";
      title = title.replace(/MAN-\d+_?/i, '').replace(/_/g, ' ') + ' OEM Manual';
    } else if (title.toUpperCase().includes('REP')) {
      category = "Inspection Report";
      title = title.replace(/_/g, ' ');
    } else {
      title = title.replace(/_/g, ' ');
    }
    return { title: title.trim(), category };
  };

  const formatSize = (bytes: number) => {
    if (!bytes) return 'N/A';
    if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(dateString));
  };

  const processedDocs = useMemo(() => {
    if (!documents) return [];
    
    let filtered = documents.map((doc: any) => {
      const meta = parseDocumentMeta(doc.original_filename);
      return { ...doc, parsedTitle: meta.title, parsedCategory: meta.category };
    });

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter((d: any) => 
        d.parsedTitle.toLowerCase().includes(q) || 
        d.original_filename.toLowerCase().includes(q)
      );
    }

    if (typeFilter !== 'All') {
      filtered = filtered.filter((d: any) => d.parsedCategory.includes(typeFilter) || d.parsedCategory === typeFilter);
    }

    filtered.sort((a: any, b: any) => {
      if (sortOrder === 'Newest') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      if (sortOrder === 'Oldest') return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      if (sortOrder === 'A-Z') return a.parsedTitle.localeCompare(b.parsedTitle);
      if (sortOrder === 'Status') return a.status.localeCompare(b.status);
      return 0;
    });

    return filtered;
  }, [documents, searchQuery, typeFilter, sortOrder]);

  if (isError) {
    return <ErrorState message="Unable to load Document Center. Engine may be offline." onRetry={refetch} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Document Intelligence Center</h1>
          <p className="text-muted-foreground">Manage and track documents processed by the AI pipeline.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button onClick={() => navigate('/documents/upload')}>
            <UploadCloud className="mr-2 h-4 w-4" />
            Upload Document
          </Button>
        </div>
      </div>
      
      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-center bg-card p-4 rounded-lg border shadow-sm">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search documents by title or filename..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-md border bg-background pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div className="flex gap-2 w-full md:w-auto overflow-x-auto">
          <select 
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="All">All Categories</option>
            <option value="SOP">SOP</option>
            <option value="Maintenance Log">Maintenance Logs</option>
            <option value="Incident Report">Incident Reports</option>
            <option value="OEM Manual">Manuals</option>
          </select>
          <select 
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
            className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="Newest">Newest</option>
            <option value="Oldest">Oldest</option>
            <option value="A-Z">A–Z</option>
            <option value="Status">Status</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-card border rounded-lg overflow-hidden shadow-sm">
        {isLoading ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : processedDocs.length === 0 ? (
          <div className="p-12">
            <EmptyState 
              title="No industrial knowledge available yet" 
              description="Upload factory manuals, SOPs, or logs to begin." 
            />
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Document Title</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Size</TableHead>
                <TableHead>Added Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {processedDocs.map((doc: any) => (
                <TableRow key={doc.id}>
                  <TableCell className="font-medium max-w-[300px] py-4">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded bg-primary/10 flex items-center justify-center flex-shrink-0 text-primary">
                        <FileText className="h-4 w-4" />
                      </div>
                      <div className="truncate" title={doc.parsedTitle}>
                        <div className="truncate text-sm">{doc.parsedTitle}</div>
                        <div className="truncate text-xs text-muted-foreground">{doc.original_filename}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="py-4 text-sm text-muted-foreground">{doc.parsedCategory}</TableCell>
                  <TableCell className="py-4">{getStatusBadge(doc)}</TableCell>
                  <TableCell className="py-4 text-sm text-muted-foreground">{formatSize(doc.file_size)}</TableCell>
                  <TableCell className="py-4 text-sm text-muted-foreground">{formatDate(doc.created_at)}</TableCell>
                  <TableCell className="text-right space-x-2 py-4">
                    <Button variant="ghost" size="sm" onClick={() => navigate(`/documents/${doc.id}`)}>
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="text-destructive hover:bg-destructive/10 hover:text-destructive" onClick={() => handleDelete(doc.id)} disabled={deleteDocument.isPending}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  )
}

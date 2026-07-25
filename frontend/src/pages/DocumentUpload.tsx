import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDocuments } from '@/hooks/useDocuments';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { UploadCloud, File, X, ArrowLeft, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ALLOWED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'image/png', 'image/jpeg'];

export default function DocumentUpload() {
  const navigate = useNavigate();
  const { uploadDocument } = useDocuments();
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  }, []);

  const validateFile = (selectedFile: File) => {
    setError(null);
    if (!ALLOWED_TYPES.includes(selectedFile.type) && !selectedFile.name.endsWith('.pdf')) {
      setError("Unsupported file type. Please upload PDF, DOCX, TXT, CSV, XLSX, PNG, or JPG.");
      return false;
    }
    if (selectedFile.size > MAX_FILE_SIZE) {
      setError("File exceeds the 50MB size limit.");
      return false;
    }
    return true;
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const selectedFiles = Array.from(e.dataTransfer.files);
      const validFiles = selectedFiles.filter(validateFile);
      if (validFiles.length > 0) {
        setFiles(prev => [...prev, ...validFiles]);
      }
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files);
      const validFiles = selectedFiles.filter(validateFile);
      if (validFiles.length > 0) {
        setFiles(prev => [...prev, ...validFiles]);
      }
    }
  };

  const handleUpload = () => {
    if (files.length === 0) return;
    uploadDocument.mutate(files, {
      onSuccess: (data) => {
        // Navigate to details if API returns an ID for a single file, else back to list
        if (data && !Array.isArray(data) && data.id) navigate(`/documents/${data.id}`);
        else navigate('/documents');
      },
      onError: () => {
        setError("Upload failed. Please try again.");
      }
    });
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto pb-10">
      <div className="flex items-center space-x-4 mb-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/documents')} className="p-0 hover:bg-transparent">
          <ArrowLeft className="h-5 w-5 mr-1" /> Back to Documents
        </Button>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight">Upload Document</h1>
        <p className="text-muted-foreground">Ingest new knowledge into the AI pipeline.</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div 
            className={cn(
              "border-2 border-dashed rounded-lg p-12 text-center transition-colors relative",
              dragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 bg-card hover:bg-secondary/20"
            )}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <UploadCloud className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-1">Drag & Drop your file here</h3>
            <p className="text-sm text-muted-foreground mb-4">or click to browse from your computer</p>
            <input
              type="file"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              onChange={handleChange}
              accept=".pdf,.docx,.txt,.csv,.xlsx,.png,.jpg,.jpeg"
              multiple
            />
            <div className="flex justify-center space-x-2 mt-4">
              <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded">PDF</span>
              <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded">DOCX</span>
              <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded">TXT</span>
              <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded">Images</span>
            </div>
            <p className="text-xs text-muted-foreground mt-4">Maximum file size: 50MB</p>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-destructive/10 text-destructive text-sm rounded-md flex items-center">
              <AlertCircle className="h-4 w-4 mr-2" />
              {error}
            </div>
          )}

          {files.length > 0 && !uploadDocument.isSuccess && (
            <div className="mt-6 border rounded-lg p-4">
              <h4 className="text-sm font-semibold mb-3">Upload Queue ({files.length})</h4>
              <div className="space-y-2">
                {files.map((f, i) => (
                  <div key={i} className="flex items-center justify-between bg-secondary/50 p-3 rounded-md">
                    <div className="flex items-center">
                      <File className="h-8 w-8 text-primary mr-3" />
                      <div>
                        <p className="text-sm font-medium truncate max-w-[200px] sm:max-w-xs">{f.name}</p>
                        <p className="text-xs text-muted-foreground">{f.size < 1024 * 1024 ? (f.size / 1024).toFixed(2) + ' KB' : (f.size / 1024 / 1024).toFixed(2) + ' MB'}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {uploadDocument.isPending ? (
                        <span className="text-xs font-medium text-primary">Uploading...</span>
                      ) : (
                        <Button variant="ghost" size="sm" onClick={() => removeFile(i)}>
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 flex justify-end space-x-2">
                 <Button variant="outline" onClick={() => setFiles([])} disabled={uploadDocument.isPending}>Cancel All</Button>
                 <Button onClick={handleUpload} disabled={uploadDocument.isPending}>
                   {uploadDocument.isPending ? "Uploading..." : "Start Upload"}
                 </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

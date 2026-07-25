import { useState } from 'react';
import { useReasoningSearch } from '@/hooks/useMemory';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { Badge } from '@/components/ui/Badge';
import { Search, GitMerge } from 'lucide-react';

export default function ReasoningMemory() {
  const [searchInput, setSearchInput] = useState('');
  const [query, setQuery] = useState('');
  const { data, isLoading } = useReasoningSearch(query);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setQuery(searchInput);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reasoning Memory</h1>
        <p className="text-muted-foreground">Search through historical AI decisions and similarity matches.</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-2xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            className="w-full rounded-md border bg-background pl-9 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Search past reasoning cases..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
        </div>
        <button type="submit" className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90">
          Search
        </button>
      </form>

      {isLoading && (
        <div className="grid gap-4 md:grid-cols-2">
          {[1, 2].map((i) => <Skeleton key={i} className="h-[150px]" />)}
        </div>
      )}

      {query && !isLoading && (!data || !data.results || data.results.length === 0) && (
        <div className="pt-10">
          <EmptyState title="No cases found" description="No similar historical reasoning cases match this query." />
        </div>
      )}

      {!query && (
        <div className="pt-10">
           <EmptyState title="Search Reasoning Memory" description="Enter a query to find similar past decisions." />
        </div>
      )}

      {data && data.results && data.results.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {data.results.map((item: any, idx: number) => (
            <Card key={idx}>
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                   <CardTitle className="text-sm font-semibold flex items-center truncate">
                     <GitMerge className="h-4 w-4 mr-2 text-primary flex-shrink-0" />
                     <span className="truncate">{item.case_id || 'Historical Case'}</span>
                   </CardTitle>
                   {item.similarity_score && (
                     <Badge variant="secondary" className="flex-shrink-0">{(item.similarity_score * 100).toFixed(0)}% Match</Badge>
                   )}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{item.summary || item.description || item.problem_summary || 'No summary available.'}</p>
                <div className="mt-3 flex gap-2 flex-wrap">
                   {item.tags?.map((tag: string, i: number) => (
                      <span key={i} className="text-xs px-2 py-1 rounded bg-secondary text-secondary-foreground">{tag}</span>
                   ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

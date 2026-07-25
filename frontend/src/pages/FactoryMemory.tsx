import { useState } from 'react';
import { useFactoryMemorySearch } from '@/hooks/useMemory';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { Badge } from '@/components/ui/Badge';
import { Search, Database, Clock } from 'lucide-react';

export default function FactoryMemory() {
  const [searchInput, setSearchInput] = useState('');
  const [query, setQuery] = useState('');
  const { data, isLoading } = useFactoryMemorySearch(query);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setQuery(searchInput);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Living Factory Memory</h1>
        <p className="text-muted-foreground">Search across institutional knowledge and past operational logs.</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-2xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            className="w-full rounded-md border bg-background pl-9 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Search factory memories..."
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

      {query && !isLoading && (!data || data.length === 0) && (
        <div className="pt-10">
          <EmptyState title="No memories found" description="Try adjusting your search terms." />
        </div>
      )}

      {!query && (
        <div className="pt-10">
           <EmptyState title="Search Factory Memory" description="Enter a query above to search the living factory memory." />
        </div>
      )}

      {data && data.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {data.map((memory: any, idx: number) => (
            <Card key={idx}>
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                   <CardTitle className="text-sm font-semibold flex items-center">
                     <Database className="h-4 w-4 mr-2 text-primary" />
                     {memory.category || 'Memory'}
                   </CardTitle>
                   {memory.similarity_score && (
                     <Badge variant="secondary">{(memory.similarity_score * 100).toFixed(0)}% Match</Badge>
                   )}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-3">{memory.content}</p>
                <div className="flex items-center text-xs text-muted-foreground">
                   <Clock className="h-3 w-3 mr-1" />
                   {memory.created_at ? new Date(memory.created_at).toLocaleString() : 'N/A'}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

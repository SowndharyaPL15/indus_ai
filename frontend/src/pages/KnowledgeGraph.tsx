import { useState } from 'react';
import { useGraphSearch } from '@/hooks/useMemory';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { Skeleton } from '@/components/ui/Skeleton';
import { Search, Network, Share2 } from 'lucide-react';

export default function KnowledgeGraph() {
  const [searchInput, setSearchInput] = useState('');
  const [query, setQuery] = useState('');
  const { data, isLoading } = useGraphSearch(query);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setQuery(searchInput);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Knowledge Graph Engine</h1>
        <p className="text-muted-foreground">Explore semantic relationships across documents, entities, and memories.</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1 max-w-2xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            className="w-full rounded-md border bg-background pl-9 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Search graph nodes..."
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
           <Skeleton className="h-[200px]" />
           <Skeleton className="h-[200px]" />
        </div>
      )}

      {query && !isLoading && (!data || (!data.connected_entities?.length && !data.edges?.length)) && (
        <div className="pt-10">
          <EmptyState title="No nodes found" description="No graph entities match this query." />
        </div>
      )}

      {!query && (
        <div className="pt-10">
           <EmptyState title="Explore Knowledge Graph" description="Enter a query to visualize relationships." />
        </div>
      )}

      {data && (data.connected_entities?.length > 0 || data.edges?.length > 0) && (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Nodes */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center">
                <Network className="mr-2 h-4 w-4 text-primary" />
                Matching Nodes ({data.connected_entities?.length || 0})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                 {data.connected_entities?.slice(0, 10).map((node: any, idx: number) => (
                    <li key={idx} className="text-sm p-2 bg-secondary/30 rounded-md border">
                       <span className="font-medium">{node.entity_id}</span>
                       <span className="ml-2 text-xs text-muted-foreground px-2 py-0.5 bg-background rounded-full border">{node.entity_type}</span>
                    </li>
                 ))}
                 {data.connected_entities?.length > 10 && <li className="text-xs text-muted-foreground text-center pt-2">+{data.connected_entities.length - 10} more nodes</li>}
              </ul>
            </CardContent>
          </Card>

          {/* Edges */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center">
                <Share2 className="mr-2 h-4 w-4 text-primary" />
                Relationships ({data.edges?.length || 0})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                 {data.edges?.slice(0, 10).map((edge: any, idx: number) => (
                    <li key={idx} className="text-sm p-2 bg-secondary/30 rounded-md border flex items-center justify-between">
                       <span className="truncate max-w-[120px] text-xs" title={edge.source_entity_id}>{edge.source_entity_id}</span>
                       <span className="text-[10px] font-mono text-muted-foreground uppercase px-2">{edge.relationship_type}</span>
                       <span className="truncate max-w-[120px] text-xs" title={edge.target_entity_id}>{edge.target_entity_id}</span>
                    </li>
                 ))}
                 {data.edges?.length > 10 && <li className="text-xs text-muted-foreground text-center pt-2">+{data.edges.length - 10} more edges</li>}
              </ul>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

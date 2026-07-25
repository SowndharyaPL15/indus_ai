import { memo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Skeleton } from '@/components/ui/Skeleton';
import { EmptyState } from '@/components/ui/EmptyState';

interface KnowledgeProps {
  data: any;
  isLoading: boolean;
}

const AnalyticsTable = memo(({ title, items }: { title: string, items: any[] }) => (
  <Card className="flex flex-col">
    <CardHeader>
      <CardTitle className="text-sm">{title}</CardTitle>
    </CardHeader>
    <CardContent className="flex-1 overflow-auto max-h-[300px]">
      {!items || items.length === 0 ? (
        <EmptyState title="No Data" description="Not enough usage data gathered." />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Entity Name</TableHead>
              <TableHead className="text-right">Usage</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item, idx) => (
              <TableRow key={idx}>
                <TableCell className="font-medium truncate max-w-[150px]" title={item.name}>{item.name}</TableCell>
                <TableCell className="text-right">{item.usage_count}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </CardContent>
  </Card>
));

export function KnowledgeAnalyticsSection({ data, isLoading }: KnowledgeProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-3">
        <Skeleton className="h-[250px]" />
        <Skeleton className="h-[250px]" />
        <Skeleton className="h-[250px]" />
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-3">
      <AnalyticsTable title="Top Documents" items={data?.most_used_documents} />
      <AnalyticsTable title="Top Factory Memories" items={data?.most_reused_factory_memories} />
      <AnalyticsTable title="Top Reasoning Cases" items={data?.most_reused_reasoning_cases} />
    </div>
  );
}

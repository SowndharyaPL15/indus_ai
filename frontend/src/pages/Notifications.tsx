import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card';

export default function Notifications() {
  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
        </CardHeader>
        <CardContent>
          <CardDescription>Welcome to the Notifications module. This is a placeholder for the enterprise UI.</CardDescription>
        </CardContent>
      </Card>
    </div>
  );
};


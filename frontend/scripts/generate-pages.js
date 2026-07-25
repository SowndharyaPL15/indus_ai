const fs = require('fs');
const path = require('path');

const pages = [
  'Dashboard', 'DecisionCases', 'DecisionDetails', 'Documents', 
  'DocumentUpload', 'KnowledgeCopilot', 'Maintenance', 'FactoryMemory', 
  'ReasoningMemory', 'KnowledgeGraph', 'Compliance', 'Reports', 
  'Approvals', 'Settings', 'Login', 'NotFound'
];

const template = (name) => `import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { Skeleton } from "@/components/ui/Skeleton"

export default function ${name}() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">${name.replace(/([A-Z])/g, ' $1').trim()}</h1>
        <p className="text-muted-foreground">Manage and view your ${name.toLowerCase()} data.</p>
      </div>
      
      <div className="grid gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">Content for ${name} will appear here once connected to the API.</p>
            <div className="space-y-2">
              <Skeleton className="h-4 w-[250px]" />
              <Skeleton className="h-4 w-[200px]" />
              <Skeleton className="h-4 w-[300px]" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
`;

pages.forEach(page => {
  const filePath = path.join(__dirname, '..', 'src', 'pages', `${page}.tsx`);
  fs.writeFileSync(filePath, template(page));
});

console.log('Pages generated.');

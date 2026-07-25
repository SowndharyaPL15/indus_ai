import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import { Wrench } from "lucide-react"

export default function Maintenance() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Maintenance Dashboard</h1>
        <p className="text-muted-foreground">Manage and view maintenance schedules and records.</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Maintenance Tasks</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">No tasks currently scheduled.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

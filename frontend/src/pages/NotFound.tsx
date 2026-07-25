import { Button } from "@/components/ui/Button"
import { Link } from "react-router-dom"
import { AlertCircle } from "lucide-react"

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-[calc(100vh-8rem)] space-y-6">
      <AlertCircle className="h-16 w-16 text-destructive" />
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight mb-2">404 - Page Not Found</h1>
        <p className="text-muted-foreground mb-6">The page you are looking for does not exist or has been moved.</p>
        <Link to="/">
          <Button>Return to Dashboard</Button>
        </Link>
      </div>
    </div>
  )
}

import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { 
  LayoutDashboard, 
  Briefcase, 
  BrainCircuit, 
  FileText, 
  Wrench, 
  Database, 
  GitMerge, 
  Network, 
  ShieldCheck, 
  FileBarChart, 
  CheckSquare, 
  Settings 
} from "lucide-react"

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Decision Cases", href: "/cases", icon: Briefcase },
  { name: "Knowledge Copilot", href: "/copilot", icon: BrainCircuit },
  { name: "Documents", href: "/documents", icon: FileText },
  { name: "Maintenance", href: "/maintenance", icon: Wrench },
  { name: "Living Memory", href: "/factory-memory", icon: Database },
  { name: "Reasoning Memory", href: "/reasoning-memory", icon: GitMerge },
  { name: "Knowledge Graph", href: "/knowledge-graph", icon: Network },
  { name: "Compliance", href: "/compliance", icon: ShieldCheck },
  { name: "Reports", href: "/reports", icon: FileBarChart },
  { name: "Approvals", href: "/approvals", icon: CheckSquare },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 border-r bg-card flex flex-col h-screen sticky top-0 hidden md:flex">
      <div className="h-16 flex items-center px-6 border-b">
        <span className="font-bold text-xl text-primary tracking-tight">INDUS AI</span>
      </div>
      <div className="flex-1 overflow-y-auto py-4">
        <nav className="space-y-1 px-3">
          {navItems.map((item) => {
            const isActive = location.pathname === item.href || location.pathname.startsWith(`${item.href}/`) && item.href !== "/"
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center px-3 py-2 text-sm font-medium rounded-md group transition-colors",
                  isActive 
                    ? "bg-secondary text-primary" 
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                <item.icon className={cn(
                  "mr-3 h-5 w-5 flex-shrink-0 transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )} />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </div>
      <div className="p-4 border-t">
        <Link 
          to="/settings"
          className={cn(
            "flex items-center px-3 py-2 text-sm font-medium rounded-md group transition-colors",
            location.pathname === "/settings" 
              ? "bg-secondary text-primary" 
              : "text-muted-foreground hover:bg-muted hover:text-foreground"
          )}
        >
          <Settings className="mr-3 h-5 w-5 flex-shrink-0" />
          Settings
        </Link>
      </div>
    </aside>
  )
}

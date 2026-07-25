import { Bell, Search, Moon, LogOut } from "lucide-react"

interface NavbarProps {
  onNotificationToggle: () => void;
}

export function Navbar({ onNotificationToggle }: NavbarProps) {
  return (
    <header className="h-16 border-b bg-background flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex-1 max-w-lg">
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <Search className="h-4 w-4 text-muted-foreground" />
          </div>
          <input
            type="text"
            className="block w-full rounded-md border-0 py-1.5 pl-10 pr-3 text-foreground ring-1 ring-inset ring-border placeholder:text-muted-foreground focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6 bg-secondary"
            placeholder="Search decisions, documents..."
          />
        </div>
      </div>
      <div className="flex items-center space-x-4 ml-4">
        <button 
          type="button" 
          className="p-2 text-muted-foreground hover:text-foreground transition-colors"
          onClick={() => document.documentElement.classList.toggle("dark")}
        >
          <Moon className="h-5 w-5" />
        </button>
        <button 
          type="button" 
          className="relative p-2 text-muted-foreground hover:text-foreground transition-colors"
          onClick={onNotificationToggle}
        >
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 block h-2 w-2 rounded-full bg-destructive ring-2 ring-background" />
        </button>
        <div className="flex items-center gap-2 pl-2 border-l ml-2">
          <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold text-sm">
            AD
          </div>
          <button
            type="button"
            className="p-2 text-muted-foreground hover:text-destructive transition-colors"
            title="Logout"
            onClick={() => {
              localStorage.removeItem('token');
              localStorage.removeItem('user');
              window.location.href = '/login';
            }}
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  )
}

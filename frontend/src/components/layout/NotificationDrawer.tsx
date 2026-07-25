import { X } from "lucide-react"

interface NotificationDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export function NotificationDrawer({ isOpen, onClose }: NotificationDrawerProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-80 bg-background border-l shadow-2xl transform transition-transform duration-300 ease-in-out flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold">Notifications</h2>
        <button onClick={onClose} className="p-1 rounded-md text-muted-foreground hover:bg-muted">
          <X className="h-5 w-5" />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Placeholder Notifications */}
        <div className="p-3 bg-secondary rounded-md">
          <p className="text-sm font-medium">Critical Conflict Detected</p>
          <p className="text-xs text-muted-foreground mt-1">Case #1023 requires human approval.</p>
        </div>
        <div className="p-3 bg-card border rounded-md">
          <p className="text-sm font-medium">Report Generated</p>
          <p className="text-xs text-muted-foreground mt-1">Compliance Report ready for download.</p>
        </div>
      </div>
    </div>
  )
}

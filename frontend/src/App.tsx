import React, { Suspense } from "react"
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from "react-router-dom"
import { QueryClientProvider } from "@tanstack/react-query"
import { queryClient } from "@/services/api"
import { MainLayout } from "@/components/layout/MainLayout"
import Dashboard from "@/pages/Dashboard"
import { Loader2 } from "lucide-react"

// Lazy loaded routes
const DecisionCases = React.lazy(() => import("@/pages/DecisionCases"))
const DecisionDetails = React.lazy(() => import("@/pages/DecisionDetails"))
const Documents = React.lazy(() => import("@/pages/Documents"))
const DocumentUpload = React.lazy(() => import("@/pages/DocumentUpload"))
const DocumentDetails = React.lazy(() => import("@/pages/DocumentDetails"))
const KnowledgeCopilot = React.lazy(() => import("@/pages/KnowledgeCopilot"))
const Maintenance = React.lazy(() => import("@/pages/Maintenance"))
const FactoryMemory = React.lazy(() => import("@/pages/FactoryMemory"))
const ReasoningMemory = React.lazy(() => import("@/pages/ReasoningMemory"))
const KnowledgeGraph = React.lazy(() => import("@/pages/KnowledgeGraph"))
const Compliance = React.lazy(() => import("@/pages/Compliance"))
const Reports = React.lazy(() => import("@/pages/Reports"))
const Approvals = React.lazy(() => import("@/pages/Approvals"))
const Settings = React.lazy(() => import("@/pages/Settings"))
const Login = React.lazy(() => import("@/pages/Login"))
const Register = React.lazy(() => import("@/pages/Register"))
const Notifications = React.lazy(() => import("@/pages/Notifications"))
const NotFound = React.lazy(() => import("@/pages/NotFound"))

const FallbackLoader = () => (
  <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
    <div className="flex flex-col items-center text-muted-foreground">
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
      <p>Loading module...</p>
    </div>
  </div>
)

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem("token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            
            <Route element={<Suspense fallback={<FallbackLoader />}><Outlet /></Suspense>}>
              <Route path="cases" element={<DecisionCases />} />
              <Route path="cases/:id" element={<DecisionDetails />} />
              <Route path="documents" element={<Documents />} />
              <Route path="documents/upload" element={<DocumentUpload />} />
              <Route path="documents/:id" element={<DocumentDetails />} />
              <Route path="copilot" element={<KnowledgeCopilot />} />
              <Route path="maintenance" element={<Maintenance />} />
              <Route path="factory-memory" element={<FactoryMemory />} />
              <Route path="reasoning-memory" element={<ReasoningMemory />} />
              <Route path="knowledge-graph" element={<KnowledgeGraph />} />
              <Route path="compliance" element={<Compliance />} />
              <Route path="reports" element={<Reports />} />
              <Route path="approvals" element={<Approvals />} />
              <Route path="settings" element={<Settings />} />
              <Route path="notifications" element={<Notifications />} />
            </Route>
          </Route>
          
          <Route path="*" element={<Suspense fallback={<FallbackLoader />}><NotFound /></Suspense>} />
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UploadCloud, 
  MessageSquare, 
  Wrench, 
  BrainCircuit, 
  Network, 
  ShieldCheck, 
  FileText, 
  Bell, 
  Settings 
} from 'lucide-react';

const SidebarLink = ({ to, icon: Icon, label, currentPath }: { to: string, icon: React.ElementType, label: string, currentPath: string }) => {
  const isActive = currentPath === to;
  return (
    <Link 
      to={to} 
      className={`flex items-center px-4 py-3 mb-1 rounded-md transition-colors ${isActive ? 'bg-primary-600 text-white' : 'text-industrial-300 hover:bg-industrial-800 hover:text-white'}`}
    >
      <Icon className="w-5 h-5 mr-3" />
      <span className="font-medium text-sm">{label}</span>
    </Link>
  );
};

export const Layout = () => {
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <div className="flex h-screen bg-industrial-50 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-industrial-900 text-white flex flex-col hidden md:flex">
        <div className="p-6 flex items-center justify-center border-b border-industrial-800">
          <div className="w-8 h-8 bg-primary-500 rounded-md flex items-center justify-center mr-3 font-bold text-xl">I</div>
          <span className="text-xl font-bold tracking-wider">INDUS <span className="text-primary-500">AI</span></span>
        </div>
        
        <div className="flex-1 overflow-y-auto py-4 px-3">
          <div className="text-xs font-semibold text-industrial-500 uppercase tracking-wider mb-2 px-4">Core</div>
          <SidebarLink to="/" icon={LayoutDashboard} label="Dashboard" currentPath={currentPath} />
          <SidebarLink to="/upload" icon={UploadCloud} label="Document Upload" currentPath={currentPath} />
          
          <div className="text-xs font-semibold text-industrial-500 uppercase tracking-wider mt-6 mb-2 px-4">Intelligence</div>
          <SidebarLink to="/copilot" icon={MessageSquare} label="Knowledge Copilot" currentPath={currentPath} />
          <SidebarLink to="/maintenance" icon={Wrench} label="Maintenance" currentPath={currentPath} />
          <SidebarLink to="/memory" icon={BrainCircuit} label="Factory Memory" currentPath={currentPath} />
          <SidebarLink to="/graph" icon={Network} label="Knowledge Graph" currentPath={currentPath} />
          
          <div className="text-xs font-semibold text-industrial-500 uppercase tracking-wider mt-6 mb-2 px-4">Management</div>
          <SidebarLink to="/compliance" icon={ShieldCheck} label="Compliance" currentPath={currentPath} />
          <SidebarLink to="/reports" icon={FileText} label="Reports" currentPath={currentPath} />
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-industrial-200 flex items-center justify-between px-6 z-10">
          <div className="flex items-center md:hidden">
            <span className="text-xl font-bold text-industrial-900 tracking-wider">INDUS <span className="text-primary-600">AI</span></span>
          </div>
          <div className="hidden md:flex items-center text-industrial-500 text-sm font-medium">
            Industrial Cognitive Memory System
          </div>
          
          <div className="flex items-center space-x-4">
            <Link to="/notifications" className="text-industrial-400 hover:text-industrial-600 relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
            </Link>
            <Link to="/settings" className="text-industrial-400 hover:text-industrial-600">
              <Settings className="w-5 h-5" />
            </Link>
            <div className="w-8 h-8 rounded-full bg-industrial-200 flex items-center justify-center text-industrial-700 font-bold border border-industrial-300">
              JD
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-industrial-50 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

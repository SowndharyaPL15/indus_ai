import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Key, User, Shield } from 'lucide-react';

export default function Settings() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Platform Settings</h1>
        <p className="text-muted-foreground">Manage your account, API keys, and system preferences.</p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-2">
              <User className="h-5 w-5 text-primary" />
              <CardTitle>Profile Information</CardTitle>
            </div>
            <CardDescription>Update your personal details and role.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                   <label className="text-sm font-medium">Full Name</label>
                   <input type="text" defaultValue="Admin User" className="w-full rounded-md border bg-background px-3 py-2 text-sm" disabled />
                </div>
                <div className="space-y-1">
                   <label className="text-sm font-medium">Email Address</label>
                   <input type="email" defaultValue="admin@indus.ai" className="w-full rounded-md border bg-background px-3 py-2 text-sm" disabled />
                </div>
                <div className="space-y-1">
                   <label className="text-sm font-medium">Role</label>
                   <input type="text" defaultValue="Super Administrator" className="w-full rounded-md border bg-secondary px-3 py-2 text-sm text-muted-foreground cursor-not-allowed" disabled />
                </div>
             </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
             <div className="flex items-center space-x-2">
              <Key className="h-5 w-5 text-primary" />
              <CardTitle>API Access</CardTitle>
            </div>
            <CardDescription>Manage your API keys for programmatic access to INDUS AI engines.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-md bg-secondary/20">
               <div>
                  <p className="font-medium text-sm">Production Key</p>
                  <p className="text-xs text-muted-foreground mt-1 font-mono">sk_live_••••••••••••••••••••</p>
               </div>
               <Button variant="outline" size="sm">Regenerate</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
             <div className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-primary" />
              <CardTitle>Security</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-sm">Two-Factor Authentication (2FA)</p>
                <p className="text-sm text-muted-foreground">Add an extra layer of security to your account.</p>
              </div>
              <Button variant="outline">Enable</Button>
            </div>
            <div className="pt-4 border-t flex justify-end">
               <Button>Save Preferences</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

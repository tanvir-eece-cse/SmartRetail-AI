export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">Manage your account and preferences</p>
      </div>
      
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Settings</h3>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Full Name</label>
                <input type="text" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input type="email" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500" />
              </div>
              <button type="submit" className="btn-primary">Save Changes</button>
            </form>
          </div>
          
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Settings</h3>
            <div className="space-y-4">
              <label className="flex items-center">
                <input type="checkbox" className="rounded border-gray-300 text-primary-600" defaultChecked />
                <span className="ml-2 text-sm text-gray-700">Email notifications for new orders</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="rounded border-gray-300 text-primary-600" defaultChecked />
                <span className="ml-2 text-sm text-gray-700">Low stock alerts</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="rounded border-gray-300 text-primary-600" />
                <span className="ml-2 text-sm text-gray-700">Weekly analytics report</span>
              </label>
            </div>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">API Keys</h3>
            <p className="text-sm text-gray-500 mb-4">Manage API access for integrations</p>
            <button className="btn-secondary w-full">Generate New Key</button>
          </div>
          
          <div className="card p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Danger Zone</h3>
            <p className="text-sm text-gray-500 mb-4">Irreversible actions</p>
            <button className="btn-danger w-full">Delete Account</button>
          </div>
        </div>
      </div>
    </div>
  );
}

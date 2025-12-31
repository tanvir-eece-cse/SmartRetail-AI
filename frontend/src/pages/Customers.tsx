export default function Customers() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
        <p className="mt-1 text-sm text-gray-500">View and manage your customers</p>
      </div>
      
      <div className="card">
        <div className="p-6 text-center text-gray-500">
          Customer list with RFM segments, lifetime value, and activity history.
        </div>
      </div>
    </div>
  );
}

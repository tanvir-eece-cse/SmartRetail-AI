export default function Analytics() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-1 text-sm text-gray-500">Business intelligence and insights</p>
      </div>
      
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sales Analytics</h3>
          <p className="text-gray-500">Revenue trends, forecasts, and comparisons.</p>
        </div>
        
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Customer Analytics</h3>
          <p className="text-gray-500">Cohort analysis, retention, and LTV metrics.</p>
        </div>
        
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Product Performance</h3>
          <p className="text-gray-500">Best sellers, conversion rates, and inventory insights.</p>
        </div>
        
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Marketing Analytics</h3>
          <p className="text-gray-500">Campaign performance and ROI tracking.</p>
        </div>
      </div>
    </div>
  );
}

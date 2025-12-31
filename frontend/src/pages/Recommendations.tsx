import { SparklesIcon } from '@heroicons/react/24/outline';

export default function Recommendations() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <SparklesIcon className="h-8 w-8 text-primary-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Recommendations</h1>
          <p className="text-sm text-gray-500">ML-powered insights and recommendations</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">🎯 Product Recommendations</h3>
          <p className="text-gray-500 text-sm mb-4">
            Personalized product suggestions for each customer based on browsing history and purchase patterns.
          </p>
          <div className="text-2xl font-bold text-primary-600">85%</div>
          <div className="text-sm text-gray-500">Accuracy Rate</div>
        </div>
        
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">👥 Customer Segments</h3>
          <p className="text-gray-500 text-sm mb-4">
            RFM-based customer segmentation to identify champions, at-risk, and new customers.
          </p>
          <div className="text-2xl font-bold text-primary-600">6</div>
          <div className="text-sm text-gray-500">Active Segments</div>
        </div>
        
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">📊 Demand Forecast</h3>
          <p className="text-gray-500 text-sm mb-4">
            Predict future demand for products to optimize inventory and reduce stockouts.
          </p>
          <div className="text-2xl font-bold text-primary-600">30</div>
          <div className="text-sm text-gray-500">Days Forecast</div>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Trending Products</h3>
        </div>
        <div className="p-6">
          <p className="text-gray-500">AI-identified trending products based on recent activity patterns.</p>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Churn Prediction</h3>
        </div>
        <div className="p-6">
          <p className="text-gray-500">Customers at risk of churning with recommended retention actions.</p>
        </div>
      </div>
    </div>
  );
}

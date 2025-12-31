export default function Products() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="mt-1 text-sm text-gray-500">Manage your product catalog</p>
        </div>
        <button className="btn-primary">Add Product</button>
      </div>
      
      <div className="card">
        <div className="p-6 text-center text-gray-500">
          Product list will be displayed here with search, filter, and pagination.
        </div>
      </div>
    </div>
  );
}

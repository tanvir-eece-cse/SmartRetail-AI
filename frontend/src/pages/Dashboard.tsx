import {
  CurrencyDollarIcon,
  ShoppingCartIcon,
  UsersIcon,
  ArrowTrendingUpIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/react/24/outline';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../lib/api';

// Mock data for demo
const revenueData = [
  { date: 'Jan 1', revenue: 4200 },
  { date: 'Jan 8', revenue: 5100 },
  { date: 'Jan 15', revenue: 4800 },
  { date: 'Jan 22', revenue: 6200 },
  { date: 'Jan 29', revenue: 7100 },
  { date: 'Feb 5', revenue: 6800 },
  { date: 'Feb 12', revenue: 8200 },
];

const topProductsData = [
  { name: 'Wireless Earbuds', sales: 245 },
  { name: 'Smart Watch', sales: 189 },
  { name: 'Phone Case', sales: 156 },
  { name: 'USB Cable', sales: 142 },
  { name: 'Power Bank', sales: 128 },
];

const stats = [
  {
    name: 'Total Revenue',
    value: '৳4,52,890',
    change: '+12.5%',
    changeType: 'positive',
    icon: CurrencyDollarIcon,
  },
  {
    name: 'Total Orders',
    value: '1,245',
    change: '+8.2%',
    changeType: 'positive',
    icon: ShoppingCartIcon,
  },
  {
    name: 'Total Customers',
    value: '3,456',
    change: '+15.3%',
    changeType: 'positive',
    icon: UsersIcon,
  },
  {
    name: 'Conversion Rate',
    value: '3.24%',
    change: '-2.1%',
    changeType: 'negative',
    icon: ArrowTrendingUpIcon,
  },
];

const recentOrders = [
  { id: 'ORD-001', customer: 'Rahim Ahmed', total: '৳2,450', status: 'Delivered', date: '2 hours ago' },
  { id: 'ORD-002', customer: 'Fatima Khan', total: '৳1,890', status: 'Processing', date: '4 hours ago' },
  { id: 'ORD-003', customer: 'Karim Islam', total: '৳3,200', status: 'Shipped', date: '6 hours ago' },
  { id: 'ORD-004', customer: 'Nusrat Jahan', total: '৳980', status: 'Pending', date: '8 hours ago' },
  { id: 'ORD-005', customer: 'Imran Hossain', total: '৳4,500', status: 'Delivered', date: '12 hours ago' },
];

export default function Dashboard() {
  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => analyticsApi.dashboard(),
    staleTime: 1000 * 60 * 5,
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back! Here's what's happening with your store today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <stat.icon className="h-6 w-6 text-gray-400" aria-hidden="true" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{stat.value}</div>
                      <div
                        className={`ml-2 flex items-baseline text-sm font-semibold ${
                          stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {stat.changeType === 'positive' ? (
                          <ArrowUpIcon className="h-4 w-4 flex-shrink-0 self-center" />
                        ) : (
                          <ArrowDownIcon className="h-4 w-4 flex-shrink-0 self-center" />
                        )}
                        <span className="ml-1">{stat.change}</span>
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Revenue Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Revenue Overview</h3>
          </div>
          <div className="card-body">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={revenueData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="date" stroke="#6B7280" fontSize={12} />
                  <YAxis stroke="#6B7280" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    dot={{ fill: '#3B82F6', strokeWidth: 2 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Top Products Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Top Products</h3>
          </div>
          <div className="card-body">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topProductsData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis type="number" stroke="#6B7280" fontSize={12} />
                  <YAxis dataKey="name" type="category" stroke="#6B7280" fontSize={12} width={100} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="sales" fill="#3B82F6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Orders & AI Insights */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        {/* Recent Orders */}
        <div className="card lg:col-span-2">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Recent Orders</h3>
            <a href="/orders" className="text-sm font-medium text-primary-600 hover:text-primary-500">
              View all
            </a>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Order ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentOrders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-600">
                      {order.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {order.customer}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {order.total}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`badge ${
                          order.status === 'Delivered'
                            ? 'badge-success'
                            : order.status === 'Shipped'
                            ? 'badge-info'
                            : order.status === 'Processing'
                            ? 'badge-warning'
                            : 'badge-danger'
                        }`}
                      >
                        {order.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {order.date}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Insights */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">🤖 AI Insights</h3>
          </div>
          <div className="card-body space-y-4">
            <div className="p-3 bg-green-50 rounded-lg border border-green-200">
              <p className="text-sm font-medium text-green-800">📈 Sales Trend</p>
              <p className="mt-1 text-sm text-green-700">
                Revenue is up 12.5% compared to last week. Electronics category is performing well.
              </p>
            </div>
            
            <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <p className="text-sm font-medium text-yellow-800">⚠️ Low Stock Alert</p>
              <p className="mt-1 text-sm text-yellow-700">
                5 products are running low on stock. Consider restocking soon.
              </p>
            </div>
            
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm font-medium text-blue-800">💡 Recommendation</p>
              <p className="mt-1 text-sm text-blue-700">
                Based on customer behavior, consider bundling wireless earbuds with phone cases.
              </p>
            </div>
            
            <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
              <p className="text-sm font-medium text-purple-800">🎯 Customer Segment</p>
              <p className="mt-1 text-sm text-purple-700">
                15% of customers are at risk of churning. Launch re-engagement campaign.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

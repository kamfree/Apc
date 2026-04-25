import React from 'react'

export default function DashboardPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Municipal Assets Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border">
          <h2 className="text-sm font-medium text-gray-500 uppercase">Total Assets</h2>
          <p className="text-2xl font-bold mt-2">Loading...</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border">
          <h2 className="text-sm font-medium text-gray-500 uppercase">Occupancy Rate</h2>
          <p className="text-2xl font-bold mt-2">Loading...</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border">
          <h2 className="text-sm font-medium text-gray-500 uppercase">Monthly Revenue</h2>
          <p className="text-2xl font-bold mt-2">Loading...</p>
        </div>
      </div>

      <div className="mt-12">
        <h2 className="text-xl font-semibold mb-4">Recent Assets</h2>
        <div className="bg-white rounded-lg shadow border overflow-hidden">
           <table className="min-w-full divide-y divide-gray-200">
             <thead className="bg-gray-50">
               <tr>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
               </tr>
             </thead>
             <tbody className="bg-white divide-y divide-gray-200">
               <tr>
                 <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500" colSpan={3}>No assets found</td>
               </tr>
             </tbody>
           </table>
        </div>
      </div>
    </div>
  )
}

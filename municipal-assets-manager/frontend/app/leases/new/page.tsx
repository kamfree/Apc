import React from 'react'

export default function NewLeasePage() {
  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Create New Lease</h1>
      <form className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">Asset</label>
          <select className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2">
            <option>Select an asset</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Tenant</label>
          <select className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2">
            <option>Select a tenant</option>
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Start Date</label>
            <input type="date" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">End Date</label>
            <input type="date" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Monthly Amount (DZD)</label>
          <input type="number" className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" placeholder="0.00" />
        </div>
        <button type="submit" className="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700">
          Create Lease
        </button>
      </form>
    </div>
  )
}

import React from 'react'

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2 bg-gray-50">
      <main className="flex flex-col items-center justify-center w-full flex-1 px-20 text-center">
        <h1 className="text-6xl font-bold text-blue-600">
          Municipal Assets Manager
        </h1>
        <p className="mt-3 text-2xl">
          Efficiently manage assets, leases, and billing.
        </p>
        <div className="flex flex-wrap items-center justify-around max-w-4xl mt-6 sm:w-full">
          <a
            href="/dashboard"
            className="p-6 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
          >
            <h3 className="text-2xl font-bold">Dashboard &rarr;</h3>
            <p className="mt-4 text-xl">
              View stats and recent activity.
            </p>
          </a>
          <a
            href="/leases/new"
            className="p-6 mt-6 text-left border w-96 rounded-xl hover:text-blue-600 focus:text-blue-600"
          >
            <h3 className="text-2xl font-bold">Create Lease &rarr;</h3>
            <p className="mt-4 text-xl">
              Start a new asset lease.
            </p>
          </a>
        </div>
      </main>
    </div>
  )
}

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full text-center">
      <div class="text-6xl font-bold text-gray-300 mb-4">404</div>
      <h1 class="text-2xl font-bold text-gray-900 mb-4">Page not found</h1>
      <p class="text-gray-600 mb-8">The page you're looking for doesn't exist.</p>
      <router-link
        to="/dashboard"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Go to Dashboard
      </router-link>
    </div>
  </div>
</template> 
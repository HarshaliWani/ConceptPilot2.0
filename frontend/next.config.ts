import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Turbopack is the default in Next.js 16
  // The Konva warning is usually harmless and doesn't affect functionality
  // If you need webpack config, use: npm run dev -- --webpack
  turbopack: {},
  
  async rewrites() {
    return [
      {
        source: '/static/:path*',
        destination: 'http://localhost:8000/static/:path*', // Proxy to FastAPI
      },
    ];
  },
};

export default nextConfig;
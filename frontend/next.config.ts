import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },
  async rewrites() {
    return [
      {
        source: '/api/coding/:path*',
        destination: 'http://127.0.0.1:8015/coding/:path*',
      },
    ];
  },
};

export default nextConfig;

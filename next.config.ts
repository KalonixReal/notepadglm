import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
  async rewrites() {
    return {
      beforeFiles: [
        // Serve the audited Notepad v9 app (public/notepad.html) at the root route.
        { source: "/", destination: "/notepad.html" },
      ],
      afterFiles: [],
      fallback: [],
    };
  },
};

export default nextConfig;

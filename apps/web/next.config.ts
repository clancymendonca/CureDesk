import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@curedesk/shared"],
  images: {
    remotePatterns: [{ protocol: "https", hostname: "**" }],
  },
};

export default nextConfig;

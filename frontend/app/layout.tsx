import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PRISM ORBIT COMMAND | Mission Control Interface",
  description: "Cinematic futuristic mission control dashboard with real-time satellite tracking, 3D Earth visualization, and AI-powered predictive modeling.",
  keywords: "satellite tracking, mission control, space operations, orbital management",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased overflow-hidden">
        {children}
      </body>
    </html>
  );
}

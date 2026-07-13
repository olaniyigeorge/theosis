import type { Metadata } from "next";
import { Fraunces, Source_Serif_4, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  display: "swap",
});

const sourceSerif = Source_Serif_4({
  subsets: ["latin"],
  variable: "--font-source-serif",
  weight: ["400", "600"],
  style: ["normal", "italic"],
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-plex-mono",
  weight: ["400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Theosis — A Knowledge Graph of Scripture",
  description:
    "Every person, place, and story in Scripture, connected by relationships that cite chapter and verse. No claim without a reference.",
   keywords: ['ajo', 'cooperative savings', 'savings groups', 'charas', 'susu', 'tontine', 'rotating savings', 'financial cooperation', 'group savings', 'community savings', 'money management', 'cooperative finance'],
  authors: [{ name: 'Abeleje Olaniyi George' }],
  creator: 'OG Bellz',
  publisher: 'Olaniyi George',
  formatDetection: { email: false, telephone: false },
  metadataBase: new URL('https://theosis-seven.vercel.app'),
  alternates: { canonical: '/' },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://theosis-seven.vercel.app',
    title: 'Theosis | A Knowledge Graph of Scripture',
    description: 'A Knowledge Graph of Scripture',
    siteName: 'Theosis',
    images: [{ url: '/assets/images/OG Image_coopwise-1.png', width: 1200, height: 630, alt: 'Theosis' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Theosis - A Knowledge Graph of Scripture',
    description: 'A Knowledge Graph of Scripture.',
    images: ['/assets/images/OG Image_coopwise-1.png'],
    creator: '@abeleje_olaniyi',
  },
  icons: {
    icon: "/icons/theosis-logo.png",
    shortcut: "/icons/theosis-logo.png",
    apple: "/icons/theosis-logo.png",
  },
  manifest: '/manifest.json',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${fraunces.variable} ${sourceSerif.variable} ${plexMono.variable}`}
      >
        {children}
      </body>
    </html>
  );
}
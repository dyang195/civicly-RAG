import { Montserrat } from 'next/font/google'
import './globals.css'
import type { Metadata } from 'next'

const montserrat = Montserrat({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Civicly.ai - City Council Records Search',
  description: 'Search and engage with City Council records',
  icons: {
    icon: [
      {
        url: '/civicly-ai-logo.svg',
        type: 'image/svg+xml',
      }
    ],
    shortcut: ['/civicly-ai-logo.svg']
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={montserrat.className}>{children}</body>
    </html>
  )
}


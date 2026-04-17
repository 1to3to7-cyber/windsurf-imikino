import './globals.css'
import { Footer } from '@/components/layout/Footer'

const inter = { className: 'font-sans' }

export const metadata = {
  title: 'Imikino - Learn, Share, Grow',
  description: 'Social-learning + micro-task platform for Rwandan youth',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
  themeColor: '#0ea5e9',
}

export default function RootLayout({
  children,
}: {
  children: any
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className={`${inter.className} bg-gray-50 text-gray-900 min-h-screen flex flex-col`}>
        <div className="flex-1">
          {children}
        </div>
        <Footer />
      </body>
    </html>
  )
}

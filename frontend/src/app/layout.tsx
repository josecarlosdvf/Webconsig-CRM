import "./globals.css";
import { Inter } from 'next/font/google'
import { Toaster } from "@/components/ui/toaster"

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Webconsig CRM/ERP',
  description: 'Sistema moderno de CRM/ERP',
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR" className={inter.className}>
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  );
}

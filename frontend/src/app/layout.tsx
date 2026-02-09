import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <header className="app-header">
            <div className="brand">Webconsig CRM/ERP</div>
            <nav className="app-nav">
              <a href="/crm">CRM</a>
              <a href="/sales">Sales</a>
              <a href="/finance">Finance</a>
              <a href="/billing">Billing</a>
              <a href="/inventory">Inventory</a>
              <a href="/auth">Auth</a>
              <a href="/hr">HR</a>
            </nav>
          </header>
          <main className="app-content">{children}</main>
        </div>
      </body>
    </html>
  );
}

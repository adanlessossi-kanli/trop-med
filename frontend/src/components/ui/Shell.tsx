"use client";

import React, { useState } from 'react';
import Link from 'next/link';

interface NavItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
  badge?: number;
}

interface ShellProps {
  children: React.ReactNode;
  navItems?: NavItem[];
  headerContent?: React.ReactNode;
}

const defaultNavItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'Patients', href: '/patients' },
  { label: 'Chat', href: '/chat' },
  { label: 'Surveillance', href: '/surveillance' },
  { label: 'Notifications', href: '/notifications' },
  { label: 'Settings', href: '/settings' },
];

export function Shell({ children, navItems = defaultNavItems, headerContent }: ShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* Sidebar overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/40 md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={[
          'fixed inset-y-0 left-0 z-30 w-64 bg-white shadow-lg flex flex-col',
          'transform transition-transform duration-200 ease-in-out',
          'md:relative md:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
        aria-label="Sidebar navigation"
      >
        <div className="flex items-center h-16 px-6 border-b border-slate-100">
          <span className="text-lg font-bold text-[#0d9488]">Trop-Med</span>
        </div>
        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1 px-3">
            {navItems.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium text-[#64748b] hover:bg-slate-100 hover:text-[#0d9488] transition-colors"
                  onClick={() => setSidebarOpen(false)}
                >
                  <span className="flex items-center gap-2">
                    {item.icon}
                    {item.label}
                  </span>
                  {item.badge != null && item.badge > 0 && (
                    <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-[#0d9488] rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top header */}
        <header className="h-16 bg-white shadow-sm flex items-center px-4 gap-4 z-10">
          {/* Hamburger — visible only on mobile */}
          <button
            className="md:hidden p-2 rounded-md text-[#64748b] hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-[#0d9488]"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation menu"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="flex-1">{headerContent}</div>
        </header>

        <main className="flex-1 p-6 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  CalendarDays,
  HeartPulse,
  Inbox,
  PackageCheck,
  RotateCcw,
  Search,
  Settings,
  Sparkles,
  Bell,
  UserRound,
  UsersRound,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Today", href: "/", icon: Activity },
  { label: "Calendar", href: "/calendar", icon: CalendarDays },
  { label: "Patients", href: "/patients", icon: UsersRound },
  { label: "Inbox", href: "/inbox", icon: Inbox },
  { label: "Follow-ups", href: "/follow-ups", icon: HeartPulse },
  { label: "Recovery", href: "/recovery", icon: RotateCcw },
  { label: "Packages", href: "/packages", icon: PackageCheck },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-transparent text-slate-950">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-slate-900/[0.08] bg-white/74 p-5 shadow-sm shadow-slate-900/[0.03] backdrop-blur-2xl lg:flex lg:flex-col">
        <Link href="/" className="flex items-center gap-3 rounded-2xl">
          <span className="relative flex h-[42px] w-[42px] items-center justify-center overflow-hidden rounded-[14px] bg-gradient-to-br from-[#2563EB] to-[#14B8A6] text-white shadow-lg shadow-blue-900/15 ring-1 ring-white/50">
            <span className="absolute inset-x-1 top-1 h-px bg-white/50" />
            <Sparkles className="h-[18px] w-[18px]" />
          </span>
          <span>
            <span className="block text-[15px] font-bold leading-5 tracking-[-0.02em] text-[#0F172A]">
              Clinic Autopilot
            </span>
            <span className="text-xs font-semibold text-[#64748B]">
              AI clinic operations
            </span>
          </span>
        </Link>

        <nav className="mt-8 space-y-1.5">
          {navItems.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "premium-transition flex h-11 items-center gap-3 rounded-[14px] px-3 text-sm font-semibold",
                  active
                    ? "bg-[#EEF6FF] text-[#1D4ED8] ring-1 ring-blue-600/10 shadow-sm shadow-blue-900/[0.04]"
                    : "text-[#64748B] hover:bg-slate-900/[0.04] hover:text-[#0F172A]",
                )}
              >
                <Icon className="h-[18px] w-[18px]" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto rounded-[22px] border border-slate-900/[0.08] bg-gradient-to-br from-white to-slate-50 p-4 shadow-sm shadow-slate-900/[0.03]">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-bold text-[#0F172A]">Dr. Karim Clinic</p>
              <p className="mt-0.5 text-xs font-semibold text-[#64748B]">
                Founder plan
              </p>
            </div>
            <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700 ring-1 ring-emerald-100">
              Live
            </span>
          </div>
        </div>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 min-h-[68px] border-b border-white/60 bg-[#F5F7FB]/58 px-5 py-3 backdrop-blur-2xl lg:px-8">
          <div className="mx-auto flex max-w-[1480px] flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-[#2563EB]">
                Friday, May 8
              </p>
              <h1 className="mt-0.5 text-sm font-bold tracking-[-0.01em] text-[#0F172A]">
                Dr. Karim Dental Clinic
              </h1>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <label className="premium-transition flex h-11 min-w-0 items-center gap-3 rounded-2xl border border-white/70 bg-white/72 px-4 text-sm text-[#94A3B8] shadow-sm shadow-slate-900/[0.025] backdrop-blur-xl ring-1 ring-slate-900/[0.04] focus-within:ring-4 focus-within:ring-blue-600/10 sm:w-[420px]">
                <Search className="h-4 w-4 shrink-0" />
                <input
                  className="min-w-0 flex-1 bg-transparent text-[#0F172A] placeholder:text-[#94A3B8]"
                  placeholder="Search patient, phone, appointment, service..."
                />
              </label>
              <button className="relative flex h-11 w-11 items-center justify-center rounded-2xl border border-white/70 bg-white/72 text-slate-600 shadow-sm shadow-slate-900/[0.025] backdrop-blur-xl ring-1 ring-slate-900/[0.04]">
                <Bell className="h-[18px] w-[18px]" />
                <span className="absolute right-3 top-3 h-2 w-2 rounded-full bg-blue-600 ring-2 ring-white" />
              </button>
              <div className="flex h-11 items-center gap-3 rounded-2xl border border-white/70 bg-white/72 px-3 shadow-sm shadow-slate-900/[0.025] backdrop-blur-xl ring-1 ring-slate-900/[0.04]">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#0F172A] text-white">
                  <UserRound className="h-4 w-4" />
                </span>
                <span className="pr-2">
                  <span className="block text-sm font-bold leading-4 text-[#0F172A]">
                    Dr. Karim
                  </span>
                  <span className="text-xs font-semibold text-[#64748B]">Owner</span>
                </span>
              </div>
            </div>
          </div>
          <nav className="mt-4 flex gap-2 overflow-x-auto pb-1 lg:hidden">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="shrink-0 rounded-full bg-white px-4 py-2 text-sm font-medium text-slate-700 ring-1 ring-slate-200"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto max-w-[1480px] px-5 py-6 lg:px-8 lg:py-8">
          {children}
        </main>
      </div>
    </div>
  );
}

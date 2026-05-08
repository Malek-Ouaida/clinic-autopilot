import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = {
  children: ReactNode;
  variant?: "primary" | "blue" | "secondary" | "ghost" | "danger";
  className?: string;
};

export function Button({ children, variant = "secondary", className }: ButtonProps) {
  const variants = {
    primary:
      "bg-[#0F172A] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.10),0_1px_2px_rgba(15,23,42,0.10)] hover:bg-[#1E293B]",
    blue:
      "bg-[#2563EB] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.18),0_8px_18px_rgba(37,99,235,0.18)] hover:bg-[#1D4ED8]",
    secondary:
      "bg-white text-[#0F172A] ring-1 ring-slate-900/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.80),0_1px_2px_rgba(15,23,42,0.04)] hover:bg-slate-50",
    ghost: "bg-transparent text-[#475569] hover:bg-slate-900/[0.05]",
    danger: "bg-rose-50 text-rose-700 ring-1 ring-rose-200/70 hover:bg-rose-100",
  };

  return (
    <button
      type="button"
      className={cn(
        "premium-transition inline-flex h-10 items-center justify-center gap-2 rounded-xl px-4 text-sm font-semibold active:scale-[0.99]",
        variants[variant],
        className,
      )}
    >
      {children}
    </button>
  );
}

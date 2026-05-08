import type { LucideIcon } from "lucide-react";
import { ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";

const toneClasses: Record<string, string> = {
  blue: "bg-blue-50 text-blue-600 ring-blue-100",
  green: "bg-emerald-50 text-emerald-600 ring-emerald-100",
  amber: "bg-amber-50 text-amber-600 ring-amber-100",
  red: "bg-rose-50 text-rose-600 ring-rose-100",
  purple: "bg-violet-50 text-violet-600 ring-violet-100",
  teal: "bg-teal-50 text-teal-600 ring-teal-100",
  indigo: "bg-indigo-50 text-indigo-600 ring-indigo-100",
  slate: "bg-slate-100 text-slate-600 ring-slate-200",
};

export function MetricCard({
  label,
  value,
  detail,
  tone = "blue",
  icon: Icon = ArrowUpRight,
}: {
  label: string;
  value: string;
  detail: string;
  tone?: string;
  icon?: LucideIcon;
}) {
  return (
    <section className="surface premium-transition lift-hover rounded-[22px] p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[#64748B]">
            {label}
          </p>
          <p className="mt-3 text-[36px] font-bold leading-[38px] tracking-[-0.04em] text-[#0F172A]">
            {value}
          </p>
        </div>
        <div
          className={cn(
            "flex h-10 w-10 items-center justify-center rounded-xl ring-1",
            toneClasses[tone],
          )}
        >
          <Icon className="h-5 w-5" />
        </div>
      </div>
      <p className="mt-4 text-sm font-medium leading-[21px] text-[#64748B]">
        {detail}
      </p>
    </section>
  );
}

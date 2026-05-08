import type { LucideIcon } from "lucide-react";
import { ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function ActionCard({
  title,
  subtitle,
  button,
  metadata,
  icon: Icon = ChevronRight,
}: {
  title: string;
  subtitle: string;
  button: string;
  metadata?: string;
  icon?: LucideIcon;
}) {
  return (
    <article className="premium-transition lift-hover rounded-[20px] border border-slate-900/[0.08] bg-white p-[18px]">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-4">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600 ring-1 ring-blue-100">
            <Icon className="h-[18px] w-[18px]" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-[15px] font-semibold leading-5 text-[#0F172A]">
                {title}
              </h3>
              {metadata ? (
                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-500">
                  {metadata}
                </span>
              ) : null}
            </div>
            <p className="mt-1 max-w-md text-sm font-medium leading-[21px] text-[#64748B]">
              {subtitle}
            </p>
          </div>
        </div>
        <Button variant="primary" className="shrink-0">
          {button}
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </article>
  );
}

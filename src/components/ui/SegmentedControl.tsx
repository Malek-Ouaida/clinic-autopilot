import { cn } from "@/lib/utils";

export function SegmentedControl({
  options,
  active,
}: {
  options: string[];
  active: string;
}) {
  return (
    <div className="inline-flex rounded-2xl bg-slate-100/80 p-1 ring-1 ring-slate-900/5">
      {options.map((option) => (
        <button
          key={option}
          type="button"
          className={cn(
            "premium-transition h-9 rounded-xl px-4 text-sm font-semibold",
            active === option
              ? "bg-white text-[#0F172A] shadow-sm shadow-slate-900/[0.05]"
              : "text-slate-500 hover:text-slate-900",
          )}
        >
          {option}
        </button>
      ))}
    </div>
  );
}

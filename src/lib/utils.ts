import type { Status } from "@/types";

export function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function statusTone(status: Status) {
  const tones: Record<Status, string> = {
    confirmed: "bg-[#DCFCE7] text-[#166534] ring-emerald-200/70",
    unconfirmed: "bg-[#FEF3C7] text-[#92400E] ring-amber-200/70",
    "high-risk": "bg-[#FEE2E2] text-[#991B1B] ring-rose-200/70",
    "follow-up": "bg-[#EDE9FE] text-[#5B21B6] ring-violet-200/70",
    completed: "bg-[#DBEAFE] text-[#1E40AF] ring-blue-200/70",
    cancelled: "bg-[#E2E8F0] text-[#475569] ring-slate-300/70",
    blocked: "bg-[#F1F5F9] text-[#52525B] ring-zinc-300/70",
    open: "bg-[#D1FAE5] text-[#047857] ring-emerald-200/70",
  };

  return tones[status];
}

export function statusDot(status: Status) {
  const dots: Record<Status, string> = {
    confirmed: "bg-[#22C55E]",
    unconfirmed: "bg-[#F59E0B]",
    "high-risk": "bg-[#EF4444]",
    "follow-up": "bg-[#8B5CF6]",
    completed: "bg-[#3B82F6]",
    cancelled: "bg-[#94A3B8]",
    blocked: "bg-[#71717A]",
    open: "bg-[#10B981]",
  };

  return dots[status];
}

export function statusLabel(status: Status) {
  const labels: Record<Status, string> = {
    confirmed: "Confirmed",
    unconfirmed: "Not confirmed",
    "high-risk": "High risk",
    "follow-up": "Follow-up",
    completed: "Completed",
    cancelled: "Cancelled",
    blocked: "Blocked",
    open: "Open slot",
  };

  return labels[status];
}

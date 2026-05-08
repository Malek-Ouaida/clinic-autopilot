import { CircleDollarSign, TrendingDown, TrendingUp } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { IconBadge } from "@/components/ui/IconBadge";

const metrics = [
  { label: "Appointments scheduled", value: "286", detail: "This month", tone: "blue" },
  { label: "Confirmed", value: "231", detail: "81% confirmation rate", tone: "green" },
  { label: "No-shows", value: "14", detail: "Actively decreasing", tone: "red" },
  { label: "No-show rate", value: "4.8%", detail: "Down from last month", tone: "teal" },
  { label: "Follow-ups sent", value: "63", detail: "Approved by staff", tone: "purple" },
  { label: "Patients rebooked", value: "19", detail: "From follow-ups", tone: "indigo" },
  { label: "Revenue recovered", value: "$1,250", detail: "Estimated", tone: "teal" },
];

const insights = [
  "No-shows are down 21% compared to last month.",
  "Follow-up rebookings increased by 31%.",
  "Recovery messages brought back 11 patients.",
  "Open slot recovery filled 7 cancelled slots.",
];

export function AnalyticsScreen() {
  return (
    <div>
      <PageHeader
        eyebrow="Analytics"
        title="Analytics"
        subtitle="See how Clinic Autopilot is improving your clinic."
      />

      <section className="hero-surface rounded-[36px] p-7 md:p-8">
        <div className="grid gap-8 xl:grid-cols-[1fr_680px] xl:items-center">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.22em] text-[#2563EB]">
              Owner briefing
            </p>
            <h3 className="mt-3 text-[38px] font-bold leading-[42px] tracking-[-0.055em] text-[#0F172A]">
              Fewer missed visits. More recovered revenue.
            </h3>
            <p className="mt-4 max-w-xl text-[15px] font-medium leading-7 text-[#64748B]">
              The business view stays focused on what changed because the clinic
              acted earlier.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-4">
            {metrics.slice(0, 4).map((metric) => (
              <AnalyticsMetric key={metric.label} {...metric} />
            ))}
          </div>
        </div>
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-[1fr_420px]">
        <Card className="rounded-[30px] p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold tracking-[-0.02em] text-[#0F172A]">
                No-show trend
              </h3>
              <p className="mt-1 text-sm font-medium text-[#64748B]">
                A lightweight chart for the clinic owner.
              </p>
            </div>
            <IconBadge icon={TrendingDown} tone="emerald" />
          </div>
          <div className="mt-8 flex h-64 items-end gap-4">
            {[74, 62, 55, 48, 39, 31].map((height, index) => (
              <div key={height} className="flex flex-1 flex-col items-center gap-3">
                <div className="flex w-full items-end rounded-t-2xl bg-slate-100">
                  <div
                    className="w-full rounded-t-2xl bg-gradient-to-t from-[#2563EB] to-[#14B8A6]"
                    style={{ height: `${height * 2}px` }}
                  />
                </div>
                <span className="text-xs font-medium text-slate-500">
                  W{index + 1}
                </span>
              </div>
            ))}
          </div>
        </Card>

        <aside className="space-y-4">
          {insights.map((insight, index) => (
            <Card key={insight} className="rounded-[24px] p-5">
              <div className="flex gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100">
                  {index === 3 ? (
                    <CircleDollarSign className="h-5 w-5" />
                  ) : (
                    <TrendingUp className="h-5 w-5" />
                  )}
                </span>
                <p className="font-bold leading-6 text-[#0F172A]">{insight}</p>
              </div>
            </Card>
          ))}
        </aside>
      </section>
    </div>
  );
}

function AnalyticsMetric({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-[24px] border border-white/80 bg-white/76 p-4 shadow-sm shadow-slate-900/[0.03] ring-1 ring-slate-900/[0.05]">
      <p className="text-[30px] font-bold leading-8 tracking-[-0.055em] text-[#0F172A]">
        {value}
      </p>
      <p className="mt-2 text-xs font-bold uppercase tracking-[0.1em] text-[#64748B]">
        {label}
      </p>
      <p className="mt-1 text-xs font-semibold text-[#94A3B8]">{detail}</p>
    </div>
  );
}

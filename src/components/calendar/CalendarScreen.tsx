import {
  AlertTriangle,
  ArrowUpRight,
  CalendarDays,
  Clock,
  Filter,
  Plus,
  Sparkles,
  UserRound,
} from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconBadge } from "@/components/ui/IconBadge";
import { SegmentedControl } from "@/components/ui/SegmentedControl";
import { appointments, blockedTimes, doctors } from "@/data/mock-data";
import { cn, statusDot } from "@/lib/utils";

export function CalendarScreen() {
  return (
    <div>
      <PageHeader
        eyebrow="Calendar"
        title="Calendar"
        subtitle="See who is coming, what needs confirmation, and which slots can be recovered."
        action={
          <Button variant="blue">
            <Plus className="h-4 w-4" />
            Add appointment
          </Button>
        }
      />

      <section className="hero-surface rounded-[34px] p-7">
        <div className="grid gap-6 xl:grid-cols-[1fr_420px] xl:items-center">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#2563EB]">
              Smart scheduling
            </p>
            <h3 className="mt-3 max-w-3xl text-[36px] font-bold leading-[40px] tracking-[-0.05em] text-[#0F172A]">
              The day is sequenced, watched, and recoverable.
            </h3>
            <p className="mt-3 max-w-2xl text-[15px] font-medium leading-7 text-[#64748B]">
              Clinic Autopilot highlights confirmation risk, blocked time, open
              slots, and waitlist matches before the schedule breaks.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
            <CalendarSignal icon={Clock} label="Working hours" value="9-6" />
            <CalendarSignal icon={UserRound} label="Doctor services" value="9" />
            <CalendarSignal icon={AlertTriangle} label="Conflicts prevented" value="2" />
          </div>
        </div>
      </section>

      <section className="mt-7 grid gap-6 xl:grid-cols-[1fr_380px]">
        <Card className="rounded-[30px] p-6">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <SegmentedControl options={["Today", "Week", "Month"]} active="Today" />
          <div className="flex flex-wrap gap-2">
            <Filter className="mt-2 h-4 w-4 text-slate-400" />
            {doctors.map((doctor) => (
              <Button key={doctor} variant="secondary">
                {doctor}
              </Button>
            ))}
            <Button variant="secondary">Status: All</Button>
          </div>
        </div>

        <div className="mt-6 grid gap-5 xl:grid-cols-[148px_1fr]">
          <aside className="rounded-[24px] bg-slate-50/80 p-4 ring-1 ring-slate-900/[0.06]">
            <h3 className="font-bold text-[#0F172A]">Hours</h3>
            <div className="mt-4 space-y-4 text-sm text-slate-500">
              {["9 AM", "10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM"].map(
                (hour) => (
                  <div key={hour} className="flex items-center gap-3">
                    <span className="h-px flex-1 bg-slate-200" />
                    {hour}
                  </div>
                ),
              )}
            </div>
          </aside>

          <div className="grid gap-4">
            {appointments.map((appointment) => (
              <article
                key={appointment.id}
                className={cn(
                  "premium-transition lift-hover grid gap-4 rounded-[22px] border bg-white p-4 md:grid-cols-[90px_1fr_auto]",
                  appointment.status === "cancelled"
                    ? "border-emerald-200 bg-emerald-50/60"
                    : "border-slate-900/[0.08]",
                )}
              >
                <div className="flex items-center gap-3 md:block">
                  <CalendarDays className="h-5 w-5 text-teal-700 md:hidden" />
                  <p className="font-bold text-[#0F172A]">{appointment.time}</p>
                  <p className="mt-1 text-xs font-semibold text-[#94A3B8]">
                    {appointment.room}
                  </p>
                </div>
                <div className="border-l-4 border-blue-400 pl-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-bold text-[#0F172A]">
                      {appointment.patient}
                    </h3>
                    <Badge status={appointment.status} />
                    {appointment.risk === "High" ? (
                      <Badge status="high-risk">High no-show risk</Badge>
                    ) : null}
                  </div>
                  <p className="mt-1 text-sm font-medium text-[#64748B]">
                    Today at {appointment.time} · {appointment.service} ·{" "}
                    {appointment.doctor}
                  </p>
                  {appointment.reason ? (
                    <p className="mt-3 rounded-2xl bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-800">
                      Reason: {appointment.reason}
                    </p>
                  ) : null}
                </div>
                <div className="flex flex-wrap items-center gap-2 md:justify-end">
                  <Button variant={appointment.status === "cancelled" ? "blue" : "ghost"}>
                    {appointment.status === "cancelled" ? "View candidates" : "Call"}
                    {appointment.status === "cancelled" ? (
                      <ArrowUpRight className="h-4 w-4" />
                    ) : null}
                  </Button>
                  <Button variant="ghost">Reminder</Button>
                </div>
              </article>
            ))}
          </div>
        </div>
        </Card>

        <aside className="space-y-5">
          <Card className="rounded-[30px] p-6">
            <div className="flex items-center gap-3">
              <IconBadge icon={Sparkles} tone="blue" />
              <div>
                <h3 className="text-xl font-bold tracking-[-0.02em] text-[#0F172A]">
                  Schedule intelligence
                </h3>
                <p className="text-sm font-medium text-[#64748B]">
                  The calendar is watching risk and capacity.
                </p>
              </div>
            </div>
            <div className="mt-5 space-y-3">
              {[
                ["3", "unconfirmed appointments", "unconfirmed"],
                ["1", "open slot", "open"],
                ["2", "high-risk patients", "high-risk"],
                ["4", "reminders ready", "completed"],
              ].map(([value, label, status]) => (
                <div
                  key={label}
                  className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3"
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={cn("h-2 w-2 rounded-full", statusDot(status as never))}
                    />
                    <span className="text-sm font-semibold text-[#475569]">{label}</span>
                  </div>
                  <span className="text-lg font-bold text-[#0F172A]">{value}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card className="rounded-[30px] p-6">
            <h3 className="text-xl font-bold text-[#0F172A]">Blocked time</h3>
            <div className="mt-4 space-y-3">
              {blockedTimes.map((block) => (
                <div
                  key={block.id}
                  className="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-900/[0.06]"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-bold text-[#0F172A]">{block.patient}</p>
                      <p className="mt-1 text-sm font-medium text-[#64748B]">
                        {block.time} · {block.service} · {block.doctor}
                      </p>
                    </div>
                    <Badge status="blocked" />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card hero className="rounded-[30px] p-6">
            <h3 className="text-xl font-bold text-[#0F172A]">Open slot recovery</h3>
            <p className="mt-2 font-medium text-[#64748B]">
              4:30 PM opened. 3 waitlisted patients match without a doctor or room
              conflict.
            </p>
            <Button variant="blue" className="mt-5">
              View candidates
            </Button>
          </Card>
        </aside>
      </section>
    </div>
  );
}

function CalendarSignal({
  icon,
  label,
  value,
}: {
  icon: typeof Clock;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-[22px] border border-white/80 bg-white/76 p-4 shadow-sm shadow-slate-900/[0.03] ring-1 ring-slate-900/[0.04]">
      <div className="flex items-center gap-3">
        <IconBadge icon={icon} tone="blue" className="rounded-2xl" />
        <p className="text-sm font-bold text-[#475569]">{label}</p>
      </div>
      <p className="text-[30px] font-bold leading-8 tracking-[-0.05em] text-[#0F172A]">
        {value}
      </p>
    </div>
  );
}

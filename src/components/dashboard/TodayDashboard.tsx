import type { LucideIcon } from "lucide-react";
import {
  Activity,
  ArrowUpRight,
  CalendarCheck,
  Clock3,
  PhoneCall,
  Send,
  Sparkles,
  UserPlus,
  WandSparkles,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { IconBadge } from "@/components/ui/IconBadge";
import { appointments } from "@/data/mock-data";
import { cn, statusDot } from "@/lib/utils";

const heroSignals = [
  { label: "At risk", value: "3", status: "high-risk" as const },
  { label: "Open slot", value: "1", status: "open" as const },
  { label: "Ready drafts", value: "6", status: "completed" as const },
];

const clinicPulse = [
  { label: "Appointments today", value: "28", status: "completed" as const },
  { label: "Confirmed", value: "19", status: "confirmed" as const },
  { label: "At risk", value: "3", status: "high-risk" as const },
  { label: "Follow-ups due", value: "5", status: "follow-up" as const },
  { label: "Open slot", value: "1", status: "open" as const },
  { label: "Messages ready", value: "8", status: "completed" as const },
];

const priorityStack = [
  {
    title: "Call high-risk patients",
    detail: "3 patients · before noon",
    tone: "rose" as const,
  },
  {
    title: "Fill open slot",
    detail: "4:30 PM · 3 candidates",
    tone: "emerald" as const,
  },
  {
    title: "Approve reminders",
    detail: "6 messages ready",
    tone: "blue" as const,
  },
];

const todayActions = [
  {
    title: "Call 3 high-risk patients",
    subtitle: "These patients may not show up unless contacted.",
    metadata: "Before noon",
    button: "Review calls",
    icon: PhoneCall,
  },
  {
    title: "Fill the 4:30 PM slot",
    subtitle:
      "A cancellation created an opening. Three waitlisted patients match this service.",
    metadata: "3 matches",
    button: "Fill slot",
    icon: CalendarCheck,
  },
  {
    title: "Approve patient reminders",
    subtitle: "Six confirmation messages are ready to send.",
    metadata: "6 drafts",
    button: "Approve",
    icon: Send,
  },
  {
    title: "Recover missed patients",
    subtitle: "Four patients missed or cancelled and never rebooked.",
    metadata: "$310 opportunity",
    button: "Start recovery",
    icon: UserPlus,
  },
];

export function TodayDashboard() {
  const timeline = [appointments[0], appointments[1], appointments[2], appointments[5]];

  return (
    <div className="space-y-7">
      <header className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.22em] text-[#2563EB]">
            Clinic mission control
          </p>
          <h2 className="mt-2 text-[34px] font-bold leading-[39px] tracking-[-0.04em] text-[#0F172A]">
            Good morning, Dr. Karim Clinic
          </h2>
          <p className="mt-2 text-base font-medium leading-6 text-[#64748B]">
            Here’s what needs attention today.
          </p>
        </div>
        <div className="flex w-fit items-center gap-3 rounded-full border border-white/80 bg-white/62 px-4 py-2.5 shadow-sm shadow-slate-900/[0.025] backdrop-blur-xl ring-1 ring-slate-900/[0.04]">
          <p className="text-sm font-bold text-[#0F172A]">Friday, May 8</p>
          <span className="h-4 w-px bg-slate-200" />
          <span className="flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700 ring-1 ring-emerald-100">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Clinic under control
          </span>
        </div>
      </header>

      <section className="grid gap-5 xl:grid-cols-12">
        <div className="hero-surface relative overflow-hidden rounded-[38px] p-7 md:p-8 xl:col-span-7">
          <div className="pointer-events-none absolute -right-20 -top-24 h-80 w-80 rounded-full bg-blue-500/[0.08] blur-3xl" />
          <div className="pointer-events-none absolute -bottom-28 left-10 h-80 w-80 rounded-full bg-teal-400/[0.09] blur-3xl" />
          <div className="pointer-events-none absolute inset-x-10 top-0 h-px bg-gradient-to-r from-transparent via-white to-transparent" />
          <div className="relative flex min-h-[330px] flex-col justify-between">
            <div>
              <div className="flex items-center gap-3">
                <IconBadge
                  icon={Sparkles}
                  tone="blue"
                  className="h-12 w-12 rounded-2xl"
                />
                <p className="text-xs font-bold uppercase tracking-[0.24em] text-[#2563EB]">
                  Today’s briefing
                </p>
              </div>
              <h3 className="mt-6 max-w-4xl text-[44px] font-bold leading-[47px] tracking-[-0.06em] text-[#0F172A] md:text-[54px] md:leading-[55px]">
                3 patients need attention before noon.
              </h3>
              <p className="mt-4 max-w-2xl text-[16px] font-medium leading-7 text-[#475569]">
                Unconfirmed appointments, one open slot, and overdue follow-ups
                are creating avoidable revenue risk today.
              </p>
            </div>

            <div>
              <div className="mt-8 grid gap-3 sm:grid-cols-3">
                {heroSignals.map((item) => (
                  <HeroSignal key={item.label} {...item} />
                ))}
              </div>
              <div className="mt-6 flex flex-wrap gap-3">
                <Button variant="blue" className="h-11 px-5">
                  Review today’s priorities
                  <ArrowUpRight className="h-4 w-4" />
                </Button>
                <Button variant="secondary" className="h-11 px-5">
                  Approve prepared messages
                </Button>
              </div>
            </div>
          </div>
        </div>

        <PriorityStack />
      </section>

      <ClinicPulseStrip />

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_430px]">
        <section className="surface rounded-[34px] p-6 md:p-8">
          <div className="mb-7 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#2563EB]">
                Intelligent assistant
              </p>
              <h3 className="mt-2 text-[26px] font-bold leading-8 tracking-[-0.04em] text-[#0F172A]">
                Recommended actions
              </h3>
              <p className="mt-1 text-sm font-medium text-[#64748B]">
                The system found what matters and prepared the next move.
              </p>
            </div>
            <span className="w-fit rounded-full bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700 ring-1 ring-blue-100">
              4 decisions ready
            </span>
          </div>
          <div className="divide-y divide-slate-900/[0.07] overflow-hidden rounded-[26px] border border-slate-900/[0.08] bg-white/78">
            {todayActions.map((action, index) => (
              <PremiumAction
                key={action.title}
                {...action}
                emphasized={index === 0 || index === 1}
              />
            ))}
          </div>
        </section>

        <TimelineFeed appointments={timeline} />
      </section>

      <section className="relative overflow-hidden rounded-[38px] bg-[#0F172A] p-7 text-white shadow-[0_34px_86px_rgba(15,23,42,0.26)] md:p-10">
        <div className="pointer-events-none absolute right-0 top-0 h-80 w-80 rounded-full bg-emerald-400/10 blur-3xl" />
        <div className="pointer-events-none absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="relative grid gap-10 lg:grid-cols-[1fr_590px] lg:items-center">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.22em] text-emerald-300">
              Impact this month
            </p>
            <h3 className="mt-3 max-w-2xl text-[38px] font-bold leading-[42px] tracking-[-0.055em]">
              Clinic Autopilot is turning missed attention into recovered visits.
            </h3>
            <p className="mt-4 max-w-xl text-[15px] font-medium leading-7 text-slate-300">
              Recovery workflows brought back 11 more patients than last month.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            <Impact value="32" label="patients recovered" />
            <Impact value="$2,480" label="estimated recovered" featured />
            <Impact value="-21%" label="no-shows" />
          </div>
        </div>
      </section>
    </div>
  );
}

function PriorityStack() {
  return (
    <aside className="relative overflow-hidden rounded-[38px] border border-slate-900/[0.08] bg-white/70 p-6 shadow-[0_1px_2px_rgba(15,23,42,0.035),0_18px_48px_rgba(15,23,42,0.07)] backdrop-blur-xl xl:col-span-5">
      <div className="pointer-events-none absolute -right-20 top-6 h-56 w-56 rounded-full bg-teal-400/[0.08] blur-3xl" />
      <div className="relative">
        <div className="flex items-start justify-between gap-5">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#14B8A6]">
              AI operator rail
            </p>
            <h3 className="mt-2 text-[31px] font-bold leading-[34px] tracking-[-0.05em] text-[#0F172A]">
              Priority Stack
            </h3>
            <p className="mt-2 max-w-sm text-sm font-medium leading-6 text-[#64748B]">
              Three moves will keep the day under control.
            </p>
          </div>
          <IconBadge icon={WandSparkles} tone="teal" className="h-12 w-12 rounded-2xl" />
        </div>

        <div className="mt-6">
          {priorityStack.map((item, index) => (
            <div key={item.title} className="group relative grid grid-cols-[44px_minmax(0,1fr)_36px] items-center gap-4 py-3">
              {index < priorityStack.length - 1 ? (
                <div className="absolute bottom-[-10px] left-[21px] top-[54px] w-px bg-slate-200" />
              ) : null}
              <span
                className={cn(
                  "relative z-10 flex h-11 w-11 items-center justify-center rounded-full text-sm font-bold ring-1",
                  item.tone === "rose" &&
                    "bg-rose-50 text-rose-700 ring-rose-100",
                  item.tone === "emerald" &&
                    "bg-emerald-50 text-emerald-700 ring-emerald-100",
                  item.tone === "blue" &&
                    "bg-blue-50 text-blue-700 ring-blue-100",
                )}
              >
                {index + 1}
              </span>
              <div>
                <p className="font-bold text-[#0F172A]">{item.title}</p>
                <p className="mt-0.5 text-sm font-medium text-[#64748B]">
                  {item.detail}
                </p>
              </div>
              <button className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-50 text-[#64748B] ring-1 ring-slate-900/[0.07] transition group-hover:bg-[#0F172A] group-hover:text-white">
                <ArrowUpRight className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>

        <div className="mt-5 rounded-[28px] bg-[#0F172A] p-5 text-white shadow-[0_22px_52px_rgba(15,23,42,0.18)]">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-300">
                Clinic Signal
              </p>
              <p className="mt-2 text-[30px] font-bold leading-8 tracking-[-0.055em]">
                42 minutes
              </p>
            </div>
            <IconBadge
              icon={Clock3}
              tone="slate"
              className="bg-white/10 text-white ring-white/10"
            />
          </div>
          <p className="mt-3 text-sm font-medium leading-6 text-slate-300">
            until the first no-show risk window.
          </p>
        </div>
      </div>
    </aside>
  );
}

function HeroSignal({
  label,
  value,
  status,
}: {
  label: string;
  value: string;
  status: "high-risk" | "open" | "completed";
}) {
  return (
    <div className="rounded-[24px] border border-white/80 bg-white/76 p-4 shadow-sm shadow-slate-900/[0.03] ring-1 ring-slate-900/[0.04]">
      <div className="flex items-center gap-2">
        <span className={cn("h-2 w-2 rounded-full", statusDot(status))} />
        <p className="text-xs font-bold uppercase tracking-[0.1em] text-[#64748B]">
          {label}
        </p>
      </div>
      <p className="mt-2 text-[32px] font-bold leading-8 tracking-[-0.055em] text-[#0F172A]">
        {value}
      </p>
    </div>
  );
}

function ClinicPulseStrip() {
  return (
    <section className="overflow-hidden rounded-[30px] border border-slate-900/[0.08] bg-white/78 shadow-[0_1px_2px_rgba(15,23,42,0.035),0_18px_44px_rgba(15,23,42,0.06)] backdrop-blur-xl">
      <div className="flex flex-col gap-0 md:flex-row md:items-stretch">
        <div className="flex items-center gap-3 border-b border-slate-900/[0.07] px-5 py-4 md:w-[220px] md:border-b-0 md:border-r">
          <IconBadge icon={Activity} tone="blue" className="h-10 w-10 rounded-2xl" />
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#94A3B8]">
              Clinic Pulse
            </p>
            <p className="text-sm font-bold text-[#0F172A]">Live operations</p>
          </div>
        </div>
        <div className="grid flex-1 grid-cols-2 md:grid-cols-6">
          {clinicPulse.map((item, index) => (
            <PulseCell key={item.label} {...item} showBorder={index > 0} />
          ))}
        </div>
      </div>
    </section>
  );
}

function PulseCell({
  label,
  value,
  status,
  showBorder,
}: {
  label: string;
  value: string;
  status: "completed" | "confirmed" | "high-risk" | "follow-up" | "open";
  showBorder: boolean;
}) {
  return (
    <div
      className={cn(
        "px-5 py-4",
        showBorder && "border-l border-slate-900/[0.07]",
      )}
    >
      <div className="flex items-center gap-2">
        <span className={cn("h-2 w-2 rounded-full", statusDot(status))} />
        <p className="truncate text-xs font-bold uppercase tracking-[0.1em] text-[#64748B]">
          {label}
        </p>
      </div>
      <p className="mt-2 text-[34px] font-bold leading-9 tracking-[-0.055em] text-[#0F172A]">
        {value}
      </p>
    </div>
  );
}

function PremiumAction({
  title,
  subtitle,
  button,
  metadata,
  icon: Icon,
  emphasized,
}: {
  title: string;
  subtitle: string;
  button: string;
  metadata: string;
  icon: LucideIcon;
  emphasized?: boolean;
}) {
  return (
    <article
      className={cn(
        "group grid gap-4 p-5 transition hover:bg-slate-50/80 md:grid-cols-[56px_minmax(0,1fr)_auto] md:items-center",
        emphasized && "bg-blue-50/45",
      )}
    >
      <span
        className={cn(
          "flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ring-1",
          emphasized
            ? "bg-white text-blue-600 ring-blue-100"
            : "bg-slate-50 text-slate-700 ring-slate-200",
        )}
      >
        <Icon className="h-5 w-5" />
      </span>
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <h4 className="text-[15px] font-bold leading-[21px] text-[#0F172A]">
            {title}
          </h4>
          <span className="rounded-full bg-white/86 px-2.5 py-1 text-xs font-bold text-[#64748B] ring-1 ring-slate-900/[0.07]">
            {metadata}
          </span>
        </div>
        <p className="mt-1 max-w-2xl text-sm font-medium leading-[22px] text-[#64748B]">
          {subtitle}
        </p>
      </div>
      <Button variant={emphasized ? "blue" : "primary"} className="shrink-0">
        {button}
        <ArrowUpRight className="h-4 w-4" />
      </Button>
    </article>
  );
}

function TimelineFeed({ appointments: items }: { appointments: typeof appointments }) {
  return (
    <aside className="rounded-[34px] border border-slate-900/[0.08] bg-white/64 p-6 shadow-[0_1px_2px_rgba(15,23,42,0.035),0_14px_36px_rgba(15,23,42,0.055)] backdrop-blur-xl md:p-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#14B8A6]">
            Intelligent feed
          </p>
          <h3 className="mt-2 text-[26px] font-bold leading-8 tracking-[-0.04em] text-[#0F172A]">
            Live clinic flow
          </h3>
          <p className="mt-1 text-sm font-medium text-[#64748B]">
            The system is monitoring today’s schedule.
          </p>
        </div>
        <IconBadge icon={Clock3} tone="teal" className="rounded-2xl" />
      </div>

      <div className="relative mt-8">
        <div className="absolute bottom-8 left-[76px] top-4 w-px bg-slate-200" />
        {items.map((appointment) => {
          const openSlot = appointment.patient === "Open slot";

          return (
            <article
              key={appointment.id}
              className="relative grid grid-cols-[64px_18px_minmax(0,1fr)] gap-3 py-4"
            >
              <p className="pt-0.5 text-right text-xs font-bold uppercase tracking-[0.12em] text-[#94A3B8]">
                {appointment.time.replace(" AM", "").replace(" PM", "")}
              </p>
              <span
                className={cn(
                  "relative z-10 mt-1.5 h-4 w-4 rounded-full border-[3px] border-white",
                  statusDot(appointment.status),
                )}
              />
              <div
                className={cn(
                  "rounded-[22px] border px-4 py-3",
                  openSlot
                    ? "border-emerald-200 bg-emerald-50/75"
                    : "border-transparent bg-transparent",
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h4 className="text-[15px] font-bold leading-5 text-[#0F172A]">
                      {appointment.patient}
                    </h4>
                    <p className="mt-1 text-sm font-medium text-[#64748B]">
                      {openSlot
                        ? "Cancelled appointment · 3 waitlist matches"
                        : `${appointment.service} · ${appointment.doctor}`}
                    </p>
                  </div>
                  <Badge status={appointment.status}>
                    {openSlot ? "Can be filled" : undefined}
                  </Badge>
                </div>
                <div className="mt-3">
                  <Button
                    variant={openSlot ? "blue" : "ghost"}
                    className="h-8 px-3 text-xs"
                  >
                    {openSlot
                      ? "Fill"
                      : appointment.status === "unconfirmed"
                        ? "Send reminder"
                        : "Action"}
                  </Button>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </aside>
  );
}

function Impact({
  value,
  label,
  featured,
}: {
  value: string;
  label: string;
  featured?: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded-[28px] border p-5 shadow-sm shadow-black/10 ring-1",
        featured
          ? "border-emerald-300/20 bg-emerald-400/[0.12] ring-emerald-300/20"
          : "border-white/10 bg-white/[0.08] ring-white/10",
      )}
    >
      <p className="text-[36px] font-bold leading-9 tracking-[-0.06em] text-white">
        {value}
      </p>
      <p className="mt-2 text-xs font-bold uppercase tracking-[0.12em] text-slate-300">
        {label}
      </p>
    </div>
  );
}

import Link from "next/link";
import { Activity, CalendarPlus, MessageCircle, Search, ShieldAlert } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconBadge } from "@/components/ui/IconBadge";
import { patients } from "@/data/mock-data";

export function PatientsScreen() {
  return (
    <div>
      <PageHeader
        eyebrow="Patients"
        title="What do we know about this patient?"
        subtitle="Find any patient, understand their status, and act without digging through records."
      />

      <section className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <div>
          <section className="hero-surface mb-6 rounded-[34px] p-7">
            <div className="grid gap-6 lg:grid-cols-[1fr_260px] lg:items-end">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#2563EB]">
                  Patient memory
                </p>
                <h3 className="mt-3 max-w-3xl text-[36px] font-bold leading-[40px] tracking-[-0.05em] text-[#0F172A]">
                  Search the clinic’s living memory.
                </h3>
                <p className="mt-3 max-w-2xl text-[15px] font-medium leading-7 text-[#64748B]">
                  Names, phones, services, follow-ups, and appointment history are
                  one command away.
                </p>
              </div>
              <div className="rounded-[24px] bg-white/76 p-4 ring-1 ring-slate-900/[0.06]">
                <div className="flex items-center gap-3">
                  <IconBadge icon={Activity} tone="blue" />
                  <div>
                    <p className="text-[30px] font-bold leading-8 tracking-[-0.05em] text-[#0F172A]">
                      10
                    </p>
                    <p className="text-xs font-bold uppercase tracking-[0.1em] text-[#64748B]">
                      active patients in view
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <label className="premium-transition mt-7 flex h-[60px] items-center gap-3 rounded-[22px] border border-white/80 bg-white/82 px-5 text-[#94A3B8] shadow-sm shadow-slate-900/[0.035] ring-1 ring-slate-900/[0.05] focus-within:ring-4 focus-within:ring-blue-600/10">
              <Search className="h-5 w-5" />
              <input
                className="min-w-0 flex-1 bg-transparent text-base font-semibold text-[#0F172A] placeholder:text-[#94A3B8]"
                placeholder="Search by name, phone, appointment, or service"
              />
            </label>
          </section>

      <div className="grid gap-4 2xl:grid-cols-2">
        {patients.map((patient) => (
          <article
            key={patient.id}
            className="surface premium-transition lift-hover rounded-[26px] p-5"
          >
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div className="flex gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-[#2563EB] to-[#14B8A6] text-sm font-bold text-white shadow-lg shadow-blue-900/10">
                  {initials(patient.name)}
                </div>
                <div>
                  <h3 className="text-[17px] font-bold tracking-[-0.02em] text-[#0F172A]">
                    {patient.name}
                  </h3>
                  <p className="mt-1 text-sm font-medium text-[#64748B]">
                    {patient.phone}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge status={patient.nextStatus} />
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">
                      {patient.preferredLanguage}
                    </span>
                  </div>
                </div>
              </div>
              <Link
                href={`/patients/${patient.id}`}
                className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
              >
                Open
              </Link>
            </div>

            <dl className="mt-5 grid gap-3 sm:grid-cols-2">
              <Info label="Next" value={patient.nextAppointment} />
              <Info label="Last visit" value={patient.lastVisit} />
              <Info label="Follow-up due" value={patient.followUpDue} />
              <Info label="No-shows" value={String(patient.noShows)} />
            </dl>

            <div className="mt-5 flex flex-wrap gap-2">
              <Button variant="secondary">
                <CalendarPlus className="h-4 w-4" />
                Book appointment
              </Button>
              <Button variant="secondary">
                <MessageCircle className="h-4 w-4" />
                Send message
              </Button>
            </div>
          </article>
        ))}
      </div>
        </div>

        <aside className="space-y-5">
          <Card hero className="sticky top-28 rounded-[30px] p-6">
            <div className="flex items-center gap-3">
              <IconBadge icon={ShieldAlert} tone="blue" />
              <div>
                <h3 className="text-xl font-bold tracking-[-0.02em] text-[#0F172A]">
                  Patient intelligence
                </h3>
                <p className="text-sm font-medium text-[#64748B]">
                  Where the clinic needs clean-up or follow-through.
                </p>
              </div>
            </div>
            <div className="mt-5 grid gap-3">
              <Intel value="12" label="overdue follow-ups" />
              <Intel value="6" label="possible duplicates" />
              <Intel value="4" label="high no-show history" />
              <Intel value="18" label="due this month" />
            </div>
          </Card>
        </aside>
      </section>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-slate-50/80 p-3">
      <dt className="text-xs font-bold uppercase tracking-[0.12em] text-[#94A3B8]">
        {label}
      </dt>
      <dd className="mt-1 text-sm font-bold text-[#0F172A]">{value}</dd>
    </div>
  );
}

function Intel({ value, label }: { value: string; label: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl bg-white/80 px-4 py-3 ring-1 ring-slate-900/[0.06]">
      <span className="text-sm font-semibold text-[#475569]">{label}</span>
      <span className="text-xl font-bold tracking-[-0.03em] text-[#0F172A]">
        {value}
      </span>
    </div>
  );
}

function initials(name: string) {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2);
}

import {
  AlertCircle,
  CalendarPlus,
  CheckCircle2,
  FileText,
  MessageCircle,
  Sparkles,
} from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconBadge } from "@/components/ui/IconBadge";
import type { Patient } from "@/types";

const tabs = [
  "Overview",
  "Appointments",
  "Visits",
  "Messages",
  "Follow-ups",
  "Payments",
  "Files",
];

const timeline = [
  "Appointment booked",
  "Reminder sent",
  "Patient confirmed",
  "Visit completed",
  "Follow-up scheduled",
  "Recovery message sent",
];

export function PatientProfile({ patient }: { patient: Patient }) {
  return (
    <div>
      <PageHeader
        eyebrow="Patient profile"
        title={patient.name}
        subtitle="A light clinical and operations record with the next best action visible immediately."
        action={
          <div className="flex flex-wrap gap-2">
            <Button variant="primary">
              <CalendarPlus className="h-4 w-4" />
              Book appointment
            </Button>
            <Button variant="secondary">
              <MessageCircle className="h-4 w-4" />
              Send message
            </Button>
          </div>
        }
      />

      <Card hero className="rounded-[30px] p-7">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
          <div className="flex gap-5">
            <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-[22px] bg-gradient-to-br from-[#2563EB] to-[#14B8A6] text-xl font-bold text-white shadow-xl shadow-blue-900/15">
              {initials(patient.name)}
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-2xl font-bold tracking-[-0.035em] text-[#0F172A]">
                  {patient.name}
                </h3>
                <Badge status={patient.nextStatus} />
              </div>
              <p className="mt-1 text-sm font-semibold text-[#64748B]">
                {patient.phone} · {patient.preferredLanguage}
              </p>
              <p className="mt-3 max-w-2xl text-sm font-medium leading-[21px] text-[#64748B]">
                The clinic memory for visits, messages, packages, payments, and
                the next action staff should take.
              </p>
            </div>
          </div>
          <div className="rounded-[22px] bg-white/78 p-4 ring-1 ring-slate-900/[0.08]">
            <p className="text-xs font-bold uppercase tracking-[0.14em] text-[#94A3B8]">
              Package/session summary
            </p>
            <p className="mt-2 text-sm font-bold text-[#0F172A]">
              {patient.packageStatus ?? "No active package"}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-5">
          <Summary label="Last visit" value={patient.lastVisit} />
          <Summary label="Next appointment" value={patient.nextAppointment} />
          <Summary label="No-shows" value={String(patient.noShows)} />
          <Summary label="Follow-up due" value={patient.followUpDue} />
          <Summary label="Balance" value={patient.balance} />
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <Button key={tab} variant={tab === "Overview" ? "primary" : "secondary"}>
              {tab}
            </Button>
          ))}
        </div>
      </Card>

      <section className="mt-6 grid gap-6 xl:grid-cols-[1fr_420px]">
        <Card className="rounded-[30px] p-6">
          <div className="flex items-center gap-3">
            <IconBadge icon={Sparkles} tone="blue" />
            <div>
              <h3 className="text-xl font-bold tracking-[-0.02em] text-[#0F172A]">
                Patient timeline
              </h3>
              <p className="text-sm font-medium text-[#64748B]">
                A clean audit trail of care and operations.
              </p>
            </div>
          </div>
          <div className="mt-5 space-y-4">
            {timeline.map((item, index) => (
              <div key={item} className="flex gap-4 rounded-[20px] bg-slate-50/80 p-4">
                <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white text-blue-600 ring-1 ring-blue-100">
                  <CheckCircle2 className="h-4 w-4" />
                </span>
                <div>
                  <p className="font-bold text-[#0F172A]">{item}</p>
                  <p className="text-sm font-medium text-[#64748B]">
                    {index < 4 ? "Completed by Clinic Autopilot" : "Needs review"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <aside className="space-y-4">
          <Card className="rounded-[30px] p-6">
            <div className="flex items-center gap-3">
              <IconBadge icon={FileText} tone="teal" />
              <h3 className="text-xl font-bold text-[#0F172A]">
                Light patient record
              </h3>
            </div>
            <div className="mt-4 space-y-3 text-sm">
              <Record label="Visit date" value={patient.lastVisit} />
              <Record label="Doctor" value="Dr. Karim" />
              <Record label="Service" value={patient.service} />
              <Record label="Reason" value="Routine visit and follow-up planning" />
              <Record label="Notes" value="Patient prefers WhatsApp reminders in the morning." />
              <Record label="Treatment done" value={patient.service} />
              <Record label="Attachments" value="2 files" />
              <Record label="Follow-up required" value="Yes" />
              <Record label="Next follow-up" value={patient.followUpDue} />
            </div>
          </Card>

          <div className="rounded-[28px] border border-amber-200/80 bg-amber-50 p-5 shadow-sm shadow-amber-900/[0.03]">
            <div className="flex gap-3">
              <AlertCircle className="h-5 w-5 shrink-0 text-amber-700" />
              <div>
                <h3 className="font-semibold text-amber-950">
                  Possible duplicate found
                </h3>
                <p className="mt-1 text-sm text-amber-800">
                  Maya H. has the same phone number.
                </p>
                <Button variant="secondary" className="mt-4">
                  Review merge
                </Button>
              </div>
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
}

function Summary({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white/76 p-3 ring-1 ring-slate-900/[0.06]">
      <p className="text-xs font-bold uppercase tracking-[0.12em] text-[#94A3B8]">
        {label}
      </p>
      <p className="mt-2 text-sm font-bold text-[#0F172A]">{value}</p>
    </div>
  );
}

function Record({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 rounded-2xl bg-slate-50 px-3 py-2">
      <span className="font-medium text-[#64748B]">{label}</span>
      <span className="text-right font-bold text-[#0F172A]">{value}</span>
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

import { CalendarPlus, PhoneCall, RotateCcw, Send } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconBadge } from "@/components/ui/IconBadge";
import { patients } from "@/data/mock-data";

const recoveryPatients = patients.filter((patient) =>
  ["rami-khoury", "karim-daher", "omar-hassan", "sara-tannous"].includes(patient.id),
);

export function RecoveryScreen() {
  return (
    <div>
      <PageHeader
        eyebrow="Recovery"
        title="Patient Recovery"
        subtitle="These are patients your clinic may lose if nobody follows up."
      />

      <section className="relative overflow-hidden rounded-[36px] bg-[#0F172A] p-7 text-white shadow-[0_30px_76px_rgba(15,23,42,0.22)] md:p-8">
        <div className="grid gap-8 xl:grid-cols-[1fr_620px] xl:items-center">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.22em] text-emerald-300">
              Recovery engine
            </p>
            <h3 className="mt-3 text-[38px] font-bold leading-[42px] tracking-[-0.055em]">
              Found money hiding in missed attention.
            </h3>
            <p className="mt-4 max-w-xl text-[15px] font-medium leading-7 text-slate-300">
              Missed appointments, cancelled slots, and overdue follow-ups become
              recovery actions the team can approve immediately.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-4">
            <RecoveryMetric value="8" label="missed" />
            <RecoveryMetric value="12" label="overdue" />
            <RecoveryMetric value="5" label="cancelled" />
            <RecoveryMetric value="$1,100" label="opportunity" />
          </div>
        </div>
      </section>

      <section className="mt-6 grid gap-5 xl:grid-cols-[1fr_420px]">
        <div className="space-y-4">
          {recoveryPatients.map((patient, index) => (
            <article
              key={patient.id}
              className="surface premium-transition lift-hover rounded-[28px] p-5"
            >
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="flex gap-4">
                  <IconBadge icon={RotateCcw} tone={index % 2 === 0 ? "rose" : "amber"} />
                  <div>
                    <h3 className="text-lg font-bold tracking-[-0.02em] text-[#0F172A]">
                      {patient.name}
                    </h3>
                    <p className="mt-1 text-sm font-medium text-[#64748B]">
                    {index % 2 === 0
                      ? "Missed appointment 3 days ago"
                      : "Cancelled without rebooking"}
                    </p>
                    <p className="mt-3 rounded-2xl bg-rose-50 px-3 py-2 text-sm font-bold text-rose-700 ring-1 ring-rose-100">
                      Suggested action: Send recovery message
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs font-bold uppercase tracking-[0.12em] text-[#94A3B8]">
                    Opportunity
                  </p>
                  <p className="mt-1 text-3xl font-bold tracking-[-0.04em] text-[#0F172A]">
                    ${index === 0 ? 180 : 120}
                  </p>
                </div>
              </div>
              <div className="mt-5 rounded-[20px] bg-teal-50 p-4 text-sm font-semibold leading-6 text-teal-800 ring-1 ring-teal-100">
                Hi {patient.name.split(" ")[0]}, we missed you at your last
                appointment. Would you like us to reserve a new time this week?
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <Button variant="blue">
                  <Send className="h-4 w-4" />
                  Approve message
                </Button>
                <Button variant="secondary">
                  <PhoneCall className="h-4 w-4" />
                  Call
                </Button>
                <Button variant="secondary">
                  <CalendarPlus className="h-4 w-4" />
                  Book appointment
                </Button>
              </div>
            </article>
          ))}
        </div>

        <Card hero className="h-fit rounded-[30px] p-6">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-700">
            Open slot recovery
          </p>
          <h3 className="mt-2 text-2xl font-bold tracking-[-0.035em] text-[#0F172A]">
            This slot is now open
          </h3>
          <p className="mt-2 font-medium text-[#64748B]">
            Today 4:30 PM · Dr. Karim · Consultation
          </p>
          <div className="mt-5 rounded-[22px] bg-white/80 p-5 ring-1 ring-emerald-100">
            <p className="text-4xl font-bold tracking-[-0.04em] text-[#0F172A]">
              3
            </p>
            <p className="mt-1 text-sm font-semibold text-[#64748B]">
              waitlisted patients match
            </p>
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            <Button variant="blue">Offer slot</Button>
            <Button variant="secondary">Broadcast to waitlist</Button>
            <Button variant="secondary">Manually assign</Button>
          </div>
        </Card>
      </section>
    </div>
  );
}

function RecoveryMetric({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-[24px] border border-white/10 bg-white/[0.08] p-4 ring-1 ring-white/10">
      <p className="text-[30px] font-bold leading-8 tracking-[-0.055em] text-white">
        {value}
      </p>
      <p className="mt-2 text-xs font-bold uppercase tracking-[0.12em] text-slate-300">
        {label}
      </p>
    </div>
  );
}

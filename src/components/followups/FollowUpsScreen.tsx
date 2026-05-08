import { CalendarPlus, Check, MessageCircle, Pencil, X } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconBadge } from "@/components/ui/IconBadge";
import { patients } from "@/data/mock-data";

const groups = [
  {
    title: "Due today",
    subtitle: "These patients need to come back.",
    patients: patients.filter((patient) => patient.followUpDue === "Today").slice(0, 3),
  },
  {
    title: "Overdue",
    subtitle: "Follow up before these patients drift away.",
    patients: patients.filter((patient) => patient.followUpDue === "Overdue").slice(0, 3),
  },
  {
    title: "Upcoming this week",
    subtitle: "Prepare reminders early while the schedule is calm.",
    patients: patients.filter((patient) => !["Today", "Overdue"].includes(patient.followUpDue)).slice(0, 3),
  },
];

export function FollowUpsScreen() {
  return (
    <div>
      <PageHeader
        eyebrow="Follow-ups"
        title="Follow-ups"
        subtitle="These patients need to come back."
      />

      <section className="grid gap-5 xl:grid-cols-3">
        {groups.map((group) => (
          <Card key={group.title} className="rounded-[30px] p-6">
            <h3 className="text-xl font-bold tracking-[-0.02em] text-[#0F172A]">
              {group.title}
            </h3>
            <p className="mt-2 text-sm font-medium text-[#64748B]">{group.subtitle}</p>
            <div className="mt-5 space-y-4">
              {group.patients.length ? (
                group.patients.map((patient) => (
                  <article
                    key={patient.id}
                    className="premium-transition lift-hover rounded-[22px] bg-white p-4 ring-1 ring-slate-900/[0.08]"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h4 className="font-bold text-[#0F172A]">{patient.name}</h4>
                        <p className="mt-1 text-sm font-medium text-[#64748B]">
                      {patient.service} follow-up due
                        </p>
                      </div>
                      <Badge status="follow-up">{patient.preferredLanguage}</Badge>
                    </div>
                    <p className="mt-3 text-sm font-semibold text-[#475569]">
                      Last visit: {patient.lastVisit}
                    </p>
                    <div className="mt-4 rounded-2xl bg-teal-50 p-3 text-sm font-semibold leading-6 text-teal-800 ring-1 ring-teal-100">
                      Hi {patient.name.split(" ")[0]}, it is time for your{" "}
                      {patient.service.toLowerCase()} follow-up. Would you like
                      us to reserve a time this week?
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <Button variant="primary">
                        <Check className="h-4 w-4" />
                        Approve message
                      </Button>
                      <Button variant="secondary">
                        <Pencil className="h-4 w-4" />
                        Edit
                      </Button>
                      <Button variant="ghost">
                        <X className="h-4 w-4" />
                        Skip
                      </Button>
                      <Button variant="secondary">
                        <CalendarPlus className="h-4 w-4" />
                        Book
                      </Button>
                    </div>
                  </article>
                ))
              ) : (
                <div className="rounded-[22px] bg-emerald-50 p-4 text-sm font-medium text-emerald-700">
                  No overdue follow-ups. All patients are up to date.
                </div>
              )}
            </div>
          </Card>
        ))}
      </section>

      <Card hero className="mt-6 rounded-[30px] p-6">
        <div className="flex items-center gap-3">
          <IconBadge icon={MessageCircle} tone="teal" />
          <div>
            <h3 className="text-xl font-bold text-[#0F172A]">
              Follow-up message logic
            </h3>
            <p className="mt-1 text-sm font-medium text-[#64748B]">
              FollowUpDue creates a Today task, drafts the message, waits for secretary
              approval, and turns patient replies into new appointment options.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}

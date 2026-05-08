import { Building2, Clock, Languages, LockKeyhole, MessageSquareText, UsersRound } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconBadge } from "@/components/ui/IconBadge";
import { clinics, doctors, services } from "@/data/mock-data";

const sections = [
  "Clinic Profile",
  "Branding",
  "Doctors",
  "Services",
  "Working Hours",
  "Message Templates",
  "Follow-Up Rules",
  "Staff Roles",
  "Language Settings",
];

const roles = [
  { role: "Owner/Admin", access: "Everything" },
  { role: "Doctor", access: "Patients, visits, own schedule" },
  { role: "Secretary", access: "Appointments, messages, reminders, basic patient info" },
  { role: "Assistant", access: "Limited appointment and status updates" },
];

const placeholders = [
  "{patient_name}",
  "{doctor_name}",
  "{appointment_time}",
  "{clinic_name}",
  "{service_name}",
];

export function SettingsScreen() {
  return (
    <div>
      <PageHeader
        eyebrow="Settings"
        title="How is this clinic configured?"
        subtitle="Simple clinic controls for doctors, services, templates, working hours, permissions, and future multilingual patient communication."
      />

      <section className="grid gap-6 xl:grid-cols-[280px_1fr]">
        <aside className="surface h-fit rounded-[28px] p-4">
          <nav className="space-y-1">
            {sections.map((section) => (
              <button
                key={section}
                type="button"
                className="premium-transition flex w-full items-center rounded-2xl px-3 py-3 text-left text-sm font-bold text-[#64748B] hover:bg-slate-900/[0.04] hover:text-[#0F172A]"
              >
                {section}
              </button>
            ))}
          </nav>
        </aside>

        <div className="grid gap-5">
          <Panel icon={Building2} title="Clinic Profile">
            <div className="grid gap-3 md:grid-cols-3">
              {clinics.map((clinic) => (
                <div key={clinic} className="rounded-2xl bg-slate-50 p-4">
                  <p className="font-semibold text-slate-950">{clinic}</p>
                  <p className="mt-1 text-sm text-slate-500">Configured workspace</p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel icon={UsersRound} title="Doctors and Services">
            <div className="grid gap-4 xl:grid-cols-2">
              <List title="Doctors" items={doctors} />
              <List title="Services" items={services} />
            </div>
          </Panel>

          <Panel icon={Clock} title="Working Hours and Follow-Up Rules">
            <div className="grid gap-3 md:grid-cols-3">
              {["Dr. Karim: 9 AM - 6 PM", "Dr. Lina: 10 AM - 5 PM", "Dr. Sara: 9 AM - 4 PM"].map(
                (item) => (
                  <div key={item} className="rounded-2xl bg-slate-50 p-4 text-sm font-semibold text-slate-800">
                    {item}
                  </div>
                ),
              )}
            </div>
          </Panel>

          <Panel icon={MessageSquareText} title="Message Templates">
            <p className="text-sm text-slate-500">
              Templates support dynamic placeholders for appointment reminders,
              follow-ups, recovery, and reactivation campaigns.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {placeholders.map((placeholder) => (
                <span
                  key={placeholder}
                  className="rounded-full bg-teal-50 px-3 py-1 text-sm font-semibold text-teal-700 ring-1 ring-teal-100"
                >
                  {placeholder}
                </span>
              ))}
            </div>
          </Panel>

          <Panel icon={LockKeyhole} title="Staff Roles and Permissions">
            <div className="grid gap-3 md:grid-cols-2">
              {roles.map((role) => (
                <div key={role.role} className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                  <p className="font-semibold text-slate-950">{role.role}</p>
                  <p className="mt-1 text-sm text-slate-500">{role.access}</p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel icon={Languages} title="Language Settings">
            <div className="flex flex-wrap gap-2">
              {["English", "Arabic", "French", "Arabizi"].map((language) => (
                <Button key={language} variant={language === "English" ? "primary" : "secondary"}>
                  {language}
                </Button>
              ))}
            </div>
          </Panel>
        </div>
      </section>
    </div>
  );
}

function Panel({
  icon: Icon,
  title,
  children,
}: {
  icon: typeof Building2;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <Card className="rounded-[30px] p-6">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <IconBadge icon={Icon} tone="blue" />
          <div>
            <h3 className="text-xl font-bold tracking-[-0.02em] text-[#0F172A]">
              {title}
            </h3>
            <p className="text-sm font-medium text-[#64748B]">
              Review summary and configure defaults.
            </p>
          </div>
        </div>
        <Button variant="secondary">Configure</Button>
      </div>
      {children}
    </Card>
  );
}

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-[22px] bg-slate-50/80 p-4">
      <h4 className="font-bold text-[#0F172A]">{title}</h4>
      <div className="mt-3 flex flex-wrap gap-2">
        {items.map((item) => (
          <span
            key={item}
            className="rounded-full bg-white px-3 py-1 text-sm font-semibold text-slate-700 ring-1 ring-slate-200"
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

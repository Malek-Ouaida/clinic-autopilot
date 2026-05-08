import { CalendarPlus, MessageCircle, PackageCheck, Repeat } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconBadge } from "@/components/ui/IconBadge";
import { packages } from "@/data/mock-data";

export function PackagesScreen() {
  return (
    <div>
      <PageHeader
        eyebrow="Packages"
        title="Which sessions and packages need action?"
        subtitle="Track purchased, completed, and remaining sessions while drafting reminders and renewal messages at the right time."
      />

      <section className="hero-surface mb-6 rounded-[34px] p-7">
        <div className="grid gap-6 xl:grid-cols-[1fr_420px] xl:items-center">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#2563EB]">
              Session intelligence
            </p>
            <h3 className="mt-3 max-w-3xl text-[36px] font-bold leading-[40px] tracking-[-0.05em] text-[#0F172A]">
              Every package has a next best action.
            </h3>
            <p className="mt-3 max-w-2xl text-[15px] font-medium leading-7 text-[#64748B]">
              Session counts, due dates, and renewal prompts stay visible before
              patients drift away.
            </p>
          </div>
          <div className="rounded-[26px] bg-white/76 p-5 ring-1 ring-slate-900/[0.06]">
            <p className="text-[34px] font-bold leading-9 tracking-[-0.055em] text-[#0F172A]">
              10
            </p>
            <p className="mt-2 text-xs font-bold uppercase tracking-[0.12em] text-[#64748B]">
              sessions remaining across active plans
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        {packages.map((plan) => {
          const progress = Math.round((plan.completed / plan.purchased) * 100);
          return (
            <Card key={plan.id} className="rounded-[30px] p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-xl font-bold tracking-[-0.02em] text-[#0F172A]">
                    {plan.name}
                  </h3>
                  <p className="mt-1 text-sm font-medium text-[#64748B]">
                    {plan.patient}
                  </p>
                </div>
                <IconBadge icon={PackageCheck} tone="teal" />
              </div>

              <div className="mt-6">
                <div className="flex items-end justify-between">
                  <p className="text-4xl font-bold tracking-[-0.04em] text-[#0F172A]">
                    {plan.remaining}
                  </p>
                  <p className="text-sm font-semibold text-[#64748B]">remaining</p>
                </div>
                <div className="mt-4 h-2 rounded-full bg-slate-100">
                  <div
                    className="h-2 rounded-full bg-gradient-to-r from-[#2563EB] to-[#14B8A6]"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="mt-3 text-sm font-medium text-[#64748B]">
                  {plan.purchased} sessions purchased · {plan.completed} completed
                </p>
              </div>

              <div className="mt-5 rounded-[22px] bg-slate-50/80 p-4 ring-1 ring-slate-900/[0.06]">
                <p className="text-sm font-bold text-[#0F172A]">
                  Next session due: {plan.nextDue}
                </p>
                <p className="mt-2 text-sm font-medium leading-6 text-[#64748B]">
                  {plan.note}
                </p>
                {plan.remaining <= 1 ? (
                  <Badge status="high-risk" className="mt-3">
                    Low-session alert
                  </Badge>
                ) : null}
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                <Button variant="primary">
                  <CalendarPlus className="h-4 w-4" />
                  Book next session
                </Button>
                <Button variant="secondary">
                  <MessageCircle className="h-4 w-4" />
                  Send reminder
                </Button>
                <Button variant="secondary">
                  <Repeat className="h-4 w-4" />
                  Draft renewal
                </Button>
              </div>
            </Card>
          );
        })}
      </section>
    </div>
  );
}

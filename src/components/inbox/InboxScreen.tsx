import {
  Bot,
  Check,
  MessageCircle,
  Pencil,
  PhoneCall,
  UserCheck,
  X,
} from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { IconBadge } from "@/components/ui/IconBadge";
import { SegmentedControl } from "@/components/ui/SegmentedControl";
import { inboxThreads, outboundApprovals } from "@/data/mock-data";

const deliveryToStatus = {
  Sent: "completed",
  Delivered: "completed",
  Read: "completed",
  Failed: "high-risk",
  Replied: "follow-up",
  "No reply": "unconfirmed",
} as const;

export function InboxScreen() {
  const activeThread = inboxThreads[0];

  return (
    <div>
      <PageHeader
        eyebrow="Inbox"
        title="WhatsApp Inbox"
        subtitle="Patient replies become intent, suggested action, and a safe message ready for approval."
      />

      <section className="hero-surface mb-6 rounded-[34px] p-7">
        <div className="grid gap-6 xl:grid-cols-[1fr_420px] xl:items-center">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#2563EB]">
              AI message desk
            </p>
            <h3 className="mt-3 max-w-3xl text-[36px] font-bold leading-[40px] tracking-[-0.05em] text-[#0F172A]">
              The system understands the reply before the clinic loses the slot.
            </h3>
            <p className="mt-3 max-w-2xl text-[15px] font-medium leading-7 text-[#64748B]">
              Arabizi, Arabic, English, and French replies are translated into
              safe next actions for the secretary.
            </p>
          </div>
          <div className="rounded-[28px] bg-[#0F172A] p-5 text-white shadow-[0_22px_52px_rgba(15,23,42,0.18)]">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-300">
              Live example
            </p>
            <p className="mt-3 text-xl font-bold leading-8 tracking-[-0.025em]">
              “ma fine eje lyom, fine bukra?”
            </p>
            <div className="mt-4 flex items-center justify-between rounded-2xl bg-white/10 px-3 py-2 ring-1 ring-white/10">
              <span className="text-sm font-semibold text-slate-300">
                Detected intent
              </span>
              <span className="text-sm font-bold text-emerald-300">Reschedule</span>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[380px_1fr]">
        <Card className="rounded-[30px] p-5">
          <SegmentedControl
            options={["All", "Needs action", "Reschedule"]}
            active="Needs action"
          />
          <div className="mt-5 space-y-3">
          {inboxThreads.map((thread) => (
            <article
              key={thread.id}
              className={`premium-transition rounded-[22px] border p-4 ${
                thread.id === activeThread.id
                  ? "border-blue-200 bg-blue-50/70"
                  : "border-slate-900/[0.08] bg-white hover:bg-slate-50"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-bold text-[#0F172A]">{thread.patient}</h3>
                  <p className="mt-1 line-clamp-2 text-sm font-medium leading-[21px] text-[#64748B]">
                    {thread.incoming}
                  </p>
                </div>
                <Badge status={deliveryToStatus[thread.delivery]}>
                  {thread.intent}
                </Badge>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <p className="text-xs font-bold text-[#94A3B8]">{thread.appointment}</p>
                <p className="text-xs font-bold text-blue-700">
                  {thread.confidence}% confidence
                </p>
              </div>
            </article>
          ))}
          </div>
        </Card>

        <div className="space-y-6">
          <Card hero className="rounded-[30px] p-6">
            <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-600">
                  Active conversation
                </p>
                <h3 className="mt-2 text-2xl font-bold tracking-[-0.035em] text-[#0F172A]">
                  {activeThread.patient}
                </h3>
                <p className="mt-1 text-sm font-semibold text-[#64748B]">
                  {activeThread.phone} · Related appointment:{" "}
                  {activeThread.appointment}
                </p>
              </div>
              <Badge status={deliveryToStatus[activeThread.delivery]}>
                {activeThread.delivery}
              </Badge>
            </div>

            <div className="mt-6 grid gap-4 lg:grid-cols-[1fr_360px]">
              <div className="rounded-[24px] bg-white/78 p-5 ring-1 ring-slate-900/[0.08]">
                <p className="text-xs font-bold uppercase tracking-[0.14em] text-[#94A3B8]">
                  Patient message
                </p>
                <p className="mt-3 text-xl font-bold leading-8 tracking-[-0.02em] text-[#0F172A]">
                  &ldquo;{activeThread.incoming}&rdquo;
                </p>
                <div className="mt-6 flex flex-wrap gap-2">
                  {["Sent", "Delivered", "Read", "Failed", "Replied", "No reply"].map(
                    (state) => (
                      <span
                        key={state}
                        className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-bold text-[#64748B]"
                      >
                        {state}
                      </span>
                    ),
                  )}
                </div>
              </div>

              <div className="rounded-[24px] bg-blue-50 p-5 ring-1 ring-blue-100">
                <div className="flex items-center gap-3">
                  <IconBadge icon={Bot} tone="blue" />
                  <div>
                    <p className="text-xs font-bold uppercase tracking-[0.14em] text-blue-700">
                      Detected intent
                    </p>
                    <p className="text-xl font-bold text-[#0F172A]">
                      {activeThread.intent}
                    </p>
                  </div>
                </div>
                <div className="mt-5 rounded-2xl bg-white/80 p-4">
                  <p className="text-sm font-bold text-[#0F172A]">
                    Confidence: {activeThread.confidence}%
                  </p>
                  <p className="mt-1 text-sm font-medium text-[#64748B]">
                    Related appointment: {activeThread.appointment}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-5 rounded-[24px] bg-teal-50 p-5 ring-1 ring-teal-100">
              <p className="text-xs font-bold uppercase tracking-[0.14em] text-teal-700">
                Suggested action
              </p>
              <p className="mt-2 font-bold text-[#0F172A]">
                {activeThread.suggestedAction}
              </p>
              <p className="mt-4 text-xs font-bold uppercase tracking-[0.14em] text-teal-700">
                Suggested reply
              </p>
              <p className="mt-2 text-sm font-semibold leading-6 text-[#475569]">
                &ldquo;{activeThread.suggestedReply}&rdquo;
              </p>
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <Button variant="blue">
                <MessageCircle className="h-4 w-4" />
                Reply
              </Button>
              <Button variant="secondary">Reschedule</Button>
              <Button variant="secondary">
                <PhoneCall className="h-4 w-4" />
                Call
              </Button>
              <Button variant="danger">Mark cancelled</Button>
              <Button variant="secondary">
                <UserCheck className="h-4 w-4" />
                Assign
              </Button>
            </div>
          </Card>

          <Card className="rounded-[30px] p-6">
            <div className="flex items-center gap-3">
              <IconBadge icon={Bot} tone="teal" />
              <h3 className="text-xl font-bold tracking-[-0.02em] text-[#0F172A]">
                Outbound approvals
              </h3>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              {outboundApprovals.map((approval) => (
                <div
                  key={approval}
                  className="rounded-[22px] bg-white p-4 ring-1 ring-slate-900/[0.08]"
                >
                  <p className="font-bold text-[#0F172A]">{approval}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <Button variant="primary">
                      <Check className="h-4 w-4" />
                      Approve
                    </Button>
                    <Button variant="secondary">
                      <Pencil className="h-4 w-4" />
                      Edit
                    </Button>
                    <Button variant="ghost">
                      <X className="h-4 w-4" />
                      Skip
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}

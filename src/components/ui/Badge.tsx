import type { Status } from "@/types";
import { cn, statusDot, statusLabel, statusTone } from "@/lib/utils";

export function Badge({
  status,
  children,
  className,
}: {
  status: Status;
  children?: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold leading-4 ring-1",
        statusTone(status),
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", statusDot(status))} />
      {children ?? statusLabel(status)}
    </span>
  );
}

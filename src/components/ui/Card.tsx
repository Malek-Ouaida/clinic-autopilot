import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Card({
  children,
  className,
  hero = false,
}: {
  children: ReactNode;
  className?: string;
  hero?: boolean;
}) {
  return (
    <section
      className={cn(
        "premium-transition rounded-3xl p-6",
        hero ? "hero-surface rounded-[32px] p-8" : "surface",
        className,
      )}
    >
      {children}
    </section>
  );
}

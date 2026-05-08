export function PageHeader({
  eyebrow,
  title,
  subtitle,
  action,
}: {
  eyebrow?: string;
  title: string;
  subtitle: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-7 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
      <div>
        {eyebrow ? (
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-600">
            {eyebrow}
          </p>
        ) : null}
        <h2 className="mt-2 text-[34px] font-bold leading-10 tracking-[-0.035em] text-[#0F172A]">
          {title}
        </h2>
        <p className="mt-3 max-w-2xl text-base font-medium leading-6 text-[#64748B]">
          {subtitle}
        </p>
      </div>
      {action}
    </div>
  );
}

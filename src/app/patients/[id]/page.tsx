import { notFound } from "next/navigation";
import { PatientProfile } from "@/components/patients/PatientProfile";
import { patients } from "@/data/mock-data";

export function generateStaticParams() {
  return patients.map((patient) => ({ id: patient.id }));
}

export default async function PatientProfilePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const patient = patients.find((item) => item.id === id);

  if (!patient) {
    notFound();
  }

  return <PatientProfile patient={patient} />;
}

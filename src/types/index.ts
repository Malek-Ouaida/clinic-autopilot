export type Status =
  | "confirmed"
  | "unconfirmed"
  | "high-risk"
  | "follow-up"
  | "completed"
  | "cancelled"
  | "blocked"
  | "open";

export type Language = "English" | "Arabic" | "French" | "Arabizi";

export type Patient = {
  id: string;
  name: string;
  phone: string;
  nextAppointment: string;
  nextStatus: Status;
  lastVisit: string;
  followUpDue: string;
  noShows: number;
  preferredLanguage: Language;
  balance: string;
  packageStatus?: string;
  service: string;
};

export type Appointment = {
  id: string;
  time: string;
  patient: string;
  service: string;
  doctor: string;
  status: Status;
  risk?: "Low" | "Medium" | "High";
  reason?: string;
  room?: string;
};

export type MessageThread = {
  id: string;
  patient: string;
  phone: string;
  appointment: string;
  incoming: string;
  intent: string;
  confidence: number;
  suggestedAction: string;
  suggestedReply: string;
  delivery: "Sent" | "Delivered" | "Read" | "Failed" | "Replied" | "No reply";
};

export type PackagePlan = {
  id: string;
  name: string;
  patient: string;
  purchased: number;
  completed: number;
  remaining: number;
  nextDue: string;
  note: string;
};

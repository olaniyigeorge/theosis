import type { Metadata } from "next";
import AdviceExperience from "./advice_experience";

export const metadata: Metadata = {
  title: "Ask · Theosis",
  description:
    "Ask a question and receive counsel composed only from Scripture verified against a live source.",
};

export default function AdvicePage() {
  return <AdviceExperience />;
}
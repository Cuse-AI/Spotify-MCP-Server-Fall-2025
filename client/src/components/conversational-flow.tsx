import { useState } from "react";
import { QuestionDisplay } from "./question-display";
import { VibeInput } from "./vibe-input";
import { ProgressDots } from "./progress-dots";
import { LoadingState } from "./loading-state";
import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import type { UserJourney, PlaylistResponse } from "@shared/schema";

const QUESTIONS = [
  {
    id: 1,
    text: "What's Your Vibe?",
    placeholder: "an imaginary place, a feeling, a real location, where your mind wanders...",
    key: "vibe" as keyof UserJourney,
  },
  {
    id: 2,
    text: "Where are you now?...",
    placeholder: "describe your current emotional state, what you're feeling right now...",
    key: "now" as keyof UserJourney,
  },
  {
    id: 3,
    text: "...and where are you going?",
    placeholder: "where you want to be, the feeling you're chasing, your destination...",
    key: "going" as keyof UserJourney,
  },
];

interface ConversationalFlowProps {
  onComplete: (data: PlaylistResponse) => void;
}

export function ConversationalFlow({ onComplete }: ConversationalFlowProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Partial<UserJourney>>({});
  const [inputValue, setInputValue] = useState("");

  const generatePlaylistMutation = useMutation({
    mutationFn: async (journey: UserJourney) => {
      const response = await apiRequest<PlaylistResponse>(
        "POST",
        "/api/generate-playlist",
        journey
      );
      return response;
    },
    onSuccess: (data) => {
      onComplete(data);
    },
  });

  const handleSubmit = () => {
    if (!inputValue.trim()) return;

    const question = QUESTIONS[currentQuestion];
    const newAnswers = { ...answers, [question.key]: inputValue };
    setAnswers(newAnswers);

    if (currentQuestion < QUESTIONS.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setInputValue("");
    } else {
      generatePlaylistMutation.mutate(newAnswers as UserJourney);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  if (generatePlaylistMutation.isPending) {
    return <LoadingState />;
  }

  return (
    <div className="flex items-center justify-center min-h-screen px-6 py-24 md:px-8">
      <div className="w-full max-w-2xl mx-auto">
        <QuestionDisplay
          question={QUESTIONS[currentQuestion].text}
          isVisible={!generatePlaylistMutation.isPending}
        />

        <div className="mt-12">
          <VibeInput
            value={inputValue}
            onChange={setInputValue}
            onSubmit={handleSubmit}
            onKeyPress={handleKeyPress}
            placeholder={QUESTIONS[currentQuestion].placeholder}
            disabled={generatePlaylistMutation.isPending}
            data-testid="input-vibe-response"
          />
        </div>

        <ProgressDots current={currentQuestion} total={QUESTIONS.length} />
      </div>
    </div>
  );
}

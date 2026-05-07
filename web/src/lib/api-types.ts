/**
 * TypeScript mirrors of the FastAPI Pydantic response schemas.
 *
 * These types describe what the backend returns from each endpoint and
 * are used by TanStack Query / fetch wrappers throughout the app.
 */

// -------------------------------------------------------------
// Auth & Users
// -------------------------------------------------------------

export interface UserResponse {
  id: string;
  email: string;
  is_active: boolean;
  is_premium: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
}


// -------------------------------------------------------------
// Courses
// -------------------------------------------------------------

export type StepType = "theory" | "quiz" | "code";

export interface StepResponse {
  id: string;
  section_id: string;
  title: string;
  step_type: StepType;
  content_data: Record<string, unknown> | null;
  order: number;
  xp_reward: number;
}

export interface SectionWithSteps {
  id: string;
  course_id: string;
  title: string;
  order: number;
  steps: StepResponse[];
}

export interface CourseResponse {
  id: string;
  title: string;
  description: string | null;
  language: string;
}

export interface CoursePathResponse extends CourseResponse {
  sections: SectionWithSteps[];
}


// -------------------------------------------------------------
// Progress
// -------------------------------------------------------------

export interface MyPathStep {
  step_id: string;
  is_completed: boolean;
}

export interface MyPathSection {
  section_id: string;
  title: string;
  order: number;
  steps: MyPathStep[];
}

export interface MyPathResponse {
  course_id: string;
  sections: MyPathSection[];
}

export interface StepCompleteResponse {
  step_id: string;
  completed_at: string;
  xp_earned: number;
}


// -------------------------------------------------------------
// Gamification
// -------------------------------------------------------------

export interface LeaderboardEntry {
  rank: number;
  user_id: string;
  email: string;
  total_xp: number;
}

export interface LeaderboardResponse {
  entries: LeaderboardEntry[];
}

export interface CommentResponse {
  id: string;
  step_id: string;
  user_id: string;
  email: string;
  line_number: number;
  content: string;
  created_at: string;
}


// -------------------------------------------------------------
// Execution (Sandbox)
// -------------------------------------------------------------

export type SubmissionStatus = "pending" | "running" | "completed" | "failed";

export interface CodeSubmitResponse {
  submission_id: string;
  status: SubmissionStatus;
}

export interface SubmissionStatusResponse {
  submission_id: string;
  status: SubmissionStatus;
  output: string | null;
}

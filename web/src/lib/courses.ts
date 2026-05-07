/**
 * Course presentation helpers.
 *
 * Course data is now sourced from the FastAPI backend
 * (`GET /api/v1/courses/`).  This module only exposes derived
 * helpers (slug, level, tag) that the UI needs.
 */

import type { CourseResponse, StepResponse } from "./api-types";

export type CourseLevel = "Beginner" | "Intermediate" | "Advanced";


/** Generate a URL-safe slug from a course title. */
export function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[^\w\s-]/g, "")
    .trim()
    .replace(/[\s_-]+/g, "-");
}


/**
 * Infer a difficulty label from the average XP reward of a course.
 * Used purely for UI badges — the backend currently does not store
 * a level field on the course model.
 */
export function deriveLevel(course: { sections?: { steps: StepResponse[] }[] }): CourseLevel {
  const steps = course.sections?.flatMap((s) => s.steps) ?? [];
  if (steps.length === 0) return "Beginner";
  const avg = steps.reduce((sum, s) => sum + (s.xp_reward ?? 0), 0) / steps.length;
  if (avg >= 35) return "Advanced";
  if (avg >= 20) return "Intermediate";
  return "Beginner";
}


/** Sum of `xp_reward` across all steps of a course. */
export function totalCourseXp(course: { sections?: { steps: StepResponse[] }[] }): number {
  return (
    course.sections
      ?.flatMap((s) => s.steps)
      .reduce((sum, s) => sum + (s.xp_reward ?? 0), 0) ?? 0
  );
}


/** Estimated hours = step_count × 15 min, rounded up. */
export function estimateHours(course: { sections?: { steps: StepResponse[] }[] }): number {
  const steps = course.sections?.flatMap((s) => s.steps) ?? [];
  return Math.max(1, Math.ceil((steps.length * 15) / 60));
}


/** Look up a course by its slug from a list. */
export function findCourseBySlug<T extends { title: string }>(
  list: T[] | undefined,
  slug: string,
): T | undefined {
  if (!list) return undefined;
  return list.find((c) => slugify(c.title) === slug);
}


// Re-export the canonical CourseResponse type for convenience
export type { CourseResponse };

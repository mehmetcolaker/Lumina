import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/site/Reveal";
import { COURSES } from "@/lib/courses";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { useState } from "react";
import { Clock, Zap, ArrowLeft, CheckCircle2, PlayCircle, Trophy, BookOpen } from "lucide-react";

export const Route = createFileRoute("/courses/$slug")({
  component: CourseDetail,
  head: ({ params }) => {
    const c = COURSES.find((x) => x.slug === params.slug);
    return {
      meta: [
        { title: `${c?.title ?? "Course"} — Lumina` },
        { name: "description", content: c?.desc ?? "Lumina course" },
      ],
    };
  },
});

function CourseDetail() {
  const { slug } = useParams({ from: "/courses/$slug" });
  const course = COURSES.find((c) => c.slug === slug);
  const { user } = useAuth();
  const [completing, setCompleting] = useState(false);

  if (!course) {
    return (
      <Layout>
        <div className="mx-auto max-w-3xl px-6 py-24 text-center">
          <h1 className="text-3xl font-bold">Course not found</h1>
          <Link to="/courses" className="mt-4 inline-block text-primary story-link">Back to courses</Link>
        </div>
      </Layout>
    );
  }

  const lessons = Array.from({ length: 8 }, (_, i) => `Lesson ${i + 1}: ${["Intro", "Setup", "Core concepts", "Practice", "Project", "Deep dive", "Patterns", "Capstone"][i]}`);

  const complete = async () => {
    if (!user) return toast.error("Sign in to track progress");
    setCompleting(true);
    const { data: cur } = await supabase.from("user_stats").select("*").eq("id", user.id).maybeSingle();
    const newXp = (cur?.xp ?? 0) + course.xp;
    const newCompleted = (cur?.completed_courses ?? 0) + 1;
    const { error } = await supabase.from("user_stats").upsert({
      id: user.id, xp: newXp, completed_courses: newCompleted, level: Math.floor(0.5 * (1 + Math.sqrt(1 + newXp / 25))),
    });
    setCompleting(false);
    if (error) return toast.error(error.message);
    toast.success(`+${course.xp} XP earned! 🎉`);
  };

  return (
    <Layout>
      <section className="relative overflow-hidden bg-[image:var(--gradient-hero)] border-b border-border">
        <div className="absolute -top-20 right-10 h-72 w-72 rounded-full bg-primary/20 blur-3xl animate-blob" />
        <div className="relative mx-auto max-w-5xl px-6 py-16">
          <Link to="/courses" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground story-link">
            <ArrowLeft className="h-4 w-4" /> All courses
          </Link>
          <Reveal>
            <div className="mt-6 flex flex-wrap gap-2">
              <Badge variant="outline">{course.level}</Badge>
              <Badge variant="secondary">{course.tag}</Badge>
              <Badge className="bg-[image:var(--gradient-primary)] text-primary-foreground"><Zap className="mr-1 h-3 w-3" />{course.xp} XP</Badge>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <h1 className="mt-4 text-4xl sm:text-5xl font-bold tracking-tight text-foreground">{course.title}</h1>
          </Reveal>
          <Reveal delay={200}>
            <p className="mt-4 max-w-2xl text-lg text-muted-foreground">{course.desc}</p>
          </Reveal>
          <Reveal delay={300}>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button size="lg" className="bg-[image:var(--gradient-primary)] text-primary-foreground glow-on-hover">
                <PlayCircle className="mr-2 h-4 w-4" /> Start learning
              </Button>
              <Button size="lg" variant="outline" onClick={complete} disabled={completing} className="hover-scale">
                <CheckCircle2 className="mr-2 h-4 w-4" /> Mark complete (+{course.xp} XP)
              </Button>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-16 grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Reveal>
            <h2 className="text-2xl font-bold flex items-center gap-2"><BookOpen className="h-5 w-5 text-primary" /> Curriculum</h2>
          </Reveal>
          {lessons.map((l, i) => (
            <Reveal key={l} delay={i * 50}>
              <Card className="p-4 flex items-center gap-3 hover-lift cursor-pointer group">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary text-secondary-foreground font-semibold transition-all group-hover:bg-[image:var(--gradient-primary)] group-hover:text-primary-foreground group-hover:scale-110">
                  {i + 1}
                </div>
                <span className="flex-1 font-medium">{l}</span>
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">{Math.ceil(course.hours / 8)}h</span>
              </Card>
            </Reveal>
          ))}
        </div>

        <aside className="space-y-4">
          <Reveal>
            <Card className="p-6 sticky top-24 hover-lift">
              <h3 className="font-semibold flex items-center gap-2"><Trophy className="h-4 w-4 text-primary" /> Course rewards</h3>
              <div className="mt-4 space-y-3 text-sm">
                <div className="flex justify-between"><span className="text-muted-foreground">XP</span><span className="font-bold text-primary">+{course.xp}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Duration</span><span>{course.hours}h</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Lessons</span><span>{lessons.length}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Certificate</span><span>✓</span></div>
              </div>
            </Card>
          </Reveal>
        </aside>
      </section>
    </Layout>
  );
}

import { createFileRoute } from "@tanstack/react-router";
import { Layout } from "@/components/site/Layout";
import { Card } from "@/components/ui/card";
import { Reveal } from "@/components/site/Reveal";
import { Sparkles, Heart, Globe, Users, Rocket, Target } from "lucide-react";

export const Route = createFileRoute("/about")({
  component: About,
  head: () => ({
    meta: [
      { title: "About — Lumina" },
      { name: "description", content: "Lumina's mission is to light up the future of learners worldwide." },
      { property: "og:title", content: "About — Lumina" },
    ],
  }),
});

const values = [
  { icon: Heart, title: "Human-first", desc: "Designed for curious humans, not algorithms." },
  { icon: Globe, title: "Worldwide", desc: "Learners in 190+ countries, in many languages." },
  { icon: Rocket, title: "Career-driven", desc: "Skills that ship — and get you hired." },
  { icon: Users, title: "Community", desc: "Learn together. Grow together." },
  { icon: Target, title: "Practical", desc: "Hands-on projects from day one." },
  { icon: Sparkles, title: "Joyful", desc: "Learning should feel like play." },
];

function About() {
  return (
    <Layout>
      <section className="relative overflow-hidden border-b border-border bg-[image:var(--gradient-hero)]">
        <div className="absolute -top-20 left-10 h-80 w-80 rounded-full bg-primary/20 blur-3xl animate-blob" />
        <div className="absolute -bottom-20 right-10 h-80 w-80 rounded-full bg-accent/40 blur-3xl animate-blob" style={{ animationDelay: "3s" }} />
        <div className="relative mx-auto max-w-4xl px-6 py-24 text-center">
          <Reveal>
            <Sparkles className="mx-auto h-12 w-12 text-primary animate-float" />
          </Reveal>
          <Reveal delay={100}>
            <h1 className="mt-4 text-5xl sm:text-6xl font-bold tracking-tight">
              We believe in <span className="bg-[image:var(--gradient-primary)] bg-clip-text text-transparent">light</span>
            </h1>
          </Reveal>
          <Reveal delay={200}>
            <p className="mt-6 text-lg text-muted-foreground">
              Lumina was built to make world-class coding education accessible, joyful, and effective — for every curious mind on the planet.
            </p>
          </Reveal>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-20">
        <Reveal><h2 className="text-3xl font-bold text-center">What we stand for</h2></Reveal>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {values.map((v, i) => (
            <Reveal key={v.title} delay={i * 80}>
              <Card className="p-6 hover-lift glow-on-hover h-full">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[image:var(--gradient-primary)] text-primary-foreground transition-transform duration-500 hover:rotate-12 hover:scale-110">
                  <v.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-lg font-semibold">{v.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{v.desc}</p>
              </Card>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-6 pb-24">
        <Reveal>
          <Card className="p-10 text-center bg-[image:var(--gradient-primary)] text-primary-foreground border-0">
            <h2 className="text-3xl font-bold">Our mission</h2>
            <p className="mt-4 text-lg opacity-95">
              To light up the path to a fulfilling tech career — one lesson, one project, one learner at a time.
            </p>
          </Card>
        </Reveal>
      </section>
    </Layout>
  );
}

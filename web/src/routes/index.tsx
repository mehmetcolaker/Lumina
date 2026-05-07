import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Layout } from "@/components/site/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { AnimatedCounter } from "@/components/site/AnimatedCounter";
import {
  ArrowRight, Code2, Database, Brain, Globe, Smartphone, ShieldCheck,
  Star, Users, Trophy, Check, Briefcase, Sparkles, Building2, BarChart3,
  GraduationCap, Rocket, BookOpen, Award, Quote, Search,
} from "lucide-react";
import hero from "@/assets/hero.jpg";

export const Route = createFileRoute("/")({
  component: Home,
  head: () => ({
    meta: [
      { title: "Lumina — Learn to code, light up your future" },
      { name: "description", content: "Lumina offers interactive coding courses in Python, JavaScript, Web Dev, Data Science and AI. Learn by doing — at your own pace." },
    ],
  }),
});

const tracks = [
  { icon: Code2, title: "Web Development", desc: "HTML, CSS, JavaScript, React" },
  { icon: Database, title: "Data Science", desc: "Python, SQL, Pandas, ML" },
  { icon: Brain, title: "AI & Machine Learning", desc: "PyTorch, LLMs, Neural Nets" },
  { icon: Globe, title: "Computer Science", desc: "Algorithms, Data Structures" },
  { icon: Smartphone, title: "Mobile Development", desc: "React Native, Swift, Kotlin" },
  { icon: ShieldCheck, title: "Cybersecurity", desc: "Networks, Ethical Hacking" },
];

const stats = [
  { icon: Users, num: 50_000_000, suffix: "+", label: "Learners worldwide" },
  { icon: Trophy, num: 600, suffix: "+", label: "Courses & paths" },
  { icon: Star, num: 0, suffix: "", label: "Average rating", display: "4.8/5" },
];

const courses = [
  { title: "Learn Python 3", level: "Beginner", hours: 25, tag: "Python" },
  { title: "Learn JavaScript", level: "Beginner", hours: 20, tag: "JavaScript" },
  { title: "Learn React", level: "Intermediate", hours: 18, tag: "Web Dev" },
  { title: "Data Science Foundations", level: "Beginner", hours: 30, tag: "Data" },
  { title: "ML with PyTorch", level: "Advanced", hours: 40, tag: "AI" },
  { title: "SQL Essentials", level: "Beginner", hours: 12, tag: "Data" },
  { title: "Build APIs with Node.js", level: "Intermediate", hours: 22, tag: "Backend" },
  { title: "Intro to Cybersecurity", level: "Beginner", hours: 15, tag: "Security" },
  { title: "iOS with Swift", level: "Intermediate", hours: 28, tag: "Mobile" },
];

const paths = [
  { title: "Front-End Engineer", months: 6, courses: 12 },
  { title: "Full-Stack Engineer", months: 9, courses: 18 },
  { title: "Data Scientist", months: 8, courses: 15 },
  { title: "AI Engineer", months: 10, courses: 20 },
];

const plans = [
  { name: "Basic", price: "Free", desc: "Perfect to get started.", features: ["100+ free courses", "Practice exercises", "Community support"], cta: "Start free" },
  { name: "Plus", price: "$24.99/mo", desc: "Best for serious learners.", features: ["All courses & paths", "Real-world projects", "Certificates", "AI tutor"], cta: "Try Plus", featured: true },
  { name: "Pro", price: "$39.99/mo", desc: "For career switchers.", features: ["Everything in Plus", "Interview prep", "Job-ready portfolio", "Priority support"], cta: "Go Pro" },
];

const testimonials = [
  { name: "Maya R.", role: "Front-End Developer", quote: "Lumina took me from zero to hired in 7 months. The projects made all the difference." },
  { name: "Daniel K.", role: "Data Analyst", quote: "The interactive lessons feel like a real classroom. I actually look forward to studying." },
  { name: "Aisha P.", role: "AI Engineer", quote: "The AI path is rigorous and practical. I deployed real models by week three." },
];

const steps = [
  { icon: GraduationCap, title: "Pick a path", desc: "Choose from 600+ courses & career paths." },
  { icon: BookOpen, title: "Learn by doing", desc: "Code in your browser with instant feedback." },
  { icon: Rocket, title: "Build projects", desc: "Real-world projects for your portfolio." },
  { icon: Award, title: "Earn certificates", desc: "Show employers what you've mastered." },
];

const faqs = [
  { q: "Do I need experience to start?", a: "No — most courses begin from absolute beginner level with zero setup needed." },
  { q: "How long does a career path take?", a: "Most learners complete a path in 6–10 months studying ~10 hours per week." },
  { q: "Are certificates recognized?", a: "Yes, our certificates are recognized by 1,000+ hiring partners worldwide." },
  { q: "Can I cancel anytime?", a: "Absolutely. Cancel your subscription at any time from your account settings." },
];

function Home() {
  const [query, setQuery] = useState("");
  const [tag, setTag] = useState<string>("All");
  const tags = useMemo(() => ["All", ...Array.from(new Set(courses.map((c) => c.tag)))], []);
  const filtered = useMemo(
    () => courses.filter((c) => (tag === "All" || c.tag === tag) && c.title.toLowerCase().includes(query.toLowerCase())),
    [query, tag],
  );
  return (
    <Layout>
      {/* Hero */}
      <section id="home" className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[image:var(--gradient-hero)] opacity-70" />
        <div className="pointer-events-none absolute -top-20 -left-20 h-72 w-72 rounded-full bg-primary/30 blur-3xl animate-blob" />
        <div className="pointer-events-none absolute top-40 -right-20 h-80 w-80 rounded-full bg-primary-glow/40 blur-3xl animate-blob" style={{ animationDelay: "3s" }} />
        <div className="relative mx-auto grid max-w-7xl gap-12 px-6 py-20 md:grid-cols-2 md:py-28">
          <div className="flex flex-col justify-center">
            <span className="mb-4 inline-flex w-fit items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-primary animate-fade-in-up hover-scale">
              ✨ New: AI Engineer Career Path
            </span>
            <h1 className="text-4xl font-bold tracking-tight text-foreground md:text-6xl animate-fade-in-up delay-100">
              Learn to code, <span className="bg-[image:var(--gradient-primary)] bg-clip-text text-transparent">light up</span> your future.
            </h1>
            <p className="mt-6 max-w-lg text-lg text-muted-foreground animate-fade-in-up delay-200">
              Interactive lessons, real projects, and career paths that take you from beginner to job-ready — all in your browser.
            </p>
            <div className="mt-8 flex flex-wrap gap-3 animate-fade-in-up delay-300">
              <Button size="lg" asChild className="group bg-[image:var(--gradient-primary)] text-primary-foreground shadow-[var(--shadow-soft)] transition-all hover:opacity-90 hover:-translate-y-0.5 glow-on-hover">
                <Link to="/courses">Start learning free <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" /></Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="hover-scale">
                <Link to="/leaderboard">View leaderboard</Link>
              </Button>
            </div>
            <div className="mt-10 flex gap-8 animate-fade-in-up delay-500">
              {stats.map((s) => (
                <div key={s.label} className="hover-scale cursor-default">
                  <div className="text-2xl font-bold text-foreground">
                    {s.display ?? <AnimatedCounter value={s.num} suffix={s.suffix} />}
                  </div>
                  <div className="text-xs text-muted-foreground">{s.label}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="relative animate-scale-in delay-200">
            <div className="absolute inset-0 rounded-2xl bg-[image:var(--gradient-primary)] opacity-30 blur-2xl animate-float" />
            <img src={hero} alt="Lumina interactive learning" className="relative rounded-2xl shadow-[var(--shadow-card)] animate-float" />
          </div>
        </div>
      </section>

      {/* Logos / trusted by */}
      <section className="border-y border-border bg-card/50 py-10">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Trusted by learners at</p>
          <div className="mt-6 grid grid-cols-3 gap-6 text-sm font-bold text-foreground/60 md:grid-cols-6">
            {["Google", "Meta", "Amazon", "Microsoft", "Netflix", "Spotify"].map((b) => (
              <div key={b} className="hover-scale transition-colors hover:text-foreground">{b}</div>
            ))}
          </div>
        </div>
      </section>

      {/* Tracks */}
      <section id="tracks" className="mx-auto max-w-7xl px-6 py-20">
        <div className="mb-12 text-center animate-fade-in-up">
          <h2 className="text-3xl font-bold text-foreground md:text-4xl">Explore learning tracks</h2>
          <p className="mt-3 text-muted-foreground">Find the right path for your goals.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {tracks.map((t, i) => (
            <Card
              key={t.title}
              className="group cursor-pointer border-border p-6 hover-lift glow-on-hover animate-fade-in-up"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent text-primary transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                <t.icon className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">{t.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{t.desc}</p>
              <div className="mt-4 flex items-center text-sm font-medium text-primary">
                Explore <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-2" />
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-secondary/40 py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-12 text-center animate-fade-in-up">
            <h2 className="text-3xl font-bold text-foreground md:text-4xl">How Lumina works</h2>
            <p className="mt-3 text-muted-foreground">Four steps from curious to confident.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-4">
            {steps.map((s, i) => (
              <Card key={s.title} className="border-border p-6 hover-lift animate-fade-in-up" style={{ animationDelay: `${i * 100}ms` }}>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[image:var(--gradient-primary)] text-primary-foreground">
                  <s.icon className="h-6 w-6" />
                </div>
                <div className="mt-4 text-xs font-semibold text-primary">STEP {i + 1}</div>
                <h3 className="mt-1 text-lg font-semibold text-foreground">{s.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{s.desc}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Catalog */}
      <section id="catalog" className="mx-auto max-w-7xl px-6 py-20">
        <div className="mb-8 flex flex-col items-start justify-between gap-4 md:flex-row md:items-end">
          <div className="animate-fade-in-up">
            <h2 className="text-3xl font-bold text-foreground md:text-4xl">Course catalog</h2>
            <p className="mt-3 text-muted-foreground">Hands-on courses crafted by industry experts.</p>
          </div>
          <Button variant="outline" className="hover-scale">View all 600+ courses</Button>
        </div>

        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search courses…"
              className="pl-9"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {tags.map((t) => (
              <button
                key={t}
                onClick={() => setTag(t)}
                className={`rounded-full border px-3 py-1 text-xs font-medium transition-all hover-scale ${
                  tag === t
                    ? "border-primary bg-[image:var(--gradient-primary)] text-primary-foreground"
                    : "border-border bg-card text-muted-foreground hover:text-foreground"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <p className="py-12 text-center text-sm text-muted-foreground">No courses match your search.</p>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filtered.map((c, i) => (
              <Card
                key={c.title}
                className="group border-border p-6 hover-lift glow-on-hover animate-fade-in-up"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <div className="flex items-center justify-between">
                  <Badge variant="secondary" className="bg-accent text-accent-foreground transition-transform group-hover:scale-105">{c.tag}</Badge>
                  <span className="text-xs text-muted-foreground">{c.hours}h</span>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-foreground">{c.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{c.level} · Self-paced</p>
                <button className="story-link mt-4 text-sm font-medium text-primary">Start course →</button>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Career paths */}
      <section id="paths" className="bg-secondary/40 py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-12 text-center animate-fade-in-up">
            <h2 className="text-3xl font-bold text-foreground md:text-4xl">Career paths</h2>
            <p className="mt-3 text-muted-foreground">Step-by-step roadmaps built with hiring managers.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {paths.map((p, i) => (
              <Card
                key={p.title}
                className="group border-border p-8 hover-lift glow-on-hover animate-fade-in-up"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent text-primary transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6">
                  <Briefcase className="h-6 w-6" />
                </div>
                <h3 className="mt-4 text-xl font-semibold text-foreground">{p.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{p.courses} courses · ~{p.months} months</p>
                <div className="mt-4 flex items-center text-sm font-medium text-primary">
                  View roadmap <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-2" />
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Why Lumina */}
      <section className="mx-auto grid max-w-7xl gap-12 px-6 py-20 md:grid-cols-2">
        <div className="animate-fade-in-up">
          <h2 className="text-3xl font-bold text-foreground md:text-4xl">Why learners choose Lumina</h2>
          <p className="mt-4 text-muted-foreground">
            Our hands-on platform combines bite-sized lessons, real-world projects, and AI-powered guidance so you actually learn — and remember — what matters.
          </p>
          <ul className="mt-6 space-y-3 text-sm text-foreground">
            {["Code in your browser — no setup", "Real projects for your portfolio", "AI tutor available 24/7", "Industry-recognized certificates"].map((i) => (
              <li key={i} className="flex items-start gap-2 hover-scale">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary" /> {i}
              </li>
            ))}
          </ul>
        </div>
        <Card className="border-border bg-card p-8 shadow-[var(--shadow-card)] hover-lift animate-scale-in">
          <div className="rounded-lg bg-foreground p-4 font-mono text-xs text-background">
            <div className="text-primary-glow">// lumina.js</div>
            <div><span className="text-primary-glow">function</span> learn() {`{`}</div>
            <div className="pl-4">return <span className="text-primary-glow">'progress'</span>;</div>
            <div>{`}`}</div>
          </div>
          <div className="mt-6">
            <div className="text-sm font-semibold text-foreground">Lesson 3 of 12 · JavaScript Basics</div>
            <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-muted">
              <div className="h-full w-1/4 rounded-full bg-[image:var(--gradient-primary)]" />
            </div>
          </div>
        </Card>
      </section>

      {/* Testimonials */}
      <section className="bg-secondary/40 py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-12 text-center animate-fade-in-up">
            <h2 className="text-3xl font-bold text-foreground md:text-4xl">Loved by millions of learners</h2>
            <p className="mt-3 text-muted-foreground">Real stories from people who changed their careers.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {testimonials.map((t, i) => (
              <Card key={t.name} className="border-border p-6 hover-lift animate-fade-in-up" style={{ animationDelay: `${i * 100}ms` }}>
                <Quote className="h-6 w-6 text-primary" />
                <p className="mt-3 text-sm text-foreground">"{t.quote}"</p>
                <div className="mt-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-sm font-bold text-primary-foreground">
                    {t.name.charAt(0)}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-foreground">{t.name}</div>
                    <div className="text-xs text-muted-foreground">{t.role}</div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="mx-auto max-w-7xl px-6 py-20">
        <div className="mb-12 text-center animate-fade-in-up">
          <h2 className="text-3xl font-bold text-foreground md:text-4xl">Simple, transparent pricing</h2>
          <p className="mt-3 text-muted-foreground">Start free. Upgrade when you're ready.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {plans.map((p, i) => (
            <Card
              key={p.name}
              className={`flex flex-col border-border p-8 hover-lift animate-fade-in-up ${p.featured ? "border-primary shadow-[var(--shadow-soft)] ring-2 ring-primary/30 md:-translate-y-2" : ""}`}
              style={{ animationDelay: `${i * 100}ms` }}
            >
              {p.featured && <Badge className="mb-3 w-fit bg-[image:var(--gradient-primary)] text-primary-foreground">Most popular</Badge>}
              <h3 className="text-lg font-semibold text-foreground">{p.name}</h3>
              <div className="mt-2 text-4xl font-bold text-foreground">{p.price}</div>
              <p className="mt-2 text-sm text-muted-foreground">{p.desc}</p>
              <ul className="mt-6 flex-1 space-y-3 text-sm">
                {p.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-foreground">
                    <Check className="mt-0.5 h-4 w-4 text-primary" /> {f}
                  </li>
                ))}
              </ul>
              <Button className={`mt-8 transition-all hover:-translate-y-0.5 ${p.featured ? "bg-[image:var(--gradient-primary)] text-primary-foreground hover:opacity-90" : ""}`} variant={p.featured ? "default" : "outline"}>
                {p.cta}
              </Button>
            </Card>
          ))}
        </div>
      </section>

      {/* For business */}
      <section id="business" className="bg-[image:var(--gradient-hero)] py-20">
        <div className="mx-auto grid max-w-7xl gap-10 px-6 md:grid-cols-2 md:items-center">
          <div className="animate-fade-in-up">
            <Badge className="mb-3 bg-card text-primary">For Business</Badge>
            <h2 className="text-3xl font-bold text-foreground md:text-4xl">Upskill your whole team</h2>
            <p className="mt-4 text-muted-foreground">Hands-on tech training trusted by 1,000+ companies. SSO, analytics, custom paths and SOC 2 compliance.</p>
            <div className="mt-6 flex gap-3">
              <Button size="lg" className="bg-[image:var(--gradient-primary)] text-primary-foreground shadow-[var(--shadow-soft)] hover:opacity-90 hover:-translate-y-0.5 transition-all">Request a demo</Button>
              <Button size="lg" variant="outline" className="hover-scale">Talk to sales</Button>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 animate-scale-in">
            {[
              { icon: Users, title: "Team management" },
              { icon: BarChart3, title: "Skill analytics" },
              { icon: ShieldCheck, title: "Enterprise security" },
              { icon: Building2, title: "Custom learning" },
            ].map((f) => (
              <Card key={f.title} className="border-border p-5 hover-lift">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-primary">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-3 text-sm font-semibold text-foreground">{f.title}</h3>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="mx-auto max-w-4xl px-6 py-20">
        <div className="mb-12 text-center animate-fade-in-up">
          <h2 className="text-3xl font-bold text-foreground md:text-4xl">Frequently asked questions</h2>
        </div>
        <Accordion type="single" collapsible className="space-y-3">
          {faqs.map((f, i) => (
            <AccordionItem key={f.q} value={`item-${i}`} className="rounded-lg border border-border bg-card px-6 animate-fade-in-up" style={{ animationDelay: `${i * 80}ms` }}>
              <AccordionTrigger className="text-left text-base font-semibold text-foreground hover:no-underline">
                {f.q}
              </AccordionTrigger>
              <AccordionContent className="text-sm text-muted-foreground">{f.a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden bg-[image:var(--gradient-primary)] py-20 text-center">
        <div className="pointer-events-none absolute -top-10 left-1/4 h-72 w-72 rounded-full bg-white/20 blur-3xl animate-blob" />
        <div className="relative mx-auto max-w-3xl px-6">
          <Sparkles className="mx-auto h-10 w-10 text-primary-foreground animate-float" />
          <h2 className="mt-4 text-3xl font-bold text-primary-foreground md:text-4xl">Ready to start your journey?</h2>
          <p className="mt-3 text-primary-foreground/90">Join millions learning with Lumina — free to start, forever.</p>
          <Button size="lg" variant="secondary" className="mt-8 hover-scale shadow-lg">
            Create free account <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </section>
    </Layout>
  );
}

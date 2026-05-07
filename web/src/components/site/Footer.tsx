import { Sparkles } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export function Footer() {
  const cols = [
    { title: "Learn", items: ["Catalog", "Career Paths", "Free Courses", "Projects"] },
    { title: "Company", items: ["About", "Careers", "Blog", "Press"] },
    { title: "Support", items: ["Help Center", "Community", "Contact", "Status"] },
    { title: "Legal", items: ["Terms", "Privacy", "Cookies", "Security"] },
  ];
  const [email, setEmail] = useState("");
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    toast.success("Thanks for subscribing!");
    setEmail("");
  };
  return (
    <footer className="border-t border-border bg-secondary/40">
      <div className="mx-auto max-w-7xl px-6 py-14">
        <div className="grid gap-10 md:grid-cols-2">
          <div>
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[image:var(--gradient-primary)] text-primary-foreground">
                <Sparkles className="h-4 w-4" />
              </div>
              <span className="text-lg font-bold text-foreground">Lumina</span>
            </div>
            <p className="mt-3 text-sm text-muted-foreground">Light up your skills.</p>
          </div>
          <div>
            <h4 className="mb-3 text-sm font-semibold text-foreground">Get the newsletter</h4>
            <p className="mb-3 text-sm text-muted-foreground">Tips, new courses, and learner stories — once a week.</p>
            <form onSubmit={submit} className="flex gap-2">
              <Input type="email" required placeholder="you@email.com" value={email} onChange={(e) => setEmail(e.target.value)} />
              <Button type="submit" className="bg-[image:var(--gradient-primary)] text-primary-foreground hover:opacity-90">Subscribe</Button>
            </form>
          </div>
        </div>
        <div className="mt-10 grid gap-8 md:grid-cols-4">
          {cols.map((c) => (
            <div key={c.title}>
              <h4 className="mb-3 text-sm font-semibold text-foreground">{c.title}</h4>
              <ul className="space-y-2">
                {c.items.map((i) => (
                  <li key={i}><a className="text-sm text-muted-foreground hover:text-foreground" href="#">{i}</a></li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
      <div className="border-t border-border px-6 py-6 text-center text-xs text-muted-foreground">
        © {new Date().getFullYear()} Lumina. All rights reserved.
      </div>
    </footer>
  );
}

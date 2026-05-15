import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Layout } from "@/components/site/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import type { CheckoutResponse } from "@/lib/api-types";
import { toast } from "sonner";

export const Route = createFileRoute("/pricing")({
  component: PricingPage,
  head: () => ({ meta: [{ title: "Pricing — Lumina" }] }),
});

const plans = [
  {
    name: "Basic",
    price: "Free",
    desc: "Start with previews and free lessons.",
    features: ["Preview lessons", "Practice exercises", "Progress dashboard"],
    cta: "Start free",
  },
  {
    name: "Plus",
    price: "$24.99/mo",
    desc: "Full access for serious learners.",
    features: [
      "All courses and paths",
      "Certificates",
      "Submission history",
      "Priority practice updates",
    ],
    cta: "Try Plus",
    featured: true,
  },
];

function PricingPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);

  const checkout = async () => {
    if (!user) {
      window.location.href = "/signup";
      return;
    }
    setLoading(true);
    try {
      const res = await api.post<CheckoutResponse>("/monetization/checkout");
      window.location.href = res.checkout_url;
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Checkout could not be started.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <section className="mx-auto max-w-5xl px-6 py-16">
        <h1 className="text-4xl font-bold">Pricing</h1>
        <p className="mt-3 text-muted-foreground">
          Start free, then upgrade when you need the full roadmap.
        </p>
        <div className="mt-10 grid gap-6 md:grid-cols-2">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`p-8 ${plan.featured ? "border-primary ring-2 ring-primary/30" : ""}`}
            >
              {plan.featured && (
                <Badge className="mb-3 bg-[image:var(--gradient-primary)] text-primary-foreground">
                  Popular
                </Badge>
              )}
              <h2 className="text-xl font-semibold">{plan.name}</h2>
              <div className="mt-2 text-4xl font-bold">{plan.price}</div>
              <p className="mt-2 text-sm text-muted-foreground">{plan.desc}</p>
              <ul className="mt-6 space-y-3 text-sm">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2">
                    <Check className="mt-0.5 h-4 w-4 text-primary" />
                    {feature}
                  </li>
                ))}
              </ul>
              {plan.name === "Basic" ? (
                <Button className="mt-8 w-full" variant="outline" asChild>
                  <Link to="/signup">{plan.cta}</Link>
                </Button>
              ) : (
                <Button
                  className="mt-8 w-full bg-[image:var(--gradient-primary)] text-primary-foreground"
                  onClick={checkout}
                  disabled={loading}
                >
                  {loading ? "Starting..." : plan.cta}
                </Button>
              )}
            </Card>
          ))}
        </div>
      </section>
    </Layout>
  );
}

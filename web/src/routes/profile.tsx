import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { Layout } from "@/components/site/Layout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { LogOut, Mail, Star, ShieldCheck } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/profile")({
  component: ProfilePage,
  head: () => ({ meta: [{ title: "Profile — Lumina" }] }),
});

function ProfilePage() {
  const { user, loading: authLoading, signOut } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!authLoading && !user) navigate({ to: "/login" });
  }, [user, authLoading, navigate]);

  const handleSignOut = async () => {
    await signOut();
    toast.success("Signed out");
    navigate({ to: "/" });
  };

  if (authLoading) {
    return (
      <Layout>
        <div className="p-12 text-center text-muted-foreground">Loading…</div>
      </Layout>
    );
  }

  if (!user) return null;

  return (
    <Layout>
      <div className="mx-auto max-w-2xl px-6 py-12">
        <h1 className="text-3xl font-bold text-foreground">Your profile</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Manage your Lumina account.
        </p>

        <Card className="mt-8 p-8 animate-fade-in-up">
          <div className="flex items-center gap-4">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-2xl font-bold text-primary-foreground">
              {user.email.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="text-lg font-semibold text-foreground">
                {user.email.split("@")[0]}
              </div>
              <div className="text-sm text-muted-foreground flex items-center gap-1">
                <Mail className="h-3 w-3" /> {user.email}
              </div>
            </div>
          </div>

          <div className="mt-8 space-y-3">
            <div className="flex items-center justify-between border-t border-border pt-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                <span className="text-sm text-muted-foreground">Account status</span>
              </div>
              <Badge variant={user.is_active ? "secondary" : "outline"}>
                {user.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
            <div className="flex items-center justify-between border-t border-border pt-4">
              <div className="flex items-center gap-2">
                <Star className="h-4 w-4 text-amber-500" />
                <span className="text-sm text-muted-foreground">Subscription</span>
              </div>
              <Badge
                className={
                  user.is_premium
                    ? "bg-[image:var(--gradient-primary)] text-primary-foreground"
                    : ""
                }
                variant={user.is_premium ? "default" : "outline"}
              >
                {user.is_premium ? "Premium" : "Free"}
              </Badge>
            </div>
            {user.is_superuser && (
              <div className="flex items-center justify-between border-t border-border pt-4">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-primary" />
                  <span className="text-sm text-muted-foreground">Role</span>
                </div>
                <Badge variant="default">Admin</Badge>
              </div>
            )}
            <div className="flex items-center justify-between border-t border-border pt-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Joined</span>
              </div>
              <span className="text-sm">
                {new Date(user.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          <div className="mt-8 border-t border-border pt-6">
            <Button onClick={handleSignOut} variant="outline" className="w-full">
              <LogOut className="mr-2 h-4 w-4" />
              Sign out
            </Button>
          </div>
        </Card>
      </div>
    </Layout>
  );
}

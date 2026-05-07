import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Layout } from "@/components/site/Layout";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { useAuth } from "@/hooks/useAuth";

export const Route = createFileRoute("/profile")({
  component: ProfilePage,
  head: () => ({ meta: [{ title: "Profile — Lumina" }] }),
});

function ProfilePage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [bio, setBio] = useState("");

  useEffect(() => {
    if (!authLoading && !user) navigate({ to: "/login" });
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (!user) return;
    (async () => {
      const { data } = await supabase.from("profiles").select("*").eq("id", user.id).maybeSingle();
      if (data) {
        setUsername(data.username ?? "");
        setDisplayName(data.display_name ?? "");
        setAvatarUrl(data.avatar_url ?? "");
        setBio(data.bio ?? "");
      }
      setLoading(false);
    })();
  }, [user]);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setSaving(true);
    const { error } = await supabase
      .from("profiles")
      .upsert({ id: user.id, username: username || null, display_name: displayName, avatar_url: avatarUrl, bio });
    setSaving(false);
    if (error) return toast.error(error.message);
    toast.success("Profile updated");
  };

  if (authLoading || loading) return <Layout><div className="p-12 text-center text-muted-foreground">Loading…</div></Layout>;

  return (
    <Layout>
      <div className="mx-auto max-w-2xl px-6 py-12">
        <h1 className="text-3xl font-bold text-foreground">Your profile</h1>
        <p className="mt-2 text-sm text-muted-foreground">{user?.email}</p>

        <Card className="mt-8 p-8 animate-fade-in-up">
          <div className="flex items-center gap-4">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-2xl font-bold text-primary-foreground overflow-hidden">
              {avatarUrl ? <img src={avatarUrl} alt="" className="h-full w-full object-cover" /> : (displayName || user?.email || "?").charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="text-lg font-semibold text-foreground">{displayName || "Unnamed"}</div>
              {username && <div className="text-sm text-muted-foreground">@{username}</div>}
            </div>
          </div>

          <form onSubmit={save} className="mt-8 space-y-4">
            <div>
              <Label htmlFor="display">Display name</Label>
              <Input id="display" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
            </div>
            <div>
              <Label htmlFor="username">Username</Label>
              <Input id="username" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="lumina-fan" />
            </div>
            <div>
              <Label htmlFor="avatar">Avatar URL</Label>
              <Input id="avatar" value={avatarUrl} onChange={(e) => setAvatarUrl(e.target.value)} placeholder="https://…" />
            </div>
            <div>
              <Label htmlFor="bio">Bio</Label>
              <Textarea id="bio" rows={4} value={bio} onChange={(e) => setBio(e.target.value)} />
            </div>
            <Button type="submit" disabled={saving} className="bg-[image:var(--gradient-primary)] text-primary-foreground hover:opacity-90">
              {saving ? "Saving…" : "Save changes"}
            </Button>
          </form>
        </Card>
      </div>
    </Layout>
  );
}

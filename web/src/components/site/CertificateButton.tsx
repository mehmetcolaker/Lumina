/**
 * Certificate download button component.
 *
 * Calls GET /api/v1/certificates/{course_id} to download a PDF.
 */

import { Button } from "@/components/ui/button";
import { tokenStorage, API_URL } from "@/lib/api";
import { useState } from "react";
import { FileText, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface Props {
  courseId: string;
  courseTitle: string;
}

export function CertificateButton({ courseId, courseTitle }: Props) {
  const [loading, setLoading] = useState(false);

  const download = async () => {
    setLoading(true);
    try {
      const token = tokenStorage.get();
      if (!token) {
        toast.error("Please sign in first.");
        return;
      }
      const response = await fetch(
        `${API_URL}/certificates/${courseId}`,
        { headers: { Authorization: `Bearer ${token}` } },
      );

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        toast.error((data as { detail?: string }).detail ?? "Failed to download certificate.");
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `certificate-${courseTitle.toLowerCase().replace(/\s+/g, "-")}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Certificate downloaded!");
    } catch {
      toast.error("Failed to download certificate.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      onClick={download}
      disabled={loading}
      variant="outline"
      className="hover-scale"
    >
      {loading ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : (
        <FileText className="mr-2 h-4 w-4" />
      )}
      {loading ? "Generating..." : "Download Certificate"}
    </Button>
  );
}

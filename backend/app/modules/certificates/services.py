"""PDF certificate generation for completed courses."""

import io
import logging
from datetime import datetime
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, Table, TableStyle

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.courses.models import Course, Section, Step
from app.modules.progress.models import UserProgress

logger = logging.getLogger(__name__)


async def check_course_completion(
    db: AsyncSession,
    user_id: UUID,
    course_id: UUID,
) -> tuple[bool, int, int]:
    """Check if a user has completed 100% of a course.

    Returns:
        (is_complete, completed_steps, total_steps)
    """
    total_result = await db.execute(
        select(func.count())
        .select_from(Step)
        .join(Section, Step.section_id == Section.id)
        .where(Section.course_id == course_id)
    )
    total_steps = total_result.scalar() or 0
    if total_steps == 0:
        return False, 0, 0

    subq = (
        select(Step.id)
        .join(Section, Step.section_id == Section.id)
        .where(Section.course_id == course_id)
    ).subquery()

    completed_result = await db.execute(
        select(func.count())
        .select_from(UserProgress)
        .where(
            UserProgress.user_id == user_id,
            UserProgress.step_id.in_(select(subq.c.id)),
            UserProgress.is_completed.is_(True),
        )
    )
    completed = completed_result.scalar() or 0

    return completed >= total_steps, completed, total_steps


def generate_certificate_pdf(
    user_name: str,
    user_email: str,
    course_title: str,
    course_language: str,
    completed_date: datetime | None = None,
) -> io.BytesIO:
    """Generate a professional PDF certificate.

    Returns:
        BytesIO buffer containing the PDF.
    """
    buf = io.BytesIO()
    width, height = landscape(A4)

    c = canvas.Canvas(buf, pagesize=landscape(A4))

    # ── Background border ──
    c.setStrokeColor(colors.HexColor("#1a56db"))
    c.setLineWidth(6)
    c.rect(20, 20, width - 40, height - 40)
    c.setStrokeColor(colors.HexColor("#3b82f6"))
    c.setLineWidth(2)
    c.rect(28, 28, width - 56, height - 56)

    # ── Decorative top line ──
    c.setStrokeColor(colors.HexColor("#6366f1"))
    c.setLineWidth(1)
    y_top = height - 80
    c.line(60, y_top, width - 60, y_top)

    # ── Title ──
    c.setFillColor(colors.HexColor("#1e293b"))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width / 2, height - 140, "Certificate of Completion")

    # ── Subtitle ──
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawCentredString(width / 2, height - 175, "This certificate is proudly presented to")

    # ── User Name ──
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 28)
    name_y = height - 220
    c.drawCentredString(width / 2, name_y, user_name)

    # ── Body ──
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#475569"))
    body_text = f"for successfully completing the course"
    c.drawCentredString(width / 2, name_y - 40, body_text)

    # ── Course Name ──
    c.setFillColor(colors.HexColor("#1a56db"))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, name_y - 75, course_title)

    # ── Date ──
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor("#64748b"))
    date_str = (completed_date or datetime.utcnow()).strftime("%B %d, %Y")
    c.drawCentredString(width / 2, name_y - 115, f"Completed on {date_str}")

    # ── Language badge ──
    c.setFillColor(colors.HexColor("#6b7280"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, name_y - 145, f"Language: {course_language}")

    # ── Bottom decorative line ──
    c.setStrokeColor(colors.HexColor("#6366f1"))
    c.setLineWidth(1)
    y_bottom = 100
    c.line(60, y_bottom, width - 60, y_bottom)

    # ── Footer ──
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawCentredString(width / 2, y_bottom - 25, "Lumina - Interactive Coding Education Platform")
    c.drawCentredString(width / 2, y_bottom - 40, user_email)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.certificates.services import (
    check_course_completion,
    generate_certificate_pdf,
)
from app.modules.courses.services import get_course_with_path
from app.modules.users.router import get_current_user
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/api/v1/certificates", tags=["Certificates"])


@router.get(
    "/{course_id}",
    summary="Download a certificate for a completed course",
)
async def download_certificate(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """Generate and return a PDF certificate if the user has completed
    100% of the course's steps.

    The PDF is returned as a downloadable file attachment.
    """
    try:
        cid = UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid course_id format.")

    is_complete, completed, total = await check_course_completion(
        db, current_user.id, cid
    )
    if not is_complete:
        raise HTTPException(
            status_code=400,
            detail=f"Course not completed yet ({completed}/{total} steps). "
            f"Complete all {total} steps first.",
        )

    course = await get_course_with_path(db, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found.")

    pdf_buffer = generate_certificate_pdf(
        user_name=current_user.email.split("@")[0],
        user_email=current_user.email,
        course_title=course.title,
        course_language=course.language,
    )

    filename = f"certificate-{course.title.lower().replace(' ', '-')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

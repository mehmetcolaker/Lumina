"""Comprehensive seed script for the Lumina development database.

Populates the database with:
    - A demo user account (demo@lumina.dev / demopass123)
    - A full Python Fundamentals course (4 sections, 12 steps)
    - Sample progress records for the demo user
    - Gamification stats with XP and a leaderboard entry
    - Sample line comments on a code step
    - A free-tier subscription record

Usage::

    python seed_data.py

Requires a running PostgreSQL instance reachable via ``DATABASE_URL``
in the ``.env`` file.  The tables must already exist (run ``alembic upgrade head``
first).

The script is **idempotent** — running it multiple times will skip
already-seeded records where possible.
"""

import asyncio
import logging
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select

from app.core.database import async_session_maker
from app.core.security import hash_password
from app.modules.courses.models import Course, Section, Step, StepType
from app.modules.gamification.models import LineComment, UserStats
from app.modules.progress.models import UserProgress
from app.modules.users.models import User

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Seed data payloads
# ---------------------------------------------------------------------------

COURSE_PYTHON = {
    "title": "Python Fundamentals",
    "description": (
        "Python'a sıfırdan başlayın! Değişkenler, döngüler, fonksiyonlar "
        "ve daha fazlasını interaktif alıştırmalarla öğrenin."
    ),
    "language": "Python",
}

SECTIONS = [
    {
        "title": "Değişkenler ve Veri Tipleri",
        "order": 0,
        "steps": [
            {
                "title": "Değişken Nedir?",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "## Değişkenler (Variables)\n\n"
                        "Değişkenler, veriyi saklamak için kullanılan isimlendirilmiş "
                        "bellek bölgeleridir.\n\n"
                        "```python\n"
                        "isim = \"Ali\"\n"
                        "yas = 25\n"
                        "pi = 3.14\n"
                        "```\n\n"
                        "Python'da değişken tanımlamak için **tür belirtmenize gerek yoktur**. "
                        "Python, değere bakarak türü otomatik çıkarır."
                    ),
                },
            },
            {
                "title": "Veri Tipleri Alıştırması",
                "step_type": StepType.QUIZ,
                "order": 1,
                "xp_reward": 20,
                "content_data": {
                    "question": "Aşağıdakilerden hangisi geçerli bir Python değişken adıdır?",
                    "options": [
                        {"id": "a", "label": "2deger"},
                        {"id": "b", "label": "my_var"},
                        {"id": "c", "label": "toplam$"},
                        {"id": "d", "label": "if"},
                    ],
                    "correct_option": "b",
                    "explanation": (
                        "Değişken adları harf veya alt çizgi ile başlamalı, "
                        "rakamla başlayamaz ve özel karakter içeremez. "
                        "'if' Python'da ayrılmış bir anahtar kelimedir."
                    ),
                },
            },
            {
                "title": "Tip Dönüşümü",
                "step_type": StepType.CODE,
                "order": 2,
                "xp_reward": 30,
                "content_data": {
                    "instruction": (
                        "Kullanıcıdan alınan yaş bilgisini (string) integer'a "
                        "çeviren bir program yazın."
                    ),
                    "starter_code": (
                        "yas_str = input(\"Yaşınızı girin: \")\n"
                        "# Burada tip dönüşümü yapın\n"
                        "yas = int(yas_str)\n"
                        "print(f\"5 yıl sonra {yas + 5} yaşında olacaksınız.\")"
                    ),
                    "expected_output_contains": "yaşında",
                },
            },
        ],
    },
    {
        "title": "Koşullu İfadeler (if/elif/else)",
        "order": 1,
        "steps": [
            {
                "title": "Koşullar ve Karar Mekanizmaları",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "## if / elif / else\n\n"
                        "Koşullu ifadeler, programınızın farklı durumlarda "
                        "farklı kodlar çalıştırmasını sağlar.\n\n"
                        "```python\n"
                        "not = 85\n\n"
                        "if not >= 90:\n"
                        "    print(\"AA\")\n"
                        "elif not >= 70:\n"
                        "    print(\"BB\")\n"
                        "else:\n"
                        "    print(\"CC\")\n"
                        "```\n\n"
                        "**İpucu:** Python'da girintileme (indentation) çok önemlidir! "
                        "4 boşluk standarttır."
                    ),
                },
            },
            {
                "title": "Mantıksal Operatörler",
                "step_type": StepType.QUIZ,
                "order": 1,
                "xp_reward": 20,
                "content_data": {
                    "question": "Aşağıdaki ifadenin sonucu nedir?\n\n```python\nnot(10 > 5) or (3 == 3)\n```",
                    "options": [
                        {"id": "a", "label": "True"},
                        {"id": "b", "label": "False"},
                        {"id": "c", "label": "Error"},
                        {"id": "d", "label": "None"},
                    ],
                    "correct_option": "a",
                    "explanation": (
                        "10 > 5 = True, not(True) = False. "
                        "3 == 3 = True. False or True = True."
                    ),
                },
            },
            {
                "title": "Not Hesaplama Uygulaması",
                "step_type": StepType.CODE,
                "order": 2,
                "xp_reward": 30,
                "content_data": {
                    "instruction": (
                        "Girilen sınav notuna göre harf notunu hesaplayan "
                        "bir program yazın:\n"
                        "- 90-100: AA\n"
                        "- 70-89: BB\n"
                        "- 50-69: CC\n"
                        "- 0-49: FF"
                    ),
                    "starter_code": (
                        "not = int(input(\"Sınav notunuzu girin: \"))\n\n"
                        "if not >= 90:\n"
                        "    print(\"AA\")\n"
                        "elif not >= 70:\n"
                        "    print(\"BB\")\n"
                        "elif not >= 50:\n"
                        "    print(\"CC\")\n"
                        "else:\n"
                        "    print(\"FF\")"
                    ),
                    "expected_output_in": ["AA", "BB", "CC", "FF"],
                },
            },
        ],
    },
    {
        "title": "Listeler ve Döngüler",
        "order": 2,
        "steps": [
            {
                "title": "Listelerle Çalışmak",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "## Listeler\n\n"
                        "Listeler, birden fazla öğeyi tek bir değişkende "
                        "saklamanızı sağlar.\n\n"
                        "```python\n"
                        "meyveler = [\"elma\", \"armut\", \"muz\"]\n"
                        "print(meyveler[0])  # elma\n"
                        "meyveler.append(\"portakal\")\n"
                        "print(len(meyveler))  # 4\n"
                        "```\n\n"
                        "## for Döngüsü\n\n"
                        "```python\n"
                        "for meyve in meyveler:\n"
                        "    print(meyve.upper())\n"
                        "```"
                    ),
                },
            },
            {
                "title": "Döngü Alıştırması",
                "step_type": StepType.QUIZ,
                "order": 1,
                "xp_reward": 20,
                "content_data": {
                    "question": "Aşağıdaki kod ne yazdırır?\n\n```python\ntoplam = 0\nfor i in range(1, 5):\n    toplam += i\nprint(toplam)\n```",
                    "options": [
                        {"id": "a", "label": "10"},
                        {"id": "b", "label": "15"},
                        {"id": "c", "label": "5"},
                        {"id": "d", "label": "20"},
                    ],
                    "correct_option": "a",
                    "explanation": (
                        "range(1,5) → [1, 2, 3, 4]. 1+2+3+4 = 10. "
                        "range(1,5) 5'i dahil etmez!"
                    ),
                },
            },
            {
                "title": "En Büyük Sayıyı Bul",
                "step_type": StepType.CODE,
                "order": 2,
                "xp_reward": 40,
                "content_data": {
                    "instruction": (
                        "Bir liste içindeki en büyük sayıyı bulan "
                        "bir fonksiyon yazın."
                    ),
                    "starter_code": (
                        "sayilar = [42, 17, 88, 3, 56, 99, 11]\n\n"
                        "en_buyuk = sayilar[0]\n"
                        "for sayi in sayilar:\n"
                        "    if sayi > en_buyuk:\n"
                        "        en_buyuk = sayi\n\n"
                        "print(f\"En büyük sayı: {en_buyuk}\")"
                    ),
                    "expected_output_contains": "99",
                },
            },
        ],
    },
    {
        "title": "Fonksiyonlar",
        "order": 3,
        "steps": [
            {
                "title": "Fonksiyon Tanımlama",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "## Fonksiyonlar\n\n"
                        "Fonksiyonlar, tekrar kullanılabilir kod bloklarıdır.\n\n"
                        "```python\n"
                        "def selamla(isim):\n"
                        "    \"\"\"Kullanıcıyı selamlayan fonksiyon\"\"\"\n"
                        "    return f\"Merhaba, {isim}!\"\n\n"
                        "print(selamla(\"Ali\"))\n"
                        "```\n\n"
                        "**return** ifadesi fonksiyonun bir değer döndürmesini sağlar. "
                        "Eğer return yoksa fonksiyon None döndürür."
                    ),
                },
            },
            {
                "title": "Fonksiyonlar Bilgi Yarışması",
                "step_type": StepType.QUIZ,
                "order": 1,
                "xp_reward": 20,
                "content_data": {
                    "question": "Bu fonksiyonun çıktısı nedir?\n\n```python\ndef carp(a, b=2):\n    return a * b\n\nprint(carp(5, 3))\nprint(carp(5))\n```",
                    "options": [
                        {"id": "a", "label": "15 ve 10"},
                        {"id": "b", "label": "15 ve 10"},
                        {"id": "c", "label": "15 ve 5"},
                        {"id": "d", "label": "8 ve 7"},
                    ],
                    "correct_option": "a",
                    "explanation": (
                        "İlk çağrıda b=3, 5*3=15. "
                        "İkinci çağrıda varsayılan b=2 kullanılır, 5*2=10."
                    ),
                },
            },
            {
                "title": "Dört İşlem Hesap Makinesi",
                "step_type": StepType.CODE,
                "order": 2,
                "xp_reward": 50,
                "content_data": {
                    "instruction": (
                        "Kullanıcıdan iki sayı ve bir işlem (+, -, *, /) "
                        "alarak sonucu döndüren bir hesap makinesi fonksiyonu yazın."
                    ),
                    "starter_code": (
                        "def hesap_makinesi(a, b, islem):\n"
                        "    if islem == \"+\":\n"
                        "        return a + b\n"
                        "    elif islem == \"-\":\n"
                        "        return a - b\n"
                        "    elif islem == \"*\":\n"
                        "        return a * b\n"
                        "    elif islem == \"/\":\n"
                        "        if b != 0:\n"
                        "            return a / b\n"
                        "        else:\n"
                        "            return \"Hata: Sıfıra bölme!\"\n"
                        "    else:\n"
                        "        return \"Geçersiz işlem\"\n\n"
                        "# Test\n"
                        "print(hesap_makinesi(10, 5, \"+\"))\n"
                        "print(hesap_makinesi(10, 5, \"/\"))\n"
                        "print(hesap_makinesi(10, 0, \"/\"))"
                    ),
                    "expected_output_contains": "15",
                },
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------


async def seed() -> None:
    """Main seeding function — idempotent by design."""
    async with async_session_maker() as db:
        # ---- 1. Demo user ----
        demo_email = "demo@lumina.dev"
        result = await db.execute(select(User).where(User.email == demo_email))
        demo_user = result.scalar_one_or_none()

        if demo_user is None:
            demo_user = User(
                email=demo_email,
                hashed_password=hash_password("demopass123"),
                is_active=True,
                is_premium=False,
            )
            db.add(demo_user)
            await db.flush()
            await db.refresh(demo_user)
            logger.info("Created demo user: %s (%s)", demo_user.email, demo_user.id)
        else:
            logger.info("Demo user already exists: %s", demo_user.id)

        # ---- 2. UserStats for demo user ----
        stats_result = await db.execute(
            select(UserStats).where(UserStats.user_id == demo_user.id)
        )
        if stats_result.scalar_one_or_none() is None:
            stats = UserStats(
                user_id=demo_user.id,
                total_xp=120,
                current_streak=3,
                last_active_date=date.today(),
            )
            db.add(stats)
            logger.info("Created UserStats for demo user (120 XP, streak=3)")
        else:
            logger.info("UserStats already exists for demo user")

        # ---- 3. Python Course ----
        result = await db.execute(
            select(Course).where(Course.title == COURSE_PYTHON["title"])
        )
        course = result.scalar_one_or_none()

        if course is None:
            course = Course(
                title=COURSE_PYTHON["title"],
                description=COURSE_PYTHON["description"],
                language=COURSE_PYTHON["language"],
            )
            db.add(course)
            await db.flush()
            await db.refresh(course)
            logger.info("Created course: %s", course.title)

            # ---- 4. Sections & Steps ----
            step_ids_by_section: dict[str, list[str]] = {}

            for sec_data in SECTIONS:
                section = Section(
                    course_id=course.id,
                    title=sec_data["title"],
                    order=sec_data["order"],
                )
                db.add(section)
                await db.flush()
                await db.refresh(section)

                step_ids: list[str] = []
                for step_data in sec_data["steps"]:
                    step = Step(
                        section_id=section.id,
                        title=step_data["title"],
                        step_type=step_data["step_type"],
                        order=step_data["order"],
                        xp_reward=step_data["xp_reward"],
                        content_data=step_data.get("content_data"),
                    )
                    db.add(step)
                    await db.flush()
                    await db.refresh(step)
                    step_ids.append(str(step.id))

                step_ids_by_section[sec_data["title"]] = step_ids
                logger.info(
                    "  Section '%s' created with %d steps",
                    section.title,
                    len(step_ids),
                )

            # ---- 5. Progress for demo user (first 5 steps completed) ----
            all_step_ids = [
                sid for ids in step_ids_by_section.values() for sid in ids
            ]
            for i, sid in enumerate(all_step_ids[:5]):
                up = UserProgress(
                    user_id=demo_user.id,
                    step_id=uuid.UUID(sid),
                    is_completed=True,
                    completed_at=datetime.now(timezone.utc),
                )
                db.add(up)
            logger.info("Marked first 5 steps as completed for demo user")

            # ---- 6. Sample line comment on the first CODE step ----
            first_code_step_id: str | None = None
            for sec_data in SECTIONS:
                for step_data in sec_data["steps"]:
                    if step_data["step_type"] == StepType.CODE:
                        sec_idx = SECTIONS.index(sec_data)
                        section_steps = list(step_ids_by_section.values())[sec_idx]
                        step_idx = sec_data["steps"].index(step_data)
                        first_code_step_id = section_steps[step_idx]
                        break
                if first_code_step_id:
                    break

            if first_code_step_id:
                comment = LineComment(
                    step_id=uuid.UUID(first_code_step_id),
                    user_id=demo_user.id,
                    line_number=3,
                    content="Harika! Tip dönüşümü burada çok net anlaşılıyor.",
                )
                db.add(comment)
                logger.info("Added sample line comment on step %s", first_code_step_id)

        else:
            logger.info("Course '%s' already exists — skipping section/step seeding", course.title)
            # Still count existing steps for logging
            from sqlalchemy import func
            count_result = await db.execute(
                select(func.count()).select_from(Step)
                .join(Section)
                .where(Section.course_id == course.id)
            )
            total_steps = count_result.scalar() or 0
            logger.info("Existing course has %d steps", total_steps)

        await db.commit()
        logger.info("=" * 40)
        logger.info("Seed complete!")
        logger.info("  Login:  email='%s'  password='demopass123'", demo_email)
        logger.info("=" * 40)


if __name__ == "__main__":
    asyncio.run(seed())

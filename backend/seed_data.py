"""Comprehensive seed script for the Lumina development database.

Usage::

    python seed_data.py

Run ``alembic upgrade head`` first to ensure all tables exist.
The script is idempotent — re-running it skips existing records.
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

# ─────────────────────────────────────────────
# COURSE 1 — Python Fundamentals
# ─────────────────────────────────────────────
COURSE_PYTHON = {
    "title": "Python Fundamentals",
    "description": (
        "Python'a sıfırdan başlayın! "
        "Değişkenler, koşullar, döngüler ve fonksiyonları "
        "gerçek kod alıştırmalarıyla öğrenin."
    ),
    "language": "Python",
}

PYTHON_SECTIONS = [
    {
        "title": "Değişkenler ve Veri Tipleri",
        "order": 0,
        "steps": [
            {
                "title": "Python'a Giriş",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "# Python Nedir?\n\n"
                        "Python, 1991 yılında **Guido van Rossum** tarafından geliştirilen, "
                        "okunabilir ve öğrenmesi kolay bir programlama dilidir.\n\n"
                        "## Neden Python?\n\n"
                        "- **Basit sözdizimi** — İngilizceye yakın, anlaşılır kod\n"
                        "- **Çok yönlü** — Web, veri bilimi, yapay zeka, otomasyon\n"
                        "- **Devasa ekosistem** — 400.000+ açık kaynak kütüphane\n"
                        "- **Endüstri standardı** — Google, Netflix, NASA kullanıyor\n\n"
                        "## İlk Python Kodu\n\n"
                        "```python\n"
                        "print(\"Merhaba, Lumina!\")\n"
                        "```\n\n"
                        "> `print()` fonksiyonu ekrana metin yazdırır. "
                        "En sık kullanılan Python fonksiyonlarından biridir."
                    ),
                },
            },
            {
                "title": "Değişken Nedir?",
                "step_type": StepType.THEORY,
                "order": 1,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "# Değişkenler\n\n"
                        "Değişkenler, programda kullanılan verileri saklayan **isimlendirilmiş kutular**dır.\n\n"
                        "## Değişken Tanımlama\n\n"
                        "```python\n"
                        "isim = \"Ali\"         # Metin (str)\n"
                        "yas = 25               # Tam sayı (int)\n"
                        "pi = 3.14             # Ondalıklı (float)\n"
                        "ogrenci_mi = True     # Mantıksal (bool)\n"
                        "```\n\n"
                        "## Dikkat Edilecekler\n\n"
                        "| ✅ Geçerli | ❌ Geçersiz |\n"
                        "|---|---|\n"
                        "| `my_var` | `2deger` (rakamla başlar) |\n"
                        "| `toplam_xp` | `toplam$xp` (özel karakter) |\n"
                        "| `kullanici` | `if` (ayrılmış kelime) |\n\n"
                        "Python'da tür belirtmek **zorunlu değildir** — Python otomatik anlar."
                    ),
                },
            },
            {
                "title": "Veri Tipleri Quiz",
                "step_type": StepType.QUIZ,
                "order": 2,
                "xp_reward": 20,
                "content_data": {
                    "question": "Hangi kod satırı geçerli bir Python değişkenidir?",
                    "options": [
                        {"id": "a", "label": "3sayi = 10"},
                        {"id": "b", "label": "sayi-toplam = 5"},
                        {"id": "c", "label": "toplam_sayi = 100"},
                        {"id": "d", "label": "class = \"Python\""},
                    ],
                    "correct_option": "c",
                    "hints": [
                        "Python değişken adları harf veya alt çizgi (_) ile başlamalı, rakamla başlayamaz.",
                        "Değişken adları özel karakter (boşluk, tire, $, @) içeremez. Sadece harf, rakam, alt çizgi kullanılabilir.",
                        "Python'da ayrılmış (reserved) kelimeler değişken adı olarak kullanılamaz: if, else, class, for, while..."
                    ],
                    "explanation": (
                        "`toplam_sayi` geçerlidir çünkü harf ile başlar, "
                        "alt çizgi içerir ve Python'da ayrılmış bir kelime değildir.\n\n"
                        "- `3sayi` rakamla başlıyor ❌\n"
                        "- `sayi-toplam` kısa çizgi içeriyor ❌\n"
                        "- `class` Python anahtar kelimesi ❌"
                    ),
                },
            },
            {
                "title": "İlk Python Programın",
                "step_type": StepType.CODE,
                "order": 3,
                "xp_reward": 30,
                "content_data": {
                    "instruction": (
                        "Aşağıdaki görevi tamamla:\n"
                        "1. `isim` adında bir değişken tanımla, değeri `\"Ada Lovelace\"` olsun\n"
                        "2. `yas` adında bir değişken tanımla, değeri `207` olsun\n"
                        "3. `print()` ile `İsim: Ada Lovelace` ve `Yaş: 207` yazdır"
                    ),
                    "starter_code": (
                        "# Değişkenlerini buraya yaz\n"
                        "isim = \"\"\n"
                        "yas = 0\n\n"
                        "# Ekrana yazdır\n"
                        "print(f\"İsim: {isim}\")\n"
                        "print(f\"Yaş: {yas}\")"
                    ),
                    "solution": (
                        "isim = \"Ada Lovelace\"\n"
                        "yas = 207\n"
                        "print(f\"İsim: {isim}\")\n"
                        "print(f\"Yaş: {yas}\")"
                    ),
                    "expected_output": "İsim: Ada Lovelace\nYaş: 207",
                    "compare_mode": "trim",
                    "test_cases": [
                        {"input": "", "expected": "İsim: Ada Lovelace\nYaş: 207"},
                        {"input": "isim = \"Einstein\"\nyas = 150\nprint(f\"İsim: {isim}\")\nprint(f\"Yaş: {yas}\")", "expected": "İsim: Einstein\nYaş: 150"},
                    ],
                    "hints": [
                        "Bu görevde değişken tanımlama ve f-string kullanımını öğreneceksin.",
                        "Değişkenlere değer atarken `degisken_adi = deger` kalıbını kullan. Örn: `isim = \"Ada\"`",
                        "f-string'ler `print(f\"Metin {degisken}\")` şeklinde yazılır. İsim ve Yaş değerlerini ayrı satırlarda yazdır."
                    ],
                },
            },
        ],
    },
    {
        "title": "Koşullu İfadeler",
        "order": 1,
        "steps": [
            {
                "title": "if / elif / else",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "# Koşullu İfadeler\n\n"
                        "Programın farklı durumlarda farklı davranmasını sağlar.\n\n"
                        "## Temel Yapı\n\n"
                        "```python\n"
                        "puan = 85\n\n"
                        "if puan >= 90:\n"
                        "    print(\"Harika! AA aldın\")\n"
                        "elif puan >= 70:\n"
                        "    print(\"İyi iş! BB aldın\")\n"
                        "elif puan >= 50:\n"
                        "    print(\"Geçtin, CC aldın\")\n"
                        "else:\n"
                        "    print(\"Maalesef, FF aldın\")\n"
                        "```\n\n"
                        "## Karşılaştırma Operatörleri\n\n"
                        "| Operatör | Anlamı |\n"
                        "|---|---|\n"
                        "| `==` | Eşit mi? |\n"
                        "| `!=` | Eşit değil mi? |\n"
                        "| `>` / `<` | Büyük / Küçük |\n"
                        "| `>=` / `<=` | Büyük eşit / Küçük eşit |\n\n"
                        "⚠️ **Python'da girintileme (4 boşluk) zorunludur!**"
                    ),
                },
            },
            {
                "title": "Mantıksal Operatörler Quiz",
                "step_type": StepType.QUIZ,
                "order": 1,
                "xp_reward": 20,
                "content_data": {
                    "question": "Aşağıdaki ifadenin sonucu nedir?\n```python\nx = 10\nprint(x > 5 and x < 20)\n```",
                    "options": [
                        {"id": "a", "label": "True"},
                        {"id": "b", "label": "False"},
                        {"id": "c", "label": "None"},
                        {"id": "d", "label": "Hata verir"},
                    ],
                    "correct_option": "a",
                    "hints": [
                        "İfadeyi parçalara ayır: önce `x > 5` sonra `x < 20` hesapla.",
                        "`and` operatörü: eğer her iki koşul da doğruysa sonuç True olur.",
                        "`x > 5` = True, `x < 20` = True. True and True = ?"
                    ],
                    "explanation": (
                        "`x > 5` → `10 > 5` → `True`\n"
                        "`x < 20` → `10 < 20` → `True`\n"
                        "`True and True` → **`True`**\n\n"
                        "`and` operatörü: her iki koşul da doğruysa `True` döner."
                    ),
                },
            },
            {
                "title": "Not Hesaplama Programı",
                "step_type": StepType.CODE,
                "order": 2,
                "xp_reward": 35,
                "content_data": {
                    "instruction": (
                        "Bir öğrencinin puanına göre harf notu belirleyen program yaz:\n"
                        "- 90-100 → **AA**\n"
                        "- 70-89  → **BB**\n"
                        "- 50-69  → **CC**\n"
                        "- 0-49   → **FF**\n\n"
                        "Örnek: `puan = 78` için `BB` yazdırmalı."
                    ),
                    "starter_code": (
                        "puan = 78\n\n"
                        "# Koşulları buraya ekle\n"
                        "if puan >= 90:\n"
                        "    print(\"AA\")\n"
                        "# elif ve else ekle\n"
                    ),
                    "solution": (
                        "puan = 78\n"
                        "if puan >= 90:\n"
                        "    print(\"AA\")\n"
                        "elif puan >= 70:\n"
                        "    print(\"BB\")\n"
                        "elif puan >= 50:\n"
                        "    print(\"CC\")\n"
                        "else:\n"
                        "    print(\"FF\")"
                    ),
                    "expected_output": "BB",
                    "compare_mode": "trim",
                    "test_cases": [
                        {"input": "puan = 95", "expected": "AA"},
                        {"input": "puan = 62", "expected": "CC"},
                        {"input": "puan = 30", "expected": "FF"},
                    ],
                    "hints": [
                        "`if/elif/else` yapısında sıralama önemlidir — önce en yüksek koşul kontrol edilir.",
                        "`elif puan >= 70:` ile 70-89 aralığını yakalarsın.",
                        "Geriye kalan tüm durumlar (0-49) `else` bloğunda işlenir."
                    ],
                },
            },
        ],
    },
    {
        "title": "Listeler ve Döngüler",
        "order": 2,
        "steps": [
            {
                "title": "Python Listeleri",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "# Listeler\n\n"
                        "Liste, birden fazla değeri **sıralı** tutan bir veri yapısıdır.\n\n"
                        "```python\n"
                        "meyveler = [\"elma\", \"armut\", \"muz\", \"kivi\"]\n\n"
                        "# Elemana erişim (0'dan başlar)\n"
                        "print(meyveler[0])   # elma\n"
                        "print(meyveler[-1])  # kivi (sondan birinci)\n\n"
                        "# Eleman ekleme / silme\n"
                        "meyveler.append(\"üzüm\")    # sona ekle\n"
                        "meyveler.remove(\"armut\")   # sil\n"
                        "print(len(meyveler))        # 4\n"
                        "```\n\n"
                        "## Dilimleme (Slicing)\n\n"
                        "```python\n"
                        "sayilar = [1, 2, 3, 4, 5]\n"
                        "print(sayilar[1:4])  # [2, 3, 4]\n"
                        "print(sayilar[:3])   # [1, 2, 3]\n"
                        "print(sayilar[::2])  # [1, 3, 5] (her ikinci)\n"
                        "```"
                    ),
                },
            },
            {
                "title": "for ve while Döngüleri",
                "step_type": StepType.THEORY,
                "order": 1,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "# Döngüler\n\n"
                        "Bir kod bloğunu tekrar tekrar çalıştırmak için kullanılır.\n\n"
                        "## for Döngüsü\n\n"
                        "```python\n"
                        "# Listede gez\n"
                        "renkler = [\"kırmızı\", \"mavi\", \"yeşil\"]\n"
                        "for renk in renkler:\n"
                        "    print(f\"Renk: {renk}\")\n\n"
                        "# range() ile say\n"
                        "for i in range(5):        # 0,1,2,3,4\n"
                        "    print(i)\n\n"
                        "for i in range(1, 11):    # 1'den 10'a\n"
                        "    print(i)\n"
                        "```\n\n"
                        "## while Döngüsü\n\n"
                        "```python\n"
                        "sayac = 0\n"
                        "while sayac < 5:\n"
                        "    print(sayac)\n"
                        "    sayac += 1   # ← bu satır olmadan sonsuz döngü!\n"
                        "```\n\n"
                        "> `break` → döngüyü kır, `continue` → sonraki adıma geç"
                    ),
                },
            },
            {
                "title": "Döngü Quiz",
                "step_type": StepType.QUIZ,
                "order": 2,
                "xp_reward": 20,
                "content_data": {
                    "question": "Bu kod ne yazdırır?\n```python\ntoplam = 0\nfor i in range(1, 6):\n    toplam += i\nprint(toplam)\n```",
                    "options": [
                        {"id": "a", "label": "10"},
                        {"id": "b", "label": "15"},
                        {"id": "c", "label": "14"},
                        {"id": "d", "label": "20"},
                    ],
                    "correct_option": "b",
                    "hints": [
                        "`range(1, 6)` hangi sayıları üretir? range'in bitiş değeri dahil edilir mi?",
                        "Döngü her adımda `toplam += i` ile toplamı güncelliyor. Hangi değerler toplanıyor?",
                        "range(1,6) = [1, 2, 3, 4, 5]. 1+2+3+4+5 = ?"
                    ],
                    "explanation": (
                        "`range(1, 6)` → `[1, 2, 3, 4, 5]` (6 dahil değil!)\n\n"
                        "`1 + 2 + 3 + 4 + 5 = 15`\n\n"
                        "range(başlangıç, bitiş) — bitiş değeri dahil edilmez."
                    ),
                },
            },
            {
                "title": "En Büyük Sayıyı Bul",
                "step_type": StepType.CODE,
                "order": 3,
                "xp_reward": 40,
                "content_data": {
                    "instruction": (
                        "Bir listede döngü kullanarak en büyük sayıyı bulan programı yaz.\n\n"
                        "- `max()` fonksiyonu kullanma!\n"
                        "- Döngü ve karşılaştırmayla çöz"
                    ),
                    "starter_code": (
                        "sayilar = [42, 17, 88, 3, 56, 99, 11, 73]\n\n"
                        "en_buyuk = sayilar[0]  # başlangıç değeri\n\n"
                        "for sayi in sayilar:\n"
                        "    # buraya karşılaştırma ekle\n"
                        "    pass\n\n"
                        "print(f\"En büyük sayı: {en_buyuk}\")"
                    ),
                    "solution": (
                        "sayilar = [42, 17, 88, 3, 56, 99, 11, 73]\n"
                        "en_buyuk = sayilar[0]\n"
                        "for sayi in sayilar:\n"
                        "    if sayi > en_buyuk:\n"
                        "        en_buyuk = sayi\n"
                        "print(f\"En büyük sayı: {en_buyuk}\")"
                    ),
                    "expected_output": "En büyük sayı: 99",
                    "compare_mode": "trim",
                    "test_cases": [
                        {"input": "", "expected": "En büyük sayı: 99"},
                        {"input": "sayilar = [1, 2, 3]\nfor s in sayilar:\n    if s > en_buyuk:\n        en_buyuk = s\nprint(f\"En büyük sayı: {en_buyuk}\")", "expected": "En büyük sayı: 3"},
                        {"input": "sayilar = [-5, -2, -10]\nfor s in sayilar:\n    if s > en_buyuk:\n        en_buyuk = s\nprint(f\"En büyük sayı: {en_buyuk}\")", "expected": "En büyük sayı: -2"},
                    ],
                    "hints": [
                        "İlk sayıyı (`sayilar[0]`) başlangıçtaki en büyük sayı olarak al.",
                        "`for` döngüsüyle her sayıyı `en_buyuk` ile karşılaştır.",
                        "Eğer `sayi > en_buyuk` ise `en_buyuk`'u güncelle."
                    ],
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
                        "# Fonksiyonlar\n\n"
                        "Fonksiyon, **bir kez yaz, defalarca kullan** prensibine dayanan "
                        "yeniden kullanılabilir kod bloğudur.\n\n"
                        "```python\n"
                        "def selamla(isim):\n"
                        "    \"\"\"Kullanıcıyı selamlayan fonksiyon.\"\"\"\n"
                        "    mesaj = f\"Merhaba, {isim}! 👋\"\n"
                        "    return mesaj\n\n"
                        "print(selamla(\"Ali\"))    # Merhaba, Ali! 👋\n"
                        "print(selamla(\"Ayşe\"))  # Merhaba, Ayşe! 👋\n"
                        "```\n\n"
                        "## Varsayılan Parametre\n\n"
                        "```python\n"
                        "def guc(taban, us=2):    # us varsayılan 2\n"
                        "    return taban ** us\n\n"
                        "print(guc(3))     # 9  (3²)\n"
                        "print(guc(3, 3))  # 27 (3³)\n"
                        "```\n\n"
                        "## Birden Fazla Dönüş Değeri\n\n"
                        "```python\n"
                        "def min_max(sayilar):\n"
                        "    return min(sayilar), max(sayilar)\n\n"
                        "kucuk, buyuk = min_max([5, 1, 9, 3])\n"
                        "print(kucuk, buyuk)  # 1 9\n"
                        "```"
                    ),
                },
            },
            {
                "title": "Fonksiyon Quiz",
                "step_type": StepType.QUIZ,
                "order": 1,
                "xp_reward": 20,
                "content_data": {
                    "question": "Bu fonksiyon ne döndürür?\n```python\ndef hesapla(a, b=10):\n    return a * 2 + b\n\nprint(hesapla(5))\n```",
                    "options": [
                        {"id": "a", "label": "10"},
                        {"id": "b", "label": "20"},
                        {"id": "c", "label": "15"},
                        {"id": "d", "label": "25"},
                    ],
                    "correct_option": "b",
                    "hints": [
                        "`b=10` fonksiyona varsayılan parametre olarak verilmiş. Eğer b gönderilmezse otomatik 10 alır.",
                        "Fonksiyon çağrısı: `hesapla(5)` → a=5, b=10. İşlem: `5 * 2 + 10`",
                        "5*2=10, 10+10=20"
                    ],
                    "explanation": (
                        "`hesapla(5)` çağrılınca `b` varsayılan değer `10`'u alır.\n\n"
                        "`5 * 2 + 10 = 10 + 10 = 20`"
                    ),
                },
            },
            {
                "title": "Hesap Makinesi",
                "step_type": StepType.CODE,
                "order": 2,
                "xp_reward": 50,
                "content_data": {
                    "instruction": (
                        "Dört işlem yapabilen bir hesap makinesi fonksiyonu yaz:\n\n"
                        "- `topla(a, b)` → a + b\n"
                        "- `cikar(a, b)` → a - b\n"
                        "- `carp(a, b)` → a * b\n"
                        "- `bol(a, b)` → a / b (b=0 ise `\"Sıfıra bölme hatası\"` döndür)\n\n"
                        "Her fonksiyonu ayrı tanımla ve test et."
                    ),
                    "starter_code": (
                        "def topla(a, b):\n"
                        "    return a + b\n\n"
                        "def cikar(a, b):\n"
                        "    pass  # tamamla\n\n"
                        "def carp(a, b):\n"
                        "    pass  # tamamla\n\n"
                        "def bol(a, b):\n"
                        "    pass  # tamamla (sıfır kontrolü unutma!)\n\n"
                        "# Test\n"
                        "print(topla(10, 5))   # 15\n"
                        "print(cikar(10, 3))   # 7\n"
                        "print(carp(4, 6))     # 24\n"
                        "print(bol(10, 2))     # 5.0\n"
                        "print(bol(7, 0))      # Sıfıra bölme hatası"
                    ),
                    "solution": (
                        "def topla(a, b):\n"
                        "    return a + b\n\n"
                        "def cikar(a, b):\n"
                        "    return a - b\n\n"
                        "def carp(a, b):\n"
                        "    return a * b\n\n"
                        "def bol(a, b):\n"
                        "    if b == 0:\n"
                        "        return \"Sıfıra bölme hatası\"\n"
                        "    return a / b\n\n"
                        "print(topla(10, 5))\n"
                        "print(cikar(10, 3))\n"
                        "print(carp(4, 6))\n"
                        "print(bol(10, 2))\n"
                        "print(bol(7, 0))"
                    ),
                    "expected_output": "15\n7\n24\n5.0\nSıfıra bölme hatası",
                    "compare_mode": "trim",
                    "test_cases": [
                        {"input": "", "expected": "15\n7\n24\n5.0\nSıfıra bölme hatası"},
                    ],
                    "hints": [
                        "`cikar(a, b)` çıkarma operatörü `-` kullan: `return a - b`",
                        "`carp(a, b)` çarpma operatörü `*` kullan: `return a * b`",
                        "`bol(a, b)` için önce `if b == 0:` kontrolü yap, sonra `return a / b`"
                    ],
                },
            },
        ],
    },
    {
        "title": "Sözlükler ve Kümeler",
        "order": 4,
        "steps": [
            {
                "title": "Sözlükler (dict)",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 15,
                "content_data": {
                    "body_markdown": (
                        "# Sözlükler\n\n"
                        "Sözlük, **anahtar-değer** çiftlerini saklayan veri yapısıdır.\n\n"
                        "```python\n"
                        "ogrenci = {\n"
                        "    \"isim\": \"Zeynep\",\n"
                        "    \"yas\": 22,\n"
                        "    \"not\": 95,\n"
                        "    \"aktif\": True\n"
                        "}\n\n"
                        "# Erişim\n"
                        "print(ogrenci[\"isim\"])            # Zeynep\n"
                        "print(ogrenci.get(\"sehir\", \"—\"))  # — (varsayılan)\n\n"
                        "# Güncelleme ve ekleme\n"
                        "ogrenci[\"sehir\"] = \"İstanbul\"\n"
                        "ogrenci[\"not\"] = 97\n\n"
                        "# Döngü\n"
                        "for anahtar, deger in ogrenci.items():\n"
                        "    print(f\"{anahtar}: {deger}\")\n"
                        "```"
                    ),
                },
            },
            {
                "title": "Sözlük Quiz",
                "step_type": StepType.QUIZ,
                "order": 1,
                "xp_reward": 25,
                "content_data": {
                    "question": "Bir sözlükteki tüm anahtarları döndüren metot hangisidir?",
                    "options": [
                        {"id": "a", "label": "dict.items()"},
                        {"id": "b", "label": "dict.keys()"},
                        {"id": "c", "label": "dict.values()"},
                        {"id": "d", "label": "dict.all()"},
                    ],
                    "correct_option": "b",
                    "hints": [
                        "Sözlük metodlarının isimleri İngilizce'dir. 'anahtar'ın İngilizcesi nedir?",
                        "items = öğeler, keys = anahtarlar, values = değerler",
                        "Cevap: dict.keys() — tüm anahtarları döndürür."
                    ],
                    "explanation": (
                        "- `dict.keys()` → tüm **anahtarlar**\n"
                        "- `dict.values()` → tüm **değerler**\n"
                        "- `dict.items()` → tüm **(anahtar, değer) çiftleri**\n"
                        "- `dict.all()` diye bir metot yoktur!"
                    ),
                },
            },
            {
                "title": "Öğrenci Not Defteri",
                "step_type": StepType.CODE,
                "order": 2,
                "xp_reward": 45,
                "content_data": {
                    "instruction": (
                        "Öğrenci notlarını sözlük kullanarak yöneten bir program yaz:\n"
                        "1. 5 öğrenci ve notlarını içeren sözlük oluştur\n"
                        "2. Sınıf ortalamasını hesapla\n"
                        "3. En yüksek notu bulan öğrenciyi yazdır"
                    ),
                    "starter_code": (
                        "notlar = {\n"
                        "    \"Ali\": 85,\n"
                        "    \"Ayşe\": 92,\n"
                        "    \"Mehmet\": 78,\n"
                        "    \"Zeynep\": 95,\n"
                        "    \"Can\": 88\n"
                        "}\n\n"
                        "# Ortalamayı hesapla\n"
                        "ortalama = sum(notlar.values()) / len(notlar)\n"
                        "print(f\"Sınıf ortalaması: {ortalama:.1f}\")\n\n"
                        "# En yüksek notu bul\n"
                        "en_iyi = max(notlar, key=notlar.get)\n"
                        "print(f\"En başarılı: {en_iyi} ({notlar[en_iyi]}\")"
                    ),
                    "solution": (
                        "notlar = {\n"
                        "    \"Ali\": 85,\n"
                        "    \"Ayşe\": 92,\n"
                        "    \"Mehmet\": 78,\n"
                        "    \"Zeynep\": 95,\n"
                        "    \"Can\": 88\n"
                        "}\n"
                        "ortalama = sum(notlar.values()) / len(notlar)\n"
                        "print(f\"Sınıf ortalaması: {ortalama:.1f}\")\n"
                        "en_iyi = max(notlar, key=notlar.get)\n"
                        "print(f\"En başarılı: {en_iyi} ({notlar[en_iyi]}\")"
                    ),
                    "expected_output": "Sınıf ortalaması: 87.6\nEn başarılı: Zeynep (95",
                    "compare_mode": "contains",
                    "hints": [
                        "`sum(notlar.values())` tüm notları toplar, `len(notlar)` öğrenci sayısını verir.",
                        "Ortalama için toplamı sayıya böl.",
                        "En yüksek notu bulmak için `max(notlar, key=notlar.get)` kullan."
                    ],
                },
            },
        ],
    },
]

# ─────────────────────────────────────────────
# COURSE 2 — JavaScript Fundamentals
# ─────────────────────────────────────────────
COURSE_JS = {
    "title": "JavaScript Fundamentals",
    "description": (
        "Webin dili JavaScript'i öğren. "
        "DOM manipülasyonu, async/await ve modern ES6+ sözdizimini keşfet."
    ),
    "language": "JavaScript",
}

JS_SECTIONS = [
    {
        "title": "Temel Kavramlar",
        "order": 0,
        "steps": [
            {
                "title": "JavaScript'e Giriş",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "# JavaScript Nedir?\n\n"
                        "JavaScript (JS), tarayıcıda çalışan tek programlama dilidir. "
                        "Günümüzde **Node.js** sayesinde sunucu tarafında da kullanılır.\n\n"
                        "## Nerede Kullanılır?\n\n"
                        "- 🌐 Web arayüzleri (React, Vue, Angular)\n"
                        "- 🖥️ Sunucu tarafı (Node.js, Express)\n"
                        "- 📱 Mobil uygulamalar (React Native)\n"
                        "- 🤖 Yapay zeka (TensorFlow.js)\n\n"
                        "## İlk Kod\n\n"
                        "```javascript\n"
                        "console.log(\"Merhaba, Dünya!\");\n\n"
                        "// Değişkenler\n"
                        "const isim = \"Lumina\";      // sabit\n"
                        "let yas = 3;                  // değişebilir\n"
                        "var eski = \"eski yöntem\";    // kullanma!\n"
                        "```\n\n"
                        "> Modern JS'te `var` kullanmayın — `const` ve `let` tercih edin."
                    ),
                },
            },
            {
                "title": "Fonksiyonlar",
                "step_type": StepType.THEORY,
                "order": 1,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "# JavaScript Fonksiyonları\n\n"
                        "## Geleneksel Fonksiyon\n\n"
                        "```javascript\n"
                        "function topla(a, b) {\n"
                        "    return a + b;\n"
                        "}\n"
                        "console.log(topla(3, 5)); // 8\n"
                        "```\n\n"
                        "## Arrow Function (Modern)\n\n"
                        "```javascript\n"
                        "const carp = (a, b) => a * b;\n"
                        "console.log(carp(4, 7)); // 28\n\n"
                        "// Çok satırlı\n"
                        "const selamla = (isim) => {\n"
                        "    const mesaj = `Merhaba, ${isim}!`;\n"
                        "    return mesaj;\n"
                        "};\n"
                        "```\n\n"
                        "## Template Literal\n\n"
                        "```javascript\n"
                        "const ad = \"Ahmet\";\n"
                        "const yas = 30;\n"
                        "console.log(`${ad} ${yas} yaşında`); // Ahmet 30 yaşında\n"
                        "```"
                    ),
                },
            },
            {
                "title": "JS Temel Quiz",
                "step_type": StepType.QUIZ,
                "order": 2,
                "xp_reward": 20,
                "content_data": {
                    "question": "JavaScript'te `const` ile tanımlanan bir değişken hakkında hangisi doğrudur?",
                    "options": [
                        {"id": "a", "label": "Sonradan değeri değiştirilebilir"},
                        {"id": "b", "label": "Yeniden atama yapılamaz"},
                        {"id": "c", "label": "Sadece sayılar için kullanılır"},
                        {"id": "d", "label": "Global scope'ta tanımlanır"},
                    ],
                    "correct_option": "b",
                    "hints": [
                        "JavaScript'te `const`, `let` ve `var` olmak uzere 3 tur degisken bildirimi vardir.",
                        "`const` = constant (sabit). Sabit seyler yeniden atanabilir mi?",
                        "const ile yeniden `=` atamasi yapilamaz ama dizi/obje icerigi degistirilebilir."
                    ],
                    "explanation": (
                        "`const` ile tanimlanan degiskene yeniden deger **atanamaz** (`=`).\n\n"
                        "Ancak objeler ve diziler icin ic icerik degistirilebilir:\n"
                        "```js\n"
                        "const arr = [1, 2];\n"
                        "arr.push(3);  // gecerli\n"
                        "arr = [4, 5]; // hata!\n"
                        "```"
                    ),
                },
            },
            {
                "title": "Dizi İşlemleri",
                "step_type": StepType.CODE,
                "order": 3,
                "xp_reward": 35,
                "content_data": {
                    "instruction": (
                        "Modern dizi metodlarını kullan:\n"
                        "1. `map()` ile sayıları karelerine çevir\n"
                        "2. `filter()` ile çift sayıları bul\n"
                        "3. `reduce()` ile toplam hesapla"
                    ),
                    "starter_code": (
                        "const sayilar = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];\n\n"
                        "// 1. Kareleri al\n"
                        "const kareler = sayilar.map(x => x * x);\n"
                        "console.log(\"Kareler:\", kareler);\n\n"
                        "// 2. Çiftleri filtrele\n"
                        "const ciftler = sayilar.filter(x => x % 2 === 0);\n"
                        "console.log(\"Çiftler:\", ciftler);\n\n"
                        "// 3. Toplam\n"
                        "const toplam = sayilar.reduce((acc, x) => acc + x, 0);\n"
                        "console.log(\"Toplam:\", toplam);"
                    ),
                    "solution": (
                        "const sayilar = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];\n"
                        "const kareler = sayilar.map(x => x * x);\n"
                        "console.log(\"Kareler:\", kareler);\n"
                        "const ciftler = sayilar.filter(x => x % 2 === 0);\n"
                        "console.log(\"Çiftler:\", ciftler);\n"
                        "const toplam = sayilar.reduce((acc, x) => acc + x, 0);\n"
                        "console.log(\"Toplam:\", toplam);"
                    ),
                    "expected_output": "Kareler: [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]\nÇiftler: [2, 4, 6, 8, 10]\nToplam: 55",
                    "compare_mode": "trim",
                    "hints": [
                        "`map()` her elemanı dönüştürür: `sayilar.map(x => x * x)`",
                        "`filter()` koşula uyanları seçer: `sayilar.filter(x => x % 2 === 0)`",
                        "`reduce()` tüm elemanları biriktirir: `sayilar.reduce((acc, x) => acc + x, 0)`"
                    ],
                },
            },
        ],
    },
]

# ─────────────────────────────────────────────
# COURSE 3 — SQL Essentials
# ─────────────────────────────────────────────
COURSE_SQL = {
    "title": "SQL Essentials",
    "description": (
        "Veritabanı sorgulama dilini öğren. "
        "SELECT, JOIN, GROUP BY ve alt sorgularla veriyi keşfet."
    ),
    "language": "SQL",
}

SQL_SECTIONS = [
    {
        "title": "Temel SQL Sorguları",
        "order": 0,
        "steps": [
            {
                "title": "SQL Nedir?",
                "step_type": StepType.THEORY,
                "order": 0,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "# SQL — Yapılandırılmış Sorgulama Dili\n\n"
                        "SQL (Structured Query Language), ilişkisel veritabanlarıyla "
                        "konuşmak için kullanılan evrensel dildir.\n\n"
                        "## Temel Komutlar\n\n"
                        "| Komut | İşlev |\n"
                        "|---|---|\n"
                        "| `SELECT` | Veri okuma |\n"
                        "| `INSERT` | Veri ekleme |\n"
                        "| `UPDATE` | Veri güncelleme |\n"
                        "| `DELETE` | Veri silme |\n\n"
                        "## İlk Sorgu\n\n"
                        "```sql\n"
                        "SELECT isim, yas, sehir\n"
                        "FROM kullanicilar\n"
                        "WHERE yas >= 18\n"
                        "ORDER BY isim ASC;\n"
                        "```\n\n"
                        "Bu sorgu: `kullanicilar` tablosundan 18 yaş ve üzeri "
                        "kullanıcıları isme göre sıralı listeler."
                    ),
                },
            },
            {
                "title": "WHERE ve Filtreler",
                "step_type": StepType.THEORY,
                "order": 1,
                "xp_reward": 10,
                "content_data": {
                    "body_markdown": (
                        "# WHERE ile Filtreleme\n\n"
                        "```sql\n"
                        "-- Eşitlik\n"
                        "SELECT * FROM urunler WHERE kategori = 'Elektronik';\n\n"
                        "-- Aralık\n"
                        "SELECT * FROM urunler WHERE fiyat BETWEEN 100 AND 500;\n\n"
                        "-- Liste\n"
                        "SELECT * FROM urunler WHERE marka IN ('Apple', 'Samsung', 'Xiaomi');\n\n"
                        "-- Metin arama\n"
                        "SELECT * FROM urunler WHERE ad LIKE '%telefon%';\n\n"
                        "-- Birden fazla koşul\n"
                        "SELECT *\n"
                        "FROM siparisler\n"
                        "WHERE toplam > 500\n"
                        "  AND durum = 'Tamamlandı'\n"
                        "  AND tarih >= '2024-01-01';\n"
                        "```"
                    ),
                },
            },
            {
                "title": "SQL Filtre Quiz",
                "step_type": StepType.QUIZ,
                "order": 2,
                "xp_reward": 20,
                "content_data": {
                    "question": "Fiyatı 100 ile 500 arasındaki ürünleri seçmek için hangi sorgu doğrudur?",
                    "options": [
                        {"id": "a", "label": "WHERE fiyat > 100 AND < 500"},
                        {"id": "b", "label": "WHERE fiyat BETWEEN 100 AND 500"},
                        {"id": "c", "label": "WHERE fiyat IN (100, 500)"},
                        {"id": "d", "label": "WHERE 100 < fiyat > 500"},
                    ],
                    "correct_option": "b",
                    "hints": [
                        "SQL'de bir aralığı sorgulamak için özel bir anahtar kelime vardır.",
                        "Cevap: BETWEEN. `WHERE fiyat BETWEEN 100 AND 500` yazılır.",
                        "BETWEEN 100 AND 500, 100 ve 500 dahil tüm değerleri seçer."
                    ],
                    "explanation": (
                        "`BETWEEN 100 AND 500` — 100 ve 500 **dahil** tüm değerleri seçer.\n\n"
                        "Alternatif: `WHERE fiyat >= 100 AND fiyat <= 500`\n\n"
                        "Diğer seçenekler SQL sözdizimi hatası verir."
                    ),
                },
            },
            {
                "title": "Temel SELECT Sorgusu",
                "step_type": StepType.CODE,
                "order": 3,
                "xp_reward": 30,
                "content_data": {
                    "language": "sql",
                    "instruction": (
                        "SQLite In-Memory veritabanında `users` tablosunu sorgula.\n\n"
                        "Kullanılabilir tablolar: `users`, `products`, `orders`, `categories`\n\n"
                        "**Görev:** 25 yaşından büyük kullanıcıların isim, email ve şehir bilgilerini getir."
                    ),
                    "starter_code": "SELECT name, email, city\nFROM users\nWHERE age > 25;",
                    "solution": "SELECT name, email, city FROM users WHERE age > 25;",
                    "expected_output": "name | email | city\n-------------------\nAli Yilmaz | ali@example.com | Istanbul\nAyse Demir | ayse@example.com | Ankara\nZeynep Celik | zeynep@example.com | Istanbul\nCan Ozturk | can@example.com | Bursa",
                    "compare_mode": "contains",
                    "hints": [
                        "Kullanılabilir tablolar: users, products, orders, categories",
                        "WHERE ile yaş filtresi: `WHERE age > 25`",
                        "Sadece name, email, city sütunlarını seç."
                    ],
                },
            },
        ],
    },
]


# ─────────────────────────────────────────────
# Seed fonksiyonu
# ─────────────────────────────────────────────
async def _seed_course(db, title, description, language, sections_data):
    """Bir kursu ve içeriğini veritabanına ekler, zaten varsa atlar."""
    result = await db.execute(select(Course).where(Course.title == title))
    if result.scalar_one_or_none():
        logger.info("Kurs zaten var, atlanıyor: %s", title)
        return None

    course = Course(title=title, description=description, language=language)
    db.add(course)
    await db.flush()
    await db.refresh(course)

    total_steps = 0
    for sec_data in sections_data:
        section = Section(
            course_id=course.id,
            title=sec_data["title"],
            order=sec_data["order"],
        )
        db.add(section)
        await db.flush()
        await db.refresh(section)

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
            total_steps += 1

    await db.flush()
    logger.info("Kurs oluşturuldu: %s (%d bölüm, %d adım)", title, len(sections_data), total_steps)
    return course


async def seed() -> None:
    """Ana seed fonksiyonu."""
    async with async_session_maker() as db:
        # ---- Demo kullanıcı ----
        demo_email = "demo@lumina.dev"
        result = await db.execute(select(User).where(User.email == demo_email))
        demo_user = result.scalar_one_or_none()

        if demo_user is None:
            demo_user = User(
                email=demo_email,
                hashed_password=hash_password("demopass123"),
                is_active=True,
                is_premium=False,
                is_superuser=False,
            )
            db.add(demo_user)
            await db.flush()
            await db.refresh(demo_user)
            logger.info("Demo kullanıcı oluşturuldu: %s", demo_email)
        else:
            logger.info("Demo kullanıcı mevcut: %s", demo_user.id)

        # ---- Admin kullanıcı ----
        admin_email = "admin@lumina.dev"
        result = await db.execute(select(User).where(User.email == admin_email))
        if not result.scalar_one_or_none():
            admin = User(
                email=admin_email,
                hashed_password=hash_password("adminpass123"),
                is_active=True,
                is_premium=True,
                is_superuser=True,
            )
            db.add(admin)
            logger.info("Admin kullanıcı oluşturuldu: %s", admin_email)

        # ---- UserStats ----
        stats_result = await db.execute(
            select(UserStats).where(UserStats.user_id == demo_user.id)
        )
        if stats_result.scalar_one_or_none() is None:
            db.add(UserStats(
                user_id=demo_user.id,
                total_xp=340,
                current_streak=5,
                last_active_date=date.today(),
            ))
            logger.info("UserStats oluşturuldu (340 XP, streak=5)")

        # ---- Kurslar ----
        py_course = await _seed_course(
            db, COURSE_PYTHON["title"], COURSE_PYTHON["description"],
            COURSE_PYTHON["language"], PYTHON_SECTIONS
        )
        await _seed_course(
            db, COURSE_JS["title"], COURSE_JS["description"],
            COURSE_JS["language"], JS_SECTIONS
        )
        await _seed_course(
            db, COURSE_SQL["title"], COURSE_SQL["description"],
            COURSE_SQL["language"], SQL_SECTIONS
        )

        # ---- Örnek tamamlama kaydı ----
        if py_course:
            # Python kursunun ilk 3 adımını tamamla
            from sqlalchemy.orm import selectinload
            stmt = (
                select(Course)
                .options(selectinload(Course.sections).selectinload(Section.steps))
                .where(Course.id == py_course.id)
            )
            res = await db.execute(stmt)
            loaded = res.scalar_one_or_none()
            if loaded:
                steps_flat = [s for sec in loaded.sections for s in sec.steps]
                for step in steps_flat[:4]:
                    prog_check = await db.execute(
                        select(UserProgress).where(
                            UserProgress.user_id == demo_user.id,
                            UserProgress.step_id == step.id,
                        )
                    )
                    if not prog_check.scalar_one_or_none():
                        db.add(UserProgress(
                            user_id=demo_user.id,
                            step_id=step.id,
                            is_completed=True,
                            completed_at=datetime.now(timezone.utc),
                        ))
                logger.info("İlk 4 adım tamamlandı olarak işaretlendi")

        await db.commit()
        logger.info("=" * 50)
        logger.info("SEED TAMAMLANDI!")
        logger.info("  Demo   → demo@lumina.dev   / demopass123")
        logger.info("  Admin  → admin@lumina.dev  / adminpass123")
        logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(seed())

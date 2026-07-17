<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# תצורת פלטפורמה

מסמך זה מתאר את תצורת הפלטפורמה הנדרשת להפעלת ספר המשחקים הזה.

## אפליקציות/מסגרות נדרשות

### Windows/Linux
יש להתקין את Lemonade מראש מ[כאן](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (אפליקציית ווב צד לקוח)
- **Lemonade Server** (שרת מודלים צד שרת)

> ספר המשחקים הזה מריץ את **Lemonade** (שרת/אפליקציית Lemonade) **באופן מקורי**. **Open WebUI** רץ כ**מיכל** על Linux (באמצעות Podman) וכ**חבילת Python** על Windows. חבילת ה-PyPI של `open-webui` תומכת ב-Python ≤ 3.12 בלבד, ולכן מיכל ה-Linux מונע את הצורך בניהול גרסאות Python ישנות יותר.

## מודלים (ב-Lemonade)

יש להוריד מודלים בתוך **אפליקציית Lemonade** (באמצעות מנהל המודלים המובנה) או דרך פקודות ניהול המודלים של Lemonade‏ (`lemonade pull <model_name>`). ספר המשחקים הזה מניח שהמודלים המומלצים שלהלן הורדו ומופיעים בנקודת הקצה של רשימת המודלים.

בדיקת זמינות מודלים:
- פתח: `http://localhost:13305/api/v1/models`
- המודלים שהורדו יופיעו תחת `"data"`.

### מודלים מומלצים

| יכולת | מזהה מודל | הערות |
|---|----|-----|
| LLM (קלט טקסט ← פלט טקסט) | `Qwen3-4B-Hybrid` (או דומה) | כל מודל LLM של Lemonade לצ'אט, השלמת טקסט, קידוד או הסקה |
| VLM (תמונה ← טקסט) | `Qwen3.5-4B-GGUF` (או כל מודל בקטגוריית **Vision**) | כל מודל רב-מודאלי/בעל יכולת ראייה שיכול לקבל תמונות כחלק מהקלט שלו |
| יצירת תמונות (טקסט ← תמונה) | `SDXL-Turbo` (או כל מודל בקטגוריית **Image**) | כל מודל Stable Diffusion שמייצר תמונות מהנחיית טקסט |
| שמע (דיבור ← טקסט) | `Whisper-Large-v3` (או כל מודל בקטגוריית **Audio**) | כל מודל ASR שממיר שמע לטקסט |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## פורטים בשימוש

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

אם פורטים אלה כבר בשימוש במערכת שלך, שנה אותם בעת הפעלת השרת/ים.
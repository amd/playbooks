<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# תצורת פלטפורמה

מסמך זה מתאר את תצורת הפלטפורמה הצפויה להרצת playbook זה.

## אפליקציות/מסגרות עבודה נדרשות

### Windows/Linux
יש להתקין מראש את Lemonade מ[כאן](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (אפליקציית web מסוג frontend)
- **Lemonade Server** (שרת מודלים מסוג backend)

> ה-playbook הזה מריץ את **Lemonade** (שרת/אפליקציית Lemonade) **באופן native**. **Open WebUI** רץ כ-**container** ב-Linux (דרך Podman) וכ-**חבילת Python** ב-Windows. חבילת ה-PyPI בשם `open-webui` תומכת רק בגרסאות Python ≤ 3.12, כך שה-container ב-Linux מונע את הצורך לנהל גרסאות Python ישנות יותר.

## מודלים (ב-Lemonade)

יש להוריד מודלים בתוך **אפליקציית Lemonade** (באמצעות Model Manager המובנה) או דרך פקודות ניהול המודלים של Lemonade (`lemonade pull <model_name>`). ה-playbook הזה מניח שהמודלים המומלצים הבאים הורדו ומופיעים ברשימת ה-endpoint של המודלים.

בדיקת זמינות מודלים:
- פתיחה: `http://localhost:13305/api/v1/models`
- מודלים שהורדו יופיעו תחת `"data"`.

### מודלים מומלצים

| יכולת | מזהה מודל | הערות |
|---|----|-----|
| LLM (קלט טקסט → פלט טקסט) | `Qwen3-4B-Hybrid` (או דומה) | כל מודל LLM של Lemonade לצ'אט, השלמת טקסט, קידוד או הסקה |
| VLM (תמונה → טקסט) | `Qwen3.5-4B-GGUF` (או כל מודל בקטגוריית **Vision**) | כל מודל multimodal/בעל יכולת ראייה שיכול לקבל תמונות כחלק מהקלט שלו |
| יצירת תמונות (טקסט → תמונה) | `SDXL-Turbo` (או כל מודל בקטגוריית **Image**) | כל מודל Stable Diffusion שיוצר תמונות עבור prompt טקסטואלי |
| שמע (דיבור → טקסט) | `Whisper-Large-v3` (או כל מודל בקטגוריית **Audio**) | כל מודל ASR הממיר שמע לטקסט |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## יציאות (Ports) בשימוש

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

אם היציאות הללו כבר נמצאות בשימוש במערכת שלך, יש לשנות אותן בעת הפעלת השרת/שרתים.
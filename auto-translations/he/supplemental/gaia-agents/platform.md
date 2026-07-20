<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# תצורת פלטפורמה

מסמך זה מתאר את תצורות הפלטפורמה הצפויות להרצת playbook זה.

## אפליקציות/מסגרות עבודה נדרשות

### Windows/Linux

GAIA צריך להיות מותקן מראש באמצעות ההוראות המסופקות ב-[מדריך התקנת GAIA](../../dependencies/gaia.md).

Lemonade Server צריך להיות מותקן מראש באמצעות ההוראות המסופקות ב-[מדריך התקנת Lemonade](../../dependencies/lemonade.md).

## מודלים נדרשים

### Windows/Linux

סוכן Hardware Advisor Agent משתמש ב-**Qwen3-Coder-30B** להיסק של הסוכן. מודל זה מורד באופן אוטומטי במהלך `gaia init`. אין צורך בהורדות ידניות של מודלים.
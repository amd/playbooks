<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. הורד את מתקין ComfyUI העדכני ל-Windows מ-[download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. בחר את הגדרת החומרה שלך: בחר `AMD ROCm`.
3. בחר היכן להתקין את ComfyUI: השתמש בנתיב ברירת המחדל או בתיקייה המועדפת עליך.
4. הגדרות אפליקציית שולחן העבודה: אנו ממליצים לבטל את הסימון של "עדכונים אוטומטיים" כדי להבטיח שאתה משתמש בגרסה המומלצת של אפליקציה זו.
5. לחץ על "Next" כדי להתחיל בהתקנה.

<!-- @os:end -->

<!-- @os:linux -->
#### שכפל את ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (אופציונלי) בדוק גרסה ספציפית
```bash
git checkout v0.19.2
```

#### התקן את דרישות ComfyUI

כאשר סביבת Python הווירטואלית מופעלת, הרץ:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **הערה**: ראה [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) למידע נוסף.

<!-- @os:end -->
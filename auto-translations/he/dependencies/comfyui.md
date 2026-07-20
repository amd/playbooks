<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. הורידו את מתקין ה-Windows העדכני ביותר של ComfyUI מ-[download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. בחרו את תצורת החומרה שלכם: בחרו ב-`AMD ROCm`.
3. בחרו היכן להתקין את ComfyUI: השתמשו בנתיב ברירת המחדל או בתיקייה המועדפת עליכם.
4. הגדרות אפליקציית שולחן העבודה: אנו ממליצים לבטל את הסימון של "Automatic Updates" כדי להבטיח שאתם משתמשים בגרסה המומלצת של אפליקציה זו.
5. לחצו על "Next" כדי להתחיל בהתקנה.

<!-- @os:end -->

<!-- @os:linux -->
#### שכפלו את ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (אופציונלי) עברו לגרסה ספציפית
```bash
git checkout v0.19.2
```

#### התקינו את הדרישות של ComfyUI

לאחר הפעלת סביבת ה-Python הווירטואלית, הריצו:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **הערה**: ראו [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) למידע נוסף.

<!-- @os:end -->
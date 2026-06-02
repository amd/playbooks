import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const PLAYBOOKS_ROOT = path.join(process.cwd(), "..", "playbooks");
const CATEGORY_ORDER: Record<string, number> = { core: 0, supplemental: 1, backup: 2 };
const HARDWARE_LABELS: Record<string, string> = {
  halo: "STX Halo",
  stx: "STX Point",
  krk: "Krackan Point",
  rx7900xt: "Radeon RX 7900 XT",
  rx9070xt: "Radeon RX 9070 XT",
};

interface PlaybookMeta {
  id: string;
  title?: string;
  published_platforms?: Record<string, string[] | undefined>;
  developed?: boolean;
  published?: boolean;
}

interface PlaybookRow {
  playbookId: string;
  title: string;
  category: string;
  releasedCombos: string[];
}

function normalizePlatform(platform: string): string {
  return platform.toLowerCase() === "windows" ? "windows" : "linux";
}

function combinationId(arch: string, platform: string): string {
  return `${arch.toLowerCase()}|${normalizePlatform(platform)}`;
}

function combinationLabel(arch: string): string {
  const normalizedArch = arch.toLowerCase();
  return HARDWARE_LABELS[normalizedArch] ?? arch;
}

function loadPlaybooks(): PlaybookRow[] {
  const categories = ["core", "supplemental", "backup"];
  const rows: PlaybookRow[] = [];

  for (const category of categories) {
    const categoryPath = path.join(PLAYBOOKS_ROOT, category);
    if (!fs.existsSync(categoryPath)) continue;
    const folders = fs.readdirSync(categoryPath, { withFileTypes: true });

    for (const folder of folders) {
      if (!folder.isDirectory()) continue;
      const jsonPath = path.join(categoryPath, folder.name, "playbook.json");
      if (!fs.existsSync(jsonPath)) continue;

      try {
        const meta = JSON.parse(fs.readFileSync(jsonPath, "utf-8")) as PlaybookMeta;
        if (meta.published === false) continue;

        const combos: string[] = [];
        const released = meta.published_platforms ?? {};
        for (const [device, platformList] of Object.entries(released)) {
          for (const platform of platformList ?? []) {
            combos.push(combinationId(device, platform));
          }
        }

        rows.push({
          playbookId: meta.id,
          title: meta.title || meta.id,
          category,
          releasedCombos: Array.from(new Set(combos)),
        });
      } catch {
        // Ignore unreadable playbooks
      }
    }
  }

  rows.sort((a, b) => {
    const categoryDiff = (CATEGORY_ORDER[a.category] ?? 99) - (CATEGORY_ORDER[b.category] ?? 99);
    if (categoryDiff !== 0) return categoryDiff;
    return a.title.localeCompare(b.title);
  });

  return rows;
}

export async function GET() {
  try {
    const playbooks = loadPlaybooks();

    // Columns are the union of every device/OS combo that at least one
    // playbook has been released on.
    const comboIds = new Set<string>();
    for (const pb of playbooks) {
      for (const combo of pb.releasedCombos) comboIds.add(combo);
    }

    const columns = Array.from(comboIds)
      .map((comboId) => {
        const [arch, platform] = comboId.split("|");
        return {
          id: comboId,
          arch,
          platform,
          hardware: combinationLabel(arch),
          os: platform === "windows" ? "Windows" : "Linux",
        };
      })
      .sort((a, b) => {
        const hwA = Object.keys(HARDWARE_LABELS).indexOf(a.arch);
        const hwB = Object.keys(HARDWARE_LABELS).indexOf(b.arch);
        const hwOrderA = hwA === -1 ? 999 : hwA;
        const hwOrderB = hwB === -1 ? 999 : hwB;
        if (hwOrderA !== hwOrderB) return hwOrderA - hwOrderB;
        if (a.hardware !== b.hardware) return a.hardware.localeCompare(b.hardware);
        return a.os.localeCompare(b.os);
      });

    const rows = playbooks.map((pb) => ({
      playbookId: pb.playbookId,
      title: pb.title,
      category: pb.category,
      releasedCombos: pb.releasedCombos,
    }));

    return NextResponse.json({ columns, rows });
  } catch (error) {
    console.error("Failed to build published matrix:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to build published matrix" },
      { status: 500 }
    );
  }
}

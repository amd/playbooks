<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Proposal: Generic Content Toggles for Playbooks

## Summary

Add a generic **content-toggle** mechanism to the playbook renderer, parallel to
the existing `@device` and `@os` selectors. A playbook declares one or more
toggle groups (e.g. **Nodes: 2 / 4**, **Interconnect: Ethernet / USB4**); content
is wrapped in `@toggle:<id>=<value>` blocks and filtered by the active selection.
Groups may declare **constraints** that restrict other groups *or the built-in OS
selector* (e.g. selecting USB4 locks Nodes to 2 and OS to Linux).

This lets several near-duplicate playbooks collapse into one. It has been used to
merge the clustering playbooks from **5 → 2**:

| Before | After |
|--------|-------|
| `clustering-rccl` (2-node), `clustering-rccl-4-node` | **`clustering-rccl`** with a Nodes toggle |
| `clustering-rpc-server` (eth 2), `clustering-rpc-server-4-node` (eth 4), `clustering-rpc-server-usb` (usb 2) | **`clustering-rpc-server`** with Interconnect + Nodes toggles |

A working reference implementation lives in this branch (see **Reference
implementation** below). The web team needs to mirror the same data schema, tag
syntax, filter logic, and constraint handling in the production renderer.

## 1. Declaration (in `playbook.json`)

```jsonc
"toggles": [
  {
    "id": "link",
    "label": "Interconnect",
    "default": "ethernet",
    "options": [
      { "value": "ethernet", "label": "Ethernet" },
      { "value": "usb4",     "label": "USB4" }
    ],
    "constraints": [
      { "when": "usb4", "restrict": { "nodes": ["2"], "os": ["linux"] } }
    ]
  },
  {
    "id": "nodes",
    "label": "Nodes",
    "default": "2",
    "options": [
      { "value": "2", "label": "2 Nodes" },
      { "value": "4", "label": "4 Nodes" }
    ]
  }
]
```

- `id` — stable key used in the content tags.
- `options[].value` — the token used in `@toggle:<id>=<value>`.
- `default` — initial selection.
- `constraints[]` — optional. When this group's value equals `when`, each key in
  `restrict` is limited to the listed values. A key is **another toggle group id**
  or the reserved dimension **`os`** (values `"windows"` / `"linux"`). Restricted
  options are disabled (greyed out) in the UI, and the active selection snaps to
  an allowed value.

## 2. Content tags (in the README)

Mirrors `@device` / `@os` exactly, including nesting and comma-separated values:

```markdown
<!-- @toggle:nodes=4 --> ...4-node-only content... <!-- @toggle:end -->
<!-- @toggle:link=usb4 --> ...USB4-only content... <!-- @toggle:end -->
<!-- @toggle:nodes=2,4 --> ...shown for either node count... <!-- @toggle:end -->
```

Blocks nest (link wrapping nodes) for regions that vary on both axes:

```markdown
<!-- @toggle:link=ethernet -->
  <!-- @toggle:nodes=2 --> ...ethernet 2-node... <!-- @toggle:end -->
  <!-- @toggle:nodes=4 --> ...ethernet 4-node... <!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
  ...usb4 (2-node, Linux)...
<!-- @toggle:end -->
```

## 3. Filter semantics

A block `@toggle:<id>=<v1,v2,...>` is **kept** when:
- its group `id` is **not** an active group (unknown/ungated → keep), **or**
- the active value for that group is in the block's value list.

Otherwise it is dropped. Process innermost blocks first (iterate to a fixed
point), identical to the existing `filterContentByDevice` / `filterContentByOS`.
Apply the toggle filter **before** the OS and device filters.

## 4. Constraint behavior (UI)

Given the current selections, compute the set of restricted dimensions. For each
restricted dimension:
- If it's a toggle group, disable its non-allowed option buttons; if the current
  value is disallowed, snap to the first allowed value.
- If it's `os`, disable the corresponding button in the existing OS selector and
  snap `selectedPlatform` to an allowed value.

Example: with `link = usb4`, the constraint `{ nodes: ["2"], os: ["linux"] }`
disables the **4 Nodes** button and the **Windows** button, and forces selections
to 2 / Linux.

## 5. Reference implementation (this branch)

Front end (`website/src/`):
- `types/playbook.ts` — `ToggleGroupDef`, `ToggleOption`, `ToggleConstraint`,
  and the `toggles?` field on `PlaybookMeta`.
- `app/playbooks/[id]/page.tsx`:
  - `filterContentByToggles(content, selections)` — the content filter.
  - `ToggleGroup` component — the button group (supports `disabledValues`).
  - `PlatformToggle` — extended with `disabledPlatforms`.
  - `selectedToggles` state, a `restrictedDims` memo, and two effects that seed
    defaults and enforce constraints.
  - Toggle filter threaded into the content pipeline; toggle bar added to the
    selector UI.

Content:
- `playbooks/supplemental/clustering-rccl/` — Nodes toggle.
- `playbooks/supplemental/clustering-rpc-server/` — Interconnect + Nodes toggles,
  with the USB4 → {nodes=2, os=linux} constraint.

## 6. Correctness guarantee

The merges are **lossless by construction** (a 3-way line merge) and were
verified mechanically: filtering each merged README to a given toggle
combination reproduces the corresponding original playbook **exactly** — zero
missing lines, zero foreign content:

| Combination | Reproduces |
|-------------|------------|
| RCCL nodes=2 / nodes=4 | the original 2-node / 4-node RCCL READMEs |
| RPC link=ethernet nodes=2 | original `clustering-rpc-server` |
| RPC link=ethernet nodes=4 | original `clustering-rpc-server-4-node` |
| RPC link=usb4 nodes=2 (os=linux) | original `clustering-rpc-server-usb` |

## 7. Migration notes

- The three now-redundant source playbooks (`clustering-rccl-4-node`,
  `clustering-rpc-server-4-node`, `clustering-rpc-server-usb`) are set
  `"published": false` and carry `_consolidatedInto`. They can be deleted once
  production adopts toggles; their content is fully preserved in the merged
  playbooks and in git history.

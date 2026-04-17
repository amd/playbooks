<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# AMD Branding Guide

This guide outlines the correct usage of AMD product names and trademarks in all documentation, playbooks, and content within this repository.

## General Rules

### 1. First Mention Rule
- **First mention** on any page: Use the full product name with the trademark symbol (™)
- **Subsequent mentions** on the same page: Use the shortened name without the trademark symbol

### 2. Trademark Symbol
- Always use the Unicode escape `\u2122` in JSON files instead of typing ™ directly
- In Markdown files, you can use either ™ or `\u2122`

## Product Names and Acceptable Shortened Forms

### Hardware Platforms

#### STX Halo (Device ID: `halo`)
- **First mention:** AMD Ryzen™ AI Max+
- **Subsequent:** Ryzen AI Max+, Halo platform, or Halo

#### STX Point (Device ID: `stx`)
- **First mention:** AMD Ryzen™ AI 300 HX
- **Subsequent:** Ryzen AI 300 HX or STX Point

#### Krackan Point (Device ID: `krk`)
- **First mention:** AMD Ryzen™ AI 300
- **Subsequent:** Ryzen AI 300 or Krackan Point

#### Radeon RX 7900 XT (Device ID: `rx7900xt`)
- **First mention:** AMD Radeon™ 7000 Series Graphics
- **Subsequent:** Radeon 7000 Series or RX 7900 XT

#### Radeon RX 9070 XT (Device ID: `rx9070xt`)
- **First mention:** AMD Radeon™ 9000 Series Graphics
- **Subsequent:** Radeon 9000 Series or RX 9070 XT

### Software and Platforms

#### ROCm
- **First mention:** AMD ROCm™ software or AMD ROCm™ platform
- **Subsequent:** ROCm software, ROCm platform, or ROCm

#### Graphics Software
- **First mention:** AMD Software: Adrenalin Edition™
- **Subsequent:** Adrenalin Edition or AMD Software

## Usage Examples

### ✅ Correct Usage

**Playbook Description:**
```markdown
This guide shows how to set up machine learning workflows on the AMD Ryzen™ Halo platform. 
The Halo platform provides powerful AI acceleration for local development.
```

**JSON File:**
```json
{
  "description": "Deploy ML models using AMD ROCm\u2122 software for GPU acceleration. ROCm provides optimized performance for AI workloads."
}
```

## Common Mistakes to Avoid

1. **Inconsistent naming:** Don't switch between different shortened forms on the same page
2. **Missing trademarks:** Always include ™ on first mention
3. **Overusing trademarks:** Don't use ™ on every mention after the first
4. **JSON encoding:** Use `\u2122` instead of ™ in JSON files
5. **Generic references:** Avoid vague terms like "the platform" when the specific product name adds clarity
6. **Possessive forms:** Never use possessive forms of AMD (e.g., "AMD's ROCm"). Use "AMD ROCm Software" instead of "AMD's ROCm"

## Checklist for Contributors

Before submitting content, verify:

- [ ] First mention of each AMD product includes full name with ™
- [ ] Subsequent mentions use appropriate shortened forms
- [ ] JSON files use `\u2122` for trademark symbols
- [ ] Product names are spelled correctly and consistently
- [ ] Device tags use correct shortened names
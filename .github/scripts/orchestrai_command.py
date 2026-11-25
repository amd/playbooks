#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
The !orc PR command
===================

Parses the first line of an `!orc` comment and resolves which playbooks to test,
in which languages, on which devices and OSes:

    !orc                                   the playbooks the PR changed, each in
                                           the language it changed in
    !orc all                               every English playbook
    !orc a,b c                             the named playbooks, in English
    !orc a locale=zh-CN                    a's zh-CN version
    !orc a locale=en,zh-CN                 both, in the same batches
    !orc all locale=all                    every playbook in English and in
                                           every locale under localized-playbooks/
    !orc locale=zh-CN                      the changed playbooks that have a zh-CN
                                           version, English or zh-CN changes alike
                                           (a localized playbook runs its English
                                           version's tests)
    !orc a device=halo,stx platform=linux  only those devices and OSes

`!localized-orc`, the command from before `locale=`, still works as it did:

    !localized-orc                         the localized playbooks the PR
                                           changed, in the one locale it changed
    !localized-orc zh-CN                   the zh-CN playbooks the PR changed
    !localized-orc zh-CN all|a,b           those zh-CN playbooks
    !localized-orc all|a,b                 those playbooks in the repo's only locale

Options may come in any order; `locales=`, `devices=` and `platforms=` work too.
English is `en`. A locale, device, OS or playbook that does not exist is an
error, so a typo fails the command instead of testing nothing.

Run with the PR head as the working directory. Env:
    BODY      the comment
    CHANGED   files the PR changed, one per line (used by a bare !orc)
    ORCHESTRAI_DEVICE_TAGS  optional device -> tags map; its devices are known too

Writes to $GITHUB_OUTPUT:
    languages  {"": [...], "zh-CN": [...]}: playbook IDs by locale ("" = English)
    devices    comma-separated, empty = every device
    platforms  comma-separated, empty = every OS
    filters    one line for the PR comment, e.g. "locales: en, zh-CN · devices: halo"
    error      the reason, when the command is refused (exit 1)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml

COMMAND = "!orc"
LOCALIZED_COMMAND = "!localized-orc"
CATEGORIES = ("core", "supplemental")
PLATFORMS = ("linux", "windows")
OPTION_NAMES = {
    "locale": "locales", "locales": "locales",
    "device": "devices", "devices": "devices",
    "platform": "platforms", "platforms": "platforms",
}
LOCALE_RE = re.compile(r"^[A-Za-z0-9]+(-[A-Za-z0-9]+)*$")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ENGLISH_PATH = re.compile(r"^playbooks/(?:core|supplemental)/([^/]+)/")
LOCALIZED_PATH = re.compile(r"^localized-playbooks/([^/]+)/(?:core|supplemental)/([^/]+)/")


class CommandError(ValueError):
    """The command cannot run; the message says why, for the PR comment."""


def parse(body):
    """(playbook names or "all" or None, options) of a command's first line.
    options maps locales/devices/platforms to lists of values."""
    line = (body or "").splitlines()[0] if (body or "").strip() else ""
    words = line.strip().split()
    if not words or words[0] != COMMAND:
        raise CommandError(f"not an `{COMMAND}` command: `{line.strip()[:80]}`")
    names, options = [], {}
    for word in words[1:]:
        if "=" in word:
            key, _, value = word.partition("=")
            option = OPTION_NAMES.get(key.lower())
            if option is None:
                raise CommandError(f"unknown option `{key}=` (use locale=, device= or platform=)")
            values = [v for v in value.split(",") if v]
            if not values:
                raise CommandError(f"`{key}=` needs a value")
            merged = options.setdefault(option, [])
            merged.extend(v for v in values if v not in merged)
        else:
            names.extend(n for n in word.split(",") if n and n not in names)
    if "all" in names:
        if len(names) > 1:
            raise CommandError("`all` cannot be combined with playbook names")
        return "all", options
    for name in names:
        if not NAME_RE.match(name):
            raise CommandError(f"not a playbook ID: `{name}`")
    return (names or None), options


def available_locales(root):
    base = Path(root) / "localized-playbooks"
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir() and LOCALE_RE.match(p.name))


def playbooks_in(root, locale=""):
    """Playbook IDs that exist in a language ("" = English)."""
    base = Path(root) / ("localized-playbooks/" + locale if locale else "playbooks")
    return sorted({p.name for cat in CATEGORIES if (base / cat).is_dir()
                   for p in (base / cat).iterdir() if p.is_dir()})


def resolve_locales(values, root):
    """Requested locales ("" = English), in order; "all" = English and every locale."""
    available = available_locales(root)
    locales = []
    for value in values:
        if value.lower() == "all":
            wanted = [""] + available
        elif value.lower() == "en":
            wanted = [""]
        elif LOCALE_RE.match(value) and value in available:
            wanted = [value]
        else:
            raise CommandError(f"unknown locale `{value}` (available: en, {', '.join(available)})"
                               if available else f"unknown locale `{value}` (available: en)")
        locales.extend(loc for loc in wanted if loc not in locales)
    return locales


def known_devices(config_path):
    cfg = yaml.safe_load(Path(config_path).read_text()) or {}
    known = set(cfg.get("device_to_tags") or {}) | set(cfg.get("device_to_gfx") or {})
    try:
        known |= set(json.loads(os.environ.get("ORCHESTRAI_DEVICE_TAGS") or "{}"))
    except (json.JSONDecodeError, TypeError):
        pass
    return known


def resolve_filters(values, known, what):
    values = [v.lower() for v in values]
    unknown = [v for v in values if v not in known]
    if unknown:
        raise CommandError(f"unknown {what} `{', '.join(unknown)}` "
                           f"(known: {', '.join(sorted(known))})")
    return values


def changed_playbooks(changed):
    """{locale: {playbook IDs}} the PR changed ("" = English)."""
    by_locale = {}
    for path in (changed or "").splitlines():
        path = path.strip()
        if m := ENGLISH_PATH.match(path):
            by_locale.setdefault("", set()).add(m.group(1))
        elif m := LOCALIZED_PATH.match(path):
            by_locale.setdefault(m.group(1), set()).add(m.group(2))
    return by_locale


def parse_localized(body, changed, root):
    """parse() for `!localized-orc [<locale>] [all|a,b]`: one locale, and with
    no playbooks named, only the playbooks the PR changed in that locale."""
    words = body.splitlines()[0].split()[1:]
    available = available_locales(root)

    def changed_in(locale):  # a playbook the PR deleted is not tested
        ids = changed_playbooks(changed).get(locale, set()) & set(playbooks_in(root, locale))
        return sorted(ids), {"locales": [locale]}

    if len(words) >= 2:  # <locale> all|a,b
        return parse(f"{COMMAND} {' '.join(words[1:])} locale={words[0]}")
    if words and words[0] in available:  # <locale>
        return changed_in(words[0])
    if words:  # all|a,b in the only locale
        if len(available) != 1:
            raise CommandError(f"name the locale: `{LOCALIZED_COMMAND} <locale> {words[0]}` "
                               f"(available: {', '.join(available) or 'none'})")
        return parse(f"{COMMAND} {words[0]} locale={available[0]}")
    changed_locales = sorted(loc for loc in changed_playbooks(changed) if loc)
    if not changed_locales:
        return [], {}  # nothing to test
    if len(changed_locales) > 1:
        raise CommandError(
            f"the PR changes localized playbooks in {', '.join(changed_locales)}; "
            f"name one (`{LOCALIZED_COMMAND} <locale>`) or use `{COMMAND}`, which tests them all")
    return changed_in(changed_locales[0])


def resolve(body, changed, root, config_path):
    """(languages, devices, platforms, filters, notes) for one command."""
    words = (body or "").strip().split(None, 1)
    if words and words[0] == LOCALIZED_COMMAND:
        selection, options = parse_localized(body.strip(), changed, root)
    else:
        selection, options = parse(body)
    devices = resolve_filters(options.get("devices", []), known_devices(config_path), "device")
    platforms = resolve_filters(options.get("platforms", []), set(PLATFORMS), "platform")
    locales = resolve_locales(options["locales"], root) if "locales" in options else None
    notes = []

    if selection is None:  # the playbooks the PR changed
        by_locale = changed_playbooks(changed)
        if locales is None:
            languages = {loc: sorted(ids) for loc, ids in by_locale.items()}
        else:
            english = by_locale.get("", set())
            languages = {loc: sorted((english | by_locale.get(loc, set()))
                                     & set(playbooks_in(root, loc))) if loc else sorted(english)
                         for loc in locales}
    else:
        locales = locales or [""]
        languages = {}
        for loc in locales:
            present = set(playbooks_in(root, loc))
            languages[loc] = (sorted(present) if selection == "all"
                              else [n for n in selection if n in present])
        if selection != "all":
            unknown = [n for n in selection if not any(n in ids for ids in languages.values())]
            if unknown:
                where = ", ".join(loc or "en" for loc in locales)
                raise CommandError(f"no such playbook in {where}: `{', '.join(unknown)}`")
            for loc in locales:
                missing = [n for n in selection if n not in languages[loc]]
                if missing:
                    notes.append(f"not in {loc or 'en'}: {', '.join(missing)}")

    languages = {loc: ids for loc, ids in languages.items() if ids}
    filters = []
    if "locales" in options:
        filters.append("locales: " + ", ".join(loc or "en" for loc in locales))
    if devices:
        filters.append("devices: " + ", ".join(devices))
    if platforms:
        filters.append("platforms: " + ", ".join(platforms))
    return languages, devices, platforms, " · ".join(filters), notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="the controller's orchestrai-config.yml")
    ap.add_argument("--root", default=".", help="the PR head checkout")
    args = ap.parse_args()

    outputs = {}
    try:
        languages, devices, platforms, filters, notes = resolve(
            os.environ.get("BODY", ""), os.environ.get("CHANGED", ""), args.root, args.config)
        outputs.update(languages=json.dumps(languages), devices=",".join(devices),
                       platforms=",".join(platforms), filters=filters)
        for note in notes:
            print(f"::notice::{note}")
        for loc, ids in languages.items():
            print(f"{loc or 'en'}: {', '.join(ids)}")
        if not languages:
            print("No playbooks to test")
        rc = 0
    except CommandError as exc:
        print(f"::error::{exc}")
        outputs["error"] = str(exc).replace("\n", " ")
        rc = 1

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            for key, value in outputs.items():
                f.write(f"{key}={value}\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())

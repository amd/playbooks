#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Names for the playbooks of one OrchestrAI batch
===============================================

A batch runs English and localized playbooks on the same machine, so one
playbook ID can appear twice in it. Each member therefore has a key:

    comfyui-image-gen          the English playbook
    zh-CN/comfyui-image-gen    its zh-CN version

and each key one plan group, whose ID the pipeline reports results under:

    playbook-comfyui-image-gen
    playbook-zh-CN-comfyui-image-gen
"""


def member_key(playbook, locale=""):
    """The batch member key of a playbook in a locale ("" = English)."""
    return f"{locale}/{playbook}" if locale else playbook


def split_key(key):
    """(locale, playbook) of a batch member key; locale is "" for English."""
    locale, _, playbook = key.rpartition("/")
    return locale, playbook


def group_id(key):
    """The plan group ID of a batch member, as the pipeline reports it."""
    locale, playbook = split_key(key)
    return f"playbook-{locale}-{playbook}" if locale else f"playbook-{playbook}"

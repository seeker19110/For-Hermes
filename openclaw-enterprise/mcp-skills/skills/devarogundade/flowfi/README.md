# OpenClaw skill – FlowFi

This folder contains an **OpenClaw skill** for interacting with the FlowFi backend from an OpenClaw agent.

## Purpose

When an OpenClaw agent (e.g. invoked from a FlowFi OpenClaw node) needs to:

- Create, read, or update workflows
- Deploy workflows or run lifecycle actions
- Call the FlowFi API for automation

…it can use this skill so the agent knows how to authenticate (Bearer token) and which endpoints to use.

## Contents

- **SKILL.md** – Main skill instructions for the agent
- **nodes.md** – FlowFi node reference (including the OpenClaw node)
- **reference.md** – API and usage reference

## Usage

This skill is intended for project or personal Cursor/OpenClaw use. Point the agent at this folder (or install it under `.cursor/skills/` or your OpenClaw skills path) so it can follow the FlowFi API and OpenClaw node behavior described in these files.

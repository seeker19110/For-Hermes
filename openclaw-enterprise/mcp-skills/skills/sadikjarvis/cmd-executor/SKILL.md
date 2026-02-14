# Cmd Executor

## Overview
Cmd Executor is an OpenClaw skill that allows a user to run local Windows shell
commands on the machine where the OpenClaw gateway is running.

This skill is intended for personal automation, debugging, and local system
management through OpenClaw.

## What this skill does
- Executes a Windows command provided by the user
- Captures standard output and standard error
- Returns the result back to the chat interface

## Supported platform
- Windows (PowerShell / CMD)

## Usage

Send a message starting with:

Run command: <your command>

Example:

Run command: dir "C:\Users\Md Sadik Laskar\Documents"

## Security notice

This skill can execute arbitrary local commands.
Only install and use this skill in a trusted environment.

Do NOT expose this skill to untrusted users.

## Typical use cases

- Listing files and folders
- Running local scripts
- Checking system tools and utilities

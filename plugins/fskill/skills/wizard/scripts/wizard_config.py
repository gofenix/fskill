#!/usr/bin/env python3
"""Read/upsert a conservative dotenv subset; values enter through stdin.

No shell evaluation, interpolation, escapes, export, duplicates or multiline
assignments. Unrelated lines are preserved. Unix directory descriptors keep
symlinks out of the destination path; replacement is atomic, not a concurrent
editor merge. `get` writes only to a pipe, never an interactive terminal.
"""

import argparse
import os
from pathlib import Path
import re
import secrets
import stat
import sys


KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
ASSIGNMENT = re.compile(r"[ \t]*([A-Za-z_][A-Za-z0-9_]*)[ \t]*=(.*)\Z")


class ConfigError(Exception):
    pass


def _literal(value):
    if any(ord(char) < 32 or char in "\\$'\x85\u2028\u2029" for char in value):
        raise ConfigError("value requires the project's dotenv parser")
    return value


def parse(text):
    values, locations = {}, {}
    for index, line in enumerate(text.splitlines(keepends=True)):
        body = line.rstrip("\r\n")
        if not body.strip() or body.lstrip().startswith("#"):
            continue
        match = ASSIGNMENT.fullmatch(body)
        if not match:
            raise ConfigError(f"unsupported syntax at line {index + 1}")
        key, raw = match.groups()
        if key in values:
            raise ConfigError(f"duplicate key at line {index + 1}")
        if raw.startswith(("'", '"')):
            quote = raw[0]
            if len(raw) < 2 or raw[-1] != quote or quote in raw[1:-1]:
                raise ConfigError(f"unsupported quoting at line {index + 1}")
            value = _literal(raw[1:-1])
        else:
            if any(char.isspace() or char in "#\"'" for char in raw):
                raise ConfigError(f"unsupported unquoted value at line {index + 1}")
            value = _literal(raw)
        values[key] = value
        locations[key] = index
    return values, locations


def _parent(path):
    absolute = Path(os.path.abspath(path))
    if absolute.name in ("", ".", ".."):
        raise ConfigError("a config filename is required")
    descriptor = os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in absolute.parent.parts[1:]:
            next_descriptor = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = next_descriptor
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor, absolute.name


def _load(parent, name):
    try:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    except FileNotFoundError:
        return None, ""
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise ConfigError("config must be a regular file owned by this user")
        if info.st_nlink != 1:
            raise ConfigError("hard-linked config is unsupported")
        text = stream.read().decode("utf-8")
    fingerprint = (info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size, info.st_mode)
    return fingerprint, text


def read_value(path, key):
    if not KEY.fullmatch(key):
        raise ConfigError("invalid key")
    parent, name = _parent(path)
    try:
        _, text = _load(parent, name)
        return parse(text)[0].get(key, "")
    finally:
        os.close(parent)


def write_value(path, key, value):
    if not KEY.fullmatch(key):
        raise ConfigError("invalid key")
    _literal(value)
    parent, name = _parent(path)
    temporary = None
    try:
        fingerprint, text = _load(parent, name)
        _, locations = parse(text)
        lines = text.splitlines(keepends=True)
        newline = "\r\n" if "\r\n" in text else "\n"
        replacement = f"{key}='{value}'"
        if key in locations:
            index = locations[key]
            previous = lines[index]
            ending = "\r\n" if previous.endswith("\r\n") else "\n" if previous.endswith("\n") else ""
            lines[index] = replacement + ending
            updated = "".join(lines)
        else:
            updated = text + (newline if text and not text.endswith("\n") else "")
            updated += replacement + newline
        temporary = f".{name}.fskill-{secrets.token_hex(8)}.tmp"
        descriptor = os.open(
            temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600, dir_fd=parent,
        )
        with os.fdopen(descriptor, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(updated.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        if _load(parent, name) != (fingerprint, text):
            raise ConfigError("config changed during update; rerun after resolving it")
        os.replace(temporary, name, src_dir_fd=parent, dst_dir_fd=parent)
        temporary = None
        os.fsync(parent)
        if parse(_load(parent, name)[1])[0].get(key) != value:
            raise ConfigError("config readback failed")
    finally:
        if temporary is not None:
            os.unlink(temporary, dir_fd=parent)
        os.close(parent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("get", "upsert"))
    parser.add_argument("file")
    parser.add_argument("key")
    args = parser.parse_args()
    try:
        if args.operation == "get":
            if sys.stdout.isatty():
                raise ConfigError("get requires a pipe; values must not be displayed")
            sys.stdout.write(read_value(args.file, args.key))
        else:
            write_value(args.file, args.key, sys.stdin.read())
    except (ConfigError, OSError, UnicodeError) as error:
        if isinstance(error, ConfigError):
            message = str(error)
        else:
            message = "cannot safely read or write config"
        print(f"wizard config: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

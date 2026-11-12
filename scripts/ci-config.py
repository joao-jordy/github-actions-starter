#!/usr/bin/env python3
"""Validate service configuration and prepare the CI matrix."""

import json
import os
import re
import sys


NAME = re.compile(r"^[a-z][a-z0-9-]{0,62}$")
PATH = re.compile(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")
LANGUAGES = {"go", "rust", "python", "typescript", "javascript", "java", "dotnet"}
TYPES = {"static", "lambda", "container"}


def services_from_json(raw):
    services = json.loads(raw)
    if not isinstance(services, list) or not services:
        raise ValueError("SERVICES must be a non-empty JSON array")
    names = set()
    paths = set()
    for service in services:
        if not isinstance(service, dict):
            raise ValueError("Each service must be an object")
        name, path = service.get("name"), service.get("path")
        if not isinstance(name, str) or not NAME.fullmatch(name) or name == "pipeline":
            raise ValueError(f"Invalid service name: {name!r}")
        if (
            not isinstance(path, str)
            or not PATH.fullmatch(path)
            or any(part in {".", ".."} for part in path.split("/"))
        ):
            raise ValueError(f"Invalid service path: {path!r}")
        if name in names or path in paths:
            raise ValueError("Service names and paths must be unique")
        if (
            not isinstance(service.get("language"), str)
            or service["language"] not in LANGUAGES
            or not isinstance(service.get("type"), str)
            or service["type"] not in TYPES
        ):
            raise ValueError(f"Unsupported language or type for {name}")
        names.add(name)
        paths.add(path)
    return services


def output(name, value):
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as file:
        file.write(f"{name}={json.dumps(value, separators=(',', ':'))}\n")


def main():
    services = services_from_json(os.environ.get("SERVICES", "[]"))
    if sys.argv[1] == "filters":
        filters = {service["name"]: [service["path"] + "/**"] for service in services}
        filters["pipeline"] = [".github/**", "scripts/ci-config.py"]
        output("filters", filters)
    elif sys.argv[1] == "matrix":
        changes = json.loads(os.environ["CHANGES"])
        if not isinstance(changes, list) or not all(isinstance(item, str) for item in changes):
            raise ValueError("CHANGES must be a JSON array of strings")
        selected = [
            service for service in services
            if os.environ.get("RUN_ALL") == "true"
            or "pipeline" in changes
            or service["name"] in changes
        ]
        output("matrix", {"include": selected})
        output("has_services", bool(selected))
    else:
        raise ValueError("Expected filters or matrix")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, IndexError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        sys.exit(1)

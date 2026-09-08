#!/usr/bin/env python3
"""Compatibility entrypoint: forward existing add arguments to registry CRUD."""
import importlib.util
from pathlib import Path
import sys


def main():
    target = Path(__file__).resolve().parents[1] / 'manage-sdk-registry.py'
    spec = importlib.util.spec_from_file_location('sdk_registry_manager', target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main(['add', *sys.argv[1:]])


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Environment File Comparison and Consolidation Script
Compares .env files across project, identifies conflicts, suggests merge strategies.
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field

# Directories to always skip
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build'}


@dataclass
class EnvFile:
    path: Path
    keys: Dict[str, str]  # key -> raw value
    relative_path: str


@dataclass
class ComparisonResult:
    shared: Dict[str, str] = field(default_factory=dict)  # Same everywhere
    conflicts: Dict[str, Dict[str, str]] = field(default_factory=dict)  # Different values
    unique: Dict[str, Tuple[str, str]] = field(default_factory=dict)  # (location, value)
    duplicates: Dict[str, List[str]] = field(default_factory=dict)  # Same value, multiple places


def find_env_files(root: Path) -> List[Path]:
    """Find all .env files, excluding examples and templates."""
    env_files = []
    for path in root.rglob('.env*'):
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        if 'example' in path.name.lower() or 'template' in path.name.lower():
            continue
        if '.backup' in path.name:
            continue
        if path.is_file():
            env_files.append(path)
    return sorted(env_files)


def parse_env_file(path: Path) -> Dict[str, str]:
    """Parse .env file into key-value dict."""
    result = {}
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    result[key] = value
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}", file=sys.stderr)
    return result


def mask_value(value: str) -> str:
    """Mask sensitive values for display."""
    if not value:
        return "(empty)"
    if len(value) <= 4:
        return "****"
    return f"{value[0]}{'*' * min(len(value) - 2, 20)}{value[-1]}"


def compare_env_files(root: Path, env_files: List[EnvFile]) -> ComparisonResult:
    """Compare all .env files and categorize keys."""
    result = ComparisonResult()

    if not env_files:
        return result

    # Collect all keys
    all_keys: Set[str] = set()
    for ef in env_files:
        all_keys.update(ef.keys.keys())

    # Categorize each key
    for key in sorted(all_keys):
        locations_with_key = {ef.relative_path: ef.keys.get(key)
                             for ef in env_files if key in ef.keys}

        if len(locations_with_key) == 1:
            loc, val = list(locations_with_key.items())[0]
            result.unique[key] = (loc, val)
        else:
            values = list(locations_with_key.values())
            if len(set(values)) == 1:
                # Same value everywhere
                result.duplicates[key] = list(locations_with_key.keys())
                result.shared[key] = values[0]
            else:
                # Different values
                result.conflicts[key] = locations_with_key

    return result


def create_backup(path: Path) -> Path:
    """Create backup of a file before modifying."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_suffix(f'.backup.{timestamp}')
    shutil.copy2(path, backup_path)
    return backup_path


def print_comparison(result: ComparisonResult, env_files: List[EnvFile]):
    """Print comparison in readable format."""
    print("=" * 60)
    print(".ENV FILE COMPARISON")
    print("=" * 60)
    print()

    # Files found
    print("## Files Analyzed")
    for ef in env_files:
        print(f"  - {ef.relative_path} ({len(ef.keys)} keys)")
    print()

    # Shared (same everywhere)
    if result.shared:
        print(f"## Shared Keys ({len(result.shared)})")
        print("Same value in all locations - can consolidate to root")
        print()
        for key in list(result.shared.keys())[:15]:
            print(f"  {key}")
        if len(result.shared) > 15:
            print(f"  ... and {len(result.shared) - 15} more")
        print()

    # Conflicts (different values)
    if result.conflicts:
        print(f"## Conflicts ({len(result.conflicts)})")
        print("Different values - MUST resolve manually")
        print()
        print("| Key | " + " | ".join(ef.relative_path for ef in env_files) + " |")
        print("|-----|" + "|".join(["-----"] * len(env_files)) + "|")
        for key, locations in list(result.conflicts.items())[:20]:
            row = []
            for ef in env_files:
                val = locations.get(ef.relative_path)
                row.append(mask_value(val) if val else "—")
            print(f"| {key} | " + " | ".join(row) + " |")
        if len(result.conflicts) > 20:
            print(f"\n... and {len(result.conflicts) - 20} more conflicts")
        print()

    # Unique (only in one place)
    if result.unique:
        print(f"## Unique Keys ({len(result.unique)})")
        print("Only exist in one location")
        print()
        for key, (loc, val) in list(result.unique.items())[:15]:
            print(f"  {key} ({loc})")
        if len(result.unique) > 15:
            print(f"  ... and {len(result.unique) - 15} more")
        print()

    # Duplicates (same value, multiple places - can consolidate)
    if result.duplicates:
        dup_keys = [k for k in result.duplicates if k not in result.shared]
        if dup_keys:
            print(f"## Duplicates ({len(dup_keys)})")
            print("Same value in multiple (but not all) locations")
            print()
            for key in dup_keys[:10]:
                locs = result.duplicates[key]
                print(f"  {key}: {', '.join(locs)}")
            print()


def suggest_strategies(result: ComparisonResult, env_files: List[EnvFile]):
    """Suggest consolidation strategies."""
    print("=" * 60)
    print("SUGGESTED ACTIONS")
    print("=" * 60)
    print()

    if result.conflicts:
        print("### Resolve Conflicts First")
        print("Before consolidating, manually resolve these conflicts:")
        for key in list(result.conflicts.keys())[:5]:
            print(f"  - {key}")
        print()
        print("Options:")
        print("  1. Edit .env files to use same value")
        print("  2. Keep different values if intentional (dev vs prod)")
        print("  3. Rename keys to be explicit (DB_URL_DEV, DB_URL_PROD)")
        print()

    if result.duplicates or result.shared:
        print("### Consolidate Duplicates")
        total_dups = len(result.shared) + len([k for k in result.duplicates if k not in result.shared])
        print(f"{total_dups} keys could be moved to root .env")
        print()
        print("Run with --consolidate to create consolidated file")
        print()

    if result.unique:
        print("### Service-Specific Keys")
        print(f"{len(result.unique)} keys are unique to specific services")
        print("These should stay in their respective .env files")
        print()


def consolidate_to_root(root: Path, result: ComparisonResult, env_files: List[EnvFile], dry_run: bool = True):
    """
    Consolidate .env files:
    - Move shared/duplicate keys to root .env
    - Keep unique keys in their locations
    - Create .env.example with all keys
    """
    root_env = root / '.env'

    if dry_run:
        print("=" * 60)
        print("DRY RUN - No changes will be made")
        print("=" * 60)
        print()

    # Determine what goes where
    to_root = {}
    to_root.update(result.shared)

    # Build consolidated root .env content
    lines = ["# Consolidated .env file", f"# Generated: {datetime.now().isoformat()}", ""]

    # Group by prefix for organization
    prefixes: Dict[str, List[Tuple[str, str]]] = {}
    for key, val in sorted(to_root.items()):
        prefix = key.split('_')[0] if '_' in key else 'GENERAL'
        if prefix not in prefixes:
            prefixes[prefix] = []
        prefixes[prefix].append((key, val))

    for prefix in sorted(prefixes.keys()):
        lines.append(f"# {prefix}")
        for key, val in prefixes[prefix]:
            lines.append(f"{key}={val}")
        lines.append("")

    consolidated_content = "\n".join(lines)

    # Create .env.example (all keys, no values)
    example_lines = ["# All environment variables used by this project", ""]
    all_keys = set(result.shared.keys())
    all_keys.update(result.unique.keys())
    all_keys.update(result.conflicts.keys())
    for k in result.duplicates:
        all_keys.add(k)

    for key in sorted(all_keys):
        example_lines.append(f"{key}=")
    example_content = "\n".join(example_lines)

    if dry_run:
        print("## Would create/update: .env")
        print("Keys to consolidate:", len(to_root))
        print()
        print("## Would create: .env.example")
        print("Total keys documented:", len(all_keys))
        print()
        print("## Would need manual update:")
        for ef in env_files:
            if ef.relative_path != '.env':
                remove_count = len([k for k in ef.keys if k in to_root])
                print(f"  {ef.relative_path}: remove {remove_count} keys (now in root)")
    else:
        # Create backups
        if root_env.exists():
            backup = create_backup(root_env)
            print(f"Backed up: {root_env} -> {backup}")

        # Write consolidated .env
        with open(root_env, 'w') as f:
            f.write(consolidated_content)
        print(f"Created: {root_env}")

        # Write .env.example
        example_path = root / '.env.example'
        with open(example_path, 'w') as f:
            f.write(example_content)
        print(f"Created: {example_path}")

        print()
        print("## Manual steps needed:")
        for ef in env_files:
            if ef.relative_path != '.env':
                remove_keys = [k for k in ef.keys if k in to_root]
                if remove_keys:
                    print(f"  {ef.relative_path}:")
                    print(f"    Remove: {', '.join(remove_keys[:5])}")
                    if len(remove_keys) > 5:
                        print(f"    ... and {len(remove_keys) - 5} more")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Compare and consolidate .env files')
    parser.add_argument('root', nargs='?', default='.', help='Project root directory')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--consolidate', action='store_true', help='Run consolidation')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Dry run (default)')
    parser.add_argument('--apply', action='store_true', help='Actually apply changes')

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"Error: {root} does not exist")
        sys.exit(1)

    # Find and parse env files
    env_paths = find_env_files(root)
    if not env_paths:
        print("No .env files found")
        sys.exit(0)

    env_files = []
    for path in env_paths:
        ef = EnvFile(
            path=path,
            keys=parse_env_file(path),
            relative_path=str(path.relative_to(root))
        )
        env_files.append(ef)

    # Compare
    result = compare_env_files(root, env_files)

    if args.json:
        output = {
            "files": [ef.relative_path for ef in env_files],
            "shared": list(result.shared.keys()),
            "conflicts": {k: {loc: mask_value(v) for loc, v in locs.items()}
                         for k, locs in result.conflicts.items()},
            "unique": {k: {"location": loc, "value": mask_value(val)}
                      for k, (loc, val) in result.unique.items()},
            "duplicates": result.duplicates
        }
        print(json.dumps(output, indent=2))
    elif args.consolidate:
        dry_run = not args.apply
        consolidate_to_root(root, result, env_files, dry_run=dry_run)
    else:
        print_comparison(result, env_files)
        suggest_strategies(result, env_files)


if __name__ == '__main__':
    main()

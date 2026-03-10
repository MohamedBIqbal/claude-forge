#!/usr/bin/env python3
"""
Project Health Audit Script
Read-only analysis of project structure, configs, and dependencies.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import re
import subprocess

# Directories to always skip
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build', '.next', '.nuxt'}


@dataclass
class CheckResult:
    name: str
    status: str  # PASS, WARN, FAIL, INFO
    details: str = ""


@dataclass
class EnvComparison:
    shared: Dict[str, str] = field(default_factory=dict)
    conflicts: Dict[str, Dict[str, str]] = field(default_factory=dict)
    unique: Dict[str, Dict[str, str]] = field(default_factory=dict)
    duplicates: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class AppStructure:
    name: str  # backend, frontend
    found: bool = False
    checks: List[CheckResult] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class AuditReport:
    claude_structure: List[CheckResult] = field(default_factory=list)
    env_comparison: EnvComparison = field(default_factory=EnvComparison)
    env_files: List[str] = field(default_factory=list)
    dependencies: Dict[str, Any] = field(default_factory=dict)
    structure_issues: List[Dict[str, str]] = field(default_factory=list)
    app_structure: Dict[str, AppStructure] = field(default_factory=dict)


def find_env_files(root: Path) -> List[Path]:
    """Find all .env files, excluding examples and templates."""
    env_files = []
    for path in root.rglob('.env*'):
        # Skip directories we don't care about
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        # Skip example/template files
        if 'example' in path.name.lower() or 'template' in path.name.lower():
            continue
        # Skip backup files
        if '.backup' in path.name:
            continue
        if path.is_file():
            env_files.append(path)
    return sorted(env_files)


def parse_env_file(path: Path) -> Dict[str, str]:
    """Parse .env file into key-value dict. Values are masked."""
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
                    # Mask the value for security
                    if value:
                        result[key] = mask_value(value)
                    else:
                        result[key] = "(empty)"
    except Exception as e:
        result['_error'] = str(e)
    return result


def mask_value(value: str) -> str:
    """Mask sensitive values, keeping first/last char for identification."""
    if len(value) <= 4:
        return "****"
    return f"{value[0]}{'*' * (len(value) - 2)}{value[-1]}"


def compare_env_files(root: Path, env_files: List[Path]) -> EnvComparison:
    """Compare all .env files and categorize keys."""
    comparison = EnvComparison()

    if not env_files:
        return comparison

    # Parse all files
    all_envs: Dict[str, Dict[str, str]] = {}
    for path in env_files:
        rel_path = str(path.relative_to(root))
        all_envs[rel_path] = parse_env_file(path)

    # Collect all keys
    all_keys = set()
    for env_data in all_envs.values():
        all_keys.update(env_data.keys())
    all_keys.discard('_error')

    # Categorize each key
    for key in sorted(all_keys):
        locations_with_key = {loc: data.get(key) for loc, data in all_envs.items() if key in data}

        if len(locations_with_key) == 1:
            # Unique to one location
            loc, val = list(locations_with_key.items())[0]
            comparison.unique[key] = {"location": loc, "value": val}
        else:
            # Multiple locations - check if values match
            values = list(locations_with_key.values())
            if len(set(values)) == 1:
                # Same value everywhere - duplicate
                comparison.duplicates[key] = list(locations_with_key.keys())
                comparison.shared[key] = values[0]
            else:
                # Different values - conflict
                comparison.conflicts[key] = locations_with_key

    return comparison


def check_claude_structure(root: Path) -> List[CheckResult]:
    """Check Claude Code directory structure."""
    results = []

    # Check CLAUDE.md
    claude_md = root / 'CLAUDE.md'
    if claude_md.exists():
        lines = len(claude_md.read_text().splitlines())
        if lines <= 200:
            results.append(CheckResult("CLAUDE.md exists", "PASS", f"{lines} lines"))
        else:
            results.append(CheckResult("CLAUDE.md exists", "WARN", f"{lines} lines (recommended: <200)"))
    else:
        results.append(CheckResult("CLAUDE.md exists", "FAIL", "Not found"))

    # Check .claude directory
    claude_dir = root / '.claude'
    if claude_dir.exists():
        results.append(CheckResult(".claude/ exists", "PASS", ""))
    else:
        results.append(CheckResult(".claude/ exists", "FAIL", "Not found"))
        return results

    # Check subdirectories
    expected_dirs = ['skills', 'agents', 'rules', 'context']
    for dirname in expected_dirs:
        dir_path = claude_dir / dirname
        if dir_path.exists():
            count = len(list(dir_path.iterdir())) if dir_path.is_dir() else 0
            results.append(CheckResult(f".claude/{dirname}/", "PASS", f"{count} items"))
        else:
            results.append(CheckResult(f".claude/{dirname}/", "WARN", "Missing"))

    # Check context subdirs
    context_dir = claude_dir / 'context'
    if context_dir.exists():
        if (context_dir / '_index.md').exists():
            results.append(CheckResult(".claude/context/_index.md", "PASS", ""))
        else:
            results.append(CheckResult(".claude/context/_index.md", "WARN", "Missing"))

        if (context_dir / 'active').exists():
            results.append(CheckResult(".claude/context/active/", "PASS", ""))
        else:
            results.append(CheckResult(".claude/context/active/", "WARN", "Missing"))

    return results


def find_misplaced_skills(root: Path) -> List[Dict[str, str]]:
    """Find skill files at root that should be in .claude/skills/."""
    issues = []

    # Look for *skill*.md files at root
    for path in root.glob('*skill*.md'):
        if path.is_file():
            # Suggest a proper location
            name = path.stem.lower().replace('skill', '').strip('-_') or 'misc'
            suggested = f".claude/skills/{name}/SKILL.md"
            issues.append({
                "type": "skill_at_root",
                "current": path.name,
                "suggested": suggested
            })

    # Check for SKILL.md at root
    skill_md = root / 'SKILL.md'
    if skill_md.exists():
        issues.append({
            "type": "skill_at_root",
            "current": "SKILL.md",
            "suggested": ".claude/skills/main/SKILL.md"
        })

    return issues


def find_scattered_docs(root: Path) -> List[Dict[str, str]]:
    """Find documentation files at root that could be in docs/."""
    issues = []
    docs_dir = root / 'docs'

    # Files that should probably be in docs/
    doc_patterns = ['CHANGELOG.md', 'LIMITATIONS.md', 'script*.md', 'HISTORY.md']

    for pattern in doc_patterns:
        for path in root.glob(pattern):
            if path.is_file():
                suggested = f"docs/{path.name}"
                issues.append({
                    "type": "doc_at_root",
                    "current": path.name,
                    "suggested": suggested
                })

    return issues


def count_files_in_dir(dir_path: Path) -> int:
    """Count Python/JS files in a directory (non-recursive)."""
    if not dir_path.exists():
        return 0
    count = 0
    for f in dir_path.iterdir():
        if f.is_file() and f.suffix in {'.py', '.js', '.ts', '.tsx', '.jsx'}:
            count += 1
    return count


def check_file_sizes(dir_path: Path, max_lines: int = 500) -> List[str]:
    """Find files over max_lines."""
    large_files = []
    if not dir_path.exists():
        return large_files

    for f in dir_path.rglob('*'):
        if any(skip in f.parts for skip in SKIP_DIRS):
            continue
        if f.is_file() and f.suffix in {'.py', '.js', '.ts', '.tsx', '.jsx'}:
            try:
                lines = len(f.read_text().splitlines())
                if lines > max_lines:
                    large_files.append(f"{f.name} ({lines} lines)")
            except Exception:
                pass
    return large_files[:5]  # Limit to 5


def analyze_backend_structure(root: Path) -> AppStructure:
    """Analyze backend folder structure."""
    result = AppStructure(name="backend")

    backend = root / 'backend'
    if not backend.exists():
        return result

    result.found = True

    # Expected directories for a well-structured backend
    expected = {
        'api': 'API routes/endpoints',
        'skills': 'Business logic modules',
        'services': 'Shared services (DB, LLM, etc.)',
        'models': 'Data models/schemas',
        'agents': 'LangGraph/CrewAI agents',
    }

    optional = {
        'core': 'Core utilities (config, logging)',
        'tests': 'Test files',
        'data': 'Data files',
        'utils': 'Utility functions',
    }

    # Check expected directories
    for dirname, desc in expected.items():
        dir_path = backend / dirname
        if dir_path.exists():
            count = count_files_in_dir(dir_path)
            result.checks.append(CheckResult(f"{dirname}/", "PASS", f"{count} files - {desc}"))
        else:
            result.checks.append(CheckResult(f"{dirname}/", "INFO", f"Not found - {desc}"))

    # Check optional but note if missing
    for dirname, desc in optional.items():
        dir_path = backend / dirname
        if dir_path.exists():
            count = count_files_in_dir(dir_path)
            result.checks.append(CheckResult(f"{dirname}/", "PASS", f"{count} files"))

    # Check for anti-patterns
    # 1. Too many files in root
    root_files = count_files_in_dir(backend)
    if root_files > 10:
        result.checks.append(CheckResult("Root files", "WARN", f"{root_files} files (consider organizing)"))
        result.suggestions.append("Move root .py files into appropriate subdirectories")

    # 2. Large files
    large_files = check_file_sizes(backend)
    if large_files:
        result.checks.append(CheckResult("Large files", "WARN", f"{len(large_files)} files >500 lines"))
        result.suggestions.append(f"Consider splitting: {', '.join(large_files[:3])}")

    # 3. Check for flat utils/helpers with many files
    for catch_all in ['utils', 'helpers', 'common']:
        catch_all_dir = backend / catch_all
        if catch_all_dir.exists():
            count = count_files_in_dir(catch_all_dir)
            if count > 20:
                result.checks.append(CheckResult(f"{catch_all}/", "WARN", f"{count} files (too many)"))
                result.suggestions.append(f"Split {catch_all}/ into domain-specific modules")

    # 4. Check for missing __init__.py
    for subdir in backend.iterdir():
        if subdir.is_dir() and subdir.name not in SKIP_DIRS and not subdir.name.startswith('.'):
            init_file = subdir / '__init__.py'
            if not init_file.exists() and any(subdir.glob('*.py')):
                result.suggestions.append(f"Add __init__.py to {subdir.name}/")

    return result


def analyze_frontend_structure(root: Path) -> AppStructure:
    """Analyze frontend folder structure."""
    result = AppStructure(name="frontend")

    frontend = root / 'frontend'
    if not frontend.exists():
        return result

    result.found = True

    # Check for src directory
    src = frontend / 'src'
    if not src.exists():
        result.checks.append(CheckResult("src/", "WARN", "Not found - flat structure"))
        src = frontend  # Fall back to frontend root
    else:
        result.checks.append(CheckResult("src/", "PASS", "Found"))

    # Expected directories
    expected = {
        'components': 'React components',
        'pages': 'Route pages',
        'hooks': 'Custom React hooks',
        'services': 'API clients',
    }

    optional = {
        'stores': 'State management',
        'types': 'TypeScript types',
        'utils': 'Utility functions',
        'assets': 'Static assets',
        'styles': 'CSS/styles',
    }

    # Check expected directories
    for dirname, desc in expected.items():
        dir_path = src / dirname
        if dir_path.exists():
            count = count_files_in_dir(dir_path)
            result.checks.append(CheckResult(f"{dirname}/", "PASS", f"{count} files - {desc}"))
        else:
            result.checks.append(CheckResult(f"{dirname}/", "INFO", f"Not found - {desc}"))

    # Check optional
    for dirname, desc in optional.items():
        dir_path = src / dirname
        if dir_path.exists():
            count = count_files_in_dir(dir_path)
            result.checks.append(CheckResult(f"{dirname}/", "PASS", f"{count} files"))

    # Check for large component files
    components = src / 'components'
    if components.exists():
        large_files = check_file_sizes(components, max_lines=300)
        if large_files:
            result.checks.append(CheckResult("Large components", "WARN", f"{len(large_files)} >300 lines"))
            result.suggestions.append(f"Split components: {', '.join(large_files[:3])}")

    # Check for index barrel exports
    if (src / 'components').exists():
        index_files = list((src / 'components').glob('**/index.ts*'))
        if not index_files:
            result.suggestions.append("Consider adding index.ts barrel exports in components/")

    return result


def check_python_deps(root: Path) -> Dict[str, Any]:
    """Analyze Python dependencies."""
    result = {"found": False, "location": None, "issues": []}

    # Find requirements or pyproject
    pyproject = root / 'pyproject.toml'
    requirements = root / 'requirements.txt'
    backend_req = root / 'backend' / 'requirements.txt'

    req_file = None
    if backend_req.exists():
        req_file = backend_req
    elif requirements.exists():
        req_file = requirements
    elif pyproject.exists():
        req_file = pyproject

    if not req_file:
        return result

    result["found"] = True
    result["location"] = str(req_file.relative_to(root))

    # Try to get outdated packages
    try:
        proc = subprocess.run(
            ['pip', 'list', '--outdated', '--format=json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if proc.returncode == 0:
            outdated = json.loads(proc.stdout)
            result["outdated_count"] = len(outdated)
            result["outdated_sample"] = outdated[:5]  # Show first 5
    except Exception:
        result["outdated_count"] = "unknown"

    return result


def check_node_deps(root: Path) -> Dict[str, Any]:
    """Analyze Node.js dependencies."""
    result = {"found": False, "location": None, "issues": []}

    # Find package.json
    pkg_json = root / 'package.json'
    frontend_pkg = root / 'frontend' / 'package.json'

    pkg_file = None
    if frontend_pkg.exists():
        pkg_file = frontend_pkg
    elif pkg_json.exists():
        pkg_file = pkg_json

    if not pkg_file:
        return result

    result["found"] = True
    result["location"] = str(pkg_file.relative_to(root))

    # Count dependencies
    try:
        with open(pkg_file) as f:
            pkg = json.load(f)
        result["deps_count"] = len(pkg.get("dependencies", {}))
        result["dev_deps_count"] = len(pkg.get("devDependencies", {}))
    except Exception:
        pass

    return result


def run_audit(root_path: str) -> AuditReport:
    """Run full project audit."""
    root = Path(root_path).resolve()
    report = AuditReport()

    # 1. Claude structure
    report.claude_structure = check_claude_structure(root)

    # 2. Find and compare .env files
    env_files = find_env_files(root)
    report.env_files = [str(f.relative_to(root)) for f in env_files]
    if env_files:
        report.env_comparison = compare_env_files(root, env_files)

    # 3. Structure issues
    report.structure_issues.extend(find_misplaced_skills(root))
    report.structure_issues.extend(find_scattered_docs(root))

    # 4. Dependencies
    report.dependencies["python"] = check_python_deps(root)
    report.dependencies["node"] = check_node_deps(root)

    # 5. Application structure
    report.app_structure["backend"] = analyze_backend_structure(root)
    report.app_structure["frontend"] = analyze_frontend_structure(root)

    return report


def format_report(report: AuditReport, root: Path) -> str:
    """Format audit report as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("PROJECT HEALTH AUDIT")
    lines.append(f"Root: {root}")
    lines.append("=" * 60)
    lines.append("")

    # Claude Structure
    lines.append("## Claude Code Structure")
    lines.append("")
    lines.append("| Check | Status | Details |")
    lines.append("|-------|--------|---------|")
    for check in report.claude_structure:
        lines.append(f"| {check.name} | {check.status} | {check.details} |")
    lines.append("")

    # Env files
    if report.env_files:
        lines.append("## Configuration Files (.env)")
        lines.append("")
        lines.append(f"Found {len(report.env_files)} .env files:")
        for f in report.env_files:
            lines.append(f"  - {f}")
        lines.append("")

        comp = report.env_comparison

        if comp.shared:
            lines.append(f"**Shared keys** ({len(comp.shared)}): Same value across all files")
            for key in list(comp.shared.keys())[:10]:
                lines.append(f"  - {key}")
            if len(comp.shared) > 10:
                lines.append(f"  ... and {len(comp.shared) - 10} more")
            lines.append("")

        if comp.conflicts:
            lines.append(f"**Conflicts** ({len(comp.conflicts)}): Different values across files")
            lines.append("| Key | " + " | ".join(report.env_files) + " |")
            lines.append("|-----|" + "|".join(["-----"] * len(report.env_files)) + "|")
            for key, locations in list(comp.conflicts.items())[:10]:
                row = [locations.get(f, "—") for f in report.env_files]
                lines.append(f"| {key} | " + " | ".join(row) + " |")
            lines.append("")

        if comp.unique:
            lines.append(f"**Unique keys** ({len(comp.unique)}): Only in one location")
            for key, info in list(comp.unique.items())[:10]:
                lines.append(f"  - {key} ({info['location']})")
            lines.append("")

        if comp.duplicates:
            lines.append(f"**Duplicates** ({len(comp.duplicates)}): Same value, multiple locations (can consolidate)")
            for key, locs in list(comp.duplicates.items())[:5]:
                lines.append(f"  - {key}: {', '.join(locs)}")
            lines.append("")
    else:
        lines.append("## Configuration Files")
        lines.append("No .env files found.")
        lines.append("")

    # Structure issues
    if report.structure_issues:
        lines.append("## Structure Issues")
        lines.append("")
        lines.append("| Type | Current | Suggested |")
        lines.append("|------|---------|-----------|")
        for issue in report.structure_issues:
            itype = issue["type"].replace("_", " ")
            lines.append(f"| {itype} | {issue['current']} | {issue['suggested']} |")
        lines.append("")

    # Dependencies
    lines.append("## Dependencies")
    lines.append("")

    py = report.dependencies.get("python", {})
    if py.get("found"):
        lines.append(f"**Python** ({py['location']})")
        if py.get("outdated_count"):
            lines.append(f"  - Outdated packages: {py['outdated_count']}")
        lines.append("")

    node = report.dependencies.get("node", {})
    if node.get("found"):
        lines.append(f"**Node.js** ({node['location']})")
        if node.get("deps_count"):
            lines.append(f"  - Dependencies: {node['deps_count']}")
            lines.append(f"  - Dev dependencies: {node.get('dev_deps_count', 0)}")
        lines.append("")

    if not py.get("found") and not node.get("found"):
        lines.append("No package managers detected.")
        lines.append("")

    # Application Structure
    for name, app in report.app_structure.items():
        if app.found:
            lines.append(f"## {name.title()} Structure")
            lines.append("")
            lines.append("| Directory | Status | Details |")
            lines.append("|-----------|--------|---------|")
            for check in app.checks:
                lines.append(f"| {check.name} | {check.status} | {check.details} |")
            lines.append("")

            if app.suggestions:
                lines.append("**Suggestions:**")
                for s in app.suggestions:
                    lines.append(f"  - {s}")
                lines.append("")

    lines.append("=" * 60)
    lines.append("END OF AUDIT")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()

    if not root.exists():
        print(f"Error: {root} does not exist")
        sys.exit(1)

    report = run_audit(str(root))

    # Output format based on argument
    if len(sys.argv) > 2 and sys.argv[2] == '--json':
        # Convert dataclasses to dict for JSON
        def to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: to_dict(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [to_dict(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: to_dict(v) for k, v in obj.items()}
            return obj
        print(json.dumps(to_dict(report), indent=2))
    else:
        print(format_report(report, root))


if __name__ == '__main__':
    main()

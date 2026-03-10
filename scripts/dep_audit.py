#!/usr/bin/env python3
"""
Dependency Audit Script
Analyzes Python and Node.js dependencies for unused, outdated, or problematic packages.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field, asdict

# Directories to skip when searching for imports
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build', '.next'}


@dataclass
class PackageInfo:
    name: str
    status: str  # OK, UNUSED, OUTDATED, MISSING
    current_version: Optional[str] = None
    latest_version: Optional[str] = None
    issue: str = ""


@dataclass
class DependencyReport:
    python: Dict[str, Any] = field(default_factory=dict)
    node: Dict[str, Any] = field(default_factory=dict)


def find_python_imports(root: Path) -> Set[str]:
    """Find all Python import statements in the codebase."""
    imports = set()
    import_patterns = [
        re.compile(r'^import\s+(\w+)'),
        re.compile(r'^from\s+(\w+)'),
    ]

    for py_file in root.rglob('*.py'):
        if any(skip in py_file.parts for skip in SKIP_DIRS):
            continue
        try:
            content = py_file.read_text()
            for line in content.splitlines():
                line = line.strip()
                for pattern in import_patterns:
                    match = pattern.match(line)
                    if match:
                        imports.add(match.group(1))
        except Exception:
            continue

    return imports


def parse_requirements(path: Path) -> Dict[str, str]:
    """Parse requirements.txt into package -> version dict."""
    packages = {}
    if not path.exists():
        return packages

    try:
        content = path.read_text()
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('-'):
                continue
            # Handle various formats: pkg, pkg==1.0, pkg>=1.0, pkg[extra]
            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
            if match:
                pkg_name = match.group(1).lower()
                # Try to extract version
                version_match = re.search(r'[=<>]+(.+?)(?:\s|$)', line)
                version = version_match.group(1) if version_match else "any"
                packages[pkg_name] = version
    except Exception:
        pass

    return packages


def parse_pyproject(path: Path) -> Dict[str, str]:
    """Parse pyproject.toml dependencies."""
    packages = {}
    if not path.exists():
        return packages

    try:
        import tomllib
        content = path.read_bytes()
        data = tomllib.loads(content.decode())

        # Look in common locations
        deps = data.get('project', {}).get('dependencies', [])
        deps.extend(data.get('tool', {}).get('poetry', {}).get('dependencies', {}).keys())

        for dep in deps:
            if isinstance(dep, str):
                match = re.match(r'^([a-zA-Z0-9_-]+)', dep)
                if match:
                    packages[match.group(1).lower()] = "specified"
    except Exception:
        pass

    return packages


def check_python_outdated() -> List[Dict[str, str]]:
    """Get list of outdated Python packages."""
    try:
        result = subprocess.run(
            ['pip', 'list', '--outdated', '--format=json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return []


def analyze_python(root: Path) -> Dict[str, Any]:
    """Analyze Python dependencies."""
    report = {
        "found": False,
        "location": None,
        "packages": [],
        "summary": {}
    }

    # Find dependency file
    req_file = None
    for path in [root / 'requirements.txt', root / 'backend' / 'requirements.txt']:
        if path.exists():
            req_file = path
            break

    pyproject = None
    for path in [root / 'pyproject.toml', root / 'backend' / 'pyproject.toml']:
        if path.exists():
            pyproject = path
            break

    if not req_file and not pyproject:
        return report

    report["found"] = True
    report["location"] = str((req_file or pyproject).relative_to(root))

    # Parse declared dependencies
    declared = {}
    if req_file:
        declared = parse_requirements(req_file)
    if pyproject:
        declared.update(parse_pyproject(pyproject))

    # Find actual imports
    actual_imports = find_python_imports(root)

    # Map common import names to package names
    import_to_package = {
        'cv2': 'opencv-python',
        'PIL': 'pillow',
        'sklearn': 'scikit-learn',
        'yaml': 'pyyaml',
        'bs4': 'beautifulsoup4',
    }

    # Standard library modules to ignore
    stdlib = {
        'os', 'sys', 're', 'json', 'logging', 'typing', 'pathlib', 'datetime',
        'collections', 'functools', 'itertools', 'subprocess', 'shutil',
        'tempfile', 'unittest', 'pytest', 'dataclasses', 'abc', 'copy',
        'io', 'time', 'random', 'math', 'hashlib', 'base64', 'uuid',
        'asyncio', 'threading', 'multiprocessing', 'queue', 'socket',
        'http', 'urllib', 'email', 'html', 'xml', 'csv', 'sqlite3',
        'contextlib', 'warnings', 'traceback', 'inspect', 'operator',
        'enum', 'secrets', 'string', 'textwrap', 'difflib', 'glob',
        'fnmatch', 'struct', 'codecs', 'locale', 'gettext', 'argparse',
        'configparser', 'fileinput', 'stat', 'filecmp', 'pickle', 'shelve',
        'dbm', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile', 'zlib',
        'signal', 'mmap', 'ctypes', 'concurrent', 'importlib', 'pkgutil',
        'builtins', 'numbers', 'decimal', 'fractions', 'statistics',
        'array', 'weakref', 'types', 'pprint', 'reprlib', 'graphlib',
        'tomllib', 'keyword', 'token', 'tokenize', 'tabnanny', 'pyclbr',
        'compileall', 'dis', 'pickletools', 'formatter', 'test', 'profile',
        'timeit', 'trace', 'gc', 'atexit', 'faulthandler', 'pdb', 'runpy',
        '__future__', '__main__', 'encodings', 'heapq', 'bisect'
    }

    # Check for outdated
    outdated_list = check_python_outdated()
    outdated = {p['name'].lower(): p for p in outdated_list}

    # Analyze each declared package
    packages = []
    unused = 0
    outdated_count = 0

    for pkg_name, version in declared.items():
        info = PackageInfo(name=pkg_name, status="OK", current_version=version)

        # Check if used
        # Normalize package name for import matching
        import_name = pkg_name.replace('-', '_').lower()
        is_used = (
            import_name in {i.lower() for i in actual_imports} or
            pkg_name in {import_to_package.get(i, i).lower() for i in actual_imports}
        )

        if not is_used and pkg_name not in ['pip', 'setuptools', 'wheel']:
            info.status = "UNUSED"
            info.issue = "No imports found"
            unused += 1

        # Check if outdated
        if pkg_name in outdated:
            info.status = "OUTDATED" if info.status == "OK" else info.status
            info.current_version = outdated[pkg_name].get('version', version)
            info.latest_version = outdated[pkg_name].get('latest_version')
            info.issue = f"Update available: {info.latest_version}"
            outdated_count += 1

        packages.append(asdict(info))

    report["packages"] = packages
    report["summary"] = {
        "total": len(packages),
        "unused": unused,
        "outdated": outdated_count,
        "ok": len(packages) - unused - outdated_count
    }

    return report


def find_node_imports(root: Path) -> Set[str]:
    """Find all Node.js imports in the codebase."""
    imports = set()
    patterns = [
        re.compile(r"require\(['\"]([^'\"./][^'\"]*)['\"]"),
        re.compile(r"from ['\"]([^'\"./][^'\"]*)['\"]"),
        re.compile(r"import ['\"]([^'\"./][^'\"]*)['\"]"),
    ]

    for ext in ['*.js', '*.ts', '*.jsx', '*.tsx', '*.mjs', '*.cjs']:
        for js_file in root.rglob(ext):
            if any(skip in js_file.parts for skip in SKIP_DIRS):
                continue
            try:
                content = js_file.read_text()
                for pattern in patterns:
                    for match in pattern.finditer(content):
                        pkg = match.group(1)
                        # Get root package name (before /)
                        if pkg.startswith('@'):
                            # Scoped package: @scope/pkg
                            parts = pkg.split('/')
                            if len(parts) >= 2:
                                imports.add('/'.join(parts[:2]))
                        else:
                            imports.add(pkg.split('/')[0])
            except Exception:
                continue

    return imports


def analyze_node(root: Path) -> Dict[str, Any]:
    """Analyze Node.js dependencies."""
    report = {
        "found": False,
        "location": None,
        "packages": [],
        "summary": {}
    }

    # Find package.json
    pkg_json = None
    for path in [root / 'package.json', root / 'frontend' / 'package.json']:
        if path.exists():
            pkg_json = path
            break

    if not pkg_json:
        return report

    report["found"] = True
    report["location"] = str(pkg_json.relative_to(root))

    try:
        with open(pkg_json) as f:
            pkg_data = json.load(f)
    except Exception:
        return report

    # Get declared dependencies
    deps = pkg_data.get('dependencies', {})
    dev_deps = pkg_data.get('devDependencies', {})

    # Find actual imports
    actual_imports = find_node_imports(root)

    # Built-in Node modules to ignore
    node_builtins = {
        'fs', 'path', 'os', 'http', 'https', 'crypto', 'stream', 'events',
        'util', 'url', 'querystring', 'buffer', 'child_process', 'cluster',
        'net', 'dns', 'tls', 'readline', 'repl', 'vm', 'zlib', 'assert',
        'process', 'module', 'timers', 'console', 'v8', 'perf_hooks',
        'worker_threads', 'async_hooks'
    }

    packages = []
    unused = 0

    # Analyze production dependencies
    for pkg_name, version in deps.items():
        info = PackageInfo(name=pkg_name, status="OK", current_version=version)

        if pkg_name not in actual_imports and pkg_name not in node_builtins:
            info.status = "UNUSED"
            info.issue = "No imports found"
            unused += 1

        packages.append(asdict(info))

    report["packages"] = packages
    report["summary"] = {
        "total": len(deps),
        "dev_total": len(dev_deps),
        "unused": unused,
        "ok": len(deps) - unused
    }

    return report


def print_report(report: DependencyReport):
    """Print dependency report in readable format."""
    print("=" * 60)
    print("DEPENDENCY AUDIT")
    print("=" * 60)
    print()

    # Python
    py = report.python
    if py.get("found"):
        print(f"## Python ({py['location']})")
        print()
        summary = py.get("summary", {})
        print(f"Total: {summary.get('total', 0)} | "
              f"OK: {summary.get('ok', 0)} | "
              f"Unused: {summary.get('unused', 0)} | "
              f"Outdated: {summary.get('outdated', 0)}")
        print()

        # Show issues
        issues = [p for p in py.get("packages", []) if p["status"] != "OK"]
        if issues:
            print("| Package | Status | Issue |")
            print("|---------|--------|-------|")
            for pkg in issues[:20]:
                print(f"| {pkg['name']} | {pkg['status']} | {pkg['issue']} |")
            if len(issues) > 20:
                print(f"\n... and {len(issues) - 20} more")
        else:
            print("All packages OK!")
        print()
    else:
        print("## Python")
        print("No Python dependencies found")
        print()

    # Node
    node = report.node
    if node.get("found"):
        print(f"## Node.js ({node['location']})")
        print()
        summary = node.get("summary", {})
        print(f"Dependencies: {summary.get('total', 0)} | "
              f"Dev: {summary.get('dev_total', 0)} | "
              f"Unused: {summary.get('unused', 0)}")
        print()

        issues = [p for p in node.get("packages", []) if p["status"] != "OK"]
        if issues:
            print("| Package | Status | Issue |")
            print("|---------|--------|-------|")
            for pkg in issues[:20]:
                print(f"| {pkg['name']} | {pkg['status']} | {pkg['issue']} |")
            if len(issues) > 20:
                print(f"\n... and {len(issues) - 20} more")
        else:
            print("All packages OK!")
        print()
    else:
        print("## Node.js")
        print("No Node.js dependencies found")
        print()

    print("=" * 60)
    print("SUGGESTED ACTIONS")
    print("=" * 60)
    print()

    if py.get("summary", {}).get("unused", 0) > 0:
        print("### Remove unused Python packages")
        unused = [p['name'] for p in py.get("packages", []) if p["status"] == "UNUSED"]
        print(f"pip uninstall {' '.join(unused[:10])}")
        print()

    if py.get("summary", {}).get("outdated", 0) > 0:
        print("### Update outdated Python packages")
        print("pip list --outdated")
        print("pip install --upgrade <package>")
        print()

    if node.get("summary", {}).get("unused", 0) > 0:
        print("### Remove unused Node packages")
        unused = [p['name'] for p in node.get("packages", []) if p["status"] == "UNUSED"]
        print(f"npm uninstall {' '.join(unused[:10])}")
        print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Audit project dependencies')
    parser.add_argument('root', nargs='?', default='.', help='Project root directory')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--python-only', action='store_true', help='Only analyze Python')
    parser.add_argument('--node-only', action='store_true', help='Only analyze Node.js')

    args = parser.parse_args()
    root = Path(args.root).resolve()

    if not root.exists():
        print(f"Error: {root} does not exist")
        sys.exit(1)

    report = DependencyReport()

    if not args.node_only:
        report.python = analyze_python(root)

    if not args.python_only:
        report.node = analyze_node(root)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print_report(report)


if __name__ == '__main__':
    main()

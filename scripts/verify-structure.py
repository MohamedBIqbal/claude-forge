#!/usr/bin/env python3
"""
Verify Claude Code project structure follows best practices.

Usage:
    python verify-structure.py [project-path]

If no path provided, uses current directory.
"""

import os
import sys
from pathlib import Path


def count_lines(file_path: Path) -> int:
    """Count non-empty lines in a file."""
    try:
        with open(file_path, 'r') as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return -1


def check_yaml_frontmatter(file_path: Path) -> bool:
    """Check if file has valid YAML frontmatter."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            return content.startswith('---') and '---' in content[3:]
    except Exception:
        return False


def verify_project(project_path: Path) -> dict:
    """Verify project structure and return results."""
    results = {
        'passed': [],
        'warnings': [],
        'failed': []
    }

    # Check CLAUDE.md exists
    claude_md = project_path / 'CLAUDE.md'
    claude_md_alt = project_path / '.claude' / 'CLAUDE.md'

    if claude_md.exists():
        results['passed'].append('CLAUDE.md exists at project root')
        lines = count_lines(claude_md)
        if lines > 200:
            results['warnings'].append(f'CLAUDE.md has {lines} lines (recommended: <200)')
        else:
            results['passed'].append(f'CLAUDE.md is {lines} lines (under 200 limit)')
    elif claude_md_alt.exists():
        results['passed'].append('CLAUDE.md exists at .claude/CLAUDE.md')
        lines = count_lines(claude_md_alt)
        if lines > 200:
            results['warnings'].append(f'CLAUDE.md has {lines} lines (recommended: <200)')
        else:
            results['passed'].append(f'CLAUDE.md is {lines} lines (under 200 limit)')
    else:
        results['failed'].append('CLAUDE.md not found (checked root and .claude/)')

    # Check .claude directory
    claude_dir = project_path / '.claude'
    if claude_dir.exists():
        results['passed'].append('.claude/ directory exists')
    else:
        results['warnings'].append('.claude/ directory not found')

    # Check context persistence
    context_dir = project_path / '.claude' / 'context'
    if context_dir.exists():
        results['passed'].append('.claude/context/ directory exists')

        index_file = context_dir / '_index.md'
        if index_file.exists():
            results['passed'].append('.claude/context/_index.md exists')
        else:
            results['warnings'].append('.claude/context/_index.md not found')

        active_dir = context_dir / 'active'
        if active_dir.exists():
            results['passed'].append('.claude/context/active/ directory exists')
        else:
            results['warnings'].append('.claude/context/active/ directory not found')
    else:
        results['warnings'].append('.claude/context/ not found (optional but recommended)')

    # Check skills
    skills_dir = project_path / '.claude' / 'skills'
    if skills_dir.exists():
        skill_files = list(skills_dir.glob('*/SKILL.md'))
        if skill_files:
            for skill in skill_files:
                if check_yaml_frontmatter(skill):
                    results['passed'].append(f'Skill {skill.parent.name} has valid frontmatter')
                else:
                    results['warnings'].append(f'Skill {skill.parent.name} missing YAML frontmatter')

    # Check agents
    agents_dir = project_path / '.claude' / 'agents'
    if agents_dir.exists():
        agent_files = list(agents_dir.glob('*.md'))
        if agent_files:
            for agent in agent_files:
                if check_yaml_frontmatter(agent):
                    results['passed'].append(f'Agent {agent.stem} has valid frontmatter')
                else:
                    results['warnings'].append(f'Agent {agent.stem} missing YAML frontmatter')

    # Check rules
    rules_dir = project_path / '.claude' / 'rules'
    if rules_dir.exists():
        rule_files = list(rules_dir.glob('*.md'))
        results['passed'].append(f'.claude/rules/ has {len(rule_files)} rule file(s)')

    return results


def print_results(results: dict) -> int:
    """Print results and return exit code."""
    print("\n" + "=" * 50)
    print("Claude Code Project Structure Verification")
    print("=" * 50)

    if results['passed']:
        print("\n[PASSED]")
        for item in results['passed']:
            print(f"  [ok] {item}")

    if results['warnings']:
        print("\n[WARNINGS]")
        for item in results['warnings']:
            print(f"  [!] {item}")

    if results['failed']:
        print("\n[FAILED]")
        for item in results['failed']:
            print(f"  [X] {item}")

    print("\n" + "-" * 50)
    total = len(results['passed']) + len(results['warnings']) + len(results['failed'])
    print(f"Total: {len(results['passed'])} passed, {len(results['warnings'])} warnings, {len(results['failed'])} failed")

    return 1 if results['failed'] else 0


def main():
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1]).resolve()
    else:
        project_path = Path.cwd()

    print(f"Checking: {project_path}")

    if not project_path.exists():
        print(f"Error: Path does not exist: {project_path}")
        sys.exit(1)

    results = verify_project(project_path)
    exit_code = print_results(results)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

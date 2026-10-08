"""Import a namespace and its reference definitions with the shared proxy planner."""
from __future__ import annotations
import argparse
import importlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

REF = re.compile(r'\[\[([^\]]+)\]\]')
SUPPORT = ('Logseq/Entity', 'Logseq/Frontmatter')

def names(root):
    return {unquote(p.stem).replace('___', '/'): p for p in (root / 'pages').glob('*.md')}

def within(name, namespace):
    return name == namespace or name.startswith(namespace + '/')

def select(source, namespace):
    files = names(source)
    selected = {n for n in files if within(n, namespace)}
    if namespace not in selected:
        raise ValueError(f'Namespace root has no source content: {namespace}')
    logical = set()
    for directory in ('pages', 'journals'):
        for file in (source / directory).glob('*.md'):
            logical.update(n for n in REF.findall(file.read_text()) if within(n, namespace))
    missing = logical - files.keys()
    queue = list(selected)
    support_missing = set()
    while queue:
        name = queue.pop()
        # Supporting entity and frontmatter dictionaries may live outside the namespace.
        refs = REF.findall(files[name].read_text())
        for ref in refs:
            if any(within(ref, p) for p in SUPPORT):
                candidates = [ref] + [ref.rsplit('/', i)[0] for i in range(1, ref.count('/') + 1)]
                for candidate in candidates:
                    if candidate in files and candidate not in selected:
                        selected.add(candidate)
                        queue.append(candidate)
                    elif candidate not in files:
                        support_missing.add(candidate)
    return files, selected, sorted(missing), sorted(support_missing)

def plan_namespace(source, destination, namespace):
    source, destination = source.resolve(), destination.resolve()
    files, selected, missing, support_missing = select(source, namespace)
    library = source / 'mise-tasks/logseq/entity/proxy/page/lib'
    sys.path.insert(0, str(library))
    core = importlib.import_module('core')
    importer = importlib.import_module('task_imports')
    plan = core.build_page_plan(source, destination, namespace, follow_embeds=True)
    for name in sorted(selected):
        core.add_page(plan, name)
    importer.extend_plan(plan)
    for relative, data in list(plan.writes.items()):
        if not relative.startswith('pages/'):
            continue
        lines, body = core.property_lines(data.decode())
        props, _ = core.parse_properties(data.decode())
        # public is destination-owned by Proxy/Page. Existing choices remain intact.
        if 'public' not in props:
            plan.writes[relative] = ('public:: true\n' + ''.join(lines) + body).encode()
    imported = plan.pages
    external = set()
    broken_embeds = set()
    for name in imported:
        for ref in REF.findall(files[name].read_text()):
            if ref not in imported:
                external.add(ref)
        for ref in core.EMBED.findall(files[name].read_text()):
            if ref not in imported:
                broken_embeds.add(ref)
    report = {'namespace': namespace, 'source_pages': len([n for n in selected if within(n, namespace)]),
              'imported_pages': sorted(imported), 'missing_namespace_content': missing,
              'missing_support_content': support_missing, 'external_references': sorted(external),
              'unresolved_embeds': sorted(broken_embeds), 'warnings': plan.warnings}
    return core, plan, report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=Path('gitp-garden'))
    parser.add_argument('--namespace', required=True)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        core, plan, report = plan_namespace(args.source, args.destination, args.namespace)
        for line in plan.details:
            print(line)
        for relative, data in sorted(plan.writes.items()):
            print(('unchanged' if plan.expected[relative] == data else 'write') + ': ' + relative)
        print(json.dumps(report, indent=2))
        if args.apply:
            core.apply_plan(plan)
        if args.report:
            args.report.write_text(json.dumps(report, indent=2) + '\n')
        print('Applied.' if args.apply else 'Preview only. Use --apply to write changes.')
    except (ValueError, OSError) as error:
        parser.exit(1, f'Cannot sync namespace: {error}\n')

if __name__ == '__main__':
    main()

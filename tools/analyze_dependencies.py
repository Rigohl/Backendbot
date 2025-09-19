"""
Script ligero para analizar imports internos `backendbot.*` y generar
un JSON con nodos/aristas y un DOT (Graphviz) simple.

Uso:
    python tools/analyze_dependencies.py

Salida:
    infra/dependency_report.json
    infra/dependency_graph.dot
"""
import ast
import os
import json
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT_JSON = os.path.join(ROOT, 'infra', 'dependency_report.json')
OUT_DOT = os.path.join(ROOT, 'infra', 'dependency_graph.dot')

nodes = set()
edges = defaultdict(set)

for dirpath, dirnames, filenames in os.walk(ROOT):
    # Omitir virtualenvs y carpetas binarias
    if any(p in dirpath for p in ['.venv', '.venv_test', '__pycache__', '.git']):
        continue
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                src = f.read()
            tree = ast.parse(src, filename=path)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    name = n.name
                    if name.startswith('backendbot'):
                        nodes.add(name.split('.')[0])
                        edges[os.path.relpath(path, ROOT)].add(name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ''
                if mod.startswith('backendbot'):
                    nodes.add(mod.split('.')[0])
                    edges[os.path.relpath(path, ROOT)].add(mod)

report = {
    'nodes': sorted(list(nodes)),
    'edges': {k: sorted(list(v)) for k, v in edges.items()}
}

os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

# Generar DOT simple
with open(OUT_DOT, 'w', encoding='utf-8') as f:
    f.write('digraph dependencies {\n')
    for src, targets in report['edges'].items():
        src_node = src.replace('/', '_').replace('.py', '')
        for t in targets:
            tgt_node = t.replace('.', '_')
            f.write(f'  "{src_node}" -> "{tgt_node}";\n')
    f.write('}\n')

print('Reporte generado:', OUT_JSON, OUT_DOT)

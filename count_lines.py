import os

tree_files = []
for f in os.listdir('sprite_editor/models'):
    if f.startswith('tree_') and f.endswith('.py'):
        tree_files.append(f)

for f in tree_files:
    lines = len(open(os.path.join('sprite_editor/models', f)).readlines())
    print(f'{f}: {lines} lines')
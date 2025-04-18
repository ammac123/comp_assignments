import sys
import io
import json
import difflib
from contextlib import redirect_stdout
from pathlib import Path
""" Code here to reload data
expected['q4'] = {}
tex_files = ['kangaroo', 'cat', 'goose']
for tex in tex_files:
    with open(f'_home/{tex}_outline_on_grid.tex','r') as file:
        lines = file.readlines()
        for idx, line in enumerate(lines):
            lines[idx] = line.replace('    ','\t')

    expected['q4'][tex] = lines

with open('tests/expected_outputs.json', 'w') as file:
    
    json.dump(expected, fp=file, indent=4)
"""


sys.path.append((Path.cwd()).__str__())

from tangram.TangramPuzzle import *

with open(Path.cwd() / 'tests' / 'expected_outputs.json') as file:
    expected = json.load(file)



tex_files = ['kangaroo', 'cat', 'goose']
user_input = ''


while user_input not in ['1', '2', '3']:
    user_input = input(f'Select question (1, 2, or 3): ')

actual_outputs = []
expected_outputs = []
f = io.StringIO()

if user_input == '1':
    print('Running Q1 tests:\n')
    key = 'q1'
    with redirect_stdout(f):
        for file in tex_files:
            T = TangramPuzzle(Path.cwd() / 'examples' / f'{file}.tex')
            print(file)
            for piece in T.transformations:
                print(f'{piece:16}', T.transformations[piece], sep=': ')
            print()
            
    actual_outputs = f.getvalue().splitlines()
            

if user_input == '2':
    print('Running Q2 tests:\n')
    key = 'q2'
    with redirect_stdout(f):
        for file in tex_files:
            print(file)
            print(TangramPuzzle(Path.cwd() / 'examples' / f'{file}.tex'))
            print()

    actual_outputs = f.getvalue().splitlines()

if user_input == '3':
    print('Running Q3 tests:\n')
    key = 'q3'
    with redirect_stdout(f):
        for file in tex_files:
            print(file)
            print(TangramPuzzle(Path.cwd() / 'examples' / f'{file}.tex').draw_pieces('', writeout=False))
            print()
    actual_outputs = f.getvalue().splitlines()
        

for e in expected[key]:
    expected_outputs += [e]
    expected_outputs += expected[key][e]
    expected_outputs += ['']


diff = difflib.HtmlDiff(wrapcolumn=80).make_file(fromlines=expected_outputs, tolines=actual_outputs, fromdesc='Expected', todesc='Actual')

with open(Path.cwd() / 'tests' / f'diff_output_{key}.html', 'w') as file:
    file.write(diff)

print(key)
for output in actual_outputs:
    print(output)
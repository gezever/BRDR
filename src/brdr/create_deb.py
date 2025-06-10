from string import Template
import toml
from os import walk, makedirs


with open('pyproject.toml', 'r') as file:
  config = toml.loads(file.read())

print(config)

values = {
  'package': config['project']['name'],
  'version': config['project']['version'],
}

pkg = walk("pkg")
for (dirpath, dirnames, filenames) in pkg:
  for f in filenames:
    if f.startswith('.'):
      continue
    print(dirpath+'/'+f)
    with open(dirpath+'/'+f, 'r') as output:
      src = Template(output.read())
      result = src.substitute(values)
      try:
        makedirs('target/'+dirpath+'/')
      except FileExistsError as e:
        print(f'[WARN] {e}')
      with open('target/'+dirpath+'/'+f, 'w+') as pkg:
        pkg.write(result)

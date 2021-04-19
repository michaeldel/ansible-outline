import pathlib

from dataclasses import dataclass, field

import yaml


@dataclass
class TasksFile:
    path: pathlib.Path

    @property
    def name(self) -> str:
        return self.path.stem

@dataclass
class VarsFile:
    path: pathlib.Path

    @property
    def name(self) -> str:
        return self.path.stem


@dataclass
class Role:
    name: str
    tasksfiles: list[TasksFile] = field(default_factory=list)
    varsfiles: list[VarsFile] = field(default_factory=list)


roles = {}

for path in sorted(pathlib.Path().glob('roles/**/tasks/*.yml')):
    taskfile = TasksFile(path=path)

    rolename = path.parent.parent.stem

    if rolename not in roles:
        roles[rolename] = Role(name=rolename)
    roles[rolename].tasksfiles.append(taskfile)

for path in sorted(pathlib.Path().glob('roles/**/vars/*.yml')):
    varsfile = VarsFile(path=path)

    rolename = path.parent.parent.stem

    if rolename not in roles:
        roles[rolename] = Role(name=rolename)
    roles[rolename].varsfiles.append(varsfile)


def tree(root: pathlib.Path, depth: int = 0):
    assert root.is_dir()

    print(depth * "  ", "📂 ", root.stem, sep='')

    for dir in sorted((p for p in root.iterdir() if p.is_dir())):
        tree(dir, depth + 1)

    for file in sorted((p for p in root.iterdir() if not p.is_dir())):
        print(depth * "  ", "  - ", file.name, sep='')


for role in roles.values():
    print("👥", role.name)

    for varsfile in role.varsfiles:
        print("  💾", varsfile.name)

        with open(varsfile.path) as f:
            for variable in yaml.load(f, Loader=yaml.CLoader):
                print("    -", variable)

    for tasksfile in role.tasksfiles:
        print("  📝", tasksfile.name)

        with open(tasksfile.path) as f:
            for block in yaml.load(f, Loader=yaml.CLoader):
                if 'import_tasks' in block:
                    print("    - 📥 import", block['import_tasks'].rstrip('.yml'))
                if 'assert' in block:
                    print("    - 👮 assert")
                if 'name' in block:
                    print("    -", block['name'])

    files = pathlib.Path(f'roles/{role.name}/files')
    if files.exists():
        tree(files, depth=1)

    templates = pathlib.Path(f'roles/{role.name}/templates')
    if templates.exists():
        tree(templates, depth=1)

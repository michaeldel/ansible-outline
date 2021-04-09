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
class Role:
    name: str
    tasksfiles: list[TasksFile] = field(default_factory=list)


roles = {}

for path in sorted(pathlib.Path().glob('roles/**/tasks/*.yml')):
    taskfile = TasksFile(path=path)

    rolename = path.parent.parent.stem

    if rolename not in roles:
        roles[rolename] = Role(name=rolename)
    roles[rolename].tasksfiles.append(taskfile)


for role in roles.values():
    print("👥", role.name)

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

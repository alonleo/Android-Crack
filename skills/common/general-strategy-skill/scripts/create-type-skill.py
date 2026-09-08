#!/usr/bin/env python3
"""Agent-facing type scaffold generator: preview, --apply, or --verify; JSON stdout.

Requires Python 3 and PyYAML. Does not infer engine implementations or activate
sniff rules. Registration instructions are emitted for the implementing Agent.
"""
import argparse
import ast
import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'skills/common/scripts/lib'))
import common


RUNTIME = '''#!/usr/bin/env python3
"""Register-driven scaffold runner; propagates failures without marking success."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import yaml

def read(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def call(base, relative, extra=()):
    target = (base / relative).resolve()
    if not target.is_relative_to(base.resolve()) or not target.is_file():
        raise ValueError("Missing or unsafe target: " + str(target))
    return subprocess.run([sys.executable, str(target), *extra]).returncode

def main(level, location):
    base = Path(location).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage")
    parser.add_argument("--action")
    args = parser.parse_args()
    if level == "stages":
        items = read(base / "sub-stage-register.yaml")["sub_stages"]
        if args.stage:
            items = [s for s in items if args.stage in (s["id"], s["name"])]
        if not items:
            raise ValueError("Unknown or empty stage selection")
        for item in items:
            extra = ["--action", args.action] if args.action else []
            rc = call(base, item["name"] + "/action-driver.py", extra)
            if rc:
                return rc
    elif level == "action":
        data = read(base / "action-register.yaml")
        selected = args.action or data["run-action"]
        items = [a for a in data["all-actions"] if a["name"] == selected]
        if len(items) != 1:
            raise ValueError("Unknown or duplicate action")
        return call(base, items[0]["path"] + "/step-driver.py")
    else:
        items = read(base / "step-register.yaml")["steps"]
        if not items:
            raise ValueError("Empty step register")
        for step in sorted(items, key=lambda s: int(s["number"])):
            rc = call(base, step["script"])
            if rc:
                return rc
    return 0
'''


def dump(data):
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def stages_from_workflow(root):
    major, stages = [], []
    for line in (root / 'WORKFLOW.md').read_text(encoding='utf-8-sig').splitlines():
        cells = [c.strip().strip('`') for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and len(cells) == 3 and re.fullmatch(r'M\d+ [a-z-]+', cells[0]):
            number, name = cells[0].split()
            major.append(dict(id=number, name=name, function=cells[1], role=cells[2]))
        if line.startswith('|') and len(cells) == 4 and re.fullmatch(r'\d{2}', cells[0]):
            stages.append(dict(id=cells[0], name=cells[1], function=cells[2], role=cells[3],
                               verify=cells[1].endswith('device-verify')))
    if not major or not stages:
        raise ValueError('WORKFLOW.md stage tables missing or unsupported format')
    for rows in (major, stages):
        for key in ('id', 'name'):
            if len({r[key] for r in rows}) != len(rows):
                raise ValueError('Duplicate workflow ' + key)
        if any(not re.fullmatch(r'[a-z][a-z0-9-]*', r['name']) for r in rows):
            raise ValueError('Unsafe workflow stage name')
    return major, stages


def wrapper(level, parent):
    return ('#!/usr/bin/env python3\nimport sys\nfrom pathlib import Path\n'
            f'sys.path.insert(0, str(Path(__file__).resolve().parents[{parent}] / "scripts/common"))\n'
            'from stage_runtime import main\n'
            f'if __name__ == "__main__":\n    sys.exit(main("{level}", __file__))\n')


def build_plan(root, type_name, label):
    if not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', type_name) or len(type_name) > 48:
        raise ValueError('Invalid type name: expected lowercase hyphenated identifier, <=48 characters')
    if not label or any(c in label for c in '\n\r|'):
        raise ValueError('Label must be a nonempty single line without table delimiters')
    relative = Path('skills/strategy') / (type_name + '-strategy-skill')
    target = root / relative
    if not target.resolve().is_relative_to(root.resolve()) or target.exists():
        raise ValueError('Existing or unsafe destination; no overwrite supported')
    major, stages = stages_from_workflow(root)
    plan = {}
    def add(name, content):
        plan[relative / name] = content
    add('SKILL.md', '---\n' + dump(dict(name=type_name + '-strategy-skill',
        description=f'{label} type 策略；仅在引擎识别证据确认属于 {type_name} 后使用。当前为待实现草稿。')) +
        '---\n\n# ' + label + '\n\n状态：draft，尚未完成引擎实现及 APK/真机验证。\n\n'
        '按序读取 [strategy.md](strategy.md)、[workflow.md](workflow.md)、[tools-index.md](tools-index.md)、'
        '[experiences.md](experiences.md)。执行规则见根 [AGENTS.md](../../../AGENTS.md)。\n')
    add('strategy.md', '# 引擎策略\n\n状态：待实现。Agent 必须补充识别证据、资源和代码格式、工具及依赖、构建方式、引擎差异与适用边界。不得直接沿用其他引擎特征。\n')
    workflow = '# ' + label + ' 阶段工作流\n\n来源：[根 WORKFLOW.md](../../../WORKFLOW.md)。交付依据：[OBJECTIVES.md](../../../OBJECTIVES.md)。\n\n'
    for stage in major + stages:
        workflow += f'## {stage["id"]} {stage["name"]}\n\n目的：{stage["function"]}。\n\n通过条件：{stage["role"]}。\n\n'
        workflow += '待 Agent 补充：引擎专属输入、工具依赖、实现方案、产物路径、验证证据及失败恢复。\n\n'
    workflow += '真机条件不满足时，记录 status.yaml 的失败阶段和原因并暂停；不得跳过。每阶段完成后检查产物并记录状态，脚本退出码不能代替验收。\n'
    add('workflow.md', workflow)
    add('experiences.md', '# Type 私有经验\n\n尚未积累经验证的经验。项目事实记入 crackings，跨 type 经验记入根 EXPERIENCES.md。\n')
    add('assets/.gitkeep', '')
    add('scripts/workflow/.gitkeep', '')
    add('scripts/common/stage_runtime.py', RUNTIME)
    add('stages/sub_stage-dispatcher.py', wrapper('stages', 1))
    for stage in stages:
        name = stage['name']
        worker = f'scripts/workflow/sub-stage-{name}.py'
        stage.update(script=(relative / worker).as_posix(), actions=['default-action'], mode='draft')
        prefix = f'stages/{name}'
        add(prefix + '/action-driver.py', wrapper('action', 2))
        add(prefix + '/action-register.yaml', dump({'default': 'default-action', 'run-action': 'default-action',
            'all-actions': [{'name': 'default-action', 'path': './default-action', 'steps': 1}]}))
        add(prefix + '/default-action/step-driver.py', wrapper('steps', 3))
        add(prefix + '/default-action/step-register.yaml', dump({'steps': [dict(number=1, name='implement-stage', script='step-implement-stage.py')]}))
        add(prefix + '/default-action/step-implement-stage.py',
            '#!/usr/bin/env python3\nimport sys\nimport subprocess\nfrom pathlib import Path\n'
            'import yaml\n'
            'if __name__ == "__main__":\n'
            '    skill = Path(__file__).resolve().parents[3]\n'
            '    repo = skill.parents[2]\n'
            '    rows = yaml.safe_load((skill / "stages/sub-stage-register.yaml").read_text(encoding="utf-8"))["sub_stages"]\n'
            f'    row = next(s for s in rows if s["name"] == {name!r})\n'
            '    target = (repo / row["script"]).resolve()\n'
            '    if not target.is_relative_to(repo.resolve()) or not target.is_file():\n        raise ValueError("Invalid worker path")\n'
            '    sys.exit(subprocess.run([sys.executable, str(target)]).returncode)\n')
        add(worker, '#!/usr/bin/env python3\n"""Replace with the engine-specific implementation and evidence checks."""\n'
            'import json\nimport sys\n'
            'if __name__ == "__main__":\n'
            f'    print(json.dumps({{"status": "implementation_required", "type": {type_name!r}, "stage": {name!r}}}))\n'
            '    sys.exit(2)\n')
    register = dict(major_stages=major, sub_stages=stages)
    add('stages/sub-stage-register.yaml', dump(register))
    index = '# 工具与脚本索引\n\n依赖：Python 3、PyYAML；Android 工具通过项目环境加载。\n\n'
    index += '| 脚本 | 用途 |\n|---|---|\n'
    for path in sorted(plan):
        if path.suffix == '.py':
            index += f'| `{path.relative_to(relative).as_posix()}` | 调度器或待实现阶段；运行失败不标记成功 |\n'
    add('tools-index.md', index)
    add('scripts/README.md', index)
    add('registration.md', '# 激活前登记清单\n\n当前草稿尚未注册到生产 sniff 路由。完成实现和识别证据审查后，Agent 必须同步：\n\n'
        '- skills/common/scripts/strategy/strategy-config.yaml：sniff_routing 的 order/patterns、stage_routing、stage_details；按消费者实际 schema 填写。\n'
        '- STRATEGY.md：新增识别特征及 type 映射。\n'
        '- skills/REGISTRY.md：登记 skill 路径和触发条件。\n'
        '- skills/common/scripts/SCRIPTS-INDEX.md：从本 skill tools-index.md 登记实际脚本。\n\n'
        '不得为未实现草稿虚构 sniff 规则或声明完整验证通过。\n')
    for path, content in plan.items():
        if path.suffix == '.py':
            ast.parse(content, filename=str(path))
    return plan


def apply_plan(root, plan):
    for relative in plan:
        path = root / relative
        if path.exists() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Existing or unsafe output: ' + str(path))
    for relative, content in plan.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(content)
        if path.suffix == '.py':
            path.chmod(path.stat().st_mode | 0o111)


def verify(root, skill):
    legacy_register = skill / 'sub-stages.yaml'
    if legacy_register.exists():
        raise ValueError('Legacy type root sub-stages.yaml is forbidden; use stages/sub-stage-register.yaml')
    major, expected = stages_from_workflow(root)
    data = yaml.safe_load((skill / 'stages/sub-stage-register.yaml').read_text(encoding='utf-8'))
    for key, rows in [('major_stages', major), ('sub_stages', expected)]:
        fields = ('id', 'name', 'function', 'role')
        if [[r[k] for k in fields] for r in data[key]] != [[r[k] for k in fields] for r in rows]:
            raise ValueError('Stage contract drift: ' + key)
    for row, expected_row in zip(data['sub_stages'], expected):
        if row['verify'] != expected_row['verify']:
            raise ValueError('Verify flag mismatch')
        worker = (root / row['script']).resolve()
        if not worker.is_relative_to(root.resolve()) or not worker.is_file():
            raise ValueError('Missing worker')
        base = skill / 'stages' / row['name']
        actions = yaml.safe_load((base / 'action-register.yaml').read_text(encoding='utf-8'))
        selected = [a for a in actions['all-actions'] if a['name'] == actions['run-action']]
        if len(selected) != 1:
            raise ValueError('Invalid default action')
        action = (base / selected[0]['path']).resolve()
        if not action.is_relative_to(base.resolve()):
            raise ValueError('Unsafe action')
        steps = yaml.safe_load((action / 'step-register.yaml').read_text(encoding='utf-8'))['steps']
        if not steps or len({int(s['number']) for s in steps}) != len(steps):
            raise ValueError('Invalid step register')
        for step in steps:
            path = (action / step['script']).resolve()
            if not path.is_relative_to(action) or not path.is_file():
                raise ValueError('Missing or unsafe step')
    for path in skill.rglob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    return dict(status='scaffold_valid', stages=len(expected), major_stages=len(major), runtime_validated=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--type', required=True, dest='type_name')
    parser.add_argument('--label')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', args.type_name):
        raise ValueError('Invalid type name')
    skill = ROOT / 'skills/strategy' / (args.type_name + '-strategy-skill')
    if args.verify:
        result = verify(ROOT, skill)
    else:
        plan = build_plan(ROOT, args.type_name, args.label or args.type_name)
        if args.apply:
            apply_plan(ROOT, plan)
            result = verify(ROOT, skill)
            result['status'] = 'created_draft'
        else:
            result = dict(status='preview', files=[p.as_posix() for p in plan])
        result.update(file_count=len(plan), skill=str(skill), next_action='Read registration.md; implement and validate each stage before activating sniff routing')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    try:
        if (ROOT / 'tools/environments/env.sh').is_file():
            common.ensure_env()
        common.log_info('Type skill generator; scaffold validation is not APK acceptance')
        main()
    except (ValueError, OSError, KeyError, yaml.YAMLError) as error:
        print(json.dumps(dict(status='error', message=str(error)), ensure_ascii=False))
        sys.exit(1)

"""Bounded source/document reconciliation; not an alternate configuration validator."""
import json
import re


class DocumentationError(AssertionError):
    """A failed source/document binding with useful local evidence."""


def fail(code, detail):
    raise DocumentationError(f'{code}: {detail}')


def inventory(value, prefix=()):
    """Inventory supplied declaration objects and leaves, not arbitrary optional API."""
    if not isinstance(value, dict) or not value:
        fail('DOC_EMPTY_SCOPE', '.'.join(prefix) or 'declaration')
    result = {}
    for key, item in value.items():
        if not isinstance(key, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', key):
            fail('DOC_UNCLASSIFIED', repr(prefix + (key,)))
        path = prefix + (key,)
        if type(item) not in (dict, list, str, int, float, bool, type(None)):
            fail('DOC_UNCLASSIFIED', '.'.join(path))
        result['.'.join(path)] = item
        if isinstance(item, dict) and item:
            result.update(inventory(item, path))
    return result


def anchor(path):
    return 'declaration-' + path.replace('.', '-').replace('_', '-')


def table_cells(line):
    """Split supported ordinary tables, keeping inline-code/escaped pipes intact."""
    cells, part, code, escaped = [], [], False, False
    for char in line.strip():
        if escaped:
            part.append(char)
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == '`':
            code = not code
            part.append(char)
        elif char == '|' and not code:
            cells.append(''.join(part).strip())
            part = []
        else:
            part.append(char)
    if code or escaped:
        fail('DOC_AMBIGUOUS', 'unsupported/unclosed table cell')
    cells.append(''.join(part).strip())
    return cells[1:-1] if not cells[0] and not cells[-1] else cells


def documented_rows(text):
    """Independently enumerate every supplied-field row in its declared section."""
    sections = re.findall(r'^## Declaration records\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    if len(sections) != 1:
        fail('DOC_AMBIGUOUS', 'expected exactly one Declaration records section')
    result, ids, fenced = {}, set(), False
    for line in sections[0].splitlines():
        if line.startswith('```'):
            fenced = not fenced
            continue
        if fenced or not line.startswith('|'):
            continue
        cells = table_cells(line)
        if cells[0] == 'Declaration path' or re.fullmatch(r'[-: ]+', cells[0]):
            continue
        if len(cells) != 2:
            fail('DOC_UNCLASSIFIED', 'expected path and selected-value columns: ' + line)
        found = re.fullmatch(r'<a id="([^"]+)"></a>`([^`]+)`', cells[0])
        fact = re.fullmatch(r'`([^`]+)`', cells[1])
        if not found or not fact:
            fail('DOC_UNCLASSIFIED', 'malformed supported declaration row: ' + line)
        record_id, path = found.groups()
        if record_id != anchor(path) or record_id in ids or path in result:
            fail('DOC_AMBIGUOUS', 'duplicate or incorrect anchor/row: ' + path)
        ids.add(record_id)
        raw = fact.group(1)
        if raw == 'object':
            value = ('object',)
        else:
            try:
                value = json.loads(raw)
            except (ValueError, TypeError):
                fail('DOC_UNCLASSIFIED', 'value must be a JSON scalar/list/empty mapping: ' + path)
        result[path] = value
    if not result:
        fail('DOC_EMPTY_SCOPE', 'Declaration records')
    return result


def typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(typed_equal(v, right[k]) for k, v in left.items())
    if isinstance(left, list):
        return len(left) == len(right) and all(typed_equal(a, b) for a, b in zip(left, right))
    return left == right


def validate_definition_pointers(registration, definitions, root):
    """Check the small source/document map against real registered definitions."""
    from pathlib import Path
    registered = {(group, name) for group in ('app_profiles', 'guest_templates')
                  for name in registration[group]}
    if not registered or not definitions:
        fail('DOC_EMPTY_SCOPE', 'registered definition pointers')
    if registered != set(definitions):
        fail('DOC_INVENTORY', f'missing definitions: {sorted(registered - set(definitions))}; '
             f'stale definitions: {sorted(set(definitions) - registered)}')
    root = Path(root).resolve()
    for (group, name), (source, document) in definitions.items():
        if registration[group][name] != {'source': source}:
            fail('DOC_STALE_SOURCE', f'{group}.{name} -> {source}')
        for locator in (source, document):
            selected = root / locator
            if not selected.is_file() or not selected.resolve().is_relative_to(root):
                fail('DOC_STALE_SOURCE', f'{group}.{name} -> {locator}')


def reconcile(value, text, source, document):
    accepted, rows = inventory(value), documented_rows(text)
    if set(accepted) != set(rows):
        fail('DOC_INVENTORY', f'{source} -> {document}; '
             f'undocumented: {sorted(set(accepted) - set(rows))}; '
             f'orphan records: {sorted(set(rows) - set(accepted))}')
    for path, source_value in accepted.items():
        expected = ('object',) if isinstance(source_value, dict) and source_value else source_value
        if not typed_equal(expected, rows[path]):
            fail('DOC_FACT_DRIFT', f'{source}#{path} = {expected!r}; '
                 f'{document}#{anchor(path)} = {rows[path]!r}')
    return len(accepted)


def read_excerpt(page, heading, reader):
    """Read exactly one YAML fence in one explicitly named second-level section."""
    pattern = r'^## ' + re.escape(heading) + r'\n(.*?)(?=^## |\Z)'
    sections = re.findall(pattern, page, re.M | re.S)
    if len(sections) != 1:
        fail('DOC_AMBIGUOUS', 'expected exactly one section: ' + heading)
    fences = re.findall(r'^```yaml[ \t]*\n(.*?)^```[ \t]*$', sections[0], re.M | re.S)
    if len(fences) != 1:
        fail('DOC_AMBIGUOUS', 'expected exactly one YAML excerpt in ' + heading)
    return reader(fences[0])


def assert_excerpt(page, heading, actual, reader):
    if not typed_equal(read_excerpt(page, heading, reader), actual):
        fail('DOC_STALE_EXCERPT', heading)


def expect_refusal(action, error_type, code, path):
    expected_path = tuple(path.split('.')) if isinstance(path, str) and path else tuple(path)
    try:
        action()
    except error_type as error:
        if error.code != code or error.path != expected_path:
            fail('DOC_WRONG_REFUSAL', f'expected {code} at {path}; got {error}')
    else:
        fail('DOC_UNEXPECTED_SUCCESS', f'expected {code} at {path}')


def mqtt_property_inventory(source, owner='validate'):
    """Read only the selected validator's literal MQTT closed-object declaration.

    This intentionally refuses changed declaration patterns instead of pretending
    to infer arbitrary procedural validation. Conditions still require review.
    """
    import ast
    module = ast.parse(source)
    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)
                 and node.name == owner]
    if len(functions) != 1:
        fail('DOC_UNCLASSIFIED', 'component_foundations.validate')
    # Only the direct if/elif adapter dispatch is understood. A recursive walk
    # could mistake a conditionally bypassed closed() call for the API owner.
    dispatches = [node for node in functions[0].body if isinstance(node, ast.If)]
    if len(dispatches) != 1 or any(not isinstance(node, (ast.Expr, ast.If))
                                   for node in functions[0].body):
        fail('DOC_UNCLASSIFIED', 'MQTT unconditional adapter dispatch')
    branch, matches = dispatches[0], []
    while True:
        test = branch.test
        if not (isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name) and test.left.id == 'adapter'
                and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and isinstance(test.comparators[0].value, str)):
            fail('DOC_UNCLASSIFIED', 'MQTT conditional/indirect adapter dispatch')
        if test.comparators[0].value == 'mqtt':
            matches.append(branch)
        if len(branch.orelse) == 1 and isinstance(branch.orelse[0], ast.If):
            branch = branch.orelse[0]
        else:
            break
    if len(matches) != 1:
        fail('DOC_UNCLASSIFIED', 'MQTT adapter branch')
    body = matches[0].body
    statement = body[0] if body else None
    if not (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call)
            and isinstance(statement.value.func, ast.Name)
            and statement.value.func.id == 'closed'):
        fail('DOC_UNCLASSIFIED', 'MQTT closed declaration must be first and unconditional')
    call = statement.value
    calls = [node for statement in body for node in ast.walk(statement)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == 'closed']
    if len(calls) != 1 or len(call.args) != 3 or call.keywords:
        fail('DOC_UNCLASSIFIED', 'MQTT closed declaration changed shape')
    if not isinstance(call.args[0], ast.Name) or call.args[0].id != 'value':
        fail('DOC_UNCLASSIFIED', 'MQTT nested/indirect declaration')
    result = []
    for argument in call.args[1:]:
        if not isinstance(argument, (ast.Tuple, ast.List)) or any(
                not isinstance(item, ast.Constant) or not isinstance(item.value, str)
                for item in argument.elts):
            fail('DOC_UNCLASSIFIED', 'MQTT computed accepted-field declaration')
        result.extend(item.value for item in argument.elts)
    if not result:
        fail('DOC_EMPTY_SCOPE', 'MQTT accepted properties')
    if len(result) != len(set(result)):
        fail('DOC_AMBIGUOUS', 'MQTT accepted properties')
    return set(result)


def mapped_mqtt_property_inventory(framework, records, validator):
    """Bind every source pointer to the actual selected executable owner."""
    import inspect
    from pathlib import Path
    if not records:
        fail('DOC_EMPTY_SCOPE', 'MQTT property source pointers')
    actual = Path(inspect.getsourcefile(validator)).resolve()
    root = Path(framework).resolve()
    if not actual.is_relative_to(root) or not actual.is_file():
        fail('DOC_STALE_SOURCE', 'MQTT validator is outside the selected framework')
    for control, (source, symbol, _, _) in records.items():
        selected = root / source
        if (not selected.is_file() or selected.resolve() != actual
                or source != actual.relative_to(root).as_posix()
                or symbol != validator.__name__):
            fail('DOC_STALE_SOURCE', f'{control}: {source}#{symbol}; '
                 f'owner is {actual.relative_to(root)}#{validator.__name__}')
    return mqtt_property_inventory(actual.read_text(), owner=validator.__name__)


def registration_rows(text):
    """Read all normal shared-catalogue table rows, including malformed additions."""
    headers = {'Selection', 'Runtime', 'Monitoring profile', 'Requirement',
               'Fragment', 'Registered declaration'}
    rows, fenced = [], False
    for line in text.splitlines():
        if line.startswith('```'):
            fenced = not fenced
            continue
        if fenced or not line.startswith('|'):
            continue
        first = table_cells(line)[0]
        if first in headers or re.fullmatch(r'[-: ]+', first):
            continue
        match = re.fullmatch(r'<a id="(registration-[^"]+)"></a>`([^`]+)`', first)
        if not match:
            fail('DOC_UNCLASSIFIED', 'shared registration row: ' + first)
        anchor_id, key = match.groups()
        if anchor_id != 'registration-' + key.replace('.', '-').replace('_', '-'):
            fail('DOC_AMBIGUOUS', 'shared registration anchor: ' + key)
        rows.append(key)
    if not rows:
        fail('DOC_EMPTY_SCOPE', 'shared registrations')
    if len(rows) != len(set(rows)):
        fail('DOC_AMBIGUOUS', 'duplicate shared registration')
    return set(rows)

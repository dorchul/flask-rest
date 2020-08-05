# pylint plugin to suppress false positives of type "method x has no y member".
# Based on: https://stackoverflow.com/a/51678586/1014208
from astroid import MANAGER, extract_node, scoped_nodes

FUNCTION_TO_WHITELISTED_PROPS = {
    'logger': ('debug', 'info', 'warning', 'error', 'addHandler', 'handlers',
               'setLevel'),
}


def register(_):
    pass


def transform(f):
    for prop in FUNCTION_TO_WHITELISTED_PROPS.get(f.name, []):
        f.instance_attrs[prop] = extract_node(
            'def {name}(arg): return'.format(name=prop))


MANAGER.register_transform(scoped_nodes.FunctionDef, transform)

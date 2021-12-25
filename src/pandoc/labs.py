import pandoc
import pandoc.types

def is_type_or_types(item):
    return isinstance(item, type) or (
        isinstance(item, tuple) and all(isinstance(x, type) for x in item)
    )

def to_function(condition):
    if is_type_or_types(condition):
        return lambda elt: isinstance(elt, condition)
    elif callable(condition):
        return condition
    else:
        error = "condition should be a type, a tuple of types, or a function"
        error += f", not {condition!r}"
        raise TypeError(error)

# Distinguish Query and (lazy) List
class Query:
    def __init__(self, *filters):
        self._filters = []
        self.add(*filters)
    def add(self, *filters):
        self._filters.extend(to_function(f) for f in filters)
    def __call__(self, root):
        output = (item for item in pandoc.iter(root, path=True))
        for _filter in self._filters:
            output = ((elt, path) for (elt, path) in output if _filter(elt))
        return output

# Nota: we have filters, transforms and "output/action" (the end of the stuff)
# getitem if the first example of transform: List -> List.
# Mmm actually filter is a special case of transform.
# List should hold this list of transforms; Query is probably not
# appropriate then as a chain of *filters*; what we have is a chain of
# *transforms* (we can call that query too if we want)

class List:
    def __init__(self, root, query):
        self._root = root
        self._query = query
    def __repr__(self):
        it = iter(self)
        return repr(list(it))
    def __iter__(self):
        return (elt for (elt, path) in self._query(self._root))
    def __getitem__(self, index):
        # not complete, need slice support (?) and also key support
        # TODO !!!
        pass


def f(root, condition):
    query = Query(condition)
    return List(root, query)

# Tmp ; need some more dynamic hook into pandoc.types (think late loading,
# reset, etc.)

pandoc.types.Constructor.f = f
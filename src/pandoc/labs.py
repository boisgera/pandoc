"""
Design
================================================================================

Fundamental object: Query.

  - Query defined independently of the root(s) it will be applied to.

  - Query is a callable ? Once defined, applied with `query(doc)` for
    example ? Or stuff = query(doc) is the aim is some extraction ?
    Or for item in query(doc): do_stuff_with(item). Root(s?) can be
    a Pandoc item or a list or tuple of stuff, etc.
    
    Could also envision query methods directly on Pandoc Elements ...
    dunno, have to think of it. Would be convenient (shorter code), 
    but messy (Elements are not "algebraic datatypes" anymore).

  - Query construction uses chaining (fluent) interface : chaining of
    transforms, chaining of filters, etc.

  - Query definition is lazy, does not compute anything: just abstract
    description of what we intend to do.

  - Query applied to a root : by default all items (in doc order)

  - Query filters: may reduce the list of items. Chaining is an "AND" thus
    a single-filter should be likely "OR"-based. E.g.
    query.filter((Para, Plain)) means keep Para OR Plain.
    Possible filters : filter(types), filter(predicate), has_attr(...),
    id_is(id=...), etc. Need to have stuff to match the existence of a feature
    has well as its value (ex: has id vs id is "main"). Also, class matching,
    etc. Essentially, many syntaxic sugar on top of "filter(predicate)".
    May need a meta stuff: .either(pred1, pred2, ...) ? Have a look at
    shader graph to see how stuff is forked/join with such interfaces.

  - Navigation: .parent, .children, .next_sibling, get_item[i]. Extract a 
    general "navigate" function such that all that stuff is merely syntaxic
    sugar ?

  - Mutation: .remove(), .replace_with(stuff), etc. Probably complex to get it
    right here. All this stuff should be TERMINAL : if any, nothing can be
    chained after that. Also: set attributes, ids, etc.
    Again, can we come up with a single, root, general mutation operation ?
    Or is it too complex here?
    Apply mutation in reverse order by default?

  - Iteration ? Query as a container "removes" path info by default so that
    we can deal with a list of "document items", make comprehensions, etc.


"""


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
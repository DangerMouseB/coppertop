from abc import ABCMeta, abstractmethod
import numpy as np

from batteries import Missing
from batteries.collections import IdentitySet, LambdaDictionary


# TODO
# provide more deepcopy like (i.e. dumb recursive) behaviour on built-in collection types, list, dict, set, tuple, string

def createClosure(*args, **kwargs):
    context = kwargs.get('context', None)
    toVisit = IdentitySet()
    for arg in args:
        if isinstance(arg, (list, tuple, set)):         # getattr(arg, "__iter__", None)
            toVisit.update(arg)
        else:
            toVisit.add(arg)
    visited = IdentitySet()
    while len(toVisit) > 0:
        obj = toVisit.pop()
        visited.add(obj)
        getter = getattr(obj, "_ccClosure", Missing)
        if getter is not Missing:
            for neighbour in getter(context):
                if neighbour not in visited: toVisit.add(neighbour)
    return visited
                
def copyClosure(closure, context=None):
    oc_map = LambdaDictionary(id)
    for original in closure:
        creator = getattr(original, "_ccCreate", Missing)
        if not creator is Missing:
            copy = creator(context)
            assert isinstance(copy, type(original)), "copy is not type(original)"
            assert copy is not original, "copy is not type(original)"
            oc_map[original] = creator(context)
        else:
            oc_map[original] = GodCopy(original)
    for original, copy in oc_map.items():
        gluer = getattr(original, "_ccGlue", Missing)
        if not gluer is Missing:
            copy._ccGlue(original, oc_map, context)
    return oc_map

class ICopyClosure(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def _ccCreate(self, context):
        pass
    @abstractmethod
    def _ccGlue(self, original, oc_map, context):
        """oc_map maps the orignal to the copy"""
        pass
    @abstractmethod
    def _ccClosure(self, context):
        pass


def GodCopy(obj):
    if isinstance(obj, np.ndarray):
        return obj.copy()
    else:
        raise TypeError("Unhandled type")


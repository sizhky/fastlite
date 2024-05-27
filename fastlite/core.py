# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['diagram']

# %% ../nbs/00_core.ipynb 3
from fastcore.utils import *
from fastcore.xml import highlight
from fastcore.xtras import hl_md

from sqlite_utils import Database
from sqlite_utils.db import Table, View

try: from graphviz import Source
except ImportError: pass

# %% ../nbs/00_core.ipynb 6
class _Getter:
    "Abstract class with dynamic attributes providing access to DB objects"
    def __init__(self, db): self.db = db
    # NB: Define `__dir__` in subclass to get list of objects
    def __repr__(self): return ", ".join(dir(self))
    def __getitem__(self, idxs):
        if isinstance(idxs,str): idxs = [idxs]
        return [self.db.table(o) for o in idxs]
    def __getattr__(self, k):
        if k[0]=='_': raise AttributeError
        return self.db[k]

class _TablesGetter(_Getter):
    def __dir__(self): return self.db.table_names()

@patch(as_prop=True)
def t(self:Database): return _TablesGetter(self)

# %% ../nbs/00_core.ipynb 11
class _Col:
    def __init__(self, t, c): self.t,self.c = t,c
    def __str__(self):  return f'"{self.t}"."{self.c}"'
    def __repr__(self):  return f'{self.c}'

class _ColsGetter:
    def __init__(self, tbl): self.tbl = tbl
    def __dir__(self): return map(repr, self())
    def __call__(self): return [_Col(self.tbl.name,o.name) for o in self.tbl.columns]
    def __repr__(self): return ", ".join(dir(self))

    def __getattr__(self, k):
        if k[0]=='_': raise AttributeError
        return _Col(self.tbl.name, k)

@patch(as_prop=True)
def c(self:Table): return _ColsGetter(self)

@patch(as_prop=True)
def c(self:View): return _ColsGetter(self)

# %% ../nbs/00_core.ipynb 16
@patch
def __str__(self:Table): return f'"{self.name}"'

@patch
def __str__(self:View): return f'"{self.name}"'

# %% ../nbs/00_core.ipynb 20
@patch
def q(self:Database, sql: str, params = None)->list:
    return list(self.query(sql, params=params))

# %% ../nbs/00_core.ipynb 27
class _ViewsGetter(_Getter):
    def __dir__(self): return self.db.view_names()

@patch(as_prop=True)
def v(self:Database): return _ViewsGetter(self)

# %% ../nbs/00_core.ipynb 33
def _edge(tbl):
    return "\n".join(f"{fk.table}:{fk.column} -> {fk.other_table}:{fk.other_column};"
                     for fk in tbl.foreign_keys)

def _edges(tbls): return "\n".join(map(_edge, tbls))

def _row(col):
    xtra = " 🔑" if col.is_pk else ""
    bg = ' bgcolor="#ffebcd"' if col.is_pk else ""
    return f'    <tr><td port="{col.name}"{bg}>{col.name}{xtra}</td></tr>'

def _tnode(tbl):
    rows = "\n".join(_row(o) for o in tbl.columns)
    bg = ' bgcolor="lightgray"'
    res = f"""<table cellborder="1" cellspacing="0">
    <tr><td{bg}>{tbl.name}</td></tr>
{rows}
  </table>"""
    return f"{tbl.name} [label=<{res}>];\n"

def _tnodes(tbls): return "\n\n".join(_tnode(o) for o in tbls)

# %% ../nbs/00_core.ipynb 34
def diagram(tbls, ratio=0.7, size="10", neato=False, render=True):
    layout = "\nlayout=neato;\noverlap=prism;\noverlap_scaling=0.5;""" if neato else ""

    res = f"""digraph G {{
rankdir=LR;{layout}
size="{size}";
ratio={ratio};
node [shape=plaintext]

{_tnodes(tbls)}

{_edges(tbls)}
}}
"""
    return Source(res) if render else res

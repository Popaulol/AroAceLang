from __future__ import annotations
import ast
import json
import sys
import typing


if typing.TYPE_CHECKING:
    DictAst = dict[str, DictAst | str | int | None]

missing = set()


class DictWalker(ast.NodeVisitor):
    def generic_visit(self, node: ast.AST, just_get_info=False) -> DictAst:
        info = {}
        if not just_get_info:
            missing.add(node.__class__.__name__)
            print(f"Unimplemented Node: {node}")
            super().generic_visit(node)
            info["type"] = f"Unimplemented: {node}"

        if hasattr(node, "type_comment"):
            type_comment = node.type_comment
        else:
            type_comment = None

        return {
            "lineno": node.lineno,
            "col_offset": node.col_offset,
            "end_lineno": node.end_lineno,
            "end_col_offset": node.end_col_offset,
            "type_comment": type_comment,
        } | info

    def visit_Module(self, node: ast.Module) -> DictAst:
        # TODO: Look if need to care about the `type_ignores` attribute.

        body = list(map(super().visit, node.body))

        return {"type": "Module", "body": body}  # | self.generic_visit(node, True)

    def visit_Expr(self, node: ast.Expr) -> DictAst:
        value = super().visit(node.value)

        return {"type": "Expr", "value": value} | self.generic_visit(node, True)

    def visit_Call(self, node: ast.Call) -> DictAst:
        func = super().visit(node.func)
        args = list(map(super().visit, node.args))
        keywords = list(map(super().visit, node.keywords))
        return {
            "type": "Call",
            "func": func,
            "args": args,
            "keywords": keywords,
        } | self.generic_visit(node, True)

    def visit_Name(self, node: ast.Name) -> DictAst:
        return {
            "type": "Name",
            "id": node.id,
            "ctx": super().visit(node.ctx),
        } | self.generic_visit(node, True)

    def visit_Load(self, node: ast.Load) -> DictAst:
        return {"type": "Load"}  # | self.generic_visit(node, True)

    def visit_Constant(self, node: ast.Constant) -> DictAst:
        return {
            "type": "Constant",
            "value": node.value,
            "kind": node.kind,
        } | self.generic_visit(node, True)

    def visit_keyword(self, node: ast.keyword) -> DictAst:
        return {"type": "keyword", "arg": node.arg, "value": self.visit(node.value)}

    def visit_Import(self, node: ast.Import) -> DictAst:
        return {
            "type": "Import",
            "names": list(map(self.visit, node.names)),
        } | self.generic_visit(node, True)

    def visit_alias(self, node: ast.alias) -> DictAst:
        return {
            "type": "alias",
            "name": node.name,
            "asname": node.asname,
        } | self.generic_visit(node, True)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> DictAst:
        return {
            "type": "ImportFrom",
            "module": node.module,
            "names": list(map(self.visit, node.names)),
            "level": node.level,
        } | self.generic_visit(node, True)

    def visit_ClassDef(self, node: ast.ClassDef) -> DictAst:
        return {
            "type": "ClassDef",
            "name": node.name,
            "bases": list(map(self.visit, node.bases)),
            "keywords": list(map(self.visit, node.keywords)),
            "body": list(map(self.visit, node.body)),
            "decorator_list": list(map(self.visit, node.decorator_list)),
        } | self.generic_visit(node, True)

    def visit_Attribute(self, node: ast.Attribute) -> DictAst:
        return {
            "type": "Attribute",
            "value": self.visit(node.value),
            "attr": node.attr,
            "ctx": self.visit(node.ctx),
        } | self.generic_visit(node, True)

    def visit_Store(self, node: ast.Store) -> DictAst:
        return {"type": "Store"}

    def visit_BitOr(self, node: ast.BitOr) -> DictAst:
        return {"type": "BitOr"}

    def visit_arguments(self, node: ast.arguments) -> DictAst:
        return {
            "type": "arguments",
            "posonlyargs": [self.visit(arg) for arg in node.posonlyargs],
            "args": [self.visit(arg) for arg in node.args],
            "vararg": self.visit(node.vararg) if node.vararg is not None else None,
            "kwonlyargs": [self.visit(arg) for arg in node.kwonlyargs],
            "kw_defaults": [
                self.visit(arg) if arg is not None else None for arg in node.kw_defaults
            ],
            "kwarg": self.visit(node.kwarg) if node.kwarg is not None else None,
            "defaults": [self.visit(default) for default in node.defaults],
        }

    def visit_Not(self, node: ast.Not) -> DictAst:
        return {"type": "Not"}

    def visit_comprehension(self, node: ast.comprehension) -> DictAst:
        return {
            "type": "comprehension",
            "target": self.visit(node.target),
            "iter": self.visit(node.iter),
            "ifs": [self.visit(if_) for if_ in node.ifs],
            "is_async": node.is_async,
        }

    def visit_IsNot(self, node: ast.IsNot) -> DictAst:
        return {"type": "IsNot"}

    def visit_Eq(self, node: ast.Eq) -> DictAst:
        return {"type": "Eq"}

    def visit_withitem(self, node: ast.withitem) -> DictAst:
        return {
            "type": "withitem",
            "context_expr": self.visit(node.context_expr),
            "optional_vars": self.visit(node.optional_vars)
            if node.optional_vars is not None
            else None,
        }

    def visit_Add(self, node: ast.Add) -> DictAst:
        return {"type": "Add"}

    def visit_Subscript(self, node: ast.Subscript) -> DictAst:
        return {
            "type": "Subscript",
            "value": self.visit(node.value),
            "slice": self.visit(node.slice),
            "ctx": self.visit(node.ctx),
        } | self.generic_visit(node, True)

    def visit_BinOp(self, node: ast.BinOp) -> DictAst:
        return {
            "type": "BinOp",
            "left": self.visit(node.left),
            "op": self.visit(node.op),
            "right": self.visit(node.right),
        } | self.generic_visit(node, True)

    def visit_With(self, node: ast.With) -> DictAst:
        return {
            "type": "With",
            "items": [self.visit(item) for item in node.items],
            "body": [self.visit(stmt) for stmt in node.body],
        } | self.generic_visit(node, True)

    def visit_Assign(self, node: ast.Assign) -> DictAst:
        return {
            "type": "Assign",
            "targets": [self.visit(target) for target in node.targets],
            "value": self.visit(node.value),
        } | self.generic_visit(node, True)

    def visit_Dict(self, node: ast.Dict) -> DictAst:
        return {
            "type": "Dict",
            "keys": [self.visit(key) if key is not None else None for key in node.keys],
            "values": [self.visit(value) for value in node.values],
        } | self.generic_visit(node, True)

    def visit_arg(self, node: ast.arg) -> DictAst:
        return {
            "type": "arg",
            "arg": node.arg,
            "annotation": self.visit(node.annotation)
            if node.annotation is not None
            else None,
        } | self.generic_visit(node, True)

    def visit_Return(self, node: ast.Return) -> DictAst:
        return {
            "type": "Return",
            "value": self.visit(node.value) if node.value is not None else None,
        } | self.generic_visit(node, True)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> DictAst:
        return {
            "type": "FunctionDef",
            "name": node.name,
            "args": self.visit(node.args),
            "body": [self.visit(stmt) for stmt in node.body],
            "decorator_list": [
                self.visit(decorator) for decorator in node.decorator_list
            ],
            "return": self.visit(node.returns) if node.returns is not None else None,
        } | self.generic_visit(node, True)

    def visit_ListComp(self, node: ast.ListComp) -> DictAst:
        return {
            "type": "ListComp",
            "elt": self.visit(node.elt),
            "generators": [self.visit(gen) for gen in node.generators],
        } | self.generic_visit(node, True)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> DictAst:
        return {
            "type": "UnaryOp",
            "op": self.visit(node.op),
            "operand": self.visit(node.operand),
        } | self.generic_visit(node, True)

    def visit_Compare(self, node: ast.Compare) -> DictAst:
        return {
            "type": "Compare",
            "ops": [self.visit(op) for op in node.ops],
            "comparators": [self.visit(comparator) for comparator in node.comparators],
        } | self.generic_visit(node, True)

    def visit_IfExp(self, node: ast.IfExp) -> DictAst:
        return {
            "type": "IfExp",
            "test": self.visit(node.test),
            "body": self.visit(node.body),
            "orelse": self.visit(node.orelse),
        } | self.generic_visit(node, True)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> DictAst:
        return {
            "type": "JoinedStr",
            "values": [self.visit(value) for value in node.values],
        } | self.generic_visit(node, True)

    def visit_Tuple(self, node: ast.Tuple) -> DictAst:
        return {
            "type": "Tuple",
            "elts": [self.visit(elt) for elt in node.elts],
            "ctx": self.visit(node.ctx),
        } | self.generic_visit(node, True)

    def visit_FormattedValue(self, node: ast.FormattedValue) -> DictAst:
        return {
            "type": "FormattedValue",
            "value": self.visit(node.value),
            "conversion": node.conversion,
            "format_spec": self.visit(node.format_spec)
            if node.format_spec is not None
            else None,
        } | self.generic_visit(node, True)

    def visit_For(self, node: ast.For) -> DictAst:
        return {
            "type": "For",
            "target": self.visit(node.target),
            "iter": self.visit(node.iter),
            "body": [self.visit(stmt) for stmt in node.body],
            "orelse": [self.visit(stmt) for stmt in node.orelse],
        } | self.generic_visit(node, True)

    def visit_If(self, node: ast.If) -> DictAst:
        return {
            "type": "If",
            "test": self.visit(node.test),
            "body": [self.visit(stmt) for stmt in node.body],
            "orelse": [self.visit(stmt) for stmt in node.orelse],
        } | self.generic_visit(node, True)


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as f1:
        source = f1.read()

    dict_code = DictWalker().visit(ast.parse(source))
    json.dump(dict_code, sys.stdout)  # , indent=4)

    for missing in missing:
        print(missing)

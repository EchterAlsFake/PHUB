import re
import ast
import sys
import glob
import autopep8

tree: ast.AST = None
BLOCK = ast.Module | ast.FunctionDef | ast.ClassDef

MSG = '''WARNING - THIS CODE IS AUTOMATICALLY GENERATED. UNSTABILITY MAY OCCUR.
FOR ADVANCED DOSCTRINGS, COMMENTS AND TYPE HINTS, PLEASE USE THE DEFAULT BRANCH.'''

FORBIDDEN_IMPORTS = [
    'typing.Self',
    'typing.LiteralString'
]

def get_parent(node: ast.AST) -> ast.AST | None:
    '''
    Get an AST node parent.
    '''
    
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child is node:
                return parent

def get_parent_block(node: ast.AST) -> ast.AST | None:
    '''
    Get the nearest parent that is a block.
    '''
    
    parent = get_parent(node)
    
    if parent is None:
        return None
    
    while not isinstance(parent, BLOCK):
        parent = get_parent(parent)
        
    return parent


class Transformer(ast.NodeTransformer):
    
    def __init__(self) -> None:
        self.walruses: list[tuple[ast.AST]] = []
        super().__init__()
    
    def visit_AnnAssign(self, node: ast.AnnAssign):
        # Remove type hints from variables
        
        if isinstance(node.target, ast.Name):
        
            # Make sure parent is not a dataclass
            parent = get_parent(node)
            if isinstance(parent, ast.ClassDef):
                for decorator in parent.decorator_list:
                    if decorator.id == 'dataclass':
                        node.annotation = ast.Name(id = 'object')
                        return node
            
            new = ast.Assign(targets = [node.target], value = node.value)
            ast.copy_location(new, node)
            ast.fix_missing_locations(new)
        
            return new        
        return node
    
    def visit_FunctionDef(self, node):
        # Remove type hints from signatures
                
        for arg in node.args.args:
            arg.annotation = None
        
        if node.returns:
            node.returns = None      
        
        self.generic_visit(node)
        return node

    def visit_NamedExpr(self, node: ast.NamedExpr):
        # Remove walrus operators
        
        parent = get_parent_block(node)
        
        new = node.value
        ast.copy_location(new, node)
        ast.fix_missing_locations(new)
        self.walruses.append((parent, node))
        
        return new
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        # Remove typing.Self imports
        
        if node.module and node.names:
            names = []
            for alias in node.names:
                if node.module + '.' + alias.name not in FORBIDDEN_IMPORTS:
                    names.append(alias)
            
            node.names = names
        
        if not node.names:
            return None
        
        return node 

    def visit_Name(self, node: ast.Name):
        # Remove walruses references
        
        if isinstance(node.ctx, ast.Load):
            parent = get_parent_block(node)
            
            for walrus_parent, walrus in self.walruses:
                if parent is walrus_parent and node.id == walrus.target.id:
                    return walrus.value
        
        return node

    def visit_BinOp(self, node: ast.BinOp):
        # Remove unions inside solid calls
        
        if isinstance(node.op, ast.BitOr) and isinstance(node.left, ast.Name):
            new = ast.Name(id = 'object', ctx = ast.Load())
            ast.copy_location(new, node)
            ast.fix_missing_locations(new)
            return new
        
        self.generic_visit(node)
        return node

def translate(code: str, msg: str = None) -> str:
    '''
    Translates 3.11ish code to 3.7ish code.
    '''
    
    global tree

    tree = ast.parse(code)
    
    transformer = Transformer()
    
    # Execute 2 times to make sure no walrus 
    # assigned after reference is bypassed
    transformed = transformer.visit(tree)
    transformed = transformer.visit(tree)
    
    unparsed = ast.unparse(transformed)
    formated = autopep8.fix_code(unparsed)
    
    if msg: formated = re.sub(
        pattern = r"^(\s*?(?:\"|'){3}.*?)((?:\"|'){3}.*)",
        repl = '\\1\n' + msg + '\n\\2',
        string = formated,
        flags = re.DOTALL
    )
    
    return formated

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Invalid parameter')
        exit(1)

    path = sys.argv[1]
    
    for file in glob.glob(path, recursive = True):
        print(f'[ translator ] Formating', file)
        
        with open(file, 'r') as handle:
            raw = handle.read()
        
        result = translate(raw, msg = MSG)
        
        with open(file, 'w') as handle:
            handle.write(result)

# EOF
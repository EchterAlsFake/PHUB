'''
    Translates modern Python code to bad quality code,
    without type hints and walruses for compatibility.
'''

import re
import ast
import sys

tree = None

# Plausible parent blocks where a walrus could be defined and used
# I'm not adding if statements because walruses can live longer than them
# BLOCK = ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
BLOCK = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.Module

def get_parent(node):
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child is node:
                return parent

class Explorer(ast.NodeTransformer):
    '''
    Code explorer. Will remove type annotations and walruses, and
    store walrus data to track further walruses references.
    '''
    
    def __init__(self) -> None:
        self.walruses = []
        super().__init__()
    
    def visit_AnnAssign(self, node):
        '''Remove variables type hints.'''
        print(f'[explorer] [AnnAssign] Found node', type(node).__name__)
        
        if isinstance(node.target, ast.Name):
            value = node.value
            target = node.target
        
            # Make sure direct parent is not a dataclass
            parent = get_parent(node)
            if isinstance(parent, ast.ClassDef):
                for decorator in parent.decorator_list:
                    if decorator.id == 'dataclass':
                        print(f'[explorer] [AnnAssign] Node Parent is dataclass, passing')
                        return node
            
            new_node = ast.Assign(targets=[target], value=value)
            ast.copy_location(new_node, node)
            ast.fix_missing_locations(new_node)
            print(f'[explorer] [AnnAssign] Removed annotations')
        
            return new_node
        
        return node

    def visit_FunctionDef(self, node):
        '''Remove function signatures type hints.'''
        
        print(f'[explorer] [FunctionDef] Found node', type(node).__name__)
        
        for arg in node.args.args:
            arg.annotation = None
        
        if node.returns:
            node.returns = None        
        
        print(f'[explorer] [AnnAssign] Removed type hints')
        self.generic_visit(node)
        return node
    
    def visit_NamedExpr(self, node: ast.NamedExpr):
        '''Remove walrus operators.'''
        
        parent = get_parent(node)
        print(f'[explorer] [NamedExpr] Found walrus', node.target.id)
        
        while not isinstance(parent, BLOCK):
            parent = get_parent(parent)
        
        print(f'[explorer] [NamedExpr] Found node closest block', type(parent).__name__)
        
        new_node = node.value
        ast.copy_location(new_node, node)
        ast.fix_missing_locations(new_node)
        
        self.walruses.append([parent, node])
        self.generic_visit(node)
        
        print(f'[explorer] [NamedExpr] Removed walrus')
        return new_node

def exterminate_walrus_references(tree, walrus_name, expression):
    '''
    Remove walrus references
    '''
    
    class DynamicExplorer(ast.NodeTransformer):
        def visit_Name(self, node):
                        
            if isinstance(node.ctx, ast.Load) and node.id == walrus_name:
                print('[fixer] Changing node', node.id, 'to', node)
                return expression
            return node

    transformer = DynamicExplorer()
    new_tree = transformer.visit(tree)
    return new_tree

def translate(source: str) -> str:
    global tree
    
    print(f'[translate] Parsing input')
    tree = ast.parse(source)
    expl = Explorer()
    print(f'[translate] Starting explorer')
    modd = expl.visit(tree)
    for parent, walrus in expl.walruses:
        print(f'[translate] [fixer] Fixing', walrus)
        exterminate_walrus_references(
            parent,
            walrus.target.id,
            walrus.value
        )

    print(f'[translate] Dumping code')
    code = ast.unparse(modd)

    # Add prevention message
    msg = 'WARNING - THIS CODE IS AUTO TRANSLATED; PREFER USING THE 3.11 VERSION'
    code = re.sub(
        pattern = r"^(\s*?(?:\"|'){3}.*?)((?:\"|'){3}.*)",
        repl = '\\1\n' + msg + '\n\\2',
        string = code,
        flags = re.DOTALL
    )
    
    return code

if __name__ == '__main__':
    
    if len(sys.argv) == 2:
        path = output = sys.argv[1]
    
    elif len(sys.argv) == 3:
        path = sys.argv[1]
        output = sys.argv[2]
    
    else:
        print('Usage: script <source> [output]')
        exit(1)
    
    with open(path, 'r') as file:
        source = file.read()
    
    print(f'# Translating\n\tINPUT - {path}\n\tOUTPUT - {output}')
    
    code = translate(source)
    
    with open(output, 'w') as file:
        file.write(code)

# EOF
from typing import Self
from copy import deepcopy


class Param:
    '''
    Represents a concatenable parameter,
    user for filtering.
    '''
    
    def __init__(self,
                 key: str = None,
                 value: str = None,
                 single: bool = True,
                 reverse: bool = False) -> None:
        '''
        Initialise a new Param object.
        
        Args:
            key      (str): The parameter key.
            value    (str): The parameter value.
            single  (bool): Wether the parameter should be single.
            reverse (bool): Wether the parameter is reversable.
        '''
        
        self.value: dict[str, set[str]] = {}
        
        self.single = single
        self.reverse = reverse
        
        if key and value:
            self.value[key] = {value}
    
    def __repr__(self) -> str:
        '''
        Represents the Param.
        '''
        
        sep = ' and '
        
        items = [(k, sep.join(v)) for k, v in self.value.items()]
        items = [f'not {v}' if 'exclude-' in k else v for k, v in items]
        
        return f'Param({sep.join(items)})'
    
    def __or__(self, other: Self) -> Self:
        '''
        Add 2 Params together.
        '''
        
        assert isinstance(other, Param), f'{other} must be a Param object ({type(other)} found)'
        
        param = deepcopy(self)
        
        for key, set_ in other.value.items():
            
            if not key in self.value or other.single:
                param.value[key] = set()
            
            param.value[key] |= set_
        
        return param
    
    def __neg__(self) -> Self:
        '''
        Reverses a Param.
        param.reverse must be True.
        '''
        
        assert self.reverse, f'{self} cannot be reversed.'
        
        param = deepcopy(self)
        items = list(param.value.items())
        param.value.clear()
        
        for key, set_ in items:
            param.value['exclude_' + key] = set_
        
        return param

    def __sub__(self, other: Self) -> Self:
        '''
        Shorthand for __neg__, without
        the pipe operator.
        '''
        
        assert isinstance(other, Param), f'{other} must be a Param object ({type(other)} found)'
        return self |- other

NO_PARAM = Param()

# EOF
from typing import Self, Any
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
    
    @staticmethod
    def _assert_self(item: Any) -> None:
        '''
        Assert that a given item is of the same type as this object.
        
        Args:
            item (Any): A suposed Param object.
        '''
        
        if not isinstance(item, Param):
            raise TypeError(f'Item `{item}` must be a Param object ({type(item)} found)')
    
    def _concat_single(self, other: Self, brute: bool = False) -> Self:
        '''
        Concatenate Params.
        
        Args:
            other: Another Param instance.
            brute: Wether to take care of wether params should be single.
        
        Returns
            Param: A new Param object.
        '''
        
        self._assert_self(other)
        param = deepcopy(self)
        
        for key, set_ in other.value.items():
            
            # Avoid taking default params into account
            if other.single and None in set_: continue
            
            if not key in self.value or (other.single and not brute):
                param.value[key] = set()
            
            param.value[key] |= set_
        
        return param
    
    def _concat(self, *args, brute: bool = False) -> Self:
        '''
        Concatenate Params.
        
        Args:
            args: One or multiple params to concat.
            brute: Wether to take care of wether params should be single.
        
        Returns
            Param: A new Param object.
        '''
    
        # Return self if no args supplied
        if not len(args):
            return self
        
        param = self
        
        for item in args:
            param = Param._concat_single(param, item, brute = brute)
        
        return param
    
    def __or__(self, other: Self) -> Self:
        '''
        Add 2 Params together.
        '''
        
        return self._concat_single(other)
    
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
        
        self._assert_self(other)
        return self |- other

    def __contains__(self, query: Self) -> bool:
        '''
        Check if a Param object is inside this object.
        '''
        
        # Assertions
        self._assert_self(query)
        assert len(query.value) == 1, f'{query} must be an un-modified Param constant to be compared.'
        
        item_key, item_values = list(query.value.items())[0]
        item_value = item_values.pop()
        
        for key, values in self.value.items():
            if key == item_key and item_value in values:
                return True
        
        return False

NO_PARAM = Param()

# EOF
from typing import Any, Self
from dataclasses import dataclass, field

from .. import errors

@dataclass
class _DataParam:
    '''
    Represents the core of a Param object,
    or exactly one filter.
    '''
    
    key: str = field(repr = None)
    id: str | int = field(repr = None)
    name: str = None
    
    def __post_init__(self) -> None:
        
        self.id = str(self.id)
        
        if self.name is None:
            self.name = self.id
    
    def insert(self, _dict: dict) -> None:
        '''
        Insert the object in a Param dictionnary.
        '''
        
        if not self.key in _dict:    
            _dict[self.key] = []
        
        _dict[self.key] += [self]


class Param:
    '''
    Represents a parameter capable of mutating,
    concatenate to others or negate itself.
    '''
    
    def __init__(self, *args) -> None:
        '''
        Initialise a new parameter with one filter.
        '''
        
        self.value: dict[str, list[_DataParam]] = {}
        
        if args:
            _DataParam(*args).insert(self.value)
    
    def __repr__(self) -> str:
        '''
        Represents the parameter.
        '''
        
        values = []
        for key, items in self.value.items():
            
            if key.startswith('exclude-'):
                values += ['not ' + items.pop(0).name]
            
            values += [dp.name for dp in items]
        
        raw = ' and '.join(values)
            
        return f'Param({raw})'
    
    def __add__(self, param: Self) -> Self:
        '''
        Concatenate two Param objects together.
        '''
        
        assert isinstance(param, Param)
        
        for dps in param.value.values():
            [dp.insert(self.value) for dp in dps]

        return self
    
    def __sub__(self, param: Self) -> Self:
        '''
        Add a parameter to exclude to the current
        parameter.
        '''
        
        assert isinstance(param, Param)
        # assert len(param.value.values()) == 1
        
        dp = list(param.value.values())[0][0]
        
        _DataParam('exclude-' + dp.key,
                   dp.id,
                   dp.name).insert(self.value)
        
        return self

    def __neg__(self) -> Self:
        '''
        Used when there is only one parameter
        to exclude.
        '''
        
        assert len(self.value) == 1
        
        return NO_PARAM - self
    
    def gen(self, key: str = 'name') -> dict:
        '''
        Generate filter dictionnary depending
        on the key (name => hubtraffic or id => scraping).
        '''
        
        data = {}
        
        for key_, dps in self.value.items():
            
            data[key_] = '-'.join(getattr(dp, key) for dp in dps)
        
        return data

NO_PARAM = Param()

# EOF
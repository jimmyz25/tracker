class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aaa = 11111
        # self.__dict__ = self
    # @property
    # def table(self):
    #     return self._table
    # @table.setter
    # def table(self,value):
    #     self._table = value

    def __getattr__(self, item):
        if item in self.keys():
            return super().__getitem__(item)
        else:
            return None

    def __setattr__(self, item, value):
        return super().__setitem__(item, value)

    # def __setitem__(self, key, item):
    #     self.__dict__[key] = item
    #
    # def __getitem__(self, key):
    #     return self.__dict__[key]
    #
    def __repr__(self):
        return repr(self.__dict__)
    #
    # def __len__(self):
    #     return len(self.__dict__)
    #
    # def __delitem__(self, key):
    #     del self.__dict__[key]
    # #
    # def clear(self):
    #     return self.__dict__.clear()
    #
    # def copy(self):
    #     return self.__dict__.copy()
    #
    # def has_key(self, k):
    #     return k in self.__dict__
    #
    # def update(self, *args, **kwargs):
    #     return self.__dict__.update(*args, **kwargs)
    # #
    # def keys(self):
    #     return self.__dict__.keys()
    #
    # def values(self):
    #     return self.__dict__.values()
    # #
    # # def items(self):
    # #     return self.__dict__.items()
    # #
    # # def pop(self, *args):
    # #     return self.__dict__.pop(*args)
    # #
    # def __cmp__(self, dict_):
    #     return self.__cmp__(self.__dict__, dict_)
    #
    # def __contains__(self, item):
    #     return item in self.__dict__
    #
    # def __iter__(self):
    #     return iter(self.__dict__)

x = AttrDict({'some': 'value'})
x['blah'] = 'hello world'
x.abcdddd = "asdf"

x.table = 0
x.clear()
print (x.aaa)
print (x.abc)
print(x.table)

print(x)
# o.foo = "bar"
# o['lumberjack'] = 'foo'
# o.update({'a': 'b'}, c=44)
# print ('lumberjack' in o)
print (x.sadf)

# self._cache_sn_table = self.__create_cache_sn_table__()
# self._cache_config_table = self.__create_cache_config_table__()
# self._cache_wip_table = self.__create_cache_wip_table__()
# self._cache_stress_table = self.__create_cache_stress_table__()
# self._cache_rel_log = self.__create_cache_rel_log__()
# self._latest_sn_history = self.__create_latest_sn_history__()
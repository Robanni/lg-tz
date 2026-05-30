from parsing.parsers.rbc_ru import RbcRuParser
from parsing.parsers.ria_ru import RiaRuParser
from parsing.registry import registry

registry.register(RbcRuParser)
registry.register(RiaRuParser)

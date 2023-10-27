from enum import Enum


class SolverType(Enum):
    MAXIMIZAR = 1
    MINIMIZAR = 2


class VariableLimitType(Enum):
    GREATER = 1
    LESS = 2
    GREATEREQ = 3
    LESSEQ = 4
    EQUAL = 5

    def __str__(self) -> str:
        if (self.name == "GREATER"):
            return ">"
        elif (self.name == "LESS"):
            return "<"
        elif (self.name == "GREATEREQ"):
            return ">="
        elif (self.name == "LESSEQ"):
            return "<="
        elif (self.name == "EQUAL"):
            return "="
        else:
            return super().__str__()


class Solver:
    def __init__(self):
        self.type = SolverType.MAXIMIZAR
        self.vars = []
        self.restrictions = []
        self.allowedSymbols = {
            ">": VariableLimitType.GREATER,
            "<": VariableLimitType.LESS,
            ">=": VariableLimitType.GREATEREQ,
            "<=": VariableLimitType.LESSEQ,
            "=": VariableLimitType.EQUAL,
        }

    def setType(self, type=SolverType.MAXIMIZAR):
        self.type = type

    def setVars(self, vars):
        self.vars = vars

    def setRestrictions(self, rest):
        restrictions = []
        for r in rest:
            result = []
            for value in r:
                if (value.isnumeric()):
                    result.append(int(value))
                elif (value in list(self.allowedSymbols.keys())):
                    result.append(self.allowedSymbols[value])
            restrictions.append(result)
        self.restrictions = restrictions

    def showTable(self):
        for var in self.vars:
            print(var, end=" ")
        print()
        for res in self.restrictions:
            for value in res:
                print(value, end=" ")
            print()

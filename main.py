from classes import *


def menu() -> Solver:
    solver = Solver()

    print("----------------------------")
    print("           SOLVER           ")
    print("----------------------------")
    print("Escolha o tipo de resolução ")
    print("1) Maximização              ")
    print("2) Minimização              ")
    type = int(input("> "))
    solver.setType(type=SolverType(type))
    print("----------------------------")
    print(f"         {solver.type.name}         ")
    print("----------------------------")
    print("Qual o número de variáveis?")
    num_var = int(input("> "))

    vars = []
    for i in range(num_var):
        vars.append(int(input(f"Valor de x{i+1}: ")))

    print("\n----------------------------")
    print("Qual o número de restrições?")
    num_restrictions = int(input("> "))

    restrictions = []
    for i in range(num_restrictions):
        print("\n----------------------------")
        value = ""
        for j in range(num_var):
            value += input(f"Restrição de x{j+1}: ") + " "
        restrictionType = input(f"Tipo de restrição (>, <, >=, <=, =): ")
        while (restrictionType not in list(solver.allowedSymbols.keys())):
            print("Tipo inválido! Tente novamente")
            restrictionType = input(f"Tipo de restrição (>, <, >=, <=, =): ")
        value += restrictionType + " "
        value += input(f"Valor da restrição: ")
        restrictions.append(value.split(" "))

    print("----------------------------")
    print("           TABELA           ")
    print("----------------------------")
    print()
    solver.setVars(vars)
    solver.setRestrictions(restrictions)
    solver.showTable()

    input("Aperte ENTER para continuar...")


if (__name__ == "__main__"):
    menu()

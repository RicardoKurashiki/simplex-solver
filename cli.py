import curses
import json
from enums import *
from solver import *

solver_type = SolverType.MAXIMIZAR
aux_vars = 0


def init(stdscr):
    stdscr.clear()
    stdscr.addstr("|----------------------------------------------|\n")
    stdscr.addstr(
        f"|              SIMPLEX - {solver_type.name}             |\n")
    stdscr.addstr("|----------------------------------------------|\n")
    stdscr.addstr("|                   ALUNOS                     |\n")
    stdscr.addstr("| Carlos Eduardo Marques Assunção Torres       |\n")
    stdscr.addstr("| Ricardo Godoi Kurashiki                      |\n")
    stdscr.addstr("|----------------------------------------------|\n")
    stdscr.addstr("\n")


def get_simplex_type(stdscr):
    curses.curs_set(0)
    global solver_type

    types = [SolverType.MAXIMIZAR, SolverType.MINIMIZAR]
    current = 0

    while True:
        stdscr.clear()
        stdscr.addstr("[>] Selecione o tipo:\n")
        for i, value in enumerate(types):
            if i == current:
                stdscr.addstr(f"> {value}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f"  {value}\n")
        key = stdscr.getch()

        if key == 10:
            solver_type = types[current]
            curses.curs_set(1)
            break
        elif key == curses.KEY_UP and current > 0:
            current -= 1
        elif key == curses.KEY_DOWN and current < len(types) - 1:
            current += 1


def get_simplex_size(stdscr):
    def get_var_size(error: bool = False):
        if (error):
            stdscr.addstr("[!] Valor inválido. Tente novamente!\n")
        stdscr.addstr("[#] Informe o número de variáveis: ")
        stdscr.refresh()
        return stdscr.getstr().decode()

    def get_contraints_size(error: bool = False):
        if (error):
            stdscr.addstr("[!] Valor inválido. Tente novamente!\n")
        stdscr.addstr("[#] Informe o número de restrições: ")
        stdscr.refresh()
        return stdscr.getstr().decode()

    curses.echo()

    num_variables = get_var_size()
    while (not num_variables.isnumeric()):
        num_variables = get_var_size(True)

    num_constraints = get_contraints_size()
    while (not num_constraints.isnumeric()):
        num_constraints = get_contraints_size(True)

    curses.noecho()
    return int(num_variables), int(num_constraints)


def get_inequation(stdscr):
    valid_inequations = [">=", "<=", "="]
    current = 0

    while True:
        stdscr.clear()

        stdscr.addstr("[>] Selecione o tipo de inequação:\n")
        for i, value in enumerate(valid_inequations):
            if i == current:
                stdscr.addstr(f"> {value}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f"  {value}\n")
        key = stdscr.getch()

        if key == 10:
            return valid_inequations[current]
        elif key == curses.KEY_UP and current > 0:
            current -= 1
        elif key == curses.KEY_DOWN and current < len(valid_inequations) - 1:
            current += 1


def print_matrix(stdscr, matrix, cursor_x=None, cursor_y=None, title=None):
    stdscr.clear()
    if (title != None):
        stdscr.addstr(f"[>] {title}\n\n")
    for i, row in enumerate(matrix):
        if (cursor_x != None):
            for j, value in enumerate(row):
                if i == cursor_x and j == cursor_y:
                    stdscr.addstr(f"[{value}]", curses.A_REVERSE)
                else:
                    stdscr.addstr(f" {value} ")
            stdscr.addstr("\n")
        else:
            if i == cursor_y:
                stdscr.addstr(f"[{row}]", curses.A_REVERSE)
            else:
                stdscr.addstr(f" {row} ")
    stdscr.addstr("\n")
    stdscr.addstr("\n[SETAS] para selecionar a célula\n")
    stdscr.addstr("[E] para editar o valor da célula\n")
    stdscr.addstr("[ENTER] para continuar\n")


def put_value(stdscr):
    curses.curs_set(1)
    valid = False
    curses.echo()
    while (not valid):
        try:
            stdscr.addstr("\n")
            stdscr.addstr("[#] Valor da célula: ")
            stdscr.refresh()
            value = float(stdscr.getstr().decode())
            valid = True
        except:
            continue
    curses.curs_set(0)
    curses.noecho()
    return value


def get_simplex_data(stdscr, num_variables, num_constraints):
    # Get Variables
    variables = [0.0] * num_variables
    cursor_y = 0
    while True:
        print_matrix(stdscr, variables, cursor_y=cursor_y, title="Variáveis")
        key = stdscr.getch()
        if key == curses.KEY_LEFT and cursor_y > 0:
            cursor_y -= 1
        elif key == curses.KEY_RIGHT and cursor_y < num_variables - 1:
            cursor_y += 1
        elif key == ord("e") or key == ord("E"):
            value = put_value(stdscr)
            variables[cursor_y] = value
        elif key == 10:
            break

    # Get Constraints
    constraints_values = [
        [0.0] * num_variables for _ in range(num_constraints)]
    constraints_inequations = ["<="] * num_constraints
    constraints_b = [0.0] * num_constraints

    constraints = []
    for i in range(len(constraints_values)):
        row = constraints_values[i] + \
            [constraints_inequations[i]] + [constraints_b[i]]
        constraints.append(row)

    cursor_x, cursor_y = 0, 0
    while True:
        print_matrix(stdscr, constraints, cursor_x,
                     cursor_y, title="Restrições")
        key = stdscr.getch()
        if key == curses.KEY_UP and cursor_x > 0:
            cursor_x -= 1
        elif key == curses.KEY_DOWN and cursor_x < num_constraints - 1:
            cursor_x += 1
        if key == curses.KEY_LEFT and cursor_y > 0:
            cursor_y -= 1
        elif key == curses.KEY_RIGHT and cursor_y < (num_variables + 2) - 1:
            cursor_y += 1
        elif key == ord("e") or key == ord("E"):
            if (type(constraints[cursor_x][cursor_y]) == str):
                value = get_inequation(stdscr)
            else:
                value = put_value(stdscr)
            constraints[cursor_x][cursor_y] = value
        elif key == 10:
            break

    return variables, constraints


def remove_inequation(variables: list, constraints: list):
    def maximize(variables: list, constraints: list):
        num_vars = len(variables)

        constraints_values = [c[:num_vars] for c in constraints]
        constraints_ineq = [c[num_vars] for c in constraints]
        constraints_b = [c[-1] for c in constraints]

        for i, value in enumerate(constraints_values):
            if (constraints_ineq[i] == "<="):
                for j, value in enumerate(constraints_values):
                    if i == j:
                        value += [1.0]
                    else:
                        value += [0.0]
            elif (constraints_ineq[i] == ">="):
                constraints_values[i] = [-v for v in value]
                constraints_b[i] = -constraints_b[i]
                for j, value in enumerate(constraints_values):
                    if i == j:
                        value += [1.0]
                    else:
                        value += [0.0]

        new_constraints = []
        for i in range(len(constraints_values)):
            row = constraints_values[i] + [constraints_b[i]]
            new_constraints.append(row)

        row_len = len(new_constraints[0])
        variables += [0.0] * (row_len - num_vars)
        return variables, new_constraints

    def minimize(variables: list, constraints: list):
        global aux_vars
        num_vars = len(variables)

        constraints_values = [c[:num_vars] for c in constraints]
        constraints_ineq = [c[num_vars] for c in constraints]
        constraints_b = [c[-1] for c in constraints]

        for i, value in enumerate(constraints_values):
            if (constraints_ineq[i] == ">="):
                for j, value in enumerate(constraints_values):
                    if i == j:
                        value += [-1.0]
                    else:
                        value += [0.0]
            elif (constraints_ineq[i] == "<="):
                constraints_values[i] = [-v for v in value]
                constraints_b[i] = -constraints_b[i]
                for j, value in enumerate(constraints_values):
                    if i == j:
                        value += [-1.0]
                    else:
                        value += [0.0]
        for i, value in enumerate(constraints_values):
            for j, value in enumerate(constraints_values):
                if i == j:
                    value += [1.0]
                    aux_vars += 1
                else:
                    value += [0.0]

        new_constraints = []
        for i in range(len(constraints_values)):
            row = constraints_values[i] + [constraints_b[i]]
            new_constraints.append(row)

        num_constraints = len(constraints)
        num_new_constraints = len(new_constraints)
        variables = [-v for v in variables]
        variables += [0.0] * num_constraints
        variables += [-1.0] * aux_vars
        variables += [0.0]
        return variables, new_constraints

    if (solver_type == SolverType.MAXIMIZAR):
        variables, constraints = maximize(variables, constraints)
    else:
        variables, constraints = minimize(variables, constraints)

    result = [variables] + constraints
    return variables, constraints, result


def showTable(stdscr, variables: list, constraints: list):
    stdscr.addstr('\n')
    for value in variables:
        stdscr.addstr(f"  {value}  ")
    stdscr.addstr('\n')
    # Mostra restrições
    for row in constraints:
        for value in row:
            stdscr.addstr(f'  {value}  ')
        stdscr.addstr('\n')
    stdscr.addstr('\n')
    stdscr.addstr('[ENTER] Para a próxima etapa')
    stdscr.addstr('\n')
    stdscr.refresh()
    stdscr.getch()


def showResult(stdscr, result: dict):
    # TODO: Colocar a amostra de variáveis artificiais
    def header(matrix: list):
        print_str = f'{"|" : >9} '
        func = matrix[0][0: (len(matrix[0]) - 1)]
        for i in range(len(func)):
            print_str += f"{f'x{i+1} ' : <11}"
        print_str += f"| {'b' : <11}"
        stdscr.addstr(print_str)

    def body(base_vars: list, matrix: list):
        print_str = ""
        column_len = len(matrix[0])
        row_len = len(matrix)
        stdscr.addstr(
            '\n--------------------------------------------------------------\n')
        for i in range(row_len):
            row_values = matrix[i]
            if i < row_len - 2:
                print_str += f"x{base_vars[i] + 1}      {'|' : >1} "
            elif i == row_len - 2:
                print_str += '--------------------------------------------------------------\n'
                print_str += f"Cj      {'|' : >1} "
            elif i == row_len - 1:
                print_str += f"Cj - Zj {'|' : >1} "
            for j in range(column_len):
                if j < column_len - 1:
                    print_str += f"{row_values[j]}" + \
                        " " * (11 - len(row_values[j]))
                else:
                    print_str += f"| {row_values[j]}\n"
        stdscr.addstr(print_str)

    solver_result = result['solver']
    best_result = result['bestResult']
    iterations = result['iterations']
    for i, iteration in enumerate(iterations):
        stdscr.clear()
        matrix = iteration['matrix']
        base_vars = iteration['bases']
        stdscr.addstr(f'[>] {i+1}º iteração\n\n')
        header(matrix)
        body(base_vars, matrix)
        stdscr.addstr('\n[ENTER] Para a próxima etapa\n\n')
        stdscr.refresh()
        stdscr.getch()

    stdscr.clear()
    stdscr.addstr(f'[!] {solver_result}\n\n')
    stdscr.addstr(f'Z = {best_result[0]}\n')
    for i, value in enumerate(best_result[1]):
        stdscr.addstr(
            f"x{best_result[1][i] + 1} = {best_result[2][i]}\n")
    stdscr.addstr('\n[ENTER] Para finalizar')
    stdscr.refresh()
    stdscr.getch()


def main(stdscr):
    # Seleciona se é problema de maximização ou minimização
    get_simplex_type(stdscr)
    curses.curs_set(1)
    # Mostra nomes dos alunos
    init(stdscr)
    # Pega o tamanho do problema a ser resolvido
    num_variables, num_constraints = get_simplex_size(stdscr)
    curses.curs_set(0)
    # Fornece os valores de cada local do problema
    variables, constraints = get_simplex_data(
        stdscr, num_variables, num_constraints)
    stdscr.clear()
    showTable(stdscr, variables, constraints)

    variables, constraints, solver_input = remove_inequation(
        variables, constraints)

    print("SOLVER:")
    print(solver_input)
    print(f"AUX: {aux_vars}")
    print(f"TYPE: {solver_type}")
    print("-"*80)

    result = json.loads(solve(solver_input, isMin=(
        solver_type == SolverType.MINIMIZAR),
        nArtificials=aux_vars))

    showResult(stdscr, result)


if __name__ == "__main__":
    curses.wrapper(main)

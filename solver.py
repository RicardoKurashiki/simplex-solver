import numpy as np

# Print na interface gráfica de cada iteração
def printIteration(baseVars, matrix, bases):
    printString = f""
    
    for i in range(len(baseVars)):
        # print(f"x{baseVars[i] + 1}      | {matrix[i]} | {bases[i]}")
        printString += f"x{baseVars[i] + 1} {'|' : >6} "
        for j in range(len(matrix[i])):
            printString += f"{round(matrix[i][j], 4) : <10} "
        printString += f"| {round(bases[i],4)}\n"

    print(printString[:-1])

# Print na interface gráfica de cada contribuição
def printContributions(changeInfo, baseZj):
    printString = "--------------------------------------------------------------\n"
    printString += "Zj      | "
    for i in range(len(changeInfo[0])):
        printString += f"{round(changeInfo[0][i], 4) : <10} "
    printString += f"| {round(baseZj, 4)}\n"
    printString += "Cj - Zj | "
    for i in range(len(changeInfo[0])):
        printString += f"{round(changeInfo[1][i], 4) : <10} "
    printString += "\n--------------------------------------------------------------"
    print(printString)
    
# Calcula o Zj e o Cj - Zj, retornando uma matriz com os valores de ambos.
def calcContribution(function, matrix, baseVars):
    result = list()
    numberOfElements = len(matrix)
    numberOfVars = len(function)
    
    zj = [0] * (numberOfVars)
    cjmzj = [0] * (numberOfVars)
    
    for i in range(numberOfVars):
        for j in range(numberOfElements):
            zj[i] += function[baseVars[j]] * matrix[j][i]
    
    for i in range(numberOfVars):
        cjmzj[i] = function[i] - zj[i]
        
    result.append(zj)
    result.append(cjmzj)
    
    return result

# Calcula Omega para cada variável de base.
def calcOmega(changeInfo, matrix, bases):
    omegaValues = [0] * len(bases) 
    
    # Selecionando coluna pivô.
    pColumn = changeInfo[-1].index(max(changeInfo[-1]))

    for i in range(len(bases)):
        try:
            omegaValues[i] = bases[i]/matrix[i][pColumn]
        except:
            omegaValues[i] = -1
    
    return omegaValues, pColumn

# Calcula base do Zj
def calcZjBase(func, baseVars, base):
    result = 0
    
    for i in range(len(base)):
        result += func[baseVars[i]] * base[i]
    
    return result

# Realiza iteração alterando tudo
def iterate(func, baseVars, matrix, bases, nIterations, bestSolution):
    # Matriz que armazena os valores de Zj (primeira linha) e Cj - Zj (segunda linha).
    changeInfo = calcContribution(func, matrix, baseVars)
    # Calcula a base do Zj.
    baseZj = calcZjBase(func, baseVars, bases)

    printContributions(changeInfo, baseZj)
    
    # Trata-se de um problema de maximização, então quanto maior, melhor.
    if bestSolution[0] <= baseZj:
        bestSolution[0] = baseZj
        bestSolution[1] = baseVars
        bestSolution[2] = bases
    
    if (max(changeInfo[-1]) <= 0):
        return True

    # Calcula o Omega para cada variável de base e seleciona qual a coluna pivô.
    omegaInfo, pColumn = calcOmega(changeInfo, matrix, bases)
    
    # Verificação de sistema degenerado
    for i in range(len(omegaInfo)):
        if omegaInfo[i] < 0:
            print(">> Sistema degenerado <<")
            return True
            
    # Verifica linha pivô
    pLine = omegaInfo.index(min(omegaInfo))    
    # Armazena elemento pivô
    pElement = matrix[pLine][pColumn]
    
    # Realiza troca das variáveis de base.
    baseVars[pLine] = pColumn
    
    # Realiza as alterações na matriz para seguir troca de variáveis de base.
    for i in range(len(matrix)):
        if i != pLine:
            coef = matrix[i][pColumn]/pElement
                
            for j in range(len(matrix[i])):
                matrix[i][j] = matrix[i][j] - (coef * matrix[pLine][j])
                
            bases[i] = bases[i] - (coef * bases[pLine])
                
    for i in range(len(matrix[pLine])): 
        matrix[pLine][i] = matrix[pLine][i]/pElement
    bases[pLine] = bases[pLine]/pElement
    
    print(f"{nIterations}° Iteracao")
    printIteration(baseVars, matrix, bases)
    
    return False

def solve(matrix):
    # bestSolution[0] = Melhor base de Zj
    # bestSolution[1] = [Melhor conjunto de variáveis de base]
    # bestSolution[2] = [Melhor conjunto de valores das variáveis de base]
    bestSolution = list()
    numberOfIterations = 1
    
    # Extraindo valores da função
    func = test_matrix[0][0 : (len(test_matrix[0]) - 1)]
    # Extraindo variáveis de base
    baseVars = [i for i in range((len(test_matrix[0]) - len(test_matrix)), (len(test_matrix[0]) - 1), 1)]
    # Extraindo matriz
    matrix = [test_matrix[i][0 : (len(test_matrix[0]) - 1)] for i in range(1, len(test_matrix))]
    # Extraindo bases
    bases = [test_matrix[i][-1] for i in range(1, len(test_matrix))]
    
    # Populando inicialmente a estrutura bestSolutions
    bestSolution.append(0)
    bestSolution.append(baseVars)
    bestSolution.append(bases)

    # Iteração inicial
    print(f"{numberOfIterations}° Iteracao")
    printIteration(baseVars, matrix, bases)
        
    numberOfIterations += 1
    while (not iterate(func, baseVars, matrix, bases, numberOfIterations, bestSolution)):
        numberOfIterations += 1
    
    print(f"Melhor resultado = {round(bestSolution[0], 4)}")
    for i in range(len(bestSolution[1])):
        print(f"x{bestSolution[1][i] + 1} = {round(bestSolution[2][i], 4)}")
    
# Exemplo:
# Maximizar L: 6*x1 + 5*x2
#        s.a.    x1 +   x2 <= 5
#              3*x1 + 2*x2 <= 12
#                x1,    x2 >= 0

# [x1, x2, x3, ..., b]
test_matrix = [[3,2,0,0,0,0],
               [2,1,1,0,0,100],
               [1,1,0,1,0,80],
               [1,0,0,0,1,40]]
# test_matrix = [[6,5,0,0,0],
#                [1,1,1,0,5],
#                [3,2,0,1,12]]

solve(test_matrix)
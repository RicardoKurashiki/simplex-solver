from enum import Enum
import json

# TODO: Ver se consegue pensar em outra lógica para lidar com os Ms, senão, usa isso mesmo.
# Funciona, mas não é muito elegante.
class BigNumber(Enum):
    M = 1000000000

def buildMString(value):
    if abs(value / BigNumber.M.value) >= 0.1:
        tempString = f"{round(value / BigNumber.M.value,1)}M"
    else:
        tempString = f"{round(value, 4)}"

    return tempString

def detectArtificialsInBase(artificials, baseVars):
    result = False
    
    for i in range(len(baseVars)):
            for j in range(len(artificials)):
                if baseVars[i] == artificials[j]:
                    result = True
    
    return result

def buildIterationStructure(baseVars, matrix, bases, changeInfo, baseZj):
    resultData = {}
    resultData["bases"] = baseVars[:]

    resultMatrix = list()
    
    for i in range(len(matrix) + len(changeInfo)):
        tempList = list()
        if i < len(matrix):
            for j in range(len(matrix[0]) + 1):
                # Populando a matriz com as variáveis de base
                if j < len(matrix[0]):
                    tempList.append(f"{round(matrix[i][j], 4)}")
                else:
                    tempList.append(f"{round(bases[i], 4)}")
            resultMatrix.append(tempList)
        else:
            tempIndex = i % len(matrix)
            for j in range(len(changeInfo[0]) + 1):
                # Populando a matriz com cálculos de impacto
                if j < len(changeInfo[0]):
                    tempList.append(f"{buildMString(changeInfo[tempIndex][j])}")
                else:
                    tempList.append(f"{buildMString(baseZj)}")
            resultMatrix.append(tempList)
    
    # Removendo calculo de base para o Cj - Zj
    resultMatrix[-1][-1] = 0.0
    resultData["matrix"] = resultMatrix
    print(resultMatrix)
    print("")
    
    return resultData
        
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
        # Verificação se Omega é viável.
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
def iterate(func, baseVars, matrix, bases, bestSolution, artificials, result, isMin):
    # Matriz que armazena os valores de Zj (primeira linha) e Cj - Zj (segunda linha).
    changeInfo = calcContribution(func, matrix, baseVars)
    # Calcula a base do Zj.
    if (detectArtificialsInBase(artificials, baseVars)):
        baseZj = 0
    else:
        baseZj = calcZjBase(func, baseVars, bases)

    # Trata-se de um problema de maximização, então quanto maior, melhor.
    if not isMin and bestSolution[0] <= baseZj:
        bestSolution[0] = baseZj
        bestSolution[1] = baseVars
        bestSolution[2] = bases
        result["bestResult"] = bestSolution
    elif isMin and bestSolution[0] >= baseZj:
        bestSolution[0] = baseZj
        bestSolution[1] = baseVars
        bestSolution[2] = bases
        result["bestResult"] = bestSolution
    
    result["iterations"].append(buildIterationStructure(baseVars, matrix, bases, changeInfo, baseZj))

    if (max(changeInfo[-1]) <= 0):
        result["solver"] = "Sucesso"
        # Verificação de sistema degenerado
        # Sistema degenerado vai possuir um 0 em umas das variáveis de base da solução.
        if 0 in bestSolution[2]:
            result["solver"] = "Sistema Degenerado"
            
        # Verificação de sistema inviável
        # Sistema inviável vai possuir uma variável artificial nas variáveis de base.
        if (detectArtificialsInBase(artificials, baseVars)):
            result["solver"] = "Sistema Inviável"

        return True

    # Calcula o Omega para cada variável de base e seleciona qual a coluna pivô.
    omegaInfo, pColumn = calcOmega(changeInfo, matrix, bases)

    # Verificação de sistema sem fronteira
    # Um sistema sem fronteira é aquele onde todos os omegas são inválidos (Omega < 0 || Omega -> Inf)
    for i in range(len(omegaInfo)):
        viableOmega = False
        if omegaInfo[i] >= 0:
            viableOmega = True
            break

    if not viableOmega:
        result["solver"] = "Sistema sem fronteira"
        return True

    # Verifica linha pivô - Menor valor positivo ou igual a zero.
    pLine = omegaInfo.index(min([i for i in omegaInfo if i >= 0]))
    # Armazena elemento pivô
    pElement = matrix[pLine][pColumn]

    # Realiza troca das variáveis de base.
    baseVars[pLine] = pColumn

    # Realiza as alterações na matriz para seguir troca de variáveis de base.
    for i in range(len(matrix)):
        if i != pLine:
            # Coeficiente de multiplicação da linha pivô -> Ly = Lx - coef*Lpivo
            # Coeficiente -> Elemento da coluna pivô, mas da linha atual / Elemento pivô
            coef = matrix[i][pColumn]/pElement

            for j in range(len(matrix[i])):
                matrix[i][j] = matrix[i][j] - (coef * matrix[pLine][j])

            bases[i] = bases[i] - (coef * bases[pLine])
                
    # Lpivo = Lpivo/Epivo
    for i in range(len(matrix[pLine])): 
        matrix[pLine][i] = matrix[pLine][i]/pElement
    bases[pLine] = bases[pLine]/pElement

    return False


def solve(input_matrix, nArtificials = 0, isMin = False):
    solverInfo = {}
    json_data = json.dumps({})
    # bestSolution[0] = Melhor base de Zj
    # bestSolution[1] = [Melhor conjunto de variáveis de base]
    # bestSolution[2] = [Melhor conjunto de valores das variáveis de base]
    bestSolution = list()
    artificials = list()

    # Extraindo valores da função
    func = input_matrix[0][0: (len(input_matrix[0]) - 1)]
    # Extraindo variáveis de base
    baseVars = [i for i in range(
        (len(input_matrix[0]) - len(input_matrix)), (len(input_matrix[0]) - 1), 1)]
    # Extraindo matriz
    matrix = [input_matrix[i][0: (len(input_matrix[0]) - 1)]
              for i in range(1, len(input_matrix))]
    # Extraindo bases
    bases = [input_matrix[i][-1] for i in range(1, len(input_matrix))]

    # Extraindo variaveis artificiais, se houver
    if nArtificials != 0:
        artificials = [i for i in range(
            (len(input_matrix[0]) - (nArtificials + 1)), (len(input_matrix[0]) - 1), 1)]
        # Alterando coeficientes da função para valores tendendo ao infinito
        for i in range(len(artificials)):
            func[artificials[i]] = func[artificials[i]] * BigNumber.M.value

    # Populando inicialmente a estrutura bestSolutions
    bestSolution.append(0)
    bestSolution.append(baseVars)
    bestSolution.append(bases)

    solverInfo["solver"] = ""
    solverInfo["bestResult"] = bestSolution
    solverInfo["iterations"] = list()
    
    while (not iterate(func, baseVars, matrix, bases, bestSolution, artificials, solverInfo, isMin)):
        pass
    
    # Parte experimental do JSON
    json_data = json.dumps(solverInfo)
    print(json_data)
    return json_data

# Exemplo:
# Maximizar L: 6*x1 + 5*x2
#        s.a.    x1 +   x2 <= 5
#              3*x1 + 2*x2 <= 12
#                x1,    x2 >= 0

# [x1, x2, x3, ..., b]
# input_matrix = [[6,5,0,0,0],
#                [1,1,1,0,5],
#                [3,2,0,1,12]]

# Exemplo com matriz maior
# input_matrix = [[3,2,0,0,0,0],
#                [2,1,1,0,0,100],
#                [1,1,0,1,0,80],
#                [1,0,0,0,1,40]]

# Exemplo de sistema sem fronteira
# input_matrix = [[4,3,0,0,0],
#                [1,-6,1,0,5],
#                [3,0,0,1,11]]

# Exemplo de sistema degenerado
# input_matrix = [[4,3,0,0,0],
#                [2,3,1,0,8],
#                [3,2,0,1,12]]

# Exemplo de sistema inviável
# input_matrix = [[4,3,0,0,-1,0],
#                 [1,4,1,0,0,3],
#                 [3,1,0,-1,1,12]]

# Exemplo de minimização
# input_matrix = [[-3,-4,0,0,-1,-1,0],
#                [2,3,-1,0,1,0,8],
#                [5,2,0,-1,0,1,12]]


# solve(input_matrix, 2, True)

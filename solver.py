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
        omegaValues[i] = bases[i]/matrix[i][pColumn]
    
    return omegaValues, pColumn

# Calcula base do Zj
def calcZjBase(func, baseVars, base):
    result = 0
    
    for i in range(len(base)):
        result += func[baseVars[i]] * base[i]
    
    return result

# Realiza iteração alterando tudo
def iterate(func, baseVars, matrix, bases):
    # Matriz que armazena os valores de Zj (primeira linha) e Cj - Zj (segunda linha).
    changeInfo = calcContribution(func, matrix, baseVars)
    # Calcula a base do Zj.
    baseZj = calcZjBase(func, baseVars, bases)

    print("------------------------------------------------------")
    print(f"Zj      | {changeInfo[0]} | {baseZj}")
    print(f"Cj - Zj | {changeInfo[1]}")
    print("------------------------------------------------------")
    
    if (max(changeInfo[-1]) <= 0):
        print(f"Melhor resultado = {baseZj}")
        for i in range(len(baseVars)):
            print(f"x{baseVars[i] + 1} = {bases[i]}")
        return True

    # Calcula o Omega para cada variável de base e seleciona qual a coluna pivô.
    omegaInfo, pColumn = calcOmega(changeInfo, matrix, bases)
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
    
    for i in range(len(baseVars)):
        print(f"x{baseVars[i] + 1}      | {matrix[i]} | {bases[i]}")
    
    return False

# Exemplo:
# Maximizar L: 3*x1 + 4*x2
#        s.a.    x1 +   x2 <= 450
#              2*x1 +   x2 <= 600
#                x1,    x2 >= 0

# [x1, x2, x3, x4, b]
test_matrix = [[3,4,0,0,0],
               [1,1,1,0,450],
               [2,1,0,1,600]]

# Extraindo valores da função
func = test_matrix[0][0 : (len(test_matrix[0]) - 1)]
# Extraindo variáveis de base
baseVars = [i for i in range((len(test_matrix) - 1), (len(test_matrix[0]) - 1), 1)]
# Extraindo matriz
matrix = [test_matrix[i][0 : (len(test_matrix[0]) - 1)] for i in range(1, len(test_matrix))]
# Extraindo bases
bases = [test_matrix[i][-1] for i in range(1, len(test_matrix))]

for i in range(len(baseVars)):
    print(f"x{baseVars[i] + 1}      | {matrix[i]} | {bases[i]}")

while (not iterate(func, baseVars, matrix, bases)):
    pass
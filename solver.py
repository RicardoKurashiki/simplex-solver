# Calcula o Zj e o Cj - Zj, retornando uma matriz com os valores de ambos.
def calcAsParada(function, matrix, chosenVars):
    result = list()
    numberOfElements = len(matrix)
    numberOfVars = len(function)
    
    zj = [0] * (numberOfVars)
    cjmzj = [0] * (numberOfVars)
    
    for i in range(numberOfVars):
        for j in range(numberOfElements):
            zj[i] += function[chosenVars[j]] * matrix[j][i]
    
    for i in range(numberOfVars):
        cjmzj[i] = function[i] - zj[i]
        
    result.append(zj)
    result.append(cjmzj)
    
    return result

# Calcula Omega para cada linha
def calcOmega(changeInfo, matrix, bases):
    omegaValues = [0] * len(bases) 
    
    # Selecionando maior coluna de Cj - Zj
    selectedCol = changeInfo[-1].index(max(changeInfo[-1]))

    for i in range(len(bases)):
        try:
            omegaValues[i] = bases[i]/matrix[i][selectedCol]
        except:
            omegaValues[i] = 0
    
    return omegaValues, selectedCol

# Calcula base do Zj
def calcZjBase(func, chosenVars, base):
    result = 0
    
    for i in range(len(base)):
        result += func[chosenVars[i]] * base[i]
    
    return result

# Realiza iteração alterando tudo
def iterate(func, chosenVars, matrix, bases):
    changeInfo = calcAsParada(func, matrix, chosenVars)
    
    print("------------------------------------------------------")
    print(f"Zj      | {changeInfo[0]} | {calcZjBase(func, chosenVars, bases)}")
    print(f"Cj - Zj | {changeInfo[1]}")
    print("------------------------------------------------------")
    
    if (max(changeInfo[-1]) <= 0):
        print(f"Melhor resultado = {calcZjBase(func, chosenVars, bases)}")
        for i in range(len(chosenVars)):
            print(f"x{chosenVars[i] + 1} = {bases[i]}")
        return True
    
    omegaInfo, colunaP = calcOmega(changeInfo, matrix, bases)
    linhaP = omegaInfo.index(min(omegaInfo))    
    elementoP = matrix[linhaP][colunaP]
    chosenVars[linhaP] = colunaP
    
    
    for i in range(len(matrix)):
        if i != linhaP:
            try:
                coef = matrix[i][colunaP]/elementoP
            except:
                coef = 0
                
            for j in range(len(matrix[i])):
                matrix[i][j] = matrix[i][j] - (coef * matrix[linhaP][j])
                
            bases[i] = bases[i] - (coef * bases[linhaP])
                
    for i in range(len(matrix[linhaP])): 
        matrix[linhaP][i] = matrix[linhaP][i]/elementoP
    bases[linhaP] = bases[linhaP]/elementoP
    
    for i in range(len(chosenVars)):
        print(f"x{chosenVars[i] + 1}      | {matrix[i]} | {currentBases[i]}")
    
    return False
    
    
func = [2,3,0,0] 

chosenVars = [2, 3]

matrix = [[1, 4, 1, 0],
          [3, 3, 0, 1]]

currentBases = [8, 9]

for i in range(len(chosenVars)):
    print(f"x{chosenVars[i] + 1}      | {matrix[i]} | {currentBases[i]}")

while(not iterate(func, chosenVars, matrix, currentBases)):
    pass
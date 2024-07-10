import re

def formatCPF( cpf ):    
    cpf = re.sub("[^0-9]", "", cpf)
    return "%s.%s.%s-%s" % ( cpf[0:3], cpf[3:6], cpf[6:9], cpf[9:11])

def isCPF( cpf ):
    # defining some variables
    lista_validacao_um = [10, 9, 8, 7, 6, 5, 4 , 3, 2]
    lista_validacao_dois = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]

    # cleaning the cpf
    cpf = re.sub("[^0-9]", "", cpf)

    # verifying the lenght of the cpf
    if len( cpf ) != 11:
        return False

    if not str.isnumeric(cpf):
        return False

    # finding out the digits
    verificadores = cpf[-2:]
    cpf = cpf[:9]

    # calculating the first digit
    soma = 0
    id = 0
    for numero in cpf:
        soma += (int( numero ) * int( lista_validacao_um[id] ))    
        id += 1

    soma = (soma * 10) % 11

    if soma == 10:
        digito_um = 0
    else:
        digito_um = soma

    digito_um = str( digito_um ) # converting to string, for later comparison

    # calculating the second digit
    # suming the two lists
    cpf = cpf + digito_um
    soma = 0
    id = 0

    # suming the two lists
    for numero in cpf:
        soma += int( numero ) * int( lista_validacao_dois[id] )
        id += 1

    # defining the digit
    soma = (soma * 10) % 11
    if soma == 10:
        digito_dois = 0
    else:
        digito_dois = soma

    digito_dois = str( digito_dois )

    # returnig
    return bool( verificadores == (digito_um + digito_dois) )

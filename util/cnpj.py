import re

def formatCNPJ( cnpj ):    
    cnpj = re.sub("[^0-9]", "", cnpj)
    return "%s.%s.%s/%s-%s" % ( cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14])

def isCNPJ( cnpj ):
    # defining some variables
    lista_validacao_um = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4 , 3, 2]
    lista_validacao_dois = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # cleaning the cnpj
    cnpj = re.sub("[^0-9]", "", cnpj)

    # verifying the lenght of the cnpj
    if len( cnpj ) != 14:
        return False

    if not str.isnumeric(cnpj):
        return False

    # finding out the digits
    verificadores = cnpj[-2:]
    cnpj = cnpj[:12]

    # calculating the first digit
    soma = 0
    id = 0
    for numero in cnpj:
        soma += (int( numero ) * int( lista_validacao_um[id] ))    
        id += 1

    soma = soma % 11

    if soma < 2:
        digito_um = 0
    else:
        digito_um = 11 - soma

    digito_um = str( digito_um ) # converting to string, for later comparison

    # calculating the second digit
    # suming the two lists
    cnpj = cnpj + digito_um
    soma = 0
    id = 0

    # suming the two lists
    for numero in cnpj:
        soma += int( numero ) * int( lista_validacao_dois[id] )
        id += 1

    # defining the digit
    soma = soma % 11
    if soma < 2:
        digito_dois = 0
    else:
        digito_dois = 11 - soma

    digito_dois = str( digito_dois )

    # returnig
    return bool( verificadores == (digito_um + digito_dois) )

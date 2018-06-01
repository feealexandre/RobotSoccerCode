# -*- coding: utf-8 -*-
"""

Objetivo:      Funções de cada jogador do time, goleiro, zagueiro e atacante, além de funções de estratégia de jogo, como penalti, e um verificador para atigiu o alvo
Data:          26/Outubro/2017
Autor:         RED DRAGONS UFSCAR - Divisão de Controle e Estratégia
Membros:       Alexandre Dias Negretti
                Carlos Basali
                George Maneta
                Marcos Augusto Faglioni Junior 
                Natália dos Santos Andrade
                Vinicius Ancheschi Strini

"""
from auxiliarControle import *
from controle import *
import numpy as np
from math import *
from controle import *

"""
Função:  goleiro
Objetivo: Guia o robô de qualquer ponto do campo, até a area do gol, uma vez atingida area do gol, o robô rotacionará ao longo com 90 ou -90 graus e então irá
apenas para frente e para trás, posicionando-se no eixo y proporcional ao posicionamento da bola.

Parametros de entrada:
    # r_g - vetor com 6 posições, sendo:
    [0] - Coordenada X do robô; [1] - Coordenada Y do robô; [2] - angulo do robô; [3] - KP (constante de controle);
    [4] - velocidade máxima;    [5] - Função do robo (0-goleiro; 1-zagueiro; 2-atacante); [6] - Código do robô (0 -> @; 1 -> &; 2 -> $)
    # bola - vetor de 2 posições, sendo:
    [0] - Coordenada X da bola; [1] - Coordenada Y da bola
    # ser - Porta serial (em caso de não haver comunicador conectado, passar 0)
    # Gleyson - Variavel booleana responsável por ativar a escrita na porta serial
    # Strini - Variavel booleana responsável por ativar a simulação
    !!!Strini e Gleyson são variveis exclusivas, assim, somente uma pode ser verdadeira por vez!!!
    # duasFaces - Variavel booleana responsável por ativar as duas frentes do robô
    # trocouCampo - Variavel booleana responsável por informar qual o lado do campo que está o jogo corrente
    # debug - Faz, em tempo de execução, exibir dados relevantes no terminal
    # clientID - Criado na main (caso Strini seja falso, fazer clientID = 0)

Retorno:
    # angulo_d - Valor na forma de float indicando o angulo desejado que o robô deverá atingir

Funções utilizadas:
    # atingiuAlvo() - Documentação disponivel em auxiliarControle.py
    # controle2() - Documentação disponivel em controle.py
    # controle() - Documentação disponivel em controle.py

"""
def goleiro(r_g, bola, ser, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID):

    #Criação da variável que armazenará o retorno
    angulo_d = 0

    #Criação do vetor que armazenará o alvo
    alvog = np.zeros([2])

    #Distancia em centimetros que deve ser considerada para o robô estar com a bola (é alta para o goleiro girar um pouco antes da bola chegar nele)
    toleranciaRoboBola = 10


    #Verifica qual gol deve proteger (Note que o X do alvo do goleiro(alvog) não muda, implicando que ele não sai do gol)
    if trocouCampo:
        alvog[0] = 150    
    else:
        alvog[0] = 18

    #O Y do alvo do goleiro será o mesmo da bola, para a bola bater no goleiro. Caso a bola esteja fora do Y do gol o goleiro irá parar no canto do gol
    if(bola[1] > 80):
        alvog[1] = 79
    elif(bola[1] < 46):
        alvog[1] = 47
    else:
        alvog[1] = bola[1]

    #Caso tenha atingido o alvog, parte para ficar com orientãção correta (+-90 graus), caso contrário, vai para o alvog
    #Nota: É preferivel que o robo fique a 90 grau, pois ele não precisará virar para chegar ao alvog toda vez que a bola se mover, tornando-o mais ágil
    if(not atingiuAlvo(r_g, bola, toleranciaRoboBola)):

        if(atingiuAlvoY(r_g, alvog, 3)):

            #Verificação em duas etapas afim de saber se o robô atingiu o angulo 90º ou -90º
            if(not atingiuAngulo(r_g, math.pi/2, 0.17)):

                if(not atingiuAngulo(r_g, -math.pi/2, 0.17)):

                    #Caso ainda não tenha atingido, virar em torno do próprio eixo até obter o ângulo desejado
                    angulo_d,flagInverteuTheta = controle2(r_g, ser, r_g[4]*0.1, r_g[4]*0.1, 0, 1, Gleyson, Strini, debug, clientID)

                else:
                    #Caso tenha atingido o ângulo -90º, para
                    angulo_d,flagInverteuTheta = controle2(r_g, ser, 0, 0, 0, 0, Gleyson, Strini, debug, clientID)
                    

            else:
                #Caso tenha atingido o ângulo 90º, para
                angulo_d,flagInverteuTheta = controle2(r_g, ser, 0, 0, 0, 0, Gleyson, Strini, debug, clientID)

        #Invoca o controle básico, com alvo na região demarcada
        else:
            angulo_d ,flagInverteuTheta = controle(r_g, alvog, ser, Gleyson, Strini, duasFaces, debug, clientID)

    else:

        #Quando a bola chega nele, ele gira para o sentido em que a bola vá para o campo adversário
        if(r_g[1] < 65):

            if(trocouCampo):
                #Girar sentido anti-horário
                angulo_d, flagInverteuTheta = controle2(r_g, ser, r_g[4]*2, r_g[4]*2, 1, 0, Gleyson, Strini, debug, clientID)

            else:
                #Girar sentido horário
                angulo_d, flagInverteuTheta = controle2(r_g, ser, r_g[4]*2, r_g[4]*2, 0, 1, Gleyson, Strini, debug, clientID)

        else:

            if(trocouCampo):
                angulo_d, flagInverteuTheta = controle2(r_g, ser, r_g[4]*2, r_g[4]*2, 0, 1, Gleyson, Strini, debug, clientID)

            else:
                angulo_d, flagInverteuTheta = controle2(r_g, ser, r_g[4]*2, r_g[4]*2, 1, 0, Gleyson, Strini, debug, clientID)


    

    return angulo_d, flagInverteuTheta





"""
Função:  zagueiro
Objetivo: A estrategia escolhida do zagueiro foi a de traçar uma circunferencia em torno de um ponto específico ((10,65) jogando no lado normal ou (160,65)
jogando no lado invertido) de modo que ele fique entre a bola e este ponto, sem entrar na area do goleiro.

Parametros de entrada:
    # r_z - vetor com 6 posições, sendo:
    [0] - Coordenada X do robô; [1] - Coordenada Y do robô; [2] - angulo do robô; [3] - KP (constante de controle);
    [4] - velocidade máxima;    [5] - Função do robo (0-goleiro; 1-zagueiro; 2-atacante); [6] - Código do robô (0 -> @; 1 -> &; 2 -> $)
    # bola - vetor de 2 posições, sendo:
    [0] - Coordenada X da bola; [1] - Coordenada Y da bola
    # ser - Porta serial (em caso de não haver comunicador conectado, passar 0)
    # Gleyson - Variavel booleana responsável por ativar a escrita na porta serial
    # Strini - Variavel booleana responsável por ativar a simulação
    !!!Strini e Gleyson são variveis exclusivas, assim, somente uma pode ser verdadeira por vez!!!
    # duasFaces - Variavel booleana responsável por ativar as duas frentes do robô
    # trocouCampo - Variavel booleana responsável por informar qual o lado do campo que está o jogo corrente
    # debug - Faz, em tempo de execução, exibir dados relevantes no terminal
    # clientID - Criado na main (caso Strini seja falso, fazer clientID = 0)

Retorno:
    # angulo_d - Valor na forma de float indicando o angulo desejado que o robô deverá atingir

Funções utilizadas:
    # atingiuAlvo() - Documentação disponivel em auxiliarControle.py
    # controle2() - Documentação disponivel em controle.py
    # controle() - Documentação disponivel em controle.py
"""

def zagueiro(r_z, bola, ser, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID):

    #Raio da circunferencia que o robo traçara
    r = 51

    #Criação do vetor que armazenará o alvo
    alvoz = np.zeros([2])

    #Distancia em centimetros que deve ser considerada para o robô estar com a bola
    toleranciaRoboBola = 8.5

    #if principal, caso o robo não esteja na bola, ele irá seguir a lógica do raio
    if(not atingiuAlvo(r_z, bola, toleranciaRoboBola)):

        #Caso trocouCampo seja verdadeiro, desenvolve a lógica para o lado contrário do campo e vice-versa
        if(trocouCampo):        
            #Distancia entre o ponto (160, 65) e a bola
            d = sqrt((bola[0] - 160)**2 + (bola[1] - 65)**2)
            
            #Angulo entre o ponto (160, 65) e a bola
            teta = acos(abs(bola[1] - 65) / d)
            
            #Verificação se a bola está acima ou abaixo de Y = 65 (metade do campo)
            if(bola[1] <= 65):
                #Decomposição do vetor entre o ponto (160, 65) com tamanho do raio em coordenadas x e y
                alvoz[0] = 160 - sin(teta)*r
                alvoz[1] = 65 - cos(teta)*r
                
            else:
                #Decomposição do vetor entre o ponto (160, 65) com tamanho do raio em coordenadas x e y
                alvoz[0] = 160 - sin(teta)*r
                alvoz[1] = 65 + cos(teta)*r
            
        else:
            #Distancia entre o ponto (10,65) e a bola
            d = sqrt((bola[0] - 10)**2 + (bola[1] - 65)**2)
            
            #Angulo entre o ponto (10,65) e a bola
            teta = acos(abs(bola[1] - 65) / d)
            
            if(bola[1] <= 65):
                #Decomposição do vetor entre o ponto (10,65) com tamanho do raio em coordenadas x e y
                alvoz[0] = sin(teta)*r
                alvoz[1] = 65 - cos(teta)*r
                
            else:
                #Decomposição do vetor entre o ponto (10,65) com tamanho do raio em coordenadas x e y
                alvoz[0] = sin(teta)*r
                alvoz[1] = 65 + cos(teta)*r
            
        angulo_d, flagInverteuTheta = controle(r_z, alvoz, ser, Gleyson, Strini, duasFaces, debug, clientID)

    #Caso o robo esteja na bola ele irá girar para o sentido mais conveniente
    else:


        if(not trocouCampo):

            if(r_z[1] > bola[1]):
                #Girar sentido horário
                angulo_d, flagInverteuTheta = controle2(r_z, ser, r_z[4]*(50/22), r_z[4]*(50/22), 0, 1, Gleyson, Strini, debug, clientID)
            else:
                #Girar sentido anti-horário
                angulo_d, flagInverteuTheta = controle2(r_z, ser, r_z[4]*(50/22), r_z[4]*(50/22), 1, 0, Gleyson, Strini, debug, clientID)

        else:

            if(r_z[1] > bola[1]):
                angulo_d, flagInverteuTheta = controle2(r_z, ser, r_z[4]*(50/22), r_z[4]*(50/22), 1, 0, Gleyson, Strini, debug, clientID)

            else:
                angulo_d, flagInverteuTheta = controle2(r_z, ser, r_z[4]*(50/22), r_z[4]*(50/22), 0, 1, Gleyson, Strini, debug, clientID)


    return angulo_d, flagInverteuTheta










"""
Função: Atacante
Objetivo: O atacante é programado para ir para um ponto atrás da bola, quando ele estiver neste ponto irá em direção a bola.
Quando o atacante estiver com a bola ele irá para o gol.

Parametros de entrada:
    # r_a - vetor com 6 posições, sendo:
    [0] - Coordenada X do robô; [1] - Coordenada Y do robô; [2] - angulo do robô; [3] - KP (constante de controle);
    [4] - velocidade máxima;    [5] - Função do robo (0-goleiro; 1-zagueiro; 2-atacante); [6] - Código do robô (0 -> @; 1 -> &; 2 -> $)
    # bola - vetor de 2 posições, sendo:
    [0] - Coordenada X da bola; [1] - Coordenada Y da bola
    # ser - Porta serial (em caso de não haver comunicador conectado, passar 0)
    # Gleyson - Variavel booleana responsável por ativar a escrita na porta serial
    # Strini - Variavel booleana responsável por ativar a simulação
    !!!Strini e Gleyson são variveis exclusivas, assim, somente uma pode ser verdadeira por vez!!!
    # duasFaces - Variavel booleana responsável por ativar as duas frentes do robô
    # trocouCampo - Variavel booleana responsável por informar qual o lado do campo que está o jogo corrente
    # debug - Faz, em tempo de execução, exibir dados relevantes no terminal
    # clientID - Criado na main (caso Strini seja falso, fazer clientID = 0)

Retorno:
    # angulo_d - Valor na forma de float indicando o angulo desejado que o robô deverá atingir

Funções utilizadas:
    # atingiuAlvo() - Documentação disponivel em auxiliarControle.py
    # controle2() - Documentação disponivel em controle.py
    # controle() - Documentação disponivel em controle.py
    # estaNaBordaSuperior() - Documentação disponivel em auxiliarControle.py
    # estaNaBordaInferior() - Documentação disponivel em auxiliarControle.py
    # estaNaBordaSuperiorGolDir() - Documentação disponivel em auxiliarControle.py
    # estaNaBordaSuperiorGolEsq() - Documentação disponivel em auxiliarControle.py
    # estaNaBordaInferiorGolDir() - Documentação disponivel em auxiliarControle.py
    # estaNaBordaInferiorGolEsq() - Documentação disponivel em auxiliarControle.py
"""

def atacante(r_a, bola, ser, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID):

    #Vetor que armazenará o alvo
    alvoa = np.zeros([2])

    #Vetor do ponto atrás da bola
    atrasBola = np.zeros([2])

    #Vetor que armazena as coordenadas do gol
    gol = np.zeros([2])
    
    #Angulo desejado
    angulo_d = 0

    #Variavel que indica se o angulo mudou (o angulo vai de 180 a -180 graus)
    flagInverteuTheta = False

    #Distancia em centimentros para considerar se o robo está na borda ou não
    tamanhoLateral = 15

    #Distancia em X atrás da bola onde há um ponto para onde o robo irá antes do chute
    distAtrasBola = 12  

    #Multiplicador da velocidade maxima usado no giro da lateral
    KgiroLateral = (50/30)

    #Tolerancia para o atacante não ficar no mesmo Y do zagueiro (impede que a bola fique rebatendo entre os dois)
    toleranciaMeio = 7

    #Distancia em centimetros que deve se considerar que o robo esteja no alvo
    ToleranciaDistRoboAlvo = 7

    #O gol para o atacante é o ponto do meio do gol real
    gol[1] = 65

    if (trocouCampo):
        gol[0] = 0

        #Caso troque o campo o "atras da bola" muda, pois muda a referencia (o gol)
        distAtrasBola = -distAtrasBola

    else:
        gol[0] = 170

    #posição atrás da bola
    atrasBola[0] = bola[0] - distAtrasBola

    #Setando o alvo como o ponto atras da bola
    if(r_a[1] > bola[1]):
        atrasBola[1] = bola[1] - distAtrasBola*0.4

    else:
        atrasBola[1] = bola[1] + distAtrasBola*0.4


    #distancia em Y do robo ate a bola
    dy = abs(r_a[1] - bola[1])

    #Utiliza-se somente o sinal da variavel dx para determinar se o robo está "atras da bola" (considerando a referencia certa)
    dx = (r_a[0] - bola[0])*distAtrasBola

    #calculo do angulo desejado
    delta_x = alvoa[0] - r_a[0]
    delta_y = alvoa[1] - r_a[1]
    angDesejado = np.arctan2(delta_y,delta_x)    

    #calculo do erro do angulo
    angErro = abs(angDesejado - r_a[2])

    #Verificação se a bola esta na defesa e o atacante está (o atacante não entra na defesa para não causar penaltis)
    if( (bola[0] < 65 and r_a[0] > bola[0]) and (not trocouCampo) ):

        if(bola[1] < 65):

            alvoa[0] = 77

            #A toleranciaMeio inpede que o atacante e o zagueiro fiquem na mesma linha de ação impendindo que o atacante rebata a bola diretamente para a defesa
            alvoa[1] = bola[1] + toleranciaMeio

        else:

            alvoa[0] = 77
            alvoa[1] = bola[1] - toleranciaMeio


        angulo_d, flagInverteuTheta = controle(r_a, alvoa, ser, Gleyson, Strini, duasFaces, debug, clientID)

    #Verificação se a bola esta na defesa com o campo trocado
    elif( (bola[0] > 105 and r_a[0] < bola[0]) and trocouCampo ):

        if(bola[1] < 65):

            alvoa[0] = 93
            alvoa[1] = bola[1] + toleranciaMeio

        else:

            alvoa[0] = 93
            alvoa[1] = bola[1] - toleranciaMeio


        angulo_d, flagInverteuTheta = controle(r_a, alvoa, ser, Gleyson, Strini, duasFaces, debug, clientID)
    
    #Os proximos 4 IF's são as verificações das 4 bordas do campo
    elif (estaNaBordaSuperior(r_a, tamanhoLateral)):

        #Verificação se o robo está na bola
        if(atingiuAlvo(r_a, bola, ToleranciaDistRoboAlvo)):

            #Bola esta na lateral superior
            if (trocouCampo):
                #girar sentido anti-horário
                angulo_d, flagInverteuTheta = controle2(r_a, ser, r_a[4]*KgiroLateral, r_a[4]*KgiroLateral, 1, 0, Gleyson, Strini, debug, clientID)
            else:
                #girar sentido horário
                angulo_d, flagInverteuTheta = controle2(r_a, ser, r_a[4]*KgiroLateral, r_a[4]*KgiroLateral, 0, 1, Gleyson, Strini, debug, clientID)

        #Se o robo não estive na bola ele irá para a bola
        else:

            alvoa = bola

            angulo_d, flagInverteuTheta = controle(r_a, alvoa, ser, Gleyson, Strini, duasFaces, debug, clientID)
        
    #Segue a mesma lógica que há dentro do if anterior      
    elif(estaNaBordaInferior(r_a, tamanhoLateral)):

        if(atingiuAlvo(r_a, bola, ToleranciaDistRoboAlvo)):

            #bola está na lateral inferior
            if (trocouCampo):
                #girar sentido horário
                angulo_d, flagInverteuTheta = controle2(r_a, ser, r_a[4]*KgiroLateral, r_a[4]*KgiroLateral, 0, 1, Gleyson, Strini, debug, clientID)
            else:
                #girar sentido anti-horário
                angulo_d, flagInverteuTheta = controle2(r_a, ser, r_a[4]*KgiroLateral, r_a[4]*KgiroLateral, 1, 0, Gleyson, Strini, debug, clientID)

        else:

            alvoa = bola

            angulo_d, flagInverteuTheta = controle(r_a, alvoa, ser, Gleyson, Strini, duasFaces, debug, clientID)

    elif((estaNaBordaSuperiorGolDir(r_a, tamanhoLateral)) or (estaNaBordaSuperiorGolEsq(r_a, tamanhoLateral))): 

        if(atingiuAlvo(r_a, bola, ToleranciaDistRoboAlvo)):


            if (trocouCampo):
                #girar sentido anti-horário
                angulo_d, flagInverteuTheta = controle2(r_a, ser, r_a[4]*KgiroLateral, r_a[4]*KgiroLateral, 1, 0, Gleyson, Strini, debug, clientID)
            else:
                #girar sentido horário
                angulo_d, flagInverteuTheta = controle2(r_a, ser, r_a[4]*KgiroLateral, r_a[4]*KgiroLateral, 0, 1, Gleyson, Strini, debug, clientID)

        else:

            alvoa = bola

            angulo_d, flagInverteuTheta = controle(r_a, alvoa, ser, Gleyson, Strini, duasFaces, debug, clientID)


    elif((estaNaBordaInferiorGolDir(r_a, tamanhoLateral)) or (estaNaBordaInferiorGolEsq(r_a, tamanhoLateral))):

        if(atingiuAlvo(r_a, bola, ToleranciaDistRoboAlvo)):


            if (not trocouCampo):
                #girar sentido anti-horário
                angulo_d, flagInverteuTheta = controle2(r_a, ser, r_a[4]*KgiroLateral, r_a[4]*KgiroLateral, 1, 0, Gleyson, Strini, debug, clientID)
            else:
                #girar sentido horário
                angulo_d, flagInverteuTheta = controle2(r_a, ser, r_a[4]*KgiroLateral, r_a[4]*KgiroLateral, 0, 1, Gleyson, Strini, debug, clientID)

        else:

            alvoa = bola

            angulo_d, flagInverteuTheta = controle(r_a, alvoa, ser, Gleyson, Strini, duasFaces, debug, clientID)

    #Após a verificação das bordas, concluisse que o robo não esta em nenhuma borda
    else:
        
        #Se o robo não esta em nenhuma borda, verifica se ele esta na bola
        if(atingiuAlvo(r_a, bola, ToleranciaDistRoboAlvo)):

            #Se o robo esta na bola ele irá para o gol
            alvoa = gol

            angulo_d, flagInverteuTheta = controle(r_a, alvoa, ser, Gleyson, Strini, duasFaces, debug, clientID)

        #Se o robo não esta na bola
        else:

            #Verificação se o robo está no ponto atrás da bola
            if(dy < ToleranciaDistRoboAlvo and dx < 0):

                #Se o robo esta neste ponto, vá para a bola
                alvoa = bola

                angulo_d, flagInverteuTheta = controle(r_a, alvoa, ser, Gleyson, Strini, duasFaces, debug, clientID)

            #Se o robo não esta no ponto, irá para o ponto atrás da bola
            else:

                alvoa = atrasBola

                angulo_d, flagInverteuTheta = controle(r_a, alvoa, ser, Gleyson, Strini, duasFaces, debug, clientID)



    return angulo_d, flagInverteuTheta



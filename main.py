# -*- coding: utf-8 -*-
"""

Objetivo: Código principal executado pelo time de futebol de robôs da equipe Red Dragons UFSCar. Neste está contido as chamadas de funções da area
de Controle  e Estratégia (indicados por '=') e da area de Visão Computacional (indicados por '-') do time (códigos genericos indicados por '.').
Data: 06/novembro/2017
Autores:
Controle e estratégia
Felipe ALexandre
Alexandre Negretti
Carlos Basali
George Maneta
Marcos Faglioni
Natalia Andrade
Vinicius Strini

Visão Computacional:
Gabriel Trevisan
Gabriel Tararam
Gleyson Oliveira
Vinicius Andrade

@author: geo
"""
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Importação de bibliotecas relacionadas a visão
import cv2
import numpy as np
import imutils
import time
import math

# Importação de arquivos elaborados pelos membros do time contendo códigos da visão
import calibracao
import tracking
import desempenho

#==================================================================================================================================================================
# Importações de bibliotecas relacionadas ao controle e estrategia
import serial
import sys
import vrep 				# Importação para uso do simulador V-rep

# Importação de arquivos elaborados pelos membros do time contendo códigos do controle e estrategia
from estrategias import *
from auxiliarControle import serialEscreverPorta
from controlevrep import *
from gui_controle import *
from controle import controle2


#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Definições de variaveis da visão
pi = math.pi 				# Criando atribuição do valor de pi como definido na biblioteca math, ao invés de usar o pi definido na biblioteca numpy
aquisicao = 0        		# Entrada de Vídeo: 0=Camera interna, 1=Camera USB, -1=Template
a = 5                		# Numero de amostras 
d_cent = 5.0         		# Distância máxima entre o centroide dos marcadores (cm)
area_minima = 10     		# Detecção de áreas abaixo desse valor são ignoradas (área em pixel^2)
adv = False           		# Ativa ou desativa detecção de adversários
ch = 3               		# Numero de canais de vídeo a serem considerados (H,S,V)
param = True         		# Habilita a configuração dos parametros do campo.
ang_corr = pi/4      		# Habilitar no caso de Marcadores diagonais (Videos atuais)
#ang_corr = 0        		# Habilitar no caso de Marcadores alinhados com a frente do robô (Video de Uberlandia)

M = True             		# Variável do Marcos, quando ativada pula a calibração, carregando padrão anterior

gravar_video = True    		# Permite gravar vídeo do jogo enquanto roda a visão (só funciona com câmera).

robot = np.zeros([3,5])     # Alocação de espaço para matriz robot: [ ] 
tempo = np.empty([0,1])     # Alocação de espaço para matriz tempo, usada para análise de desempenho
counter = 0                 # Inicializa Contador
vec_len = 55
if adv == False:
    n_robos = a-2 
else:
    n_robos = a-3

#==================================================================================================================================================================
# Definições de variaveis do controle e estrategia
Gleyson = False				# Gleyson ativa ou desativa o Xbee
Strini = True				# Strini ativa(True) o simulador ou ativa(False) a modo de ambiente real
trocouCampo = False			# Responsavel por tratar o caso de inversão de campo
debug = True				# Ativa relatorios do software (os relatorios são apresentados no terminal)
duasFaces = True			# Ativa(True) a parte do código para que o robo utilize as duas faces para jogar
vetBuffer = np.zeros([3]) 	# Vetor responsavel por amazenar as 3 ultimas velocidade enviadas
vetPosicao = np.zeros([3]) 	# Vetor responsavel por amazenar as 3 ultimas posicoes
contBuffer = 0				# Contador de buffer (responsavel pela limpeza do buffer)
bola = np.zeros([1,2])		# Vetor responsavel por amazenar as coordenadas da bola
angulo_d = np.zeros(3)		# Vetor responsavel por amazenar os angulos de cada robô
flagInverteuTheta = np.zeros(3)		# Vetor responsavel por determinar se o angulo do robo será invertido, para o caso de duas frentes ativas

# Caso a variavel Strini seja falsa, ou seja, não esta executando o simulador, é criado uma variavel clientID, necessaria para o simulador, mas não necessaria a execução real, porem algumas funções a recebem como parametro, logo existe a necessidade de existir tal variavel
if (not Strini):
    clientID = 0

# Caso a variavel Gleyson esteja ativa, indicando que possui um Xbee conectado, é necessario criar parametros para a comunicação serial, tais parametros são porta de comunicação (porta) e velocidade de comunicação (velocidade), e ainda criar o objeto serial (chamado de ser). Caso a variavel seja falsa, indicando que não existe um Xbee conectado, o objeto ser será apenas uma variavel, apenas para passagem de parametros
if(Gleyson):
    porta = "/dev/ttyUSB0"            # Porta serial do Xbee
    velocidade = 57600
    
    ser = serial.Serial(porta, velocidade)
else:
    ser = 0


#..................................................................................................................................................................
# Inicio do loop de processamento da visao e controle estrategico, caso a variavel Strini seja falsa, ou seja, o programa sera executado em ambiente real, fazendo a checagem das posições atraves da camera, e encaminhando o comando para o robô atraves do xbee (o comando só será efetivamente encaminhado se a variavel Gleyson for verdadeira).
if(not Strini):
    print ("Iniciando o modo de ambiente real")
    #--------------------------------------------------------------------------------------------------------------------------------------------------------------
    # MODO -1: SEM CÂMERA (processa arquivo de vídeo)
    if aquisicao == -1:
        gravacao = "exemp.avi"
    else:
        gravacao = aquisicao

    snap,M = calibracao.snapshot(gravacao,M)

    # CASO SEJA NECESSÁRIO CALIBRAR
    if M == False:
        calibracao.visualizacao(snap)                           # Permite visualizar imagem da câmera
        parametros, origem = calibracao.parametro(snap,param)    # Rotina de calibração dos parametros espaciais do campo (cantos e cruzetas)  
        print('Parâmetros:')
        print (parametros)
        
        calibracao.visualizacao(snap)                           # Permite visualizar imagem da câmera
        #snap = calibracao.crop(snap,parametros,False)          # Antiga função crop que corta a imagem, muito rápida mas que não corrige campo torto nem redimensiona
        snap = calibracao.planificar(snap,parametros)           # Função 'planificar' bem mais lenta, mas corrige campo torto e redimensiona a imagem

        calib, upper, lower, mask1 = calibracao.color(snap,a,ch,parametros,gravacao,area_minima)  # Rotina de calibração das cores

    # CASO NAO SEJA NECESSÁRIO CALIBRAR, PULA ESSA ETAPA E CARREGA CALIBRAÇÃO ANTERIOR
    else:
        parametros = np.load('parametros.npy')
        lower = np.load('lower.npy')
        upper = np.load ('upper.npy')
        calib = np.load('calib.npy')

    #..............................................................................................................................................................
    # ORGANIZA VARIÁVEIS DOS PARÂMETROS ESPACIAIS OBTIDOS
    campo_maxY = parametros[2, 1]
    campo_maxX = parametros[1, 0]
    origem = (parametros[0, 0],parametros[0, 1])
    cruzetas_x = [parametros[4,0],parametros[5,0]];
    cruzetas_y = [parametros[4,1],parametros[6,1]];

    distCruzX = abs(cruzetas_x[0] - cruzetas_x[1])
    distCruzY = abs(cruzetas_y[0] - cruzetas_y[1])

    # CALCULA A ESCALA CM/PIXEL LEVANDO EM CONTA A DISTÂNCIA DAS CRUZETAS
    if (distCruzX > distCruzY):

    #    constX = 69/distCruzX      # Campo velho medida estava errada
    #    constY = 32.0/distCruzY    # Campo velho medida estava errada 
        
        constX = 70.0/distCruzX     # Campo novo
        constY = 37.5/distCruzY     # Campo novo
    else:
    #    constX = 32.0/distCruzY    # Campo velho medida estava errada 
    #    constY = 69/distCruzX      # Campo velho medida estava errada 
        
        constX = 37.5/distCruzY     # Campo novo
        constY = 70.0/distCruzX     # Campo novo

    d_pixel = (d_cent/constX)**2 +  (d_cent/constY)**2      # Distância quadrática entre os marcadores em pixel

    #--------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Tracking
    cap = cv2.VideoCapture(gravacao)

    # Inicializa o gravador de video
    if gravar_video == True:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        ext = str(time.time())
        #out = cv2.VideoWriter('out' + ext + '.avi',fourcc, 30.0, (640,480))
        out = cv2.VideoWriter('out' + ext + '.avi',fourcc, 20.0, (640,480))
    # Compatibiliza as versões 2.x e 3.x do openCV para repetição do video
    if imutils.is_cv2:
        opencv_version = 2
        if aquisicao == -1:
            frame_max = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if imutils.is_cv3:
        opencv_version = 3
        if aquisicao == -1:
            frame_max = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    frame_counter = 0  
    cv2.namedWindow("Tracking")
    cv2.moveWindow("Tracking",200,200)  
    media = 0
    bola_sumiu = 0
    percent = 0
    s = 3

    #==============================================================================================================================================================
    # Trackbars do controle
    # Cria a janela e a move para o canto da tela
    cv2.namedWindow('Controle')
    cv2.moveWindow('Controle', 100, 100)

    # Carrega a imagem que será exibida
    nat = cv2.imread('nat.jpg',1)

    # Cria os objetos da trackbar
    jogar =cv2.createTrackbar('Jogar', 'Controle', 1,2, jg)
    PT = cv2.createTrackbar('PararTudo', 'Controle', 0,1, jg)
    Campo = cv2.createTrackbar('Campo', 'Controle', 0,1, jg)
    BolaNossa = cv2.createTrackbar('BolaNossa', 'Controle', 0,1, jg)


    #..............................................................................................................................................................
    # Loop principal do jogo
    while (cap.isOpened()):   
        #----------------------------------------------------------------------------------------------------------------------------------------------------------
        # Captura frames e recorta a imagem
        ret,frame = cap.read()      # Variável ret verifica se a câmera funciona, frame guarda a imagem
                

        startv = time.time()        # Começa a contar o tempo para o desempenho da visão
        if ret == True:
            
            # Grava o video enquanto roda o algortimo da visão
            if aquisicao !=-1 and gravar_video == True:
                out.write(frame)
                

    		# frame = calibracao.crop(frame,parametros,False)    # Antiga função crop, que recorta o campo.
            frame = calibracao.planificar(frame,parametros)     # Recorta, desentorta e redimensiona o campo
            
            
            # Obtenção dos centroides
            bola, view, centroid_cores = tracking.tracking(lower,upper,frame, calib,area_minima,ch)        
    		# bola_sumiu, percent = desempenho.detect_ball(frame_counter,frame_max,bola,bola_sumiu,percent,s)
            
            
            # Permite executar arquivos de video quando não há a camera
            frame_counter += 1
            
            # Processamento com o openCV 2.X
            if opencv_version == 2 and aquisicao==-1:   #Conta frames para recomeçar o vídeo quando acabar
                if frame_counter == frame_max-s:
                    frame_counter = 0
                    tempo = np.empty([0,1])
                    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)  
            
            # Pocessamento com o openCV 3.X
            elif opencv_version == 3 and aquisicao ==-1:
                if frame_counter == frame_max-s:
                    # Exibe no terminal o desempenho da visão a cada frame
                    
                    desv_pad, media = desempenho.loop_time(tempo)
                    
                    print ('\n=========== DESEMPENHO VISÃO ===========')
                    print ('Tempo Médio:',media, 'ms')
                    print ('Desvio Padrão:',desv_pad, 'ms')    
                    print ('Frames Sem Bola:',bola_sumiu)
                    print ('Detecção de Bola:',round(percent,2),'%')
                    print ('=========================================')
                    
                    frame_counter = 0
                    bola_sumiu = 0
                    percent = 0
                    tempo = np.empty([0,1])
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0) 
                    
            
            # Detecção de adversários
            if adv == True:
                aux = centroid_cores[a-1,:,:]
                AD = aux[~np.all(aux == 0, axis=1)]
                centroid_cores = centroid_cores[0:a-1,:,:]
            
            # Rastreio dos robôs
            robot_ant = robot                                                   # Salva posição anterior dos robôs para fazer um filtro e diminuir tremida dos centroides 
            robot = tracking.pao_da_visao(centroid_cores,d_pixel,ang_corr)      # Adquirie posição atual dos robôs
        
            #robot = (robot*0.8 + robot_ant*0.2)                                # Filtro da média ponderada dos centroides atuais com os centroides do frame anterior    
            
            
           # Plotagem dos centroides e vetor sobre a imagem
            cv2.circle(view, (int(bola[0]),int(bola[1])), 5, (255, 0, 255), -1)  # Plota centroide da bola

            #------------------------------------------------------------------------------------------------------------------------------------------------------
            # Tempo para verificação do desempenho do controle
            startc = time.time()

            # Obtenção da posição da trackbar "PararTudo", responsavel por parar os robôs
            PT1 = cv2.getTrackbarPos('PararTudo', 'Controle')
            if (PT1 == 1):             		# Apertando f destroi a janela
                cv2.destroyAllWindows()    	# Necessário essa instrução, senao a janela trava
                break

            # Obtenção da posição da trackbar "BolaNossa", responsavel por determinar se nossos robôs podem entrar no centro de campo antes do primeiro contato com a bola
            bolaNossa1 = cv2.getTrackbarPos('BolaNossa', 'Controle')
            # Obtenção da posição da trackbar "Campo", responsavel por determinar qual a validação da variavel trocouCampo
            Campo1 = cv2.getTrackbarPos('Campo', 'Controle')
            if (Campo1 == 0):
                trocouCampo = False
            else:
                trocouCampo = True

            # Obtenção da posição da trackbar "Jogar", responsavel por determinar se está em modo de jogo, modo parados ou para encaminhar os robos para a posição de inicio de jogo
            jogar1 = cv2.getTrackbarPos('Jogar', 'Controle')
            # Caso jogar seja 0, os robôs deverão ir para a posição inicial do jogo, e se manter nesta posição, até a liberação para iniciar o jogo
            if (jogar1 == 0):
            	# Invoca a função que guia os robôs até o ponto desejado
                posicaoInicial(robot, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, bolaNossa1, debug, clientID)

                angulo_d = [0,0,0] 
                flagInverteuTheta = False

               	# Insere um texto na tela indicando processamento da posição inicial
                cv2.putText(view,"POSICAO INICIAL", (25,25), cv2.FONT_HERSHEY_COMPLEX, 1, [0,255,0])

            # Caso jogar seja 1, todos os robôs devem estar parados
            elif (jogar1 == 1):
            	# Invoca a função que para os robôs
                parada(robot, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID)

                angulo_d = [0,0,0] 
                flagInverteuTheta = False

                # Insere um texto na tela indicando jogo parado
                cv2.putText(view,"PAUSE", (25,25), cv2.FONT_HERSHEY_COMPLEX, 1, [0,255,0])

            # Caso jogar seja 2, os robôs devem executar a estratégia determinada pelo controle e estratégia
            elif (jogar1 == 2):
            	# Invoca a função que executa a lógia do jogo
                angulo_d, flagInverteuTheta = estrategia(robot, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID)

                #cv2.putText(view,"JOGO NORMAL", (25,25), cv2.FONT_HERSHEY_COMPLEX, 1, [0,255,0])
            #print (PT1)
            #print (jogar1)
            #print (Campo1)
            #print (BolaNossa)

           # Plotagem do angulo desejado dependente do modulo do controle
            for r in xrange(3):
                x_ang_d = int(robot[r,3] + vec_len*math.cos(angulo_d[r]))
                y_ang_d = int(robot[r,4] + vec_len*math.sin(angulo_d[r]))
       
                cv2.line(view, (int(robot[r,0]),int(robot[r,1])), (x_ang_d,y_ang_d), (0,255,255), 3)  ## Orientação de cada robô (vermelho)
           
            
            # Plota, um a um, os centroides e angulos dos robôs  (VISAO)
            for r in xrange(3):
         
                x_view = int(robot[r,3] + vec_len*math.cos(robot[r,2]))         # Cálculo do ponto extremidade da reta visual em x do ângulo do robô usando coordenadas polares
                y_view = int(robot[r,4] + vec_len*math.sin(robot[r,2]))         # Cálculo do ponto extremidade da reta visual em y do ângulo do robô usando coordenadas polares
                '''
                if flagInverteuTheta[r] == False:
                    mark = frame[int(robot[r,4]),int(robot[r,3])]
                else:
                    mark = frame[int(robot[r,3]),int(robot[r,2])]
                '''
                mark = frame[int(robot[r,4]),int(robot[r,3])]

                cv2.circle(view, (int(robot[r,0]),int(robot[r,1])), 5, (0, 255, 255), -1)          ## Centroide de cada robô aliado (Amarelo)
                cv2.line(view, (int(robot[r,0]),int(robot[r,1])), (x_view,y_view), (int(mark[0]),int(mark[1]),int(mark[2])), 3)   ## Orientação de cada robô (Vermelho)
            
            if adv == True:
                for r in xrange(len(AD)):
                    cv2.circle(view, (int(AD[r,0]),int(AD[r,1])), 5, (255, 0, 0), -1)  ## Centroide de cada robô adversário (Azul)
                
            # Encerra a contagem do tempo do controle
            endc = time.time()

            #......................................................................................................................................................
            flag = 0    # Flag de finalização do software, inicia abaixada.
            
            # CASO APERTE 'S' PAUSA O JOGO, SE APERTAR 'F' EM SEGUIDA, FINALIZA PROGRAMA
            if cv2.waitKey(1) & 0xFF == ord('s'):
                
                desv_pad, media = desempenho.loop_time(tempo)

                print ('\n=========== DESEMPENHO VISÃO ===========')
                print ('Tempo Médio:',media, 'ms')
                print ('Desvio Padrão:',desv_pad, 'ms')    
                print ('=========================================')
                
                
                if Gleyson:
                    for i in xrange(10):
                        serialEscreverPorta(ser, '&0,0000,0,0000#', Gleyson)
                        serialEscreverPorta(ser, '@0,0000,0,0000#', Gleyson)
                        serialEscreverPorta(ser, '!0,0000,0,0000#', Gleyson)
                    
                # ESPERA APERTAR 'R' PARA RETORNAR OU 'F' PARA FECHAR
                while flag == 0:            
                    if cv2.waitKey(20) & 0xFF == ord('r'):
                        break
                        
                    if cv2.waitKey(20) & 0xFF == ord('f'):
                        flag = 1    # Ativa flag de finalização do software
                        break
            
            cv2.imshow('Controle', nat)
            cv2.imshow("Tracking",view)
            
            endv = time.time()      #Encerra contagem de tempo do loop da visão
            
            ## ANÁLISE DE DESEMPENHO =============================================
            total_time = 1000*(endv-startv)
            tempo = np.append(tempo,[[total_time]], axis = 0)
            


            if flag == 1:
                print ('ALGORITMO ENCERRADO')
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()
    if gravar_video == True:
        out.release()

#..................................................................................................................................................................
# Caso a variavel Strini, que indica se será executada a simulação ou se será executado o jogo em ambiente real, for verdadeira, será executado o seguinte trecho de código, que não utiliza a visão. Todos os comandos são enviados e recebidos atraves do simulador V-Rep.
else:
	# Exibe no terminal o status do programa
    print ("Iniciando o modo de ambiente simulado")
    # Corrige o angulo com relação ao simulador
    ang_corr = pi/4 

    # Cria a janela e a move para o canto
    cv2.namedWindow('Controle')
    cv2.moveWindow('Controle', 100, 100)

    # Carrega a imagem a ser exibida
    nat = cv2.imread('nat.jpg',1)

    # Cria o objeto da trackbar
    jogar =cv2.createTrackbar('Jogar', 'Controle', 1,2, jg)
    PT = cv2.createTrackbar('PararTudo', 'Controle', 0,1, jg)
    Campo = cv2.createTrackbar('Campo', 'Controle', 0,1, jg)
    BolaNossa = cv2.createTrackbar('BolaNossa', 'Controle', 0,1, jg)

    # Distancia entre as cruzetas (como a metrica do V-Rep para a métrica deste software é de 1 para 1)
    constX = 1     # Campo novo
    constY = 1     # Campo novo



    vrep.simxFinish(-1) 											# Caso necessário, fecha todas as conexões anteriores
    clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5) 	# Abre a conexão com o V-Rep

    # Caso a conexão esteja fechada
    if clientID!=-1:
        print ('Conectado com a API remota V-REP')
    # Caso a conexão não tenha sucesso 
    else:   
        print('Falha na conexão, verifique se a simulação no V-REP está ativada')
        sys.exit('Não foi possivel conectar')

    # Caso a comunicação já esteja estabelecida, o código é encaminhado para o loop principal
    while (1):
    	# Criação das variáveis globais para a interface
        global jogar1,PT1,Campo1,bolaNossa1
        
        # Obtenção dos dados de posição atraves do V-Rep
        robot, bola = visaovrep(clientID, ang_corr)

        # Obtenção da posição da trackbar "PararTudo", responsavel por parar os robôs
        PT1 = cv2.getTrackbarPos('PararTudo', 'Controle')
        # Obtenção da posição da trackbar "BolaNossa", responsavel por determinar se nossos robôs podem entrar no centro de campo antes do primeiro contato com a bola
        bolaNossa1 = cv2.getTrackbarPos('BolaNossa', 'Controle')
        # Obtenção da posição da trackbar "Campo", responsavel por determinar qual a validação da variavel trocouCampo
        Campo1 = cv2.getTrackbarPos('Campo', 'Controle')
        if (Campo1 == 0):
            trocouCampo = False
        else:
            trocouCampo = True
        # Obtenção da posição da trackbar "Jogar", responsavel por determinar se está em modo de jogo, modo parados ou para encaminhar os robos para a posição de inicio de jogo
        jogar1 = cv2.getTrackbarPos('Jogar', 'Controle')

		# Caso jogar seja 0, os robôs deverão ir para a posição inicial do jogo, e se manter nesta posição, até a liberação para iniciar o jogo        
        if (jogar1 == 0):
        	# Invoca a função que guia os robôs até o ponto desejado
            posicaoInicial(robot, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, bolaNossa1, debug, clientID)

            cv2.imshow('Controle', nat)
            # Condiçao de parada
            if (PT1 == 1):             		#Apertando f destroi a janela
                cv2.destroyAllWindows()    	# Necessário essa instrução, senao a janela trava
                break  
        # Caso jogar seja 1, todos os robôs devem estar parados
        elif (jogar1 == 1):  
            while (jogar1 == 1):
            	#Refaz as leituras das variaveis, para não gastar com processamento desnecessário
                jogar1 = cv2.getTrackbarPos('Jogar', 'Controle')
                PT1 = cv2.getTrackbarPos('PararTudo', 'Controle')

                # Invoca a função que para os robôs
                parada(robot, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID)


                cv2.imshow('Controle', nat)
                ## CONDIÇÃO DE PARADA.
                k = cv2.waitKey(20) & 0xFF
                if (k == ord('f') or PT1 == 1):             # Apertando f destroi a janela
                    cv2.destroyAllWindows()    # Necessário essa instrução, senao a janela trava
                    break      
        # Caso jogar seja 2, os robôs devem executar a estratégia determinada pelo controle e estratégia
        elif (jogar1 == 2):    
            cv2.imshow('Controle', nat)
            # Condição de parada
            k = cv2.waitKey(20) & 0xFF
            if (k == ord('f') or PT1 == 1):             # Apertando f destroi a janela
                cv2.destroyAllWindows()    				# Necessário essa instrução, senao a janela trava
                break  

            startv = time.time()        # Começa a contar o tempo para o desempenho da visão    

            angulo_d, flagInverteuTheta = estrategia(robot, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID)
            
            endv = time.time()      # Encerra contagem de tempo do loop da visão
            
            # Analise de desempenho
            total_time = 1000*(endv-startv)
            #print(total_time)

# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 21:00:10 2016

@author: GEO
"""

import cv2
import numpy as np

# APLICAÇÃO DE FILTROS MORFOLÓGICOS
def morph(img,filtro,ke, kSelect, iterations):
    
    #Seletor de Kernel
    if kSelect == 0 or 1 or 2 or 3:
        ke = 2*ke    # Coeficiente do kernel precisa ser par 
        kernel = np.ones((ke,ke),np.float32)/(ke*ke)    #Criação do kernel
        
    # Sem filtro
    if filtro == 0:
        res = img
    
    # Filtros Singulares
    if filtro == 1:
        res = cv2.erode(img, kernel,iterations = 1)
    if filtro == 2:
        res = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    if filtro == 3:
        res = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)        
        
    #Filtros Compostos
    if filtro == 4:
        res = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        res = cv2.erode(res, kernel,iterations = 1)
    if filtro == 5:
        res = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        res = cv2.erode(res, kernel,iterations = 1)
    if filtro == 6:
        res = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel) 
        res = cv2.erode(res, kernel, iterations = 1)
    if filtro == 7:
        res = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel) 
        res = cv2.morphologyEx(res, cv2.MORPH_GRADIENT, kernel)
                
        
    return res

    
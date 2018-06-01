#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 22:47:56 2017

@author: geo
"""

import cv2
import numpy

## FUNÇÃO CALLBACK DE RETORNO NULO (Simplifica o uso de Trackbar)
def jg(x):
    global jogar1,PT1,Campo1,bolaNossa1
    jogar1 = cv2.getTrackbarPos('Jogar', 'Controle')
    PT1 = cv2.getTrackbarPos('PararTudo', 'Controle')
    Campo1 = cv2.getTrackbarPos('Campo', 'Controle')
    bolaNossa1 = cv2.getTrackbarPos('BolaNossa', 'Controle')
#    FormacaodoTerror1 = cv2.getTrackbarPos('PosInicial', 'Controle'
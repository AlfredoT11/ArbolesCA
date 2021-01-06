import OptimizacionesC
import numpy as np
from math import sqrt
import os
import re
import json

"""import networkx as nx
import matplotlib.pyplot as plt

from graphviz import Digraph, Graph

from igraph import *"""

from PIL import Image, ImageDraw

def list_to_string(s):  
    
    str1 = ""  
    
    for ele in s:  
        str1 += ele   
    
    return str1  

def validar_regla_ingresada(regla_ingresada):
    print(type(regla_ingresada))
    if re.search("^B[0]?[1]?[2]?[3]?[4]?[5]?[6]?[7]?[8]?/S[0]?[1]?[2]?[3]?[4]?[5]?[6]?[7]?[8]?$", regla_ingresada):
        print("Regla válida.")
        print(regla_ingresada.split("/"))
        B_S = regla_ingresada.split("/")

        B = []
        if len(B_S[0]) > 1:
            for valor in B_S[0][1:]:
                B.append(int(valor))

        S = []
        if len(B_S[1]) > 1:
            for valor in B_S[1][1:]:
                S.append(int(valor))

        return B, S

    else:
        print("Regla inválida.")
        return False, False

def asignar_nombre_canonico(estado, is_ciclo = False, siguiente_elemento_ciclo = -1):
    """Cálculo de Knuth-tuples.
    Función utilizada para calcular el nombre canónico de un árbol y de esta manera determinar si existe algún árbol
    isomorfo dentro del conjunto. (AHU algorithm)
    """
    
    global relacion_incidencias

    if estado not in relacion_incidencias.keys():
        return 2

    #Eliminar estados ciclados. 
    if relacion_incidencias[estado][0] == estado:
        hijos = relacion_incidencias[estado][1:].copy()
    elif is_ciclo:
        #Remover el siguiente elemento.
        hijos = relacion_incidencias[estado].copy()
        #print("Estado ciclado {} - > {}".format(estado, siguiente_elemento_ciclo))
        #print("Hijos antes: ", hijos)
        hijos.remove(siguiente_elemento_ciclo)
        #print("Hijos: ", hijos)
    else:
        hijos = relacion_incidencias[estado].copy()

    valores_canonicos_hijos = []
    for h in hijos:
        valores_canonicos_hijos.append(asignar_nombre_canonico(h))

    valores_canonicos_hijos.sort()
    valores_canonicos_binario = ['1']

    for valor in valores_canonicos_hijos:
        valores_canonicos_binario.append(bin(valor)[2:])

    valores_canonicos_binario.append('0')

    valor_canonico = list_to_string(valores_canonicos_binario)
    return int(valor_canonico, 2)


def dibujar_hijos(estado, angulo_propio, rango_disponible, centro_estado, radio = 1000, is_ciclo = False, siguiente_elemento_ciclo = -1):
    
    global relacion_incidencias
    global draw
    global centro_x 
    global centro_y
    global tamanio_cuadrado

    if relacion_incidencias[estado][0] == estado:
        hijos = relacion_incidencias[estado][1:]
    elif is_ciclo:
        #Remover el siguiente elemento.
        hijos = relacion_incidencias[estado]
        #print("Estado ciclado {} - > {}".format(estado, siguiente_elemento_ciclo))
        #print("Hijos antes: ", hijos)
        hijos.remove(siguiente_elemento_ciclo)
        #print("Hijos: ", hijos)
    else:
        hijos = relacion_incidencias[estado]

    num_hijos = len(hijos)

    rango_por_hijo = rango_disponible/num_hijos

    angulo_hijo_1 = angulo_propio-(rango_disponible/2) + rango_por_hijo/2
    #print("1: ", angulo_hijo_1)
    #Dibujar hijo.
    offset_x, offset_y = radio*np.cos(angulo_hijo_1), radio*np.sin(angulo_hijo_1)
    draw.rectangle((centro_x+offset_x-tamanio_cuadrado, centro_y+offset_y-tamanio_cuadrado, centro_x+offset_x+tamanio_cuadrado, centro_y+offset_y+tamanio_cuadrado), fill = 0)
    draw.line((centro_estado[0], centro_estado[1], centro_x+offset_x, centro_y+offset_y), fill=128, width=1)

    if hijos[0] in relacion_incidencias:
        dibujar_hijos(hijos[0], angulo_hijo_1, rango_por_hijo, (centro_x+offset_x, centro_y+offset_y), radio+1000)


    if num_hijos > 1:
        for i, estado_hijo in enumerate(hijos[1:]):
            #print(i+1, ": ", angulo_hijo_1+(i+1)*rango_por_hijo)
            #Dibujar hijo.
            offset_x, offset_y = radio*np.cos(angulo_hijo_1+(i+1)*rango_por_hijo), radio*np.sin(angulo_hijo_1+(i+1)*rango_por_hijo)
            draw.rectangle((centro_x+offset_x-tamanio_cuadrado, centro_y+offset_y-tamanio_cuadrado, centro_x+offset_x+tamanio_cuadrado, centro_y+offset_y+tamanio_cuadrado), fill = 0)
            draw.line((centro_estado[0], centro_estado[1], centro_x+offset_x, centro_y+offset_y), fill=128, width=1)

            if estado_hijo in relacion_incidencias:
                dibujar_hijos(estado_hijo, angulo_hijo_1+(i+1)*rango_por_hijo, rango_por_hijo, (centro_x+offset_x, centro_y+offset_y), radio+1000)


filas = int(input("Ingresa las filas: "))
columnas = int(input("Ingresa las columnas: "))

#B = [0, 1, 2, 3, 4, 5, 6]
#S = [3, 7]

#B = [3]
#S = [2, 3]

B = False
S = False

regla = "B3/S23"

while not B:
    B, S = validar_regla_ingresada(regla)

resultados = OptimizacionesC.generarRelacionesArbol(filas, columnas, B, S)
#print(type(resultados))

#resultados[0] = siguiente estado.
#resultados[1] = nivel del estado.
#resultados[2] = incidencias para ese estado.

estados_ciclo_encontrados = []
ciclos = []
still_life = []

print("Numero estados-ciclo", resultados[1].count(0))

for i in range(len(resultados[0])):
    if resultados[1][i] == 0:
        if not (i in estados_ciclo_encontrados):
            if not (resultados[2][i] == 1 and resultados[0][i] == i):                
                #print("Atractor: {} -> {} con {} incidencias.".format(i, resultados[0][i], resultados[2][i]))
                
                ciclos.append([])
                inicio_ciclo = i
                estado_actual = resultados[0][i]
                estados_ciclo_encontrados.append(inicio_ciclo)
                ciclos[-1].append(inicio_ciclo)

                while estado_actual != inicio_ciclo:
                    ciclos[-1].append(estado_actual)
                    estados_ciclo_encontrados.append(estado_actual)
                    estado_actual = resultados[0][estado_actual]
                    


            else:
                #print("Aislado: {} -> {} con {} incidencias.".format(i, resultados[0][i], resultados[2][i]))
                still_life.append(i)

print("Ciclos")
for i, ciclo in enumerate(ciclos):
    print("Ciclo ", i)
    print(ciclo)


"""
for i in range(len(resultados[0])):
    if resultados[1][i] == 0:
        if not (resultados[2][i] == 1 and resultados[0][i] == i):                
            print("Atractor: {} -> {} con {} incidencias.".format(i, resultados[0][i], resultados[2][i]))

        else:
            print("Aislado: {} -> {} con {} incidencias.".format(i, resultados[0][i], resultados[2][i]))
"""

relacion_incidencias = {}
for estado, siguiente_estado in enumerate(resultados[0]):
    if not siguiente_estado in relacion_incidencias:
        relacion_incidencias[siguiente_estado] = []
        relacion_incidencias[siguiente_estado].append(estado)
    else:
        relacion_incidencias[siguiente_estado].append(estado)

#print(relacion_incidencias)
#print(resultados[0])
#print(resultados[1])
#print(resultados[2])

combinaciones = 2**(filas*columnas)
#print(combinaciones)

valores_canonicos_ciclos = []


for num_ciclo, ciclo in enumerate(ciclos):

    valores_canonicos_ciclos.append({})

    #image = Image.new('RGB', (n, m), (0, 0, 0))
    #draw.line((0, 0) + image.size, fill=128)
    #draw.line((0, image.size[1], image.size[0], 0), fill=128)

    #Dibujado    
    """image = Image.new('RGB', (n, m), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle(((image.size[0]/2)-5, (image.size[1]/2)-5, (image.size[0]/2)+5, (image.size[1]/2)+5), fill = 0)"""

    #Dibujo.
    #centro_x, centro_y = image.size[0]/2, image.size[1]/2
    
    centro_x, centro_y = 2500, 2500
    tamanio_cuadrado = 2

    if len(ciclo) > 1:
    
        #print("Ciclo :o")
        estados_ciclo = len(ciclo)
        tamanio_arco = 2*np.pi/estados_ciclo
        radio_ciclo = 500
        diagonal = radio_ciclo*sqrt(2)

        #Dibujado
        #draw.ellipse((centro_x - radio_ciclo, centro_y - radio_ciclo, centro_x + radio_ciclo, centro_y + radio_ciclo), outline=128)

        for i in range(estados_ciclo):
        
            offset_x, offset_y = radio_ciclo*np.cos(i*tamanio_arco), radio_ciclo*np.sin(i*tamanio_arco)
            offset_x_sig, offset_y_sig = radio_ciclo*np.cos((i+1)*tamanio_arco), radio_ciclo*np.sin((i+1)*tamanio_arco)

            #Dibujado
            #draw.rectangle((centro_x+offset_x-tamanio_cuadrado, centro_y+offset_y-tamanio_cuadrado, centro_x+offset_x+tamanio_cuadrado, centro_y+offset_y+tamanio_cuadrado), fill = 0)
        
            if ciclo[i] in relacion_incidencias:

                ###########
                #Fragmento para la generacion de valores canónicos.
                if i == 0:
                    sig_ele_ciclo = ciclo[-1]
                else:
                    sig_ele_ciclo = ciclo[i-1]
                valor_canonico = asignar_nombre_canonico(ciclo[i], True, sig_ele_ciclo)
                if valor_canonico not in valores_canonicos_ciclos[-1]:
                    valores_canonicos_ciclos[-1][valor_canonico] = 1
                else:
                    valores_canonicos_ciclos[-1][valor_canonico] += 1

                ###########


                if len(relacion_incidencias[ciclo[i]]) > 1:
                    if i == 0:
                        sig_ele_ciclo = ciclo[-1]
                    else:
                        sig_ele_ciclo = ciclo[i-1]

                    #Dibujado
                    #dibujar_hijos(ciclo[i], i*tamanio_arco, tamanio_arco, (centro_x+offset_x, centro_y+offset_y), is_ciclo=True, siguiente_elemento_ciclo=sig_ele_ciclo)

    else:
        #Dibujado
        #dibujar_hijos(0, 0, 360, (centro_x, centro_y))
        pass

    #Dibujado
    #image.save( "{}\{}_{}.png".format(nombre_directorio, regla.replace("/", "_"), num_ciclo),  "PNG")

#Lista valores canonicos...
#for i, diction in enumerate(valores_canonicos_ciclos):
    #print("Ciclo ", i, " : ", diction)

arboles_finales = {}
for i, diction in enumerate(valores_canonicos_ciclos):
    if json.dumps(diction) not in arboles_finales.keys():
        arboles_finales[json.dumps(diction)] = []
        arboles_finales[json.dumps(diction)].append(i)
    else:
        arboles_finales[json.dumps(diction)].append(i)

#for arbol in arboles_finales:
    #print(arbol, " : ", arboles_finales[arbol])
#print(arboles_finales)

###########################################################
#Dibujado de arboles finales.
#Creación del directorio para almacenar los árboles resultantes.

nombre_directorio = "Resultados\{}_{}x{}".format(regla.replace("/", "_"), filas, columnas)

if not os.path.exists(nombre_directorio):
    print("No encontrado, creando.")
    os.makedirs(nombre_directorio)

n = 5000
m = 5000
print("Procesamiento de la imagen")

for num_arbol, arbol in enumerate(arboles_finales):

    ciclo = ciclos[arboles_finales[arbol][0]]

    image = Image.new('RGB', (n, m), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle(((image.size[0]/2)-5, (image.size[1]/2)-5, (image.size[0]/2)+5, (image.size[1]/2)+5), fill = 0)

    centro_x, centro_y = image.size[0]/2, image.size[1]/2
    tamanio_cuadrado = 2

    if len(ciclo) > 1:
    
        #print("Ciclo :o")
        estados_ciclo = len(ciclo)
        tamanio_arco = 2*np.pi/estados_ciclo
        radio_ciclo = 500
        diagonal = radio_ciclo*sqrt(2)

        draw.ellipse((centro_x - radio_ciclo, centro_y - radio_ciclo, centro_x + radio_ciclo, centro_y + radio_ciclo), outline=128)

        for i in range(estados_ciclo):
        
            offset_x, offset_y = radio_ciclo*np.cos(i*tamanio_arco), radio_ciclo*np.sin(i*tamanio_arco)
            offset_x_sig, offset_y_sig = radio_ciclo*np.cos((i+1)*tamanio_arco), radio_ciclo*np.sin((i+1)*tamanio_arco)

            draw.rectangle((centro_x+offset_x-tamanio_cuadrado, centro_y+offset_y-tamanio_cuadrado, centro_x+offset_x+tamanio_cuadrado, centro_y+offset_y+tamanio_cuadrado), fill = 0)
        
            if ciclo[i] in relacion_incidencias:


                if len(relacion_incidencias[ciclo[i]]) > 1:
                    if i == 0:
                        sig_ele_ciclo = ciclo[-1]
                    else:
                        sig_ele_ciclo = ciclo[i-1]

                    dibujar_hijos(ciclo[i], i*tamanio_arco, tamanio_arco, (centro_x+offset_x, centro_y+offset_y), is_ciclo=True, siguiente_elemento_ciclo=sig_ele_ciclo)

    else:
        dibujar_hijos(0, 0, 360, (centro_x, centro_y))

    image.save( "{}\{}_{}.png".format(nombre_directorio, regla.replace("/", "_"), num_arbol),  "PNG")


#Pruebas con Wolfram
"""with open("prueba.wls", 'w') as archivo_WLS:
    archivo_WLS.write("DirectedGraph[{")
    for combinacion, estado in enumerate(arregloRelaciones[:-2]):
        archivo_WLS.write("{} -> {}, ".format(combinacion, estado))

    archivo_WLS.write("{} -> {}".format(combinaciones-1, arregloRelaciones[-1]))
    archivo_WLS.write('}, GraphLayout -> "RadialEmbedding"]')
"""
#Para ejecutar el archivo:
# wolframscript -code -print -format PNG -file prueba.wls > pruebaWLS.png

#Pruebas con iGraph
"""g = Graph(directed=True)
g.add_vertices(combinaciones)
g.add_edges([(combinacion, estado) for combinacion, estado in enumerate(arregloRelaciones)])

visual_style = {}



# Set bbox and margin
visual_style["bbox"] = (5000,5000)
visual_style["margin"] = 27
# Set vertex colours
visual_style["vertex_color"] = 'white'
# Set vertex size
visual_style["vertex_size"] = 10
# Set vertex lable size
visual_style["vertex_label_size"] = 22

#g.write_svg("salidaSVG", labels=None, vertex_size = 2, font_size = 10)
#g.layout_davidson_harel(weight_edge_lengths = 10)
plot(g, "{}.pdf".format(nombreArchivo), **visual_style)"""

#Pruebas con graphiz
"""G = Graph()
for combinacion in range(combinaciones):
    G.node(str(combinacion))

for combinacion in range(combinaciones):
    G.edge(str(combinacion), str(arregloRelaciones[combinacion]))

G.view()"""
#G.render("Prueba.gv.pdf", view = True)

#Pruebas con Networkx
"""G = nx.Graph()
G.add_nodes_from(list(range(combinaciones)))

for i in range(combinaciones):
    G.add_edge(i, arregloRelaciones[i])

nx.draw(G, with_labels=False, node_size = 10, width=0.1)
plt.show()"""
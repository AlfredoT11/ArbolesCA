import OptimizacionesC
import numpy as np

"""import networkx as nx
import matplotlib.pyplot as plt

from graphviz import Digraph, Graph

from igraph import *"""

from PIL import Image, ImageDraw

def dibujar_hijos(estado, angulo_propio, rango_disponible, centro_estado, radio = 1000):
    
    global relacion_incidencias
    global draw
    global centro_x 
    global centro_y
    global tamanio_cuadrado

    if relacion_incidencias[estado][0] == estado:
        hijos = relacion_incidencias[estado][1:]
    else:
        hijos = relacion_incidencias[estado]

    num_hijos = len(hijos)

    rango_por_hijo = rango_disponible/num_hijos

    angulo_hijo_1 = angulo_propio-(rango_disponible/2) + rango_por_hijo/2
    print("1: ", angulo_hijo_1)
    #Dibujar hijo.
    offset_x, offset_y = radio*np.cos(angulo_hijo_1), radio*np.sin(angulo_hijo_1)
    draw.rectangle((centro_x+offset_x-tamanio_cuadrado, centro_y+offset_y-tamanio_cuadrado, centro_x+offset_x+tamanio_cuadrado, centro_y+offset_y+tamanio_cuadrado), fill = 0)
    draw.line((centro_estado[0], centro_estado[1], centro_x+offset_x, centro_y+offset_y), fill=128, width=1)

    if hijos[0] in relacion_incidencias:
        dibujar_hijos(hijos[0], angulo_hijo_1, rango_por_hijo, (centro_x+offset_x, centro_y+offset_y), radio+1000)


    if num_hijos > 1:
        for i, estado_hijo in enumerate(hijos[1:]):
            print(i+1, ": ", angulo_hijo_1+(i+1)*rango_por_hijo)
            #Dibujar hijo.
            offset_x, offset_y = radio*np.cos(angulo_hijo_1+(i+1)*rango_por_hijo), radio*np.sin(angulo_hijo_1+(i+1)*rango_por_hijo)
            draw.rectangle((centro_x+offset_x-tamanio_cuadrado, centro_y+offset_y-tamanio_cuadrado, centro_x+offset_x+tamanio_cuadrado, centro_y+offset_y+tamanio_cuadrado), fill = 0)
            draw.line((centro_estado[0], centro_estado[1], centro_x+offset_x, centro_y+offset_y), fill=128, width=1)

            if estado_hijo in relacion_incidencias:
                dibujar_hijos(estado_hijo, angulo_hijo_1+(i+1)*rango_por_hijo, rango_por_hijo, (centro_x+offset_x, centro_y+offset_y), radio+1000)


#for i in range(10):
#    print("Hola")

filas = int(input("Ingresa las filas: "))
columnas = int(input("Ingresa las columnas: "))
nombreArchivo = input("Nombre del archivo: ")

#B = [0, 1, 2, 3, 4, 5, 6]
#S = [3, 7]

B = [3]
S = [2, 3]

resultados = OptimizacionesC.generarRelacionesArbol(filas, columnas, B, S)
print(type(resultados))

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
                print("Aislado: {} -> {} con {} incidencias.".format(i, resultados[0][i], resultados[2][i]))
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

print(relacion_incidencias)
#print(resultados[0])
#print(resultados[1])
#print(resultados[2])

combinaciones = 2**(filas*columnas)
print(combinaciones)


n = 5000
m = 5000
print("Procesamiento de la imagen")
image = Image.new('RGB', (n, m), (255, 255, 255))
draw = ImageDraw.Draw(image)
#draw.line((0, 0) + image.size, fill=128)
#draw.line((0, image.size[1], image.size[0], 0), fill=128)
draw.rectangle(((image.size[0]/2)-5, (image.size[1]/2)-5, (image.size[0]/2)+5, (image.size[1]/2)+5), fill = 0)

centro_x, centro_y = image.size[0]/2, image.size[1]/2
tamanio_cuadrado = 2

dibujar_hijos(0, 0, 360, (centro_x, centro_y))

"""total_rectangulos = 7
radio = 1000


for i in range(total_rectangulos):
    offset_x, offset_y = radio*np.cos(i*(2*np.pi/total_rectangulos)), radio*np.sin(i*(2*np.pi/total_rectangulos))
    print(centro_x+offset_x, " , ", centro_y+offset_y)
    draw.rectangle((centro_x+offset_x-tamanio_cuadrado, centro_y+offset_y-tamanio_cuadrado, centro_x+offset_x+tamanio_cuadrado, centro_y+offset_y+tamanio_cuadrado), fill = 0)
    draw.line((centro_x, centro_y, centro_x+offset_x, centro_y+offset_y), fill=128, width=1)
"""

image.save("imagenPrueba.png", "PNG")

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
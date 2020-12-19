import OptimizacionesC
import numpy as np

import networkx as nx
import matplotlib.pyplot as plt

from graphviz import Digraph, Graph

from igraph import *

#for i in range(10):
#    print("Hola")

filas = int(input("Ingresa las filas: "))
columnas = int(input("Ingresa las columnas: "))
nombreArchivo = input("Ingresa las columnas: ")

#B = [0, 1, 2, 3, 4, 5, 6]
#S = [3, 7]

B = [3]
S = [2, 3]

arregloRelaciones = OptimizacionesC.generarRelacionesArbol(filas, columnas, B, S)
print(arregloRelaciones)

combinaciones = 2**(filas*columnas)

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
g = Graph(directed=True)
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
plot(g, "{}.pdf".format(nombreArchivo), **visual_style)

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
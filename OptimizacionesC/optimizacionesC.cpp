#include <iostream>
#include <../../../Arboles/venv/Lib/site-packages/pybind11/include/pybind11/pybind11.h>
#include <../../../Arboles/venv/Lib/site-packages/pybind11/include/pybind11/numpy.h>
#include <vector>
#include <algorithm>


namespace py = pybind11;
using namespace std;

int potencia(int x, int p)
{
    if (p == 0) return 1;
    if (p == 1) return x;

    int tmp = potencia(x, p / 2);
    if (p % 2 == 0) return tmp * tmp;
    else return x * tmp * tmp;
}

int asignarNivel(int combinacion, int &posInicioCiclo, int *relacionEstados, int *niveles, vector<int> &pilaRegistro) {
    if (niveles[relacionEstados[combinacion]] > 0) {
        niveles[combinacion] = niveles[relacionEstados[combinacion]] + 1;
        return niveles[relacionEstados[combinacion]] + 1;
    }

    int posicionEnPila = -1;
    for (int i = 0; i < pilaRegistro.size(); i++) {
        if (pilaRegistro[i] == combinacion) {
            posicionEnPila = i;
            break;
        }
    }

    if (posicionEnPila != -1) {
        if (niveles[combinacion] == -1) {
            niveles[combinacion] = 0;
        }
        posInicioCiclo = posicionEnPila;
        return 0;
    }
    else {
        pilaRegistro.push_back(combinacion);
        int anterior = asignarNivel(relacionEstados[combinacion], posInicioCiclo, relacionEstados, niveles, pilaRegistro);
        if (pilaRegistro.size() <= posInicioCiclo) {
            niveles[combinacion] = anterior + 1;
        }
        else {
            niveles[combinacion] = 0;
        }
        pilaRegistro.pop_back();
        return niveles[combinacion];
    }
}

py::array_t<int> generarRelacionesArbol(int filas, int columnas, py::list B, py::list S) {
    //Se almacena memoria para el espacio del autómata celular.
    bool** grid_automata = (bool**)calloc(filas, sizeof(bool*));
    for (int i = 0; i < filas; i++) {
        grid_automata[i] = (bool*)calloc(columnas, sizeof(bool));
    }

    int combinaciones = potencia(2, filas * columnas);
    std::cout << "Combinaciones: " << combinaciones << std::endl;

    //Se almacena espacio para la relación de estados.
    //py::array_t<int> relacionEstados = py::array_t<int>(combinaciones);
    int* relacionEstados = (int*)calloc(combinaciones, sizeof(int));
    py::array_t<int> relacionesResultantes = py::array_t<int>(combinaciones);

    //Se almacena espacio para el nivel de cada estado para la representación gráfica.
    int* nivelEstado = (int*)calloc(combinaciones, sizeof(int));
    for (int i = 0; i < combinaciones; i++) {
        nivelEstado[i] = -1;
    }

    //Se almacena espacio para el nuevo estado procesado (Se almacena en una sola dimensión por simplicidad)
    bool* nuevoEstado = (bool*)calloc(filas * columnas, sizeof(bool));

    //Preparando las reglas
    int tamanioB = B.size();
    int tamanioS = S.size();

    int* BC = (int*)calloc(tamanioB, sizeof(int));
    int* SC = (int*)calloc(tamanioS, sizeof(int));

    for (int i = 0; i < tamanioB; i++) {
        BC[i] = B[i].cast<int>();
    }

    for (int i = 0; i < tamanioS; i++) {
        SC[i] = S[i].cast<int>();
    }

    //Inicia el recorrido de todas las posibles combinaciones.
    for (int numCombinacion = 0; numCombinacion < combinaciones; numCombinacion++) {

        for (int k = 0; k < filas * columnas; k++) {
            nuevoEstado[k] = false;
        }

        //Se obtiene el estado a evaluar.
        int posBit = 0;
        for (int i = filas - 1; i >= 0; i--) {
            for (int j = columnas - 1; j >= 0; j--) {
                grid_automata[i][j] = numCombinacion & (1 << posBit);
                posBit++;
            }
        }

        //Procesamiento de las celulas.
        for (int i = 0; i < filas; i++) {
            for (int j = 0; j < columnas; j++) {
                int indiceIzquierdo = ((j - 1) % columnas + columnas) % columnas;
                int indiceDerecho = ((j + 1) % columnas + columnas) % columnas;
                int indiceSuperior = ((i - 1) % filas + filas) % filas;
                int indiceInferior = ((i + 1) % filas + filas) % filas;

                //std::cout << "Indices calculados." << std::endl;   
                //std::cout << "izq: " << indiceIzquierdo << " der: " << indiceDerecho << " sup: " << indiceSuperior << " inf: " << indiceInferior << std::endl;   

                int sumaVecinos = grid_automata[indiceSuperior][indiceIzquierdo] + grid_automata[indiceSuperior][j] + grid_automata[indiceSuperior][indiceDerecho] +
                    grid_automata[i][indiceIzquierdo] + grid_automata[i][indiceDerecho] +
                    grid_automata[indiceInferior][indiceIzquierdo] + grid_automata[indiceInferior][j] + grid_automata[indiceInferior][indiceDerecho];

                //std::cout << "Suma vecinos calculada: " << sumaVecinos << std::endl;

                if (grid_automata[i][j]) {
                    bool encontrado = false;
                    for (int k = 0; k < tamanioS; k++) {
                        if (sumaVecinos == SC[k]) {
                            encontrado = true;
                            nuevoEstado[j + i * filas] = 1;
                            break;
                        }
                    }
                }
                else {
                    for (int k = 0; k < tamanioB; k++) {
                        if (sumaVecinos == BC[k]) {
                            nuevoEstado[j + i * filas] = 1;
                            break;
                        }
                    }
                }
            }

        }

        int nuevoEstadoValor = 0;
        for (int k = 0; k < filas * columnas; ++k) {
            if (nuevoEstado[k]) {
                nuevoEstadoValor |= 1 << filas * columnas - k - 1;
            }
        }

        relacionEstados[numCombinacion] = nuevoEstadoValor;

    }

    /*for (int i = 0; i < combinaciones; i++) {
        std::cout << relacionEstados[i] << std::endl;
    }*/

    //relacionesResultantes.resize({ combinaciones,1 });
    //return relacionesResultantes;

    for (int i = 0; i < combinaciones; i++) {

        vector<int> pilaRegistroNiveles;
        int posicionCiclo = -1;
        asignarNivel(i, posicionCiclo, relacionEstados, nivelEstado, pilaRegistroNiveles);
    }

    /*for (int i = 0; i < combinaciones; i++) {
        cout << "Combinacion: " << i << " Siguiente: " << relacionEstados[i] << " Nivel combinacion: " << nivelEstado[i] << endl;
    }*/

    return py::array_t<int>(
        { combinaciones },
        { 4 },
        relacionEstados
        //free_when_done);
        );

}


PYBIND11_MODULE(OptimizacionesC, m) {
    m.doc() = "Optimizaciones de C para la generacion de arboles de relaciones de estados."; // optional module docstring

    m.def("generarRelacionesArbol", &generarRelacionesArbol, "Genera las relaciones del arbol de relaciones de estados.");
    
}
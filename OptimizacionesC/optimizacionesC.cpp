#include <iostream>
#include <../../../Arboles/venv/Lib/site-packages/pybind11/include/pybind11/pybind11.h>
#include <../../../Arboles/venv/Lib/site-packages/pybind11/include/pybind11/numpy.h>
#include <vector>
#include <algorithm>
#include <fstream>


namespace py = pybind11;
using namespace std;

//Calculo de potencias. (n > 4)  
long long int potencia(long long int x, long long int p) {
    if (p == 0) return 1;
    if (p == 1) return x;

    long long int tmp = potencia(x, p / 2);
    if (p % 2 == 0) return tmp * tmp;
    else return x * tmp * tmp;
}

//Calculo de potencias. (n = 1, 2, 3 y 4)
int potencia(int x, int p)
{
    if (p == 0) return 1;
    if (p == 1) return x;

    int tmp = potencia(x, p / 2);
    if (p % 2 == 0) return tmp * tmp;
    else return x * tmp * tmp;
}

// Version de la funcion para asignar niveles a mundos con c > 4.
int asignarNivelGrande(long long int combinacion, int& posInicioCiclo, long long int* relacionEstados, int* niveles, vector<long long int>& pilaRegistro) {

    //Se verifica si el siguiente estado tiene un nivel superior a 0, de ser asi, se le asigna el nivel siguiente a este. 
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
        int anterior = asignarNivelGrande(relacionEstados[combinacion], posInicioCiclo, relacionEstados, niveles, pilaRegistro);
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

int asignarNivel(int combinacion, int &posInicioCiclo, int *relacionEstados, int *niveles, vector<int> &pilaRegistro) {
    
    //Se verifica si el siguiente estado tiene un nivel superior a 0, de ser as�, se le asigna el nivel siguiente a este. 
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

// Versi�n de generaci�n de relaciones para �rboles de mundos n > 4.
int generarRelacionesArbolGrande(long long int filas, long long int columnas, py::list B, py::list S) {
    //Se almacena memoria para el espacio del automata celular.
    bool** grid_automata = (bool**)calloc(filas, sizeof(bool*));
    for (int i = 0; i < filas; i++) {
        grid_automata[i] = (bool*)calloc(columnas, sizeof(bool));
    }

    long long int base = 2;

    long long int combinaciones = potencia(base, filas * columnas);
    std::cout << "Combinaciones: " << combinaciones << std::endl;

    //Se almacena espacio para la relacion de estados.
    //py::array_t<int> relacionEstados = py::array_t<int>(combinaciones);
    long long int* relacionEstados = (long long int*)calloc(combinaciones, sizeof(long long int));
    py::array_t<long long int> relacionesResultantes = py::array_t<long long int>(combinaciones);

    //Se almacena espacio para el conteo de estados de llegada a cada estado.
    long long int* contadoresIncidencia = (long long int*)calloc(combinaciones, sizeof(long long int));

    //Se almacena espacio para el nivel de cada estado para la representacion grafica.
    int* nivelEstado = (int*)calloc(combinaciones, sizeof(int));
    for (int i = 0; i < combinaciones; i++) {
        nivelEstado[i] = -1;
    }

    //Se almacena espacio para el nuevo estado procesado (Se almacena en una sola dimension por simplicidad)
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
    for (long long int numCombinacion = 0; numCombinacion < combinaciones; numCombinacion++) {

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

        long long int nuevoEstadoValor = 0;
        for (long long int k = 0; k < filas * columnas; ++k) {
            if (nuevoEstado[k]) {
                nuevoEstadoValor |= 1 << filas * columnas - k - 1;
            }
        }

        relacionEstados[numCombinacion] = nuevoEstadoValor;
        contadoresIncidencia[nuevoEstadoValor]++;

    }

    /*for (int i = 0; i < combinaciones; i++) {
        std::cout << relacionEstados[i] << std::endl;
    }*/

    //relacionesResultantes.resize({ combinaciones,1 });
    //return relacionesResultantes;

    for (long long int i = 0; i < combinaciones; i++) {

        vector<long long int> pilaRegistroNiveles;
        int posicionCiclo = -1;
        asignarNivelGrande(i, posicionCiclo, relacionEstados, nivelEstado, pilaRegistroNiveles);
    }

    /*for (int i = 0; i < combinaciones; i++) {
        cout << "Combinacion: " << i << " Siguiente: " << relacionEstados[i] << " Nivel combinacion: " << nivelEstado[i] << endl;
    }*/

    fstream datosUniverso;
    datosUniverso.open("../Arboles/pruebaDatos.txt", ios::out);
    if (!datosUniverso){
        cout << "Creaci�n de archivo de datos fallido.";
    }
    else {
        cout << "Creaci�n del archivo de datos exitoso.";
        //datosUniverso << "Esta es una l�nea de prueba.";

        for (int i = 0; i < combinaciones; i++) {
            datosUniverso << relacionEstados[i] << ", " << nivelEstado[i] << ", " << contadoresIncidencia[i] << "\n";
        }

        datosUniverso.close(); // Step 4: Closing file
    }

    delete relacionEstados;
    delete nivelEstado;
    delete contadoresIncidencia;

    return 0;

    /*py::list resultados;
    resultados.append(py::list(py::array_t<long long int>(
        { combinaciones },
        { 8 },
        relacionEstados
        //free_when_done);
        )));

    resultados.append(py::list(py::array_t<int>(
        { combinaciones },
        { 4 },
        nivelEstado
        //free_when_done);
        )));

    resultados.append(py::list(py::array_t<long long int>(
        { combinaciones },
        { 8 },
        contadoresIncidencia
        //free_when_done);
        )));

    return resultados;*/

    /*return py::array_t<int>(
        { combinaciones },
        { 4 },
        relacionEstados
        //free_when_done);
        );*/

}

py::list generarRelacionesArbol(int filas, int columnas, py::list B, py::list S) {
    //Se almacena memoria para el espacio del aut�mata celular.
    bool** grid_automata = (bool**)calloc(filas, sizeof(bool*));
    for (int i = 0; i < filas; i++) {
        grid_automata[i] = (bool*)calloc(columnas, sizeof(bool));
    }

    int combinaciones = potencia(2, filas * columnas);
    std::cout << "Combinaciones: " << combinaciones << std::endl;

    //Se almacena espacio para la relaci�n de estados.
    //py::array_t<int> relacionEstados = py::array_t<int>(combinaciones);
    int* relacionEstados = (int*)calloc(combinaciones, sizeof(int));
    py::array_t<int> relacionesResultantes = py::array_t<int>(combinaciones);

    //Se almacena espacio para el conteo de estados de llegada a cada estado.
    int* contadoresIncidencia = (int*)calloc(combinaciones, sizeof(int));

    //Se almacena espacio para el nivel de cada estado para la representaci�n gr�fica.
    int* nivelEstado = (int*)calloc(combinaciones, sizeof(int));
    for (int i = 0; i < combinaciones; i++) {
        nivelEstado[i] = -1;
    }

    //Se almacena espacio para el nuevo estado procesado (Se almacena en una sola dimensi�n por simplicidad)
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
        contadoresIncidencia[nuevoEstadoValor]++;

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

    py::list resultados;
    resultados.append(py::list(py::array_t<int>(
        { combinaciones },
        { 4 },
        relacionEstados
        //free_when_done);
        )));

    resultados.append(py::list(py::array_t<int>(
        { combinaciones },
        { 4 },
        nivelEstado
        //free_when_done);
        )));

    resultados.append(py::list(py::array_t<int>(
        { combinaciones },
        { 4 },
        contadoresIncidencia
        //free_when_done);
        )));

    return resultados;

    /*return py::array_t<int>(
        { combinaciones },
        { 4 },
        relacionEstados
        //free_when_done);
        );*/

}


PYBIND11_MODULE(OptimizacionesC, m) {
    m.doc() = "Optimizaciones de C para la generacion de arboles de relaciones de estados."; // optional module docstring

    m.def("generarRelacionesArbol", &generarRelacionesArbol, "Genera las relaciones del arbol de relaciones de estados.");
    m.def("generarRelacionesArbolGrande", &generarRelacionesArbolGrande, "Genera las relaciones del arbol de relaciones de estados.");
    
}
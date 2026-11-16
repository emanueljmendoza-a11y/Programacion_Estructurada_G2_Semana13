"""Estructuras y algoritmos implementados mediante programación estructurada.

Listas de diccionarios, árbol binario de búsqueda balanceado, grafo con
listas de adyacencia, BFS y montículos con la biblioteca estándar heapq.
"""

from collections import deque
from datetime import date
import heapq
import unicodedata


def normalizar(texto):
    """Permite búsquedas ignorando mayúsculas y tildes."""
    texto = unicodedata.normalize("NFD", str(texto).casefold())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def construir_arbol_isbn(libros):
    """Construye un árbol BST balanceado desde la lista, O(n log n)."""
    ordenados = sorted(libros, key=lambda libro: libro["isbn"])

    def construir(inicio, fin):
        if inicio > fin:
            return None
        medio = (inicio + fin) // 2
        return {
            "clave": ordenados[medio]["isbn"],
            "libro": ordenados[medio],
            "izquierda": construir(inicio, medio - 1),
            "derecha": construir(medio + 1, fin),
        }

    return construir(0, len(ordenados) - 1)


def buscar_en_arbol(raiz, isbn):
    """Búsqueda iterativa BST, O(log n) por árbol balanceado."""
    actual = raiz
    while actual is not None:
        if isbn == actual["clave"]:
            return actual["libro"]
        if isbn < actual["clave"]:
            actual = actual["izquierda"]
        else:
            actual = actual["derecha"]
    return None


def buscar_lineal(libros, consulta):
    """Recorrido de listas O(n) para título, autor y categoría."""
    termino = normalizar(consulta.strip())
    return [
        libro for libro in libros
        if termino in normalizar(" ".join((
            libro["titulo"], libro["autor"], libro["categoria"], libro["isbn"]
        )))
    ]


def construir_grafo(libros):
    """Grafo no dirigido; arista si comparten autor o categoría. O(n²)."""
    grafo = {libro["id"]: [] for libro in libros}
    for i in range(len(libros)):
        for j in range(i + 1, len(libros)):
            a, b = libros[i], libros[j]
            puntos = 0
            if normalizar(a["autor"]) == normalizar(b["autor"]):
                puntos += 2
            if normalizar(a["categoria"]) == normalizar(b["categoria"]):
                puntos += 1
            if puntos:
                grafo[a["id"]].append((b["id"], puntos))
                grafo[b["id"]].append((a["id"], puntos))
    return grafo


def recomendar_bfs(libros, libro_id, limite=5):
    """BFS O(V+E), seguido de ordenamiento O(V log V) de hallazgos."""
    grafo = construir_grafo(libros)
    if libro_id not in grafo:
        return []
    indice = {libro["id"]: libro for libro in libros}
    cola = deque([(libro_id, 0)])
    visitados = {libro_id}
    encontrados = []

    while cola:
        actual, distancia = cola.popleft()
        for vecino, afinidad in grafo[actual]:
            if vecino in visitados:
                continue
            visitados.add(vecino)
            cola.append((vecino, distancia + 1))
            encontrados.append({
                "libro": indice[vecino],
                "distancia": distancia + 1,
                "afinidad": afinidad,
            })

    encontrados.sort(key=lambda item: (item["distancia"], -item["afinidad"], item["libro"]["titulo"]))
    return encontrados[:limite]


def heap_reservas_pendientes(reservas, libro_id):
    """Min-heap FIFO por fecha de solicitud; construcción O(n)."""
    monticulo = [
        (reserva["creada_en"], reserva["id"])
        for reserva in reservas
        if reserva["libro_id"] == libro_id and reserva["estado"] == "pendiente"
    ]
    heapq.heapify(monticulo)
    return monticulo


def reservas_por_prioridad(reservas, libro_id):
    """Extrae solicitudes en orden, cada extracción O(log n)."""
    monticulo = heap_reservas_pendientes(reservas, libro_id)
    por_id = {reserva["id"]: reserva for reserva in reservas}
    resultado = []
    while monticulo:
        _, reserva_id = heapq.heappop(monticulo)
        resultado.append(por_id[reserva_id])
    return resultado


def prestamos_vencidos_heap(prestamos, hoy=None):
    """Maximiza días de retraso con una clave negativa y heapq."""
    hoy = hoy or date.today()
    monticulo = []
    for prestamo in prestamos:
        if prestamo["devuelto_en"] is not None:
            continue
        dias = (hoy - date.fromisoformat(prestamo["vence_en"])).days
        if dias > 0:
            monticulo.append((-dias, prestamo["vence_en"], prestamo["id"]))
    heapq.heapify(monticulo)
    resultado = []
    while monticulo:
        negativos, _, prestamo_id = heapq.heappop(monticulo)
        resultado.append((prestamo_id, -negativos))
    return resultado


def estadisticas_grafo(grafo):
    vertices = len(grafo)
    aristas = sum(len(vecinos) for vecinos in grafo.values()) // 2
    return {"vertices": vertices, "aristas": aristas}


if __name__ == "__main__":
    # Demostración rápida con datos de ejemplo (el proyecto usa biblioteca.json).
    libros = [
        {"id": "L1", "isbn": "978-03", "titulo": "Cien años de soledad", "autor": "Gabriel García Márquez", "categoria": "Novela"},
        {"id": "L2", "isbn": "978-01", "titulo": "El amor en los tiempos del cólera", "autor": "Gabriel García Márquez", "categoria": "Novela"},
        {"id": "L3", "isbn": "978-02", "titulo": "Azul...", "autor": "Rubén Darío", "categoria": "Poesía"},
        {"id": "L4", "isbn": "978-04", "titulo": "Cantos de vida y esperanza", "autor": "Rubén Darío", "categoria": "Poesía"},
    ]
    reservas = [
        {"id": "R2", "libro_id": "L1", "estado": "pendiente", "creada_en": "2026-11-05"},
        {"id": "R1", "libro_id": "L1", "estado": "pendiente", "creada_en": "2026-11-01"},
    ]
    prestamos = [
        {"id": "P1", "devuelto_en": None, "vence_en": "2026-11-10"},
        {"id": "P2", "devuelto_en": None, "vence_en": "2026-11-01"},
    ]

    print("Lista (búsqueda lineal 'dario'):", [l["titulo"] for l in buscar_lineal(libros, "dario")])
    raiz = construir_arbol_isbn(libros)
    print("Árbol (ISBN 978-02):", buscar_en_arbol(raiz, "978-02")["titulo"])
    print("Grafo:", estadisticas_grafo(construir_grafo(libros)))
    print("BFS desde L1:", [r["libro"]["titulo"] for r in recomendar_bfs(libros, "L1")])
    print("Heap reservas L1:", [r["id"] for r in reservas_por_prioridad(reservas, "L1")])
    print("Heap vencidos:", prestamos_vencidos_heap(prestamos, hoy=date(2026, 11, 16)))

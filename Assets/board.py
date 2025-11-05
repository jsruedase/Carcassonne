from collections import deque
import tiles

class Board:
    def __init__(self):
        self.grid = {(0, 0): tiles.Tile13()}  # losa inicial
        self.caminosCerrados = set()
        self.ciudadesCerradas = set()

    def get_tile(self, position):
        return self.grid.get(position, None)

    def _tile_at_with_placement(self, pos, placed_tile, placed_pos):
        if pos == placed_pos:
            return placed_tile
        return self.grid.get(pos, None)

    # --- NUEVA versión: respeta orientación y tipos de terreno ---
    def can_place_tile(self, tile: tiles.Tile, position: tuple[int, int]):
        # No se puede colocar sobre una losa existente
        if position in self.grid:
            return False

        x, y = position
        adjacent_positions = {
            (x, y + 1): ("north", "south"),
            (x + 1, y): ("east", "west"),
            (x, y - 1): ("south", "north"),
            (x - 1, y): ("west", "east"),
        }

        has_neighbor = False
        for adj_pos, (my_side, neighbor_side) in adjacent_positions.items():
            neighbor = self.grid.get(adj_pos, None)
            if neighbor:
                has_neighbor = True
                my_feature = getattr(tile, my_side)
                neighbor_feature = getattr(neighbor, neighbor_side)
                if my_feature != neighbor_feature:
                    return False

        # Debe tener al menos un vecino
        return has_neighbor

    def place_tile(self, tile: 'tiles.Tile', position: tuple[int, int], feed=None):
        """
        Coloca la losa si es válida. Si la colocación cierra caminos o ciudades,
        empuja mensajes a `feed` (si se proporciona).
        """
        if self.can_place_tile(tile, position):
            self.grid[position] = tile

            # Verificar si se cerró un camino (la función devuelve (cerrado, visitados))
            camino_cerrado, camino_visitados = self.verificar_camino_cerrado(position)
            if camino_cerrado:
                # detectar si hay nuevas posiciones cerradas (evitar anuncios duplicados)
                nuevos = camino_visitados - self.caminosCerrados
                if nuevos:
                    self.caminosCerrados.update(camino_visitados)
                    if feed:
                        ejemplo = sorted(list(nuevos))[:6]
                        feed.push(f"Camino cerrado! tamaño={len(camino_visitados)}. coords ejemplo: {ejemplo}")

            # Verificar si se cerró un castillo/ciudad (devuelve (cerrado, visitados))
            ciudad_cerrada, ciudad_visitados = self.verificar_castillo_cerrado(position)
            if ciudad_cerrada:
                nuevos = ciudad_visitados - self.ciudadesCerradas
                if nuevos:
                    self.ciudadesCerradas.update(ciudad_visitados)
                    if feed:
                        ejemplo = sorted(list(nuevos))[:6]
                        feed.push(f"Ciudad cerrada! tamaño={len(ciudad_visitados)}. coords ejemplo: {ejemplo}")

            return True
        return False


    def verificar_camino_cerrado(self, start_pos):
        """
        Retorna (cerrado: bool, visitados: set).
        Un camino está abierto si alguna arista 'road' del componente toca
        una celda vacía o toca una losa cuyo lado opuesto NO es 'road'.
        """
        visitados = set()
        cola = deque([start_pos])
        abierto = False

        while cola:
            pos = cola.popleft()
            if pos in visitados:
                continue
            visitados.add(pos)

            tile = self.grid.get(pos)
            if not tile:
                continue

            x, y = pos
            lados = {
                "north": (x, y + 1, "south"),
                "east":  (x + 1, y, "west"),
                "south": (x, y - 1, "north"),
                "west":  (x - 1, y, "east"),
            }

            for lado, (nx, ny, lado_opuesto) in lados.items():
                if getattr(tile, lado) == "road":
                    vecino = self.grid.get((nx, ny))
                    if not vecino:
                        # Camino que termina sin conectar: no cerrado
                        abierto = True
                    else:
                        # Si el vecino NO tiene 'road' en la cara opuesta, es una arista abierta
                        if getattr(vecino, lado_opuesto) != "road":
                            abierto = True
                        else:
                            # vecino con 'road' en la cara opuesta -> seguir explorando
                            if (nx, ny) not in visitados:
                                cola.append((nx, ny))

        cerrado = not abierto
        if cerrado:
            self.caminosCerrados.update(visitados)
        return cerrado, visitados

    def verificar_castillo_cerrado(self, start_pos):
        """
        Retorna (cerrado: bool, visitados: set).
        Una ciudad está abierta si alguna arista 'city' del componente toca
        una celda vacía o una losa que no tiene 'city' en la cara opuesta.
        """
        visitados = set()
        cola = deque([start_pos])
        abierto = False

        while cola:
            pos = cola.popleft()
            if pos in visitados:
                continue
            visitados.add(pos)

            tile = self.grid.get(pos)
            if not tile:
                continue

            x, y = pos
            lados = {
                "north": (x, y + 1, "south"),
                "east":  (x + 1, y, "west"),
                "south": (x, y - 1, "north"),
                "west":  (x - 1, y, "east"),
            }

            for lado, (nx, ny, lado_opuesto) in lados.items():
                if getattr(tile, lado) == "city":
                    vecino = self.grid.get((nx, ny))
                    if not vecino:
                        # borde sin losa vecina
                        abierto = True
                    else:
                        vecino_feature = getattr(vecino, lado_opuesto)
                        if vecino_feature != "city":
                            # vecino no conecta correctamente
                            abierto = True
                        else:
                            # vecino conecta: explorar
                            if (nx, ny) not in visitados:
                                cola.append((nx, ny))

        cerrado = not abierto
        return cerrado, visitados

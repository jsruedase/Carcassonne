from collections import deque
from Assets import tiles
from Assets import utils


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
            camino_cerrado, camino_visitados, longitud = self.verificar_camino_cerrado(position)
            if camino_cerrado:
                nuevos=camino_visitados-self.caminosCerrados
                if nuevos:
                    self.caminosCerrados.update(camino_visitados)
                    if feed:
                        ejemplo = sorted(list(nuevos))[:6]
                        feed.push(
                            f"Camino cerrado! longitud={longitud}, tamaño={len(camino_visitados)}. "
                            f"coords ejemplo: {ejemplo}"
                        )

        
            # Verificar si se cerró un castillo/ciudad (devuelve (cerrado, visitados))
            cerrada, ciudad_visitados, tamaño = self.verificar_castillo_cerrado(position)
            if cerrada:
                nuevos = ciudad_visitados - self.ciudadesCerradas
                if nuevos:
                    self.ciudadesCerradas.update(ciudad_visitados)
                    if feed:
                        ejemplo = sorted(list(nuevos))[:6]
                        feed.push(f"Ciudad cerrada! tamaño={tamaño}. coords ejemplo: {ejemplo}")
            return True
        return False


    def verificar_camino_cerrado(self, start_pos):
        """
        Detecta si al menos uno de los caminos (componentes de 'road')
        que salen de start_pos se ha cerrado completamente.

        Retorna:
          (hay_cierre: bool, tiles_visitados: set[(x,y)], longitud_total: int)
        """

        start_tile = self.get_tile(start_pos)
        if not start_tile:
            return False, set(), 0

        dirs = {
            "north": (0, +1, "south"),
            "east":  (+1, 0, "west"),
            "south": (0, -1, "north"),
            "west":  (-1, 0, "east"),
        }

        # Lados del start_pos que son caminos
        road_sides = [s for s in dirs if getattr(start_tile, s) == "road"]
        if not road_sides:
            return False, set(), 0

        cerrados = []          # lista de componentes cerrados
        tiles_usados = set()   # tiles ya explorados 

        # Exploramos cada camino por separado (por lado)
        for side in road_sides:
            nodo_inicial = (start_pos, side)
            if nodo_inicial in tiles_usados:
                continue

            q = deque([nodo_inicial])
            visit_nodes = set()
            visit_tiles = set()
            abierto = False
            longitud = 0

            while q:
                (pos, s) = q.popleft()
                if (pos, s) in visit_nodes:
                    continue
                visit_nodes.add((pos, s))
                visit_tiles.add(pos)

                t = self.get_tile(pos)
                if not t:
                    abierto = True
                    continue

                dx, dy, opp = dirs[s]
                nbr_pos = (pos[0] + dx, pos[1] + dy)
                nbr = self.get_tile(nbr_pos)

                if not nbr:
                    abierto = True
                else:
                    if getattr(nbr, opp) != "road":
                        abierto = True
                    else:
                        # conectar al siguiente segmento
                        for next_side, (dx2, dy2, opp2) in dirs.items():
                            if getattr(nbr, next_side) == "road":
                                # si el centro del tile vecino es "start", no conecta entre lados
                                if nbr.center == "start" and next_side != opp:
                                    continue
                                q.append((nbr_pos, next_side))

                # Si el centro de este tile es "road" y no "start", puede conectar entre lados
                if t.center == "road":
                    for s2 in dirs:
                        if getattr(t, s2) == "road" and (pos, s2) not in visit_nodes:
                            q.append((pos, s2))

            tiles_usados.update(visit_nodes)
            if not abierto and visit_tiles:
                longitud = len(visit_tiles)
                cerrados.append((visit_tiles, longitud))

        if cerrados:
            # Si hay al menos un camino cerrado, devolvemos la unión de tiles y la longitud total
            union_tiles = set().union(*(tiles for tiles, _ in cerrados))
            total_len = sum(l for _, l in cerrados)
            return True, union_tiles, total_len

        return False, set(), 0


    def verificar_castillo_cerrado(self, start_pos):
        """
        BFS a nivel de nodos (pos, side) para ciudades.
        Retorna (any_closed: bool, closed_tiles_union: set[pos], tamaño_total: int)

        Reglas y puntualizaciones (compatibles con tu set de tiles):
         - Un nodo = (pos, side) donde getattr(tile, side) == "city".
         - Conexión entre nodos:
             * Entre tiles: (pos, side) <-> (nbr_pos, opp) si ambos lados son "city".
             * Dentro de la misma losa: si tile.center == "city", entonces todas las sides "city"
               de esa losa están conectadas internamente.
         - Una componente está "abierta" si algún nodo apunta a vacío o a vecino cuyo lado opuesto
           NO sea "city".
         - Se exploran sólo las componentes que tocan start_pos (es decir, comenzamos BFS por cada side
           de start_pos que sea "city").
         - Devolvemos la unión de tiles (pos) de todas las componentes cerradas que tocan start_pos.
        """
        
       

      
        start_tile = self.get_tile(start_pos)
        if not start_tile:
            return False, set(), 0

        sides = ("north", "east", "south", "west")
        # Considerar cualquier side que sea 'city' — aunque center != 'city'
        start_sides = [s for s in sides if getattr(start_tile, s) == "city"]
        if not start_sides:
            return False, set(), 0

        dirs = {
            "north": (0, +1, "south"),
            "east":  (+1, 0, "west"),
            "south": (0, -1, "north"),
            "west":  (-1, 0, "east"),
        }

        visited_nodes = set()       # (pos, side) ya procesados globalmente
        closed_components_tiles_union = set()
        any_closed = False

        for side in start_sides:
            start_node = (start_pos, side)
            if start_node in visited_nodes:
                continue

            queue = deque([start_node])
            component_nodes = set()
            component_tiles = set()
            abierto = False

            while queue:
                pos, s = queue.popleft()
                if (pos, s) in component_nodes:
                    continue
                component_nodes.add((pos, s))

                t = self.get_tile(pos)
                if not t:
                    # apuntaba a vacío -> abierto
                    abierto = True
                    continue

                # registrar tile
                component_tiles.add(pos)

                # 1) Conexión hacia el vecino a través del lado s
                dx, dy, opp = dirs[s]
                nbr_pos = (pos[0] + dx, pos[1] + dy)
                nbr = self.get_tile(nbr_pos)
                if not nbr:
                    abierto = True
                else:
                    if getattr(nbr, opp) != "city":
                        # vecino existe pero su lado opuesto no es city -> abierto
                        abierto = True
                    else:
                        # vecino y su lado opuesto son "city" -> conectar ese nodo
                        if (nbr_pos, opp) not in component_nodes:
                            queue.append((nbr_pos, opp))
                        # si el vecino tiene center == 'city', conectar sus otras sides 'city' internamente
                        if nbr.center in ("city", "start"):
                            for s2 in sides:
                                if getattr(nbr, s2) == "city" and (nbr_pos, s2) not in component_nodes:
                                    queue.append((nbr_pos, s2))

                # 2) conexiones internas del mismo tile: solo si center == 'city'
                if t.center in ("city", "start"):
                    for s2 in sides:
                        if getattr(t, s2) == "city" and (pos, s2) not in component_nodes:
                            queue.append((pos, s2))

            # marcar nodos de esta componente como visitados globalmente
            visited_nodes.update(component_nodes)
            if not abierto:
                any_closed = True
                closed_components_tiles_union.update(component_tiles)

        return any_closed, closed_components_tiles_union, len(closed_components_tiles_union)

    def getLegalPlacements(self, tile: tiles.Tile) -> None:
                positions = []
                for position, placed_tile in self.grid.items():
                    x, y = position
                    adjacent_positions = {
                        (x, y + 1): 'north',
                        (x + 1, y): 'east',
                        (x, y - 1): 'south',
                        (x - 1, y): 'west',
                    }
                    for pos in adjacent_positions.keys():
                        can, orientations = self.can_place_tile_in(tile, pos)
                        if can:
                            for orientation in orientations:
                                positions.append((pos, orientation))
            
                return positions

    def can_place_tile_in(self, tile: tiles.Tile, position: tuple[int, int]):
        """ Devuelve True si se puede colocar la ficha en la posición dada y todas las orientaciones posibles."""

        if self.grid.get(position, None):
            return False, []

        x, y = position
        adjacent_positions = {
            (x, y + 1): 'north',
            (x + 1, y): 'east',
            (x, y - 1): 'south',
            (x - 1, y): 'west',
        }
        valid = False
        rotations = []
        for i in range(4):
            matches = 0
            for adj_pos, direction in adjacent_positions.items():
                if adj_pos in self.grid:
                    placed_tile = self.get_tile(adj_pos)
                    if direction == "north":
                        if placed_tile.south == tile.north:
                            matches += 1
                            
                    if direction == "east":
                        if placed_tile.west == tile.east:
                            matches += 1
                            
                    if direction == "south":
                        if placed_tile.north == tile.south:
                            matches += 1
                            
                    if direction == "west":
                        if placed_tile.east == tile.west:
                            matches += 1
                else:
                    matches += 1
            if matches == 4:
                tile.reset_orientation()
                valid = True
                rotations.append(90*i)
            else:
                tile.rotate()
        tile.reset_orientation()
        return valid, rotations

    def calculateScore(self):
        score = len(self.grid)  # 1 punto por cada losa colocada
        for road in self.caminosCerrados:
            score += len(road)
        for city in self.ciudadesCerradas:
            score += 2 * len(city)
        return score
    
if __name__ == "__main__":
    board = Board()
    print(board.getLegalPlacements(tiles.Tile7()))
    #board.place_tile(tiles.Tile7(), (0, 1))
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
        Detecta si el componente 'road' que toca start_pos conecta exactamente dos tiles con center == 'start'.
        Devuelve:
          (cerrado: bool, visitados: set[(x,y)], longitud: int)
        """

        # Hay problemas con las losas que en el centro tiene en start y al rededor tienen road
        # Parece que no las detecta correctamente 
        # Cuando en el mismo camino que ya tiene 2starts se extiende con otra casilla que tambien tiene start no contempla este como un camino cerrado 
        # Ejemplo de fallo: se concetan tile 1 tile 13 y tile 16, en la primera lo acepta como conectado pero cuando se junta con la otra no
        # Creo que tiene que ver con 

        """ camino_cerrado, camino_visitados, longitud = self.verificar_camino_cerrado(position)
            if camino_cerrado:
                nuevos=camino_visitados-self.caminosCerrados
                if nuevos:
                    self.caminosCerrados.update(camino_visitados)"""
        #
        

        start_tile = self.get_tile(start_pos)
        if not start_tile:
            return False, set(), 0

        dirs = {
           "north": (0, +1, "south"),
            "east":  (+1, 0, "west"),
            "south": (0, -1, "north"),
            "west":  (-1, 0, "east"),
        }

        # BFS principal: construir el componente de road
        q = deque([start_pos])
        visitados = set()

        while q:
            pos = q.popleft()
            if pos in visitados:
               continue
            visitados.add(pos)

            t = self.get_tile(pos)
            if not t:
                continue

            for side, (dx, dy, opp) in dirs.items():
                if getattr(t, side) != "road":
                    continue
                nbr_pos = (pos[0] + dx, pos[1] + dy)
                nbr = self.get_tile(nbr_pos)
                if not nbr:
                    continue
                if getattr(nbr, opp) != "road":
                    continue
                if nbr_pos not in visitados:
                    q.append(nbr_pos)

        # Buscar losas 'start' en el componente
        starts = [p for p in visitados if self.get_tile(p).center == "start"]

        if len(starts) == 2:
        # BFS para encontrar la distancia mínima entre los dos starts
            q2 = deque([(starts[0], 0)])
            seen = {starts[0]}
            while q2:
                pos, dist = q2.popleft()
                if pos == starts[1]:
                    return True, visitados, dist
                t = self.get_tile(pos)
                for side, (dx, dy, opp) in dirs.items():
                    if getattr(t, side) != "road":
                        continue
                    nbr_pos = (pos[0] + dx, pos[1] + dy)
                    nbr = self.get_tile(nbr_pos)
                    if nbr and getattr(nbr, opp) == "road" and nbr_pos not in seen:
                        seen.add(nbr_pos)
                        q2.append((nbr_pos, dist + 1))

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




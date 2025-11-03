import tiles
import utils
class Board:
    def __init__(self):
        self.grid = {(0, 0): tiles.Tile13()} # Empezamos con la ficha inicial en el centro
        self.caminosCerrados=set() #Se guardan las posiciones que ya hacen parte de un camino cerrado
        
    def get_tile(self, position: tuple[int, int]) -> tiles.Tile | None:
        return self.grid.get(position, None)

    def valid_placements_for_tile(self, tile: tiles.Tile) -> None:
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
                can, orientation = self.can_place_tile(tile, pos)
                if can:
                    positions.append(pos)
                    # print(tile.orientation)
                    # print(pos, orientation)
    
        return positions
                
    def can_place_tile(self, tile: tiles.Tile, position: tuple[int, int]):
        """ Devuelve True si se puede colocar la ficha en la posición dada"""
        # ! Se podría modificar para que devuelva todas las orientaciones válidas, devuelve la primera que cumple.

        if self.grid.get(position, None):
            return False, None

        x, y = position
        adjacent_positions = {
            (x, y + 1): 'north',
            (x + 1, y): 'east',
            (x, y - 1): 'south',
            (x - 1, y): 'west',
        }
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
                return True, 90*i
            else:
                tile.rotate()
        tile.reset_orientation()
        return False, None
    
    def place_tile(self, tile: tiles.Tile, position: tuple[int, int]):
        can_place, orientation = self.can_place_tile(tile, position)
        if can_place:
            while tile.orientation != orientation:
                tile.rotate()
            self.grid[position] = tile
    
    def connects_road(self, tile: tiles.Tile, position: tuple[int, int]) -> bool:
        """ Devuelve True si la ficha colocada en la posición dada une dos puntos de inicio de caminos.
        Recorre todo el componente conectado por aristas 'road' y cuenta cuántas fichas con center == 'start' hay"""
        #Se inicia en una losa dada, a partir de esta se busca primero si tiene camino en el centro o si tiene start si no se aborta
        #Tiene que verificar si el camino contiene dos tile.start en sus extremos o sea no pueden haber bucles circulares solo de camino sin propósito
        #Se verifican las direcciones a las que hay camino, si ya hace parte a un camino cerrado no se tiene en cuenta tile.cerrado= true or false
        #Para las direcciones válidas se continúa, en caso de que se llegue a una casilla que no tenga vecino se cancela
        #Como mantengo la cantidad de start? que pasa si un start sirve para cerrar varios caminos? hay tile que son start en centro y al rededor camino esa no se marca como usada
        #Como me muevo entre las losas 

        # Condicion inicial
        if tile.center not in ("road", "start"):
            return False

       

        visitados=set()
        q=utils.Queue()
        q.push(position)
        visitados.add(position)

        conteoStarts=0
        tiles_component=[]  # guarda las posiciones del componente si quieres usarlas luego

        # Mapa de vecinos (delta -> (mi lado, lado del vecino))
        vecinos = {
            (0, 1): ("north", "south"),
            (1, 0): ("east",  "west"),
            (0, -1):("south", "north"),
            (-1, 0):("west",  "east"),
        }

        # BFS 
        while not q.isEmpty():
            pos=q.pop()
            losa=self.get_tile(pos)
            if not losa:
                continue

            tiles_component.append(pos)
            # Contamos starts que estén en el centro de las losas
            if losa.center=="start":
                conteoStarts+= 1

            x, y = pos
            for (dx, dy), (miLado, ladoVecino) in vecinos.items():
                # Sólo nos interesa expandir por aristas que sean 'road'
                if getattr(losa, miLado) != "road":
                    continue

                npos = (x+dx,y+dy)
                neigh=self.get_tile(npos)

                # Si existe vecino y el lado opuesto también es 'road', se conecta y lo encolamos

                if neigh and getattr(neigh, ladoVecino) == "road":

                    if npos not in visitados:
                        visitados.add(npos)
                        q.push(npos)
                else:
                    # Aquí hay un borde abierto (hueco o vecino sin 'road'), pero NO retornamos False.
                    # Simplemente seguimos explorando el resto del componente porque puede haber otros caminos
                    # que conecten dos 'start'.
                    pass

        # Tras explorar todo el componente, si encontramos >= 2 'start' -> conecta dos puntos
        if conteoStarts >= 2:
         #marcar casillas cerradas para no tenerlas en cuenta
       
            return True

        return False



        

        pass
    
    def closes_city(self, tile: tiles.Tile, position: tuple[int, int]) -> bool:
        # Se lanza un bfs desde el castillo; si todo está cerrado entonces se retorna True, si no False
        # En este caso no se tienen que marcar como visitadas solamente contar la cantidad; 
        # un castillo cerrado no puede extenderse más de lo que ya está como los caminos que sí.
        # Se tiene que verificar primero que alguna de las casillas tenga castillo
        # Se sabe que está cerrado si en una losa que se llegó el castillo le sigue un start o grass
        # Se tiene que retornar False apenas se encuentre una posición con castillo que no tenga losa adyacente 
        # con castillo y grass o start


        # Verificamos que la losa actual tenga al menos un borde de tipo city
        if (tile.north != "city" and tile.south != "city" and tile.east != "city" and tile.west != "city"):
            return False

        visitados=set()
        q=utils.Queue()
        q.push(position)
        visitados.add(position)

        conteoCastillo=0

        # BFS
        while not q.isEmpty():
            pos=q.pop()
            losa=self.get_tile(pos)  # Accedemos a la losa en sí

            if not losa:
                continue

            # Si la losa tiene partes de ciudad, la contamos
            if (losa.north == "city" or losa.south == "city" or losa.east == "city" or losa.west == "city"):
                conteoCastillo += 1

            x,y = pos
            # Diccionario de vecinos: desplazamiento → (mi lado, lado del vecino)
            vecinos = {
                (0, 1): ("north", "south"),
                (1, 0): ("east", "west"),
                (0, -1): ("south", "north"),
                (-1, 0): ("west", "east"),
            }

            for (dx, dy), (miLado, ladoVecino) in vecinos.items():
                # Solo exploramos si este lado de la losa es ciudad
                if getattr(losa, miLado) != "city":
                    continue

                npos=(x+dx,y+dy)
                losaVecina=self.get_tile(npos)

                # Si no hay losa vecina, el borde está abierto → ciudad no cerrada
                if losaVecina is None:
                    return False  # retorno inmediato

                # Si la losa vecina no tiene ciudad en ese lado → borde abierto
                if getattr(losaVecina, ladoVecino) != "city":
                    return False  # retorno inmediato

                # Si la losa vecina continúa la ciudad, la exploramos
                if npos not in visitados:
                    visitados.add(npos)
                    q.push(npos)

    # Si terminó el BFS sin encontrar bordes abiertos → ciudad cerrada
        return True
        


if __name__ == "__main__":
    board = Board()
    print(board.valid_placements_for_tile(tiles.Tile7()))
    board.place_tile(tiles.Tile7(), (0, 1))
    
    

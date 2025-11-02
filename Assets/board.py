import tiles

class Board:
    def __init__(self):
        self.grid = {(0, 0): tiles.Tile13()} # Empezamos con la ficha inicial en el centro
        
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
        """ Devuelve True si la ficha colocada en la posición dada une dos puntos de inicio de caminos y la longitud del camino creado"""
        pass
    
    def closes_city(self, tile: tiles.Tile, position: tuple[int, int]) -> bool:
        """ Devuelve True si la ficha colocada en la posición dada cierra una ciudad y el tamaño de la ciudad cerrada"""
        pass

if __name__ == "__main__":
    board = Board()
    print(board.valid_placements_for_tile(tiles.Tile7()))
    board.place_tile(tiles.Tile7(), (0, 1))
    
    

class Tile:
    def __init__(self):
        # Tile information
        self.north = None
        self.east = None
        self.south = None
        self.west = None
        self.center = None
        
        self.orientation = 0

    def rotate(self):
        # Rotate the tile 90 degrees counter-clockwise
        self.north, self.east, self.south, self.west = (
            self.east,
            self.south,
            self.west,
            self.north,
        )
        self.orientation = (self.orientation + 90) % 360
        
    def reset_orientation(self):
        while self.orientation != 0:
            self.rotate()
    
    def sides_match(self, other_tile: 'Tile', direction: str) -> bool:
        if direction == 'north':
            return self.north == other_tile.south
        elif direction == 'east':
            return self.east == other_tile.west
        elif direction == 'south':
            return self.south == other_tile.north
        elif direction == 'west':
            return self.west == other_tile.east
        return False

class Tile1(Tile):
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "grass"
        self.south = "road"
        self.west = "grass"
        self.center = "start"

class Tile2(Tile):
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "city"
        self.south = "city"
        self.west = "city"
        self.center = "city"

class Tile3(Tile):
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "road"
        self.south = "grass"
        self.west = "road"
        self.center = "road"
        
class Tile4(Tile):
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "grass"
        self.south = "grass"
        self.west = "grass"
        self.center = "grass"

class Tile5(Tile):
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "city"
        self.south = "grass"
        self.west = "city"
        self.center = "city"
        
class Tile6(Tile):
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "city"
        self.south = "grass"
        self.west = "city"
        self.center = "grass"
        
class Tile7(Tile):
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "road"
        self.south = "road"
        self.west = "grass"
        self.center = "road"

class Tile8(Tile):
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "grass"
        self.south = "road"
        self.west = "road"
        self.center = "road"

class Tile9(Tile):
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "road"
        self.south = "road"
        self.west = "road"
        self.center = "start"

class Tile10(Tile):
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "city"
        self.south = "grass"
        self.west = "grass"
        self.center = "city"

class Tile11(Tile):
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "road"
        self.south = "road"
        self.west = "city"
        self.center = "road"
        
class Tile12(Tile):
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "city"
        self.south = "grass"
        self.west = "city"
        self.center = "city"
        
class Tile13(Tile):
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "city"
        self.south = "road"
        self.west = "city"
        self.center = "start" #cuidado con esta al detectar conexidad de ciudades.
    
class Tile14(Tile):
    def __init__(self):
        super().__init__()
        self.north = "road"
        self.east = "grass"
        self.south = "road"
        self.west = "grass"
        self.center = "road"
        
class Tile15(Tile):
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "grass"
        self.south = "road"
        self.west = "road"
        self.center = "road"

class Tile16(Tile):
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "road"
        self.south = "road"
        self.west = "road"
        self.center = "start"

class Tile17(Tile):
    def __init__(self):
        super().__init__()
        self.north = "road"
        self.east = "road"
        self.south = "road"
        self.west = "road"
        self.center = "start"
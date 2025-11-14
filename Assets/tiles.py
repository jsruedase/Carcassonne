import random
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

class Tile1(Tile): #x2
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "grass"
        self.south = "road"
        self.west = "grass"
        self.center = "start"

class Tile2(Tile): #x1
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "city"
        self.south = "city"
        self.west = "city"
        self.center = "city"

class Tile3(Tile):#x4
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "road"
        self.south = "grass"
        self.west = "road"
        self.center = "road"
        
class Tile4(Tile):#x5
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "grass"
        self.south = "grass"
        self.west = "grass"
        self.center = "grass"

class Tile5(Tile):#x3
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "city"
        self.south = "grass"
        self.west = "city"
        self.center = "city"
        
class Tile6(Tile):#x3
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "city"
        self.south = "grass"
        self.west = "city"
        self.center = "grass"
        
class Tile7(Tile):#x3
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "road"
        self.south = "road"
        self.west = "grass"
        self.center = "road"

class Tile8(Tile):#x3
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "grass"
        self.south = "road"
        self.west = "road"
        self.center = "road"

class Tile9(Tile):#x3
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "road"
        self.south = "road"
        self.west = "road"
        self.center = "start"

class Tile10(Tile):#x5
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "city"
        self.south = "grass"
        self.west = "grass"
        self.center = "city"

class Tile11(Tile):#x4
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "grass"
        self.south = "grass"
        self.west = "city"
        self.center = "grass"


        
class Tile12(Tile):#x4
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "city"
        self.south = "grass"
        self.west = "city"
        self.center = "city"
        
class Tile13(Tile):#x3
    def __init__(self):
        super().__init__()
        self.north = "city"
        self.east = "city"
        self.south = "road"
        self.west = "city"
        self.center = "start" #cuidado con esta al detectar conexidad de ciudades.
    
class Tile14(Tile):#x8
    def __init__(self):
        super().__init__()
        self.north = "road"
        self.east = "grass"
        self.south = "road"
        self.west = "grass"
        self.center = "road"
        
class Tile15(Tile):#x9
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "grass"
        self.south = "road"
        self.west = "road"
        self.center = "road"

class Tile16(Tile):#x4
    def __init__(self):
        super().__init__()
        self.north = "grass"
        self.east = "road"
        self.south = "road"
        self.west = "road"
        self.center = "start"

class Tile17(Tile):#x1
    def __init__(self):
        super().__init__()
        self.north = "road"
        self.east = "road"
        self.south = "road"
        self.west = "road"
        self.center = "start"

def revolverLosas():
    # Crear la lista de losas según sus cantidades
    losas = (
        [Tile1() for _ in range(2)] +
        [Tile2() for _ in range(1)] +
        [Tile3() for _ in range(4)] +
        [Tile4() for _ in range(5)] +
        [Tile5() for _ in range(3)] +
        [Tile6() for _ in range(3)] +
        [Tile7() for _ in range(3)] +
        [Tile8() for _ in range(3)] +
        [Tile9() for _ in range(3)] +
        [Tile10() for _ in range(5)] +
        [Tile11() for _ in range(4)] +

        [Tile12() for _ in range(4)] +
        [Tile13() for _ in range(3)] +
        [Tile14() for _ in range(8)] +
        [Tile15() for _ in range(9)] +
        [Tile16() for _ in range(4)] +
        [Tile17() for _ in range(1)]
    )
    
    # Mezclar aleatoriamente las losas
    random.shuffle(losas)
    
    # Devolverlas como una lista (se puede usar como pila con .pop())
    return losas
from Assets import board
from Assets import tiles

import copy
import random

class GameStateData:
    """ 
    Cada GameState tiene información del tablero, el puntaje de los jugadores, las piezas restantes, el turno actual y la pieza al tope de la pila.
    """
    
    def __init__(self, prev_state: 'GameStateData' = None):
        if prev_state is not None:
            self.board = copy.deepcopy(prev_state.board)
            self.scores = prev_state.scores[:]
            self.turn = prev_state.turn
            self.tile_stack = prev_state.tile_stack[:]
            self.current_tile = prev_state.current_tile
        else:
            self.board = board.Board()
            self.scores = []
            self.turn = 0
            self.tile_stack = []
            self.current_tile = None

        
    def initialize(self, num_players: int, tile_stack: list):
        self.board = board.Board()
        self.scores = [0 for _ in range(num_players)]
        self.tile_stack = tile_stack[:]
        self.turn = 0
        self.current_tile = tile_stack[-1] if tile_stack else None

    
    
class GameState:
    """ 
    Maneja el estado actual del juego.
    """
    def __init__(self, prev_state: "GameState"= None):
        if prev_state is not None:
            self.data = GameStateData(prev_state.data)
        else:
            self.data = GameStateData()
    
    def initialize(self, num_players: int, tile_stack: list):
        """
        Inicializa el estado del juego con el número de jugadores y la pila de piezas dada. 
        """
        
        self.data.initialize(num_players, tile_stack)
    
    def getLegalActions(self, turn):
        """
        Devuelve las acciones legales para el jugador actual. Si no hat posiciones válidas 
        para colocar la pieza actual, devuelve "pass". Si no hay piezas restantes, devuelve "exit".
        """
        if self.tilesLeft() == 0:
            return "exit"
        
        legal = self.data.board.getLegalPlacements(self.data.current_tile)
        return legal if legal != [] else "pass"

    def generateSuccessor(self, turn, action):
        """ 
        Devuelve el estado sucesor después de que el jugador actual realice la acción dada. 
        La acción puede ser "pass" o una tupla ((x, y), orientation) para colocar la pieza en la posición (x, y) con la orientación dada.
        Si coloca una pieza se le otorgan puntos por losas colocadas y estructuras cerradas.
        """
        if action == "exit":
            raise Exception("EXIT")
        
        successor = GameState(self)
        
        if action == "pass":
            successor.data.turn = (successor.data.turn + 1) % len(successor.data.scores)
            return successor
        else:
            #breakpoint()
            pos, orientation = action
            tile = successor.data.current_tile
            tile.reset_orientation()
            rot_steps = (orientation // 90) % 4
            for _ in range(rot_steps):
                tile.rotate()
            successor.data.board.place_tile(tile, pos)
            
            successor.data.scores[turn] += 1
            
            old_roads = self.data.board.caminosCerrados
            new_roads = successor.data.board.caminosCerrados
            successor.data.scores[turn] += len(new_roads - old_roads) * 2 # 2 points per closed road 
            
            old_cities = self.data.board.ciudadesCerradas
            new_cities = successor.data.board.ciudadesCerradas
            successor.data.scores[turn] += len(new_cities - old_cities) * 4 # 4 points per closed city
            
            # Draw next tile
            successor.data.tile_stack.pop()
            successor.data.current_tile = successor.data.tile_stack[-1] if successor.data.tile_stack else None
            
            # Next turn
            successor.data.turn = (successor.data.turn + 1) % len(successor.data.scores)
            #print(f"Turn changed to {successor.data.turn}")
            
            return successor
    
    def getScore(self):
        """
        Devuelve el puntaje calculado por la configuración actual del tablero.
        """
        return self.data.board.calculateScore()
    
    def tilesLeft(self):
        return len(self.data.tile_stack)
    
    def getNumAgents(self):
        return len(self.data.scores)


class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:
    """

    def __init__(self, turn=0):
        self.turn = turn

    def getAction(self, state):
        pass
    

class PlayerAgent(Agent):
    """ 
    Agente para la simulación.
    """
    def __init__(self, turn=0):
        self.turn = turn

    def getAction(self, state: GameState):
        """
        The Agent will receive a GameState and return an action (pass or place tile at x,y with orientation)
        """
        legal = state.getLegalActions(self.turn)
        print(legal)
        ans = input("Enter your action (pass or x y orientation): ")
        if ans.strip().lower() == "pass":
            return "pass"
        else:
            x, y, orientation = map(int, ans.strip().split())
            
            if ((x,y), orientation) in legal:
                return ((x, y), orientation)
            else:
                print("Illegal action. Passing instead.")
                return "pass"

class RandomAgent(Agent):
    """ 
    Agente que elige acciones aleatorias.
    """
    def __init__(self, turn=0):
        self.turn = turn
        
    def getAction(self, state: GameState):
        legal = state.getLegalActions(self.turn)

        if legal == []:
            return "pass"
        else:
            return random.choice(legal)


def scoreEvaluationFunction(currentGameState: GameState):
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    
    def __init__(self, turn, evalFn = 'scoreEvaluationFunction', depth = '1'):
        self.turn = turn
        self.evaluationFunction = scoreEvaluationFunction
        self.depth = int(depth)

class ExpectimaxAgent(MultiAgentSearchAgent):
    
    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction
        """
        def exp_value(gameState: GameState, turn, depth):
            num_agents = gameState.getNumAgents()
            next_turn = (turn + 1) % num_agents 
            
            actions = gameState.getLegalActions(turn)
            v = 0
            for action in actions:     
                if next_turn == 0:
                    v +=  value(gameState.generateSuccessor(turn, action), 0, depth + 1)
                else:
                    v +=  value(gameState.generateSuccessor(turn, action), next_turn, depth)
            v /= len(actions) # Devolvemos el promedio
            return v

        def max_value(gameState: GameState, turn, depth):
            actions = gameState.getLegalActions(turn)
            v = -1e9
            for action in actions:
                v = max(v, value(gameState.generateSuccessor(turn, action), 1, depth))
            return v
        
        def value(gameState: GameState, turn, depth):
            if gameState.tilesLeft() == 0 or depth == self.depth:
                return self.evaluationFunction(gameState)

            if turn == 0:
                return max_value(gameState, turn, depth)
            else:
                return exp_value(gameState, turn, depth)

        
        ans = None
        best_val = -1e9
        
        for action in gameState.getLegalActions(0):
            suc = gameState.generateSuccessor(0, action)
            val = value(suc, 1, 0)
            if val > best_val:
                best_val = val
                ans = action

        return ans
    
class CarcassonneGame:
    """ 
    El juego tiene un tablero, una pila de piezas, un número de jugadores, el estado del juego y los agentes que juegan.
    """
    def __init__(self, num_players = 2, player_agent = PlayerAgent(0)):
        self.board = board.Board()
        self.tile_stack = tiles.revolverLosas()
        self.num_players = num_players
        self.data = GameState()
        self.data.initialize(num_players, self.tile_stack)
        self.agents = [player_agent] + [ExpectimaxAgent(turn=i) for i in range(1, num_players)]
        
    def isOver(self):
        return self.data.tilesLeft() == 0
    
    def getWinner(self):
        scores = self.data.data.scores
        max_score = max(scores)
        winners = [i for i, score in enumerate(scores) if score == max_score]
        return winners, max_score
    
    def playTurn(self, turn, action):
        self.data = self.data.generateSuccessor(turn, action) # actualizar el estado del juego

    
        
if __name__ == "__main__":
    # game = CarcassonneGame(num_players=2)
    # print(game.data.data.board.grid, game.data.data.scores, game.data.data.turn, game.data.data.current_tile)
    # player = game.agents[0]
    # possible_actions = game.data.getLegalActions(0)
    # print("Possible actions for player 0:", possible_actions)
    # game.data = game.data.generateSuccessor(0, possible_actions[0])
    # print(game.data.data.board.grid, game.data.data.scores, game.data.data.turn, game.data.data.current_tile)
    
    # ai = game.agents[1]
    # possible_actions = game.data.getLegalActions(1)
    # print("Possible actions for player 1:", possible_actions)
    # game.data = game.data.generateSuccessor(1, possible_actions[0])
    # print(game.data.data.board.grid, game.data.data.scores, game.data.data.turn, game.data.data.current_tile)
    
    game = CarcassonneGame(num_players=2, player_agent=RandomAgent(0))
    while not game.isOver():
        current_turn = game.data.data.turn
        agent = game.agents[current_turn]
        action = agent.getAction(game.data)
        print(f"Player {current_turn} chose action: {action}")
        game.playTurn(current_turn, action)
        print(f"Scores: {game.data.data.scores}")
    winners, score = game.getWinner()
    print(f"\n Game over! Winner(s): {winners} with {score} points.")
    

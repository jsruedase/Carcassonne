import sys, os
import copy

from Assets import board
from Assets import tiles


class GameStateData:
    
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
    """ Maneja el estado actual del juego. """
    def __init__(self, prev_state: "GameState" = None):
        if prev_state is not None:
            self.data = GameStateData(prev_state.data)
        else:
            self.data = GameStateData()
    
    def initialize(self, num_players: int, tile_stack: list):
        self.data.initialize(num_players, tile_stack)
    
    def getLegalActions(self, turn):
        if self.tilesLeft() == 0:
            return "exit"
        
        legal = self.data.board.getLegalPlacements(self.data.current_tile)
        return legal if legal != [] else ["pass"]

    def generateSuccessor(self, turn, action):
        if action == "exit":
            raise Exception("EXIT")
        
        successor = GameState(self)
        
        if action == "pass":
            successor.data.turn = (successor.data.turn + 1) % len(successor.data.scores)
            return successor
        else:
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
            successor.data.scores[turn] += len(new_roads - old_roads) * 2
            
            old_cities = self.data.board.ciudadesCerradas
            new_cities = successor.data.board.ciudadesCerradas
            successor.data.scores[turn] += len(new_cities - old_cities) * 4
            
            # Saca la siguiente losa
            successor.data.tile_stack.pop()
            successor.data.current_tile = successor.data.tile_stack[-1] if successor.data.tile_stack else None
            
            # Cambia turno
            successor.data.turn = (successor.data.turn + 1) % len(successor.data.scores)
            
            return successor
    
    def getScore(self):
        return self.data.board.calculateScore()
    
    def tilesLeft(self):
        return len(self.data.tile_stack)
    
    def getNumAgents(self):
        return len(self.data.scores)


class Agent:
    """ Clase base para todos los agentes. """
    def __init__(self, turn=0):
        self.turn = turn

    def getAction(self, state):
        pass


def scoreEvaluationFunction(currentGameState: GameState):
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    
    def __init__(self, turn, evalFn='scoreEvaluationFunction', depth='1'):
        self.turn = turn
        self.evaluationFunction = scoreEvaluationFunction
        self.depth = int(depth)


class ExpectimaxAgent(MultiAgentSearchAgent):

    def getAction(self, gameState: GameState):

        def exp_value(gameState: GameState, turn, depth):
            num_agents = gameState.getNumAgents()
            next_turn = (turn + 1) % num_agents 
            actions = gameState.getLegalActions(turn)

            if actions == [] or actions == "exit":
                return self.evaluationFunction(gameState)

            v = 0
            for action in actions:     
                if next_turn == self.turn:
                    v += value(gameState.generateSuccessor(turn, action), self.turn, depth + 1)
                else:
                    v += value(gameState.generateSuccessor(turn, action), next_turn, depth)
            v /= len(actions)
            return v

        def max_value(gameState: GameState, turn, depth):
            actions = gameState.getLegalActions(turn)
            if actions == [] or actions == "exit":
                return self.evaluationFunction(gameState)
            
            v = -1e9
            for action in actions:
                next_turn = (turn + 1) % gameState.getNumAgents()
                v = max(v, value(gameState.generateSuccessor(turn, action), next_turn, depth))
            return v
        
        def value(gameState: GameState, turn, depth):
            if gameState.tilesLeft() == 0 or depth == self.depth:
                return self.evaluationFunction(gameState)

            if turn == self.turn:
                return max_value(gameState, turn, depth)
            else:
                return exp_value(gameState, turn, depth)

        ans = None
        best_val = -1e9
        
        for action in gameState.getLegalActions(self.turn):
            suc = gameState.generateSuccessor(self.turn, action)
            next_turn = (self.turn + 1) % gameState.getNumAgents()
            val = value(suc, next_turn, 0)
            if val > best_val:
                best_val = val
                ans = action

        return ans


class CarcassonneGame:
    def __init__(self, num_players=2):
        self.board = board.Board()
        self.tile_stack = tiles.revolverLosas()
        self.num_players = num_players
        self.data = GameState()
        self.data.initialize(num_players, self.tile_stack)
        # Ambos agentes son Expectimax
        self.agents = [ExpectimaxAgent(turn=i) for i in range(num_players)]
        
    def isOver(self):
        return self.data.tilesLeft() == 0
    
    def getWinner(self):
        scores = self.data.data.scores
        max_score = max(scores)
        winners = [i for i, score in enumerate(scores) if score == max_score]
        return winners, max_score
    
    def playTurn(self, turn, action):
        self.data = self.data.generateSuccessor(turn, action)


if __name__ == "__main__":
    game = CarcassonneGame(num_players=2)
    while not game.isOver():
        current_turn = game.data.data.turn
        agent = game.agents[current_turn]
        action = agent.getAction(game.data)
        print(f"Player {current_turn} chose action: {action}")
        game.playTurn(current_turn, action)
        print(f"Scores: {game.data.data.scores}")
    
    winners, score = game.getWinner()
    print(f"\n Game over! Winner(s): {winners} with {score} points.")

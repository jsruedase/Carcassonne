import pygame
import sys
import os
import time
from Assets import board as bd
from Assets import tiles
from Game import carcassone

# ----------------------- Pygame config (idéntico al original) -----------------------
TILE_PIX = 100
FPS = 60
SCREEN_W = 1200
SCREEN_H = 800
IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), "images")
from pathlib import Path
IMAGES_FOLDER = Path(__file__).resolve().parent.parent / "Assets" / "images"


def draw_wrapped_text(surface, text, font, color, x, y, max_width, line_height):
	words = text.split(' ')
	lines = []
	current_line = ""
	for word in words:
		test_line = current_line + word + " "
		if font.size(test_line)[0] <= max_width:
			current_line = test_line
		else:
			lines.append(current_line.strip())
			current_line = word + " "
	if current_line:
		lines.append(current_line.strip())
	for i, line in enumerate(lines):
		txt_surf = font.render(line, True, color)
		surface.blit(txt_surf, (x, y + i * line_height))


def load_tile_images():
    images = {}
    for i in range(1, 18):
        fname = os.path.join(IMAGES_FOLDER, f"tile{i}.png")
        if os.path.exists(fname):
            try:
                surf = pygame.image.load(fname).convert_alpha()
                images[i] = surf
            except Exception:
                images[i] = None
        else:
            images[i] = None
    return images

def tile_index(tile: 'Tile'):
    name = type(tile).__name__
    if name.startswith("Tile"):
        try:
            return int(name[4:])
        except Exception:
            return None
    return None

def draw_tile(surface, tile: 'Tile', img_map, topleft, cell_size):
    idx = tile_index(tile)
    if idx is None:
        return
    img = img_map.get(idx, None)
    if img is None:
        r = pygame.Rect(topleft, (cell_size, cell_size))
        pygame.draw.rect(surface, (200,200,200), r)
        pygame.draw.rect(surface, (0,0,0), r, 2)
        return
    rotated = pygame.transform.rotate(img, tile.orientation)
    rotated = pygame.transform.smoothscale(rotated, (cell_size, cell_size))
    rect = rotated.get_rect(topleft=topleft)
    surface.blit(rotated, rect.topleft)

def grid_to_pixel(grid_x, grid_y, center_pixel, cell_size):
    cx, cy = center_pixel
    px = cx + grid_x * cell_size
    py = cy - grid_y * cell_size
    return (px - cell_size // 2, py - cell_size // 2)

def pixel_to_grid(px, py, center_pixel, cell_size):
    cx, cy = center_pixel
    gx = round((px - cx) / cell_size)
    gy = round((cy - py) / cell_size)
    return gx, gy

class MessageFeed:
    def __init__(self, max_len=6):
        self.max_len = max_len
        self.items = []

    def push(self, text):
        self.items.insert(0, text)
        if len(self.items) > self.max_len:
            self.items.pop()

    def draw(self, surf, x, y, font):
        for i, t in enumerate(self.items):
            txt = font.render(t, True, (0,0,0))
            surf.blit(txt, (x, y + i * 22))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Carcassonne básico")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    big_font = pygame.font.SysFont(None, 30)

    images = load_tile_images()
    
    game = carcassone.CarcassonneGame(num_players=2)
    board = game.data.data.board
    deck = game.data.data.tile_stack
    current_tile = game.data.data.current_tile

    feed = MessageFeed()
    announcement = ""  # mensaje temporal en pantalla
    announcement_timer = 0

    center_pixel = [SCREEN_W // 2 - 200, SCREEN_H // 2]
    cell_size = TILE_PIX
    zoom_speed = 0.1
    pan_speed = 30
    dragging = False

    running = game.isOver() == False
    while running:
        if game.data.data.turn == 0:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                        
                    elif ev.key == pygame.K_r:
                        if current_tile:
                            current_tile.rotate()
                            
                    elif ev.key == pygame.K_SPACE:
                        print(board.calculateScore())
                        print(game.data.data.scores)
                        
                    elif ev.key == pygame.K_n:
                        game.playTurn(0, "pass")
                        board = game.data.data.board
                        deck = game.data.data.tile_stack
                        current_tile = game.data.data.current_tile
                        
                    elif ev.key in (pygame.K_EQUALS, pygame.K_PLUS):
                        cell_size = int(cell_size * (1 + zoom_speed))
                        
                    elif ev.key == pygame.K_MINUS:
                        cell_size = int(cell_size * (1 - zoom_speed))
                        if cell_size < 20:
                            cell_size = 20
                            
                    elif ev.key in (pygame.K_LEFT, pygame.K_a):
                        center_pixel[0] += pan_speed
                        
                    elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                        center_pixel[0] -= pan_speed
                        
                    elif ev.key in (pygame.K_UP, pygame.K_w):
                        center_pixel[1] += pan_speed
                        
                    elif ev.key in (pygame.K_DOWN, pygame.K_s):
                        center_pixel[1] -= pan_speed

                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        mx, my = ev.pos
                        gx, gy = pixel_to_grid(mx, my, center_pixel, cell_size)
                        
                        if current_tile and board.can_place_tile(current_tile, (gx, gy)):
                            feed.push(f"Colocada {type(current_tile).__name__} en {gx,gy}")
                            
                            game.playTurn(0, ((gx, gy), current_tile.orientation))
                            
                            board = game.data.data.board
                            deck = game.data.data.tile_stack
                            current_tile = game.data.data.current_tile

                            cerrado, visitados, longitud = board.verificar_camino_cerrado((gx, gy))
                            if cerrado:
                                announcement = f"¡Camino cerrado! Longitud: {longitud}"
                                announcement_timer = 120
                                feed.push(f"Camino cerrado detectado (longitud={longitud})")



                            cerrada, visitados, tamaño = board.verificar_castillo_cerrado((gx, gy))
                            if cerrada:
                                announcement = f"¡Ciudad cerrada! Tamaño: {tamaño}"
                                announcement_timer = 120  
                                feed.push(f"Ciudad cerrada detectada (tamaño={tamaño})")



                            #current_tile = deck.pop() if deck else None
                        else:
                            feed.push("Movimiento inválido")
                    elif ev.button == 3:
                        dragging = True
                        drag_origin = ev.pos
                    elif ev.button == 4:
                        cell_size = int(cell_size * (1 + zoom_speed))
                    elif ev.button == 5:
                        cell_size = int(cell_size * (1 - zoom_speed))
                        if cell_size < 20:
                            cell_size = 20
                elif ev.type == pygame.MOUSEBUTTONUP:
                    if ev.button == 3:
                        dragging = False
                elif ev.type == pygame.MOUSEMOTION and dragging:
                    dx, dy = ev.rel
                    center_pixel[0] += dx
                    center_pixel[1] += dy

            screen.fill((180, 210, 180))

            # Dibujar tablero
            if board.grid:
                xs = [p[0] for p in board.grid.keys()]
                ys = [p[1] for p in board.grid.keys()]
                minx, maxx = min(xs)-3, max(xs)+3
                miny, maxy = min(ys)-3, max(ys)+3
            else:
                minx, maxx, miny, maxy = -5, 5, -5, 5

            for gx in range(minx, maxx+1):
                for gy in range(miny, maxy+1):
                    px, py = grid_to_pixel(gx, gy, center_pixel, cell_size)
                    rect = pygame.Rect(px, py, cell_size, cell_size)
                    pygame.draw.rect(screen, (210,210,210), rect)
                    pygame.draw.rect(screen, (50,50,50), rect, 1)

            for pos, losa in board.grid.items():
                gx, gy = pos
                px, py = grid_to_pixel(gx, gy, center_pixel, cell_size)
                draw_tile(screen, losa, images, (px, py), cell_size)

            # Panel lateral derecho
            ui_x = SCREEN_W - 260
            ui_y = 40
            pygame.draw.rect(screen, (230,230,230), (ui_x-10, ui_y-10, 240, 700))

			# Mostrar turno actual y puntajes
            turn_text = big_font.render(f"Jugador actual: {game.data.data.turn}", True, (0, 0, 0))
            screen.blit(turn_text, (ui_x + 10, ui_y+230))

            scores = game.data.data.scores
            for i, score in enumerate(scores):
                color = (0, 100, 200) if i == game.data.data.turn else (0, 0, 0)
                score_text = font.render(f"Jugador {i}: {score} pts", True, color)
                screen.blit(score_text, (ui_x + 10, ui_y + 270 + i * 25))


            # Losa actual
            if current_tile:
                draw_tile(screen, current_tile, images, (ui_x+40, ui_y+30), TILE_PIX)

            # Anuncio simple
            # 
            if announcement:
                draw_wrapped_text(screen,announcement, big_font,(200, 50, 50),ui_x + 30, ui_y + 160,max_width=200,line_height=25 )

            # Instrucciones
            instrucciones = [
                "Controles:",
                "R - Rotar losa",
                "N - Nueva losa",
                "Click - Colocar",
                "Click der - Mover vista",
                "Rueda / +/- - Zoom",
                "WASD / Flechas - Mover",
                "ESC - Salir"
            ]
            for i, line in enumerate(instrucciones):
                txt = font.render(line, True, (0, 0, 0))
                screen.blit(txt, (ui_x+10, ui_y+340 + i * 22))

            # Feed de mensajes
            feed.draw(screen, ui_x+10, ui_y + 550, font)

            # Actualizar temporizador del anuncio
            if announcement_timer > 0:
                announcement_timer -= 1
            else:
                announcement = ""

            pygame.display.flip()
            clock.tick(FPS)
        else:
            time.sleep(1)  # pequeña pausa para no saturar la CPU
            if len(deck) == 0:
                running = False
                break
            current_turn = game.data.data.turn
            agent = game.agents[current_turn]
            action = agent.getAction(game.data)
            game.playTurn(current_turn, action)
            board = game.data.data.board
            deck = game.data.data.tile_stack
            current_tile = game.data.data.current_tile

    winners, score = game.getWinner()
    print(f"\n Game over! Winner(s): {winners} with {score} points.")
    
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()

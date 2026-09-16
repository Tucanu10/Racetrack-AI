import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import shutil
import pygame
import engine.game as game
import engine.debug as debug
import map0.checkpoints as checkpoints
import communication.serversocket as serversocket
import ai.raycasting as raycasting

pygame.init()
screen = pygame.display.set_mode((1080, 720))
clock = pygame.time.Clock()
running = True
dt = 0
debug_font = pygame.font.SysFont(None, 28)
show_debug = False
POP_SIZE = 100
epoch = 1

track_map = game.Track("src/map0/map.png")
ai = serversocket.AICLient(host='localhost', port=8080)

import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="web", **kwargs)

    def do_GET(self):
        if self.path == '/save':
            ai.sock.sendall("SAVE\n".encode('utf-8'))
            self.send_response(200)
            self.end_headers()
        elif self.path == '/load':
            ai.sock.sendall("LOAD\n".encode('utf-8'))
            self.send_response(200)
            self.end_headers()
        else:
            super().do_GET()

# The dashboard's HTTP server only serves files out of web/, and index.html
# was pointing at '../map0/map.png' which resolves outside that directory -
# the request just 404s. Copy the track image into web/assets/ once at
# startup so it's actually reachable.
os.makedirs("web/assets", exist_ok=True)
shutil.copy("src/map0/map.png", "web/assets/map.png")

threading.Thread(target=lambda: HTTPServer(('localhost', 8000), DashboardHandler).serve_forever(), daemon=True).start()

def spawn_population(size):
    cars = []
    for _ in range(size):
        c = game.Player("images/car.png", 83, 325)
        c.alive = True
        c.fitness = 0.0
        c.current_lap_time = 0.0
        cars.append(c)
    return cars

cars = spawn_population(POP_SIZE)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                show_debug = not show_debug
            if event.key == pygame.K_s:
                print("Saving champion network...")
                ai.sock.sendall("SAVE\n".encode('utf-8'))

    screen.fill((48, 51, 53))
    screen.blit(track_map.image, (0, 0))

    # Filter out dead cars
    active_indices = [i for i, c in enumerate(cars) if c.alive]

    # End of epoch if all cars are dead
    if not active_indices:
        scores = [c.fitness for c in cars]
        ai.send_epoch_end(scores)
        epoch += 1
        cars = spawn_population(POP_SIZE)
        continue

    batch_payload_parts = []
    car_hitpoints = {}

    for idx in active_indices:
        car = cars[idx]
        distances, hits = raycasting.get_data(car, track_map.mask, 250)
        car_hitpoints[idx] = hits
        norm_dists = [f"{d / 250.0:.4f}" for d in distances]
        batch_payload_parts.append(f"{idx}:{','.join(norm_dists)}")

    commands = ai.get_batch_commands("|".join(batch_payload_parts))

    lead_dashboard_updated = False # Ensure we only update JSON once per frame

    for idx in active_indices:
        car = cars[idx]
        if idx in commands:
            st, th, hidden = commands[idx]
            actual_steering = (st * 2) - 1
            car.rotate(actual_steering * 300 * dt)
            speed = th * 200

            car.current_lap_time += dt
            car.time_since_last_checkpoint += dt # Increment the new timer
            
            crashed = car.move(speed, dt, track_map)
            laps = car.check_checkpoints(checkpoints.checkpoints)
            
            if laps > 0:
                car.laps += int(laps)

            # Kill car if it crashes OR takes more than 5 seconds to reach the next checkpoint
            if crashed or car.time_since_last_checkpoint > 5.0:
                car.alive = False
                
                # Subtract time to penalize slowness instead of rewarding it
                car.fitness = (car.current_checkpoint * 100) + (car.laps * 1000) - (car.current_lap_time * 2)

            # Update the web dashboard with the lead car's brain
            if not lead_dashboard_updated:
                distances, _ = raycasting.get_data(car, track_map.mask, 250)
                lead_inputs = [d / 250.0 for d in distances]
                
                network_state = {
                    "inputs": lead_inputs,
                    "hidden": hidden,  # list of hidden layers, each a list of activations
                    "outputs": [st, th],
                    "stats": {
                        "epoch": epoch,
                        "time": round(car.current_lap_time, 2),
                        "checkpoint": car.current_checkpoint,
                        "laps": car.laps
                    },
                    "pos": {
                        "x": car.pos_x,
                        "y": car.pos_y,
                        "angle": car.angle
                    }
                }
                with open("web/state.json", "w") as f:
                    json.dump(network_state, f)
                lead_dashboard_updated = True

        screen.blit(car.image, car.rect.topleft)

    if show_debug:
        debug.draw_fps(screen, clock, debug_font)
        
        # Only draw UI lines for the lead car to prevent clutter
        if active_indices:
            lead_idx = active_indices[0]
            lead_car = cars[lead_idx]
            debug.draw_pos_info(screen, lead_car, debug_font)
            debug.draw_rays(screen, lead_car, car_hitpoints[lead_idx])

        for checkpoint in checkpoints.checkpoints:
            pygame.draw.rect(screen, (0, 255, 0), checkpoint, 2) 

    pygame.display.flip()
    dt = clock.tick(20) / 1000 

ai.close()
pygame.quit()
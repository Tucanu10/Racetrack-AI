import sys
import os
import json
import importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
import engine.game as game
import engine.debug as debug
import communication.serversocket as serversocket
import ai.raycasting as raycasting
import math
import time
import config

# Dynamically load the active map's checkpoints and image
checkpoints = importlib.import_module(f"{config.ACTIVE_MAP}.checkpoints")
MAP_IMAGE_PATH = f"src/{config.ACTIVE_MAP}/map.png"

pygame.init()
screen = pygame.display.set_mode((1080, 720))
clock = pygame.time.Clock()
running = True
dt = 0
debug_font = pygame.font.SysFont(None, 28)
show_debug = False
POP_SIZE = 200
epoch = 1
RESET_SIGNAL = "web/reset.signal"

# Pre-load and scale sprites to prevent memory leaks during the loop
img_normal = pygame.transform.scale(pygame.image.load("images/car.png").convert_alpha(), (40, 40))
img_best = pygame.transform.scale(pygame.image.load("images/car_best.png").convert_alpha(), (40, 40))
img_worst = pygame.transform.scale(pygame.image.load("images/car_worst.png").convert_alpha(), (40, 40))

track_map = game.Track(MAP_IMAGE_PATH)
ai = serversocket.AICLient(host='localhost', port=8081)

# Fetch custom start pos if defined in checkpoints.py, otherwise default to (83, 325)
START_X, START_Y = getattr(checkpoints, 'START_POS', (0, 0))

def spawn_population(size):
    cars = []
    for _ in range(size):
        c = game.Player("images/car.png", START_X, START_Y)
        c.alive = True
        c.fitness = 0.0
        c.current_lap_time = 0.0
        cars.append(c)
    return cars

cars = spawn_population(POP_SIZE)

if 'prev_steppings' not in globals():
    prev_steppings = {}

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                show_debug = not show_debug
            if event.key == pygame.K_s:
                print("Saving champion network...")
                ai.send_command("SAVE")
            if event.key == pygame.K_l:
                print("Loading champion network...")
                ai.send_command("LOAD")
            if event.key == pygame.K_r:
                print("Resetting population...")
                ai.send_command("RESET")
                cars = spawn_population(POP_SIZE)
                epoch = 1
                continue

    # Check for web-dashboard-triggered reset
    if os.path.exists(RESET_SIGNAL):
        try:
            os.remove(RESET_SIGNAL)
        except OSError:
            pass
        epoch = 1
        cars = spawn_population(POP_SIZE)
        prev_steppings.clear()

    screen.fill((48, 51, 53))
    screen.blit(track_map.image, (0, 0))

    # Filter out dead cars and sort them by fitness (best first)
    active_indices = [i for i, c in enumerate(cars) if c.alive]
    active_indices.sort(key=lambda i: cars[i].fitness, reverse=True)

    # Assign sprites based on performance rank
    for rank, idx in enumerate(active_indices):
        if rank == 0:
            target_img = img_best
        elif rank == len(active_indices) - 1 and len(active_indices) > 1:
            target_img = img_worst
        else:
            target_img = img_normal
            
        # Only trigger an update if the sprite needs to change
        if cars[idx].original_image is not target_img:
            cars[idx].original_image = target_img
            cars[idx].rotate(0) # Forces Pygame to re-render the image and collision mask

    # End of epoch if all cars are dead
    if not active_indices:
        scores = [c.fitness for c in cars]
        ai.send_epoch_end(scores)
        epoch += 1
        cars = spawn_population(POP_SIZE)
        
        init_state = {
            "inputs": [0]*9,
            "hidden": [],
            "outputs": [0, 0],
            "stats": {"epoch": epoch, "time": 0.0, "checkpoint": 0, "laps": 0, "alive_cars": POP_SIZE, "pop_size": POP_SIZE},
            "pos": {"x": START_X, "y": START_Y, "angle": 0},
            "others": []
        }
        temp_path = "web/state.json.tmp"
        target_path = "web/state.json"
        
        with open(temp_path, "w") as f:
            json.dump(init_state, f)
            
        for _ in range(5):
            try:
                os.replace(temp_path, target_path)
                break
            except PermissionError:
                time.sleep(0.01)
        continue

    batch_payload_parts = []
    car_hitpoints = {}

    for idx in active_indices:
        car = cars[idx]
        distances, hits = raycasting.get_data(car, track_map.mask, 2000)
        car_hitpoints[idx] = hits
        
        current_speed = getattr(car, 'current_speed', 0.0)
        speed_norm = current_speed / 200.0

        target_rect = checkpoints.checkpoints[car.current_checkpoint]
        target_center = (target_rect.centerx, target_rect.centery)
        angle_to_target = math.degrees(math.atan2(target_center[1] - car.pos_y, target_center[0] - car.pos_x))
        angle_diff = (car.angle - angle_to_target + 180) % 360 - 180
        angle_norm = angle_diff / 180.0

        norm_dists = [f"{d / 250.0:.4f}" for d in distances] + [f"{speed_norm:.4f}", f"{angle_norm:.4f}"]
        batch_payload_parts.append(f"{idx}:{','.join(norm_dists)}")

    commands = ai.get_batch_commands("|".join(batch_payload_parts))

    lead_dashboard_updated = False

    # Iterate backwards so the best cars are drawn last (on top)
    for idx in reversed(active_indices):
        car = cars[idx]
        if idx in commands:
            st, th, hidden = commands[idx]
            actual_steering = (st * 2) - 1
            
            prev_st = prev_steppings.get(idx, actual_steering)
            steering_jitter = abs(actual_steering - prev_st)
            prev_steppings[idx] = actual_steering

            car.rotate(actual_steering * 300 * dt)
            speed = th * 200
            car.current_speed = speed

            car.current_lap_time += dt
            car.time_since_last_checkpoint += dt
            
            crashed = car.move(speed, dt, track_map)
            laps = car.check_checkpoints(checkpoints.checkpoints)
            
            if laps > 0:
                car.laps += int(laps)
                car.current_lap_time = 0.0

            target_rect = checkpoints.checkpoints[car.current_checkpoint]
            target_center = (target_rect.centerx, target_rect.centery)
            dist_to_target = math.hypot(car.pos_x - target_center[0], car.pos_y - target_center[1])

            car.fitness = (car.current_checkpoint * 300) + (car.laps * 3000) - (dist_to_target * 0.05) - (car.current_lap_time * 2) - (steering_jitter * 15)
            if th < 0.2:
                car.fitness -= dt * 20

            if crashed or car.time_since_last_checkpoint > 4.0:
                car.alive = False

            # Update the web dashboard ONLY for the true lead car
            if not lead_dashboard_updated and idx == active_indices[0]:
                distances, _ = raycasting.get_data(car, track_map.mask, 2000)
                speed_norm = speed / 200.0
                angle_diff = (car.angle - angle_to_target + 180) % 360 - 180
                angle_norm = angle_diff / 180.0
                
                lead_inputs = [d / 250.0 for d in distances] + [speed_norm, angle_norm]
                
                # Gather positions of the rest of the pack
                other_cars_data = []
                for rank, other_idx in enumerate(active_indices):
                    if rank == 0: 
                        continue # Skip the lead car
                    
                    other_car = cars[other_idx]
                    other_cars_data.append({
                        "x": other_car.pos_x,
                        "y": other_car.pos_y,
                        "angle": other_car.angle,
                        "is_worst": (rank == len(active_indices) - 1 and len(active_indices) > 1)
                    })

                network_state = {
                    "inputs": lead_inputs,
                    "hidden": hidden,  
                    "outputs": [st, th],
                    "stats": {
                        "epoch": epoch,
                        "time": round(car.current_lap_time, 2),
                        "checkpoint": car.current_checkpoint,
                        "laps": car.laps,
                        "alive_cars": len(active_indices),
                        "pop_size": POP_SIZE
                    },
                    "pos": {
                        "x": car.pos_x,
                        "y": car.pos_y,
                        "angle": car.angle
                    },
                    "others": other_cars_data
                }
                
                temp_path = "web/state.json.tmp"
                target_path = "web/state.json"
                
                with open(temp_path, "w") as f:
                    json.dump(network_state, f)
                
                for _ in range(5):
                    try:
                        os.replace(temp_path, target_path)
                        break
                    except PermissionError:
                        time.sleep(0.01)
                
                lead_dashboard_updated = True

        screen.blit(car.image, car.rect.topleft)

    if show_debug:
        debug.draw_fps(screen, clock, debug_font)
        
        if active_indices:
            lead_idx = active_indices[0]
            lead_car = cars[lead_idx]
            debug.draw_pos_info(screen, lead_car, debug_font)
            debug.draw_population_info(screen, cars, debug_font)
            debug.draw_rays(screen, lead_car, car_hitpoints[lead_idx])

        for checkpoint in checkpoints.checkpoints:
            pygame.draw.rect(screen, (0, 255, 0), checkpoint, 2) 

    pygame.display.flip()
    dt = clock.tick(100) / 1000 

ai.close()
pygame.quit()
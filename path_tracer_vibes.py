# path_tracer.py
import math
import random
import pygame
from utilities import intersect  # uses your utilities.py intersect()

pygame.init()  # <- actually initialize

WIDTH, HEIGHT = 800, 1000
LENGTH = 150
WALL_LENGTH = 10
LOOPS = 50  # "do this 20 times" (tweak as you like)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Start at center
center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
path = [center]

# Each wall is stored as a pair of endpoints: (C, D)
walls: list[tuple[pygame.math.Vector2, pygame.math.Vector2]] = []

def inbound(v):
    if v.x>0 and v.x<WIDTH and v.y>0 and v.y<HEIGHT:
        return True
    else:
        return False
    
def unit(v: pygame.math.Vector2) -> pygame.math.Vector2:
    if v.length() == 0:
        return v
    return v.normalize()


previous_angle = 0

def build_wall(prev_pt, pivot_pt, next_pt):
    u = pivot_pt - prev_pt
    v = next_pt - pivot_pt
    if u.length() == 0 or v.length() == 0:
        return None

    u = u.normalize()
    v = v.normalize()

    # Angle bisector
    b = u + v

    if b.length() < 1e-6:
        # 180° turn: use a perpendicular to the incoming direction
        wdir = pygame.math.Vector2(-u.y, u.x)
    else:
        # PERPENDICULAR to the bisector
        # Option A (explicit perp):
        # wdir = pygame.math.Vector2(-b.y, b.x)
        # Option B (rotate 90°):
        wdir = b.rotate(0)  # degrees

    wdir = wdir.normalize()
    C = pivot_pt + wdir * WALL_LENGTH
    D = pivot_pt - wdir * WALL_LENGTH
    return (C, D)



for _ in range(LOOPS):
    # Keep sampling random directions until the step doesn't hit any wall
    attempts = 0
    while True:
        attempts += 1
        angle = previous_angle + random.uniform(0.5, 1.5 * math.pi)  # radians
        origin = path[-1]
        candidate = pygame.math.Vector2(
            origin.x + LENGTH * math.cos(angle),
            origin.y + LENGTH * math.sin(angle)
        )
        # Check if the candidate is inbound
        if inbound(candidate): 
            # Check against all existing walls
            hits_wall = False
            for C, D in walls:
                if intersect(origin, candidate, C, D):
                    hits_wall = True
                    break

            if not hits_wall:
                # Add a wall at the bend (needs at least 2 prior points)
                if len(path)==1:
                    path.append(candidate)
                    previous_angle = angle
                    break
                else:
                    prev_pt = path[-2]
                    pivot_pt = origin  # bend is at current end before we step
                    wall = build_wall(prev_pt, pivot_pt, candidate)
                    
                    wall_hits_path = True
                    for x in range(len(path)):
                        wall_hits_path = intersect(wall[0], wall[1], path[x-1], path[x])
                        if wall_hits_path:
                            break
                        
                    walls.append(wall)
                    path.append(candidate)
                    previous_angle = angle
                    break

            # Safety valve to avoid infinite loops if boxed in
            if attempts > 2000:
                # Give up on this step
                break


# --- draw loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")

    # Draw path
    if len(path) >= 2:
        colors = ["red", "blue", "green", "orange", "purple"]
        mycolor = random.choice(colors)
        pygame.draw.lines(screen, mycolor, False, path)

    # Draw walls
    for C, D in walls:
        pygame.draw.line(screen, "black", C, D)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

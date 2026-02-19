import pygame
import sys
import math
import random
import time

pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Project")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

# Colors
SUN_COLOR     = (255, 165, 0)
MERCURY_COLOR = (169, 169, 169)
VENUS_COLOR   = (218, 165, 32)
EARTH_COLOR   = (0, 102, 204)
MARS_COLOR    = (255, 69, 0)
JUPITER_COLOR = (205, 133, 63)
SATURN_COLOR  = (222, 184, 135)
URANUS_COLOR  = (72, 209, 204)
NEPTUNE_COLOR = (0, 0, 139)
ASTEROID_COLOR = (169,169,169)

font = pygame.font.SysFont("Arial", 22, bold=True)

# Details order (serial facts)
details_order = [
    ("sun", "Sun: Surface ~5500°C"),
    ("mercury", "Mercury: Smallest planet"),
    ("venus", "Venus: Hottest planet"),
    ("earth", "Earth: Your home planet"),
    ("mars", "Mars: Red planet"),
    ("jupiter", "Jupiter: Largest planet"),
    ("saturn", "Saturn: Has rings"),
    ("uranus", "Uranus: Rotates sideways"),
    ("neptune", "Neptune: Farthest planet"),
    ("asteroid", "Asteroid Belt: Between Mars & Jupiter"),
    ("system", "Your Solar System")
]
current_detail_index = -1  # start with no detail shown

def draw_ellipse(xc, yc, rx, ry, color=WHITE):
    rect = pygame.Rect(xc-rx, yc-ry, 2*rx, 2*ry)
    pygame.draw.ellipse(screen, color, rect, 1)

def draw_sphere(xc, yc, r, base_color):
    pygame.draw.circle(screen, base_color, (int(xc), int(yc)), r)
    pygame.draw.circle(screen, WHITE, (int(xc), int(yc)), r, 1)

def draw_planet(xc, yc, r, color, details=None):
    draw_sphere(xc, yc, r, color)
    if details == "earth":
        pygame.draw.circle(screen, (34,139,34), (int(xc)+r//3, int(yc)), r//3)
    elif details == "mars":
        pygame.draw.circle(screen, (139,0,0), (int(xc)-r//2, int(yc)+r//3), r//3)
    elif details == "jupiter":
        ellipse_rect = pygame.Rect(int(xc-r*0.8), int(yc-r*0.3), int(r*1.6), int(r*0.6))
        pygame.draw.ellipse(screen, (139,69,19), ellipse_rect)
    elif details == "saturn":
        ring_rect = pygame.Rect(int(xc-r*2), int(yc-r//2), r*4, r)
        pygame.draw.ellipse(screen, (200,200,150), ring_rect, 2)
    elif details == "uranus":
        ring_rect = pygame.Rect(int(xc-r//2), int(yc-r*2), r, r*4)
        pygame.draw.ellipse(screen, (50,50,50), ring_rect, 2)

def draw_asteroid_belt(xc, yc, asteroids, angle_shift, zoom):
    for rx, ry, base_angle in asteroids:
        angle = base_angle + angle_shift
        x = xc + (rx*zoom) * math.cos(angle)
        y = yc + (ry*zoom) * math.sin(angle)
        pygame.draw.circle(screen, ASTEROID_COLOR, (int(x), int(y)), 1)

def draw_stars(stars):
    for star in stars:
        x, y, brightness = star
        if random.random() < 0.01:
            brightness = random.choice([50, 150, 255])
            star[2] = brightness
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)

# Shooting star
def spawn_shooting_star():
    start_x = random.randint(0, WIDTH//2)
    start_y = random.randint(0, HEIGHT//2)
    dx = random.uniform(8, 12)
    dy = random.uniform(4, 7)
    return [start_x, start_y, dx, dy, 60]

def update_shooting_star(shooting_star):
    if shooting_star:
        x, y, dx, dy, life = shooting_star
        end_x = x + dx*10
        end_y = y + dy*10
        pygame.draw.line(screen, WHITE, (int(x), int(y)), (int(end_x), int(end_y)), 2)
        shooting_star[0] += dx
        shooting_star[1] += dy
        shooting_star[4] -= 1
        if shooting_star[4] <= 0:
            shooting_star = None
    return shooting_star

# Comet
def spawn_comet():
    start_x = random.randint(0, WIDTH//2)
    start_y = random.randint(0, HEIGHT//2)
    dx = random.uniform(5, 8)
    dy = random.uniform(3, 6)
    return [start_x, start_y, dx, dy, 120]  # lasts longer

def update_comet(comet, planet_positions, sizes):
    hit = False
    if comet:
        x, y, dx, dy, life = comet
        end_x = x + dx*15
        end_y = y + dy*15
        pygame.draw.line(screen, GOLD, (int(x), int(y)), (int(end_x), int(end_y)), 3)
        comet[0] += dx
        comet[1] += dy
        comet[4] -= 1
        # Collision check
        for planet, pos in planet_positions.items():
            px, py = pos
            pr = sizes[planet]
            if math.hypot(comet[0]-px, comet[1]-py) < pr+5:
                hit = True
        if comet[4] <= 0:
            comet = None
    return comet, hit

def main():
    global current_detail_index
    angles = {
        "mercury": 0, "venus": math.pi/4, "earth": math.pi/2,
        "mars": math.pi/3, "jupiter": math.pi/6, "saturn": math.pi/8,
        "uranus": math.pi/5, "neptune": math.pi/7
    }
    orbits = {
        "mercury": (50, 40), "venus": (80, 50), "earth": (100, 60),
        "mars": (150, 80), "jupiter": (200, 100), "saturn": (270, 150),
        "uranus": (320, 180), "neptune": (370, 210)
    }
    sizes = {
        "mercury": 5, "venus": 8, "earth": 12, "mars": 9,
        "jupiter": 25, "saturn": 18, "uranus": 14, "neptune": 14
    }
    colors = {
        "mercury": MERCURY_COLOR, "venus": VENUS_COLOR, "earth": EARTH_COLOR,
        "mars": MARS_COLOR, "jupiter": JUPITER_COLOR, "saturn": SATURN_COLOR,
        "uranus": URANUS_COLOR, "neptune": NEPTUNE_COLOR
    }
    speeds = {
        "mercury": 0.05, "venus": 0.03, "earth": 0.02, "mars": 0.015,
        "jupiter": 0.01, "saturn": 0.008, "uranus": 0.006, "neptune": 0.004
    }
    details = {
        "mercury": "mercury", "venus": "venus", "earth": "earth", "mars": "mars",
        "jupiter": "jupiter", "saturn": "saturn", "uranus": "uranus", "neptune": "neptune"
    }

    asteroids = [(random.uniform(160, 190), random.uniform(85, 95), random.uniform(0, 2*math.pi)) for _ in range(400)]
    asteroid_angle_shift = 0
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.choice([100, 150, 255])] for _ in range(200)]

    shooting_star = None
    comet = None
    zoom = 1.0

    streak = 0
    bad_luck_time = 0  # timestamp when BAD LUCK should disappear

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_UP:
                    zoom = min(3.0, zoom + 0.1)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_DOWN:
                    zoom = max(0.5, zoom - 0.1)
                elif event.key == pygame.K_SPACE:
                    current_detail_index = (current_detail_index + 1) % len(details_order)
                elif event.key == pygame.K_s:   # Shooting star
                    shooting_star = spawn_shooting_star()
                elif event.key == pygame.K_c:   # Comet
                    comet = spawn_comet()
                    streak += 1   # increment streak only when pressing C

        screen.fill(BLACK)

        # Background stars
        draw_stars(stars)

        # Orbits
        for planet, (rx, ry) in orbits.items():
            draw_ellipse(400, 400, int(rx*zoom), int(ry*zoom))

        # Asteroid belt
        asteroid_angle_shift += 0.002
        draw_asteroid_belt(400, 400, asteroids, asteroid_angle_shift, zoom)

        # Sun
        draw_sphere(400, 400, int(40*zoom), SUN_COLOR)

        # Planets
        planet_positions = {}
        for planet in angles:
            rx, ry = orbits[planet]
            angles[planet] += speeds[planet]
            x = 400 + (rx*zoom) * math.cos(angles[planet])
            y = 400 + (ry*zoom) * math.sin(angles[planet])
            draw_planet(x, y, int(sizes[planet]*zoom), colors[planet], details[planet])
            planet_positions[planet] = (x, y)

        # Show ONE detail at a time when SPACE is pressed
        if current_detail_index >= 0:
            obj, detail_text = details_order[current_detail_index]
            if obj == "sun":
                text = font.render(detail_text, True, (255, 215, 0))
                screen.blit(text, (420, 400))
            elif obj in planet_positions:
                pos = planet_positions[obj]
                text = font.render(detail_text, True, WHITE)
                screen.blit(text, (int(pos[0])+20, int(pos[1])-20))
            elif obj == "asteroid":
                text = font.render(detail_text, True, WHITE)
                screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 + 300))
            elif obj == "system":
                text = font.render(detail_text, True, WHITE)
                screen.blit(text, (WIDTH//2 - 100, HEIGHT//2))

        # Shooting star update
        shooting_star = update_shooting_star(shooting_star)

        # Comet update
        comet, hit = update_comet(comet, planet_positions, sizes)
        if hit:
            bad_luck_time = time.time() + 2  # show BAD LUCK for 2 seconds
            streak = 0   # reset streak if comet hits
            comet = None

        # Display streak
        streak_text = font.render(f"Streak: {streak}", True, WHITE)
        screen.blit(streak_text, (10, 10))

        # Display BAD LUCK if active
        if bad_luck_time > time.time():
            bad_text = font.render("BAD LUCK", True, (255, 0, 0))
            screen.blit(bad_text, (WIDTH//2 - 60, HEIGHT//2))

        pygame.display.flip()
        clock.tick(20)

if __name__ == "__main__":
    main()
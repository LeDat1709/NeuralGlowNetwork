import pygame
import math
import random
import colorsys

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mạng Lưới Thần Kinh Động")

BLACK = (0, 0, 0)

BASE_COLOR_HUE = 0.68
BASE_COLOR_SATURATION = 0.8
BASE_COLOR_VALUE = 0.08

ACTIVE_COLOR_HUES = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25,
                     0.3]
ACTIVE_COLOR_SATURATION = 1.0
ACTIVE_COLOR_VALUE = 0.9

def hsv_to_rgb(h, s, v):
    h = max(0.0, min(1.0, h))
    s = max(0.0, min(1.0, s))
    v = max(0.0, min(1.0, v))
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

NODE_RADIUS = 5
MAX_NODE_ACTIVITY = 100
NODE_SPAWN_AREA_BUFFER = 50

NODES = []
EDGES = []

class Node:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.radius = NODE_RADIUS
        self.activity = 0
        self.base_value = BASE_COLOR_VALUE
        self.target_value = BASE_COLOR_VALUE
        self.hue = random.choice(ACTIVE_COLOR_HUES)
        self.velocity = pygame.Vector2(random.uniform(-0.5, 0.5),
                                       random.uniform(-0.5,
                                                      0.5))

    def activate(self, strength=MAX_NODE_ACTIVITY):
        self.activity = min(MAX_NODE_ACTIVITY, self.activity + strength)
        self.target_value = ACTIVE_COLOR_VALUE
        self.hue = random.choice(ACTIVE_COLOR_HUES)

    def update(self):
        if self.activity > 0:
            self.activity -= 1
            if self.activity <= 0:
                self.target_value = BASE_COLOR_VALUE
        
        self.base_value += (self.target_value - self.base_value) * 0.1
        self.base_value = max(BASE_COLOR_VALUE,
                               min(ACTIVE_COLOR_VALUE, self.base_value))

        self.pos += self.velocity
        if self.pos.x < NODE_SPAWN_AREA_BUFFER or self.pos.x > WIDTH - NODE_SPAWN_AREA_BUFFER:
            self.velocity.x *= -1
        if self.pos.y < NODE_SPAWN_AREA_BUFFER or self.pos.y > HEIGHT - NODE_SPAWN_AREA_BUFFER:
            self.velocity.y *= -1

    def draw(self, surface):
        current_hue = BASE_COLOR_HUE + (self.hue - BASE_COLOR_HUE) * (
            self.base_value - BASE_COLOR_VALUE) / (ACTIVE_COLOR_VALUE -
                                                   BASE_COLOR_VALUE + 0.001)
        current_saturation = BASE_COLOR_SATURATION + (
            ACTIVE_COLOR_SATURATION -
            BASE_COLOR_SATURATION) * (self.base_value - BASE_COLOR_VALUE) / (
                ACTIVE_COLOR_VALUE - BASE_COLOR_VALUE + 0.001)

        node_color = hsv_to_rgb(current_hue, current_saturation,
                                 self.base_value)

        pygame.draw.circle(surface, node_color,
                           (int(self.pos.x), int(self.pos.y)), self.radius, 0)

        if self.activity > 0:
            glow_radius = self.radius + 5
            for i in range(3):
                alpha = int(255 * (self.activity / MAX_NODE_ACTIVITY) *
                            (0.5 - i * 0.1))
                if alpha <= 0: continue
                glow_color = hsv_to_rgb(current_hue, current_saturation,
                                        self.base_value +
                                        (0.1 * i))

                temp_surface = pygame.Surface(
                    (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                temp_surface.fill((0, 0, 0, 0))
                pygame.draw.circle(
                    temp_surface,
                    (glow_color[0], glow_color[1], glow_color[2], alpha),
                    (glow_radius, glow_radius), glow_radius, 0)
                
                surface.blit(temp_surface, (int(self.pos.x - glow_radius),
                                            int(self.pos.y - glow_radius)))

class Edge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.activity = 0
        self.base_value = BASE_COLOR_VALUE
        self.target_value = BASE_COLOR_VALUE
        self.flow_position = 0.0
        self.flow_speed = random.uniform(0.01, 0.03)

    def activate(self, strength=MAX_NODE_ACTIVITY):
        self.activity = min(MAX_NODE_ACTIVITY, self.activity + strength)
        self.target_value = ACTIVE_COLOR_VALUE
        self.flow_position = 0.0

    def update(self):
        if self.activity > 0:
            self.activity -= 1
            if self.activity <= 0:
                self.target_value = BASE_COLOR_VALUE
        
        self.base_value += (self.target_value - self.base_value) * 0.08
        self.base_value = max(BASE_COLOR_VALUE,
                               min(ACTIVE_COLOR_VALUE, self.base_value))

        if self.activity > 0:
            self.flow_position += self.flow_speed
            if self.flow_position > 1.0:
                self.flow_position = 0.0

    def draw(self, surface):
        edge_color = hsv_to_rgb(BASE_COLOR_HUE, BASE_COLOR_SATURATION,
                                 self.base_value)

        pygame.draw.line(surface, edge_color, self.node1.pos, self.node2.pos,
                         1)

        if self.activity > 0:
            flow_point = self.node1.pos.lerp(self.node2.pos,
                                             self.flow_position)

            flow_hue = self.node1.hue
            flow_color_rgb = hsv_to_rgb(flow_hue, ACTIVE_COLOR_SATURATION,
                                        ACTIVE_COLOR_VALUE)

            flow_radius = NODE_RADIUS * 0.6

            pygame.draw.circle(
                surface, flow_color_rgb,
                (int(flow_point.x), int(flow_point.y)),
                int(flow_radius * (self.activity / MAX_NODE_ACTIVITY)), 0)

            for i in range(2):
                alpha = int(255 * (self.activity / MAX_NODE_ACTIVITY) *
                            (0.4 - i * 0.1))
                if alpha <= 0: continue
                glow_color = (flow_color_rgb[0], flow_color_rgb[1],
                              flow_color_rgb[2], alpha)

                temp_surface = pygame.Surface(
                    (flow_radius * 2, flow_radius * 2), pygame.SRCALPHA)
                temp_surface.fill((0, 0, 0, 0))
                pygame.draw.circle(temp_surface, glow_color,
                                   (flow_radius, flow_radius), flow_radius, 0)
                
                surface.blit(temp_surface, (int(flow_point.x - flow_radius),
                                            int(flow_point.y - flow_radius)))

NUM_NODES = 50
MAX_EDGE_DISTANCE = 200

def create_network():
    for _ in range(NUM_NODES):
        x = random.randint(NODE_SPAWN_AREA_BUFFER,
                           WIDTH - NODE_SPAWN_AREA_BUFFER)
        y = random.randint(NODE_SPAWN_AREA_BUFFER,
                           HEIGHT - NODE_SPAWN_AREA_BUFFER)
        NODES.append(Node(x, y))

    for i, node1 in enumerate(NODES):
        for j, node2 in enumerate(NODES):
            if i < j:
                distance = node1.pos.distance_to(node2.pos)
                if distance < MAX_EDGE_DISTANCE:
                    EDGES.append(Edge(node1, node2))

create_network()

running = True
clock = pygame.time.Clock()

activity_timer = 0
ACTIVITY_INTERVAL = 50
current_active_node = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.Vector2(event.pos)
            closest_node = None
            min_dist = float('inf')
            for node in NODES:
                dist = node.pos.distance_to(mouse_pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_node = node
            
            if closest_node and min_dist < NODE_RADIUS * 3:
                closest_node.activate(strength=MAX_NODE_ACTIVITY *
                                       1.5)
                current_active_node = closest_node
                
                for edge in EDGES:
                    if edge.node1 == closest_node or edge.node2 == closest_node:
                        edge.activate(strength=MAX_NODE_ACTIVITY)

    activity_timer += 1

    if activity_timer >= ACTIVITY_INTERVAL:
        activity_timer = 0
        
        if NODES:
            if current_active_node:
                neighbors = []
                for edge in EDGES:
                    if edge.node1 == current_active_node and edge.node2.activity < MAX_NODE_ACTIVITY * 0.5:
                        neighbors.append(edge.node2)
                        edge.activate(strength=MAX_NODE_ACTIVITY)
                    elif edge.node2 == current_active_node and edge.node1.activity < MAX_NODE_ACTIVITY * 0.5:
                        neighbors.append(edge.node1)
                        edge.activate(strength=MAX_NODE_ACTIVITY)
                
                if neighbors:
                    current_active_node = random.choice(neighbors)
                    current_active_node.activate(strength=MAX_NODE_ACTIVITY)
                else:
                    current_active_node = random.choice(NODES)
                    current_active_node.activate(strength=MAX_NODE_ACTIVITY)
            else:
                current_active_node = random.choice(NODES)
                current_active_node.activate(strength=MAX_NODE_ACTIVITY)
                
                for edge in EDGES:
                    if edge.node1 == current_active_node or edge.node2 == current_active_node:
                        edge.activate(strength=MAX_NODE_ACTIVITY)

    for node in NODES:
        node.update()
    for edge in EDGES:
        edge.update()

    screen.fill(BLACK)

    for edge in EDGES:
        edge.draw(screen)

    for node in NODES:
        node.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()

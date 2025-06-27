import pygame
import math
import random
import colorsys

# --- Khởi tạo Pygame ---
pygame.init()

# --- Cấu hình màn hình ---
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mạng Lưới Thần Kinh Động")

# --- Cấu hình màu sắc ---
BLACK = (0, 0, 0)  # Nền đen

# Màu cơ bản cho Nodes/Edges khi không hoạt động (hơi xanh tím than)
BASE_COLOR_HUE = 0.68  # Tím xanh
BASE_COLOR_SATURATION = 0.8
BASE_COLOR_VALUE = 0.08  # Rất tối, chỉ đủ để thấy mờ

# Dải màu khi Nodes/Edges được kích hoạt (gradient rực rỡ)
# Sử dụng một dải màu để tạo hiệu ứng chuyển sắc đẹp mắt
ACTIVE_COLOR_HUES = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25,
                     0.3]  # Từ đỏ sang vàng sang xanh lá
ACTIVE_COLOR_SATURATION = 1.0
ACTIVE_COLOR_VALUE = 0.9  # Rất sáng


# Hàm chuyển đổi HSV sang RGB (đã sửa lỗi kẹp giá trị)
def hsv_to_rgb(h, s, v):
    h = max(0.0, min(1.0, h))
    s = max(0.0, min(1.0, s))
    v = max(0.0, min(1.0, v))
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


# --- Cấu hình Nodes và Edges ---
NODE_RADIUS = 5  # Bán kính cơ bản của Node
MAX_NODE_ACTIVITY = 100  # Thời gian Node/Edge sáng lên sau khi kích hoạt
NODE_SPAWN_AREA_BUFFER = 50  # Đảm bảo Node không quá sát biên

NODES = []
EDGES = []


# --- Lớp Node ---
class Node:

    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.radius = NODE_RADIUS
        self.activity = 0  # Mức độ hoạt động (0 = tối, MAX_NODE_ACTIVITY = sáng nhất)
        self.base_value = BASE_COLOR_VALUE
        self.target_value = BASE_COLOR_VALUE
        self.hue = random.choice(
            ACTIVE_COLOR_HUES)  # Màu riêng cho mỗi node khi kích hoạt
        self.velocity = pygame.Vector2(random.uniform(-0.5, 0.5),
                                       random.uniform(-0.5,
                                                      0.5))  # Di chuyển nhẹ

    def activate(self, strength=MAX_NODE_ACTIVITY):
        self.activity = min(MAX_NODE_ACTIVITY, self.activity + strength)
        self.target_value = ACTIVE_COLOR_VALUE
        self.hue = random.choice(ACTIVE_COLOR_HUES)  # Đổi màu khi kích hoạt

    def update(self):
        # Giảm hoạt động và làm mờ dần
        if self.activity > 0:
            self.activity -= 1
            if self.activity <= 0:  # Khi hết hoạt động, chuyển về màu nền
                self.target_value = BASE_COLOR_VALUE

        # Nội suy giá trị độ sáng
        self.base_value += (self.target_value - self.base_value) * 0.1
        self.base_value = max(BASE_COLOR_VALUE,
                              min(ACTIVE_COLOR_VALUE, self.base_value))

        # Di chuyển Node (rất nhẹ nhàng)
        self.pos += self.velocity
        # Giới hạn trong màn hình
        if self.pos.x < NODE_SPAWN_AREA_BUFFER or self.pos.x > WIDTH - NODE_SPAWN_AREA_BUFFER:
            self.velocity.x *= -1
        if self.pos.y < NODE_SPAWN_AREA_BUFFER or self.pos.y > HEIGHT - NODE_SPAWN_AREA_BUFFER:
            self.velocity.y *= -1

    def draw(self, surface):
        # Tính toán màu sắc dựa trên độ hoạt động
        current_hue = BASE_COLOR_HUE + (self.hue - BASE_COLOR_HUE) * (
            self.base_value - BASE_COLOR_VALUE) / (ACTIVE_COLOR_VALUE -
                                                   BASE_COLOR_VALUE + 0.001)
        current_saturation = BASE_COLOR_SATURATION + (
            ACTIVE_COLOR_SATURATION -
            BASE_COLOR_SATURATION) * (self.base_value - BASE_COLOR_VALUE) / (
                ACTIVE_COLOR_VALUE - BASE_COLOR_VALUE + 0.001)

        node_color = hsv_to_rgb(current_hue, current_saturation,
                                self.base_value)

        # Vẽ Node
        pygame.draw.circle(surface, node_color,
                           (int(self.pos.x), int(self.pos.y)), self.radius, 0)

        # Vẽ hiệu ứng phát sáng nhẹ (vẽ thêm các vòng tròn mờ)
        if self.activity > 0:
            glow_radius = self.radius + 5
            for i in range(3):
                alpha = int(255 * (self.activity / MAX_NODE_ACTIVITY) *
                            (0.5 - i * 0.1))  # Giảm dần alpha
                if alpha <= 0: continue
                glow_color = hsv_to_rgb(current_hue, current_saturation,
                                        self.base_value +
                                        (0.1 * i))  # Hơi sáng hơn

                # Tạo bề mặt riêng để vẽ vòng tròn với alpha
                temp_surface = pygame.Surface(
                    (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                temp_surface.fill((0, 0, 0, 0))  # Đảm bảo nền trong suốt
                pygame.draw.circle(
                    temp_surface,
                    (glow_color[0], glow_color[1], glow_color[2], alpha),
                    (glow_radius, glow_radius), glow_radius, 0)

                # Blit lên màn hình chính
                surface.blit(temp_surface, (int(self.pos.x - glow_radius),
                                            int(self.pos.y - glow_radius)))


# --- Lớp Edge ---
class Edge:

    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.activity = 0  # Mức độ hoạt động
        self.base_value = BASE_COLOR_VALUE
        self.target_value = BASE_COLOR_VALUE
        self.flow_position = 0.0  # Vị trí "dòng chảy dữ liệu" trên cạnh
        self.flow_speed = random.uniform(0.01, 0.03)  # Tốc độ dòng chảy

    def activate(self, strength=MAX_NODE_ACTIVITY):
        self.activity = min(MAX_NODE_ACTIVITY, self.activity + strength)
        self.target_value = ACTIVE_COLOR_VALUE
        self.flow_position = 0.0  # Bắt đầu dòng chảy từ đầu

    def update(self):
        # Giảm hoạt động và làm mờ dần
        if self.activity > 0:
            self.activity -= 1
            if self.activity <= 0:
                self.target_value = BASE_COLOR_VALUE

        # Nội suy giá trị độ sáng
        self.base_value += (self.target_value - self.base_value) * 0.08
        self.base_value = max(BASE_COLOR_VALUE,
                              min(ACTIVE_COLOR_VALUE, self.base_value))

        # Cập nhật vị trí dòng chảy
        if self.activity > 0:
            self.flow_position += self.flow_speed
            if self.flow_position > 1.0:
                self.flow_position = 0.0  # Lặp lại dòng chảy

    def draw(self, surface):
        # Tính toán màu sắc cho cạnh
        edge_color = hsv_to_rgb(BASE_COLOR_HUE, BASE_COLOR_SATURATION,
                                self.base_value)

        # Vẽ đường kết nối
        pygame.draw.line(surface, edge_color, self.node1.pos, self.node2.pos,
                         1)

        # Vẽ hiệu ứng dòng chảy dữ liệu
        if self.activity > 0:
            # Tính điểm trên đường thẳng cho dòng chảy
            flow_point = self.node1.pos.lerp(self.node2.pos,
                                             self.flow_position)

            flow_hue = self.node1.hue  # Sử dụng màu của node nguồn
            flow_color_rgb = hsv_to_rgb(flow_hue, ACTIVE_COLOR_SATURATION,
                                        ACTIVE_COLOR_VALUE)

            flow_radius = NODE_RADIUS * 0.6  # Kích thước hạt dòng chảy

            # Vẽ hạt dòng chảy
            pygame.draw.circle(
                surface, flow_color_rgb,
                (int(flow_point.x), int(flow_point.y)),
                int(flow_radius * (self.activity / MAX_NODE_ACTIVITY)), 0)

            # Vẽ hiệu ứng phát sáng cho dòng chảy
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


# --- Tạo mạng lưới ---
NUM_NODES = 50
MAX_EDGE_DISTANCE = 200  # Khoảng cách tối đa để kết nối Node


def create_network():
    # Tạo Nodes
    for _ in range(NUM_NODES):
        x = random.randint(NODE_SPAWN_AREA_BUFFER,
                           WIDTH - NODE_SPAWN_AREA_BUFFER)
        y = random.randint(NODE_SPAWN_AREA_BUFFER,
                           HEIGHT - NODE_SPAWN_AREA_BUFFER)
        NODES.append(Node(x, y))

    # Tạo Edges giữa các Node gần nhau
    for i, node1 in enumerate(NODES):
        for j, node2 in enumerate(NODES):
            if i < j:  # Tránh tạo cạnh trùng lặp và nối với chính nó
                distance = node1.pos.distance_to(node2.pos)
                if distance < MAX_EDGE_DISTANCE:
                    EDGES.append(Edge(node1, node2))


create_network()

# --- Vòng lặp chính của game ---
running = True
clock = pygame.time.Clock()

activity_timer = 0
ACTIVITY_INTERVAL = 50  # Kích hoạt ngẫu nhiên mỗi 50 frame
current_active_node = None  # Theo dõi node đang hoạt động để lan truyền

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Kích hoạt node gần chuột khi click
            mouse_pos = pygame.Vector2(event.pos)
            closest_node = None
            min_dist = float('inf')
            for node in NODES:
                dist = node.pos.distance_to(mouse_pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_node = node

            if closest_node and min_dist < NODE_RADIUS * 3:  # Nếu click đủ gần
                closest_node.activate(strength=MAX_NODE_ACTIVITY *
                                      1.5)  # Kích hoạt mạnh hơn
                current_active_node = closest_node  # Đặt làm node nguồn lan truyền

                # Kích hoạt các cạnh nối với node này
                for edge in EDGES:
                    if edge.node1 == closest_node or edge.node2 == closest_node:
                        edge.activate(strength=MAX_NODE_ACTIVITY)

    # --- Cập nhật logic mạng lưới ---
    activity_timer += 1

    if activity_timer >= ACTIVITY_INTERVAL:
        activity_timer = 0

        # Ngẫu nhiên kích hoạt một Node
        if NODES:
            # Lấy node cũ hoặc chọn ngẫu nhiên
            if current_active_node:
                # Lan truyền hoạt động từ node cũ sang các node lân cận
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
                else:  # Nếu không có hàng xóm mới để lan truyền, chọn một node ngẫu nhiên
                    current_active_node = random.choice(NODES)
                    current_active_node.activate(strength=MAX_NODE_ACTIVITY)
            else:  # Lần đầu chạy hoặc không có node hoạt động
                current_active_node = random.choice(NODES)
                current_active_node.activate(strength=MAX_NODE_ACTIVITY)

                # Kích hoạt các cạnh nối với node mới
                for edge in EDGES:
                    if edge.node1 == current_active_node or edge.node2 == current_active_node:
                        edge.activate(strength=MAX_NODE_ACTIVITY)

    # Cập nhật tất cả Nodes và Edges
    for node in NODES:
        node.update()
    for edge in EDGES:
        edge.update()

    # --- Vẽ ---
    screen.fill(BLACK)  # Xóa màn hình với màu đen

    # Vẽ Edges trước để Nodes nằm trên Edges
    for edge in EDGES:
        edge.draw(screen)

    # Vẽ Nodes
    for node in NODES:
        node.draw(screen)

    pygame.display.flip()  # Cập nhật toàn bộ màn hình

    clock.tick(60)  # Giới hạn 60 khung hình/giây

pygame.quit()

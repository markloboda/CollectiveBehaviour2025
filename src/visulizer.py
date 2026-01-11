import os
from dataclasses import dataclass

import pygame
import pygame_gui
import time
from typing import Tuple, Generator, Iterator
import math

from PIL import Image

from simulation_state import SimulationState

BACKGROUND_COLOR = (200, 200, 200)
GRID_COLOR = (160, 160, 160)
SHEEP_COLOR = (255, 0, 0)
DOG_COLOR = (0, 0, 255)
GOAL_COLOR = (0, 200, 50)
TEXT_COLOR = (0, 0, 0)


@dataclass
class Camera:
  x: float = 0
  y: float = 0
  zoom: float = 1.0

  def screen_to_world(self, screen_pos: Tuple[int, int], screen_size: Tuple[int, int]) -> Tuple[float, float]:
    screen_x, screen_y = screen_pos
    screen_width, screen_height = screen_size
    world_x = (screen_x - screen_width / 2) / self.zoom + self.x
    world_y = (screen_y - screen_height / 2) / self.zoom + self.y
    return world_x, world_y

  def world_to_screen(self, world_pos: Tuple[float, float], screen_size: Tuple[int, int]) -> Tuple[float, float]:
    world_x, world_y = world_pos
    screen_width, screen_height = screen_size
    screen_x = (world_x - self.x) * self.zoom + screen_width / 2
    screen_y = (world_y - self.y) * self.zoom + screen_height / 2
    return screen_x, screen_y


class SimulationVisualizer:
  CELL_SIZE = 3

  def __init__(self, sim = None, world_width: int = 300, world_height: int = 300, headless=False):
    pygame.init()
    self.world_width = world_width
    self.world_height = world_height

    self.sim = sim

    self.screen_width = 1200
    self.screen_height = 800

    if not headless:
      self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
      pygame.display.set_caption("Simulation Visualizer")

      self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))

      # Dropdown for selecting forces to visualize
      self.force_dropdown = pygame_gui.elements.UIDropDownMenu(
        relative_rect=pygame.Rect((self.screen_width - 210, 10), (200, 30)),
        options_list=[
          "None",
          "social_attraction",
          "social_alignment",
          "social_repulsion",
          "dog_repulsion",
          "obstacle_repulsion",
          "noise",
          "splitting_lines",
        ],
        starting_option="None",
        manager=self.ui_manager,
      )

      self.selected_force = None

      # Pause button
      self.pause_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, self.screen_height - 35), (100, 30)),
        text="Pause",
        manager=self.ui_manager,
      )

      self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((120, self.screen_height - 35), (200, 30)),
        start_value=50.0,
        value_range=(1.0, 500.0),
        manager=self.ui_manager
      )

      self.speed_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((330, self.screen_height - 35), (100, 40)),
        text="Speed: 1.0x",
        manager=self.ui_manager
      )

    self.paused = False
    self.simulation_speed = self.speed_slider.get_current_value() if not headless else 1.0
    self.last_tick_time = time.time()
    self.tick_interval = 1.0  # seconds per tick

    self.camera = Camera()
    # Center camera on world and fit to screen
    self.camera.x = 0
    self.camera.y = 0
    ui_margin = 50
    zoom_x = self.screen_width / world_width
    zoom_y = (self.screen_height - ui_margin) / world_height
    self.camera.zoom = min(zoom_x, zoom_y) * 0.95

    self.dragging = False
    self.last_mouse_pos = None

    self.goal_pos = self.sim.cfg.goal_pos

    self.font = pygame.font.Font(None, 36)

  def stop(self):
    pygame.quit()

  def handle_events(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        return False

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == self.pause_button:
          self.paused = not self.paused
          self.pause_button.set_text("Resume" if self.paused else "Pause")

      if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
        if event.ui_element == self.force_dropdown:
          self.selected_force = event.text if event.text != "None" else None

      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == pygame.BUTTON_LEFT:
          self.dragging = True
          self.last_mouse_pos = event.pos

          if pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.goal_pos = self.camera.screen_to_world(event.pos, (self.screen_width, self.screen_height))
            self.sim.cfg.goal_pos = self.goal_pos
        elif event.button == pygame.BUTTON_WHEELUP:
          self.camera.zoom *= 1.1
        elif event.button == pygame.BUTTON_WHEELDOWN:
          self.camera.zoom /= 1.1

      if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
          self.dragging = False

      if event.type == pygame.MOUSEMOTION and self.dragging and not self.ui_manager.focused_set:
        current_pos = event.pos
        dx = (current_pos[0] - self.last_mouse_pos[0]) / self.camera.zoom
        dy = (current_pos[1] - self.last_mouse_pos[1]) / self.camera.zoom
        self.camera.x -= dx
        self.camera.y -= dy
        self.last_mouse_pos = current_pos

      if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
        if event.ui_element == self.speed_slider:
          self.simulation_speed = event.value
          self.speed_label.set_text(f"Speed: {self.simulation_speed:.1f}x")

      self.ui_manager.process_events(event)

    return True

  def draw_rect(self, p0, p1, color, border_width=0):
    x1, y1 = self.camera.world_to_screen(p0, (self.screen_width, self.screen_height))
    x2, y2 = self.camera.world_to_screen(p1, (self.screen_width, self.screen_height))

    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    rect = [
      left, top, width, height
    ]
    pygame.draw.rect(self.screen, color, rect, border_width)


  def draw_circle(self, pos: Tuple[float, float], color: Tuple[int, int, int], radius=1.0, width=0):
    screen_pos = self.camera.world_to_screen(pos, (self.screen_width, self.screen_height))
    pygame.draw.circle(self.screen, color, screen_pos, radius * self.camera.zoom, width)

  def draw_grid(self):
    world_width = self.world_width
    world_height = self.world_height

    #self.draw_rect((0, 0), (world_width, world_height), GRID_COLOR, 5)

    for obstacle in self.sim.cfg.obstacles:
      p0 = obstacle.xmin, obstacle.ymin
      p1 = obstacle.xmax, obstacle.ymax
      self.draw_rect(p0, p1, GRID_COLOR, 0)

  def draw_frame(self, state: SimulationState):
    self.screen.fill(BACKGROUND_COLOR)
    self.draw_grid()

    self.draw_circle(self.goal_pos, GOAL_COLOR, 10, 2)

    # Define dog colors
    dog1_color = (200, 0, 0)    # Red
    dog2_color = (0, 0, 200)    # Blue

    # Color sheep based on assigned dog groups
    if len(self.sim.shepherds) == 2 and self.sim.sheep:
      group1, group2 = self.sim.split_sheep_groups()

      # Draw sheep with their assigned dog colors
      for sheep in group1:
        self.draw_circle((sheep.x, sheep.y), dog1_color)

      for sheep in group2:
        self.draw_circle((sheep.x, sheep.y), dog2_color)
    else:
      # Default coloring for sheep when not split
      for sheep in state.sheep:
        self.draw_circle((sheep.x, sheep.y), SHEEP_COLOR)

    # Draw dogs with distinct colors
    dog_colors = [dog1_color, dog2_color]
    for i, dog in enumerate(state.dogs):
      color = dog_colors[i] if i < len(dog_colors) else DOG_COLOR
      self.draw_circle((dog.x, dog.y), color, radius=2.0)

    # Handle selected mode
    if self.selected_force == "splitting_lines":
        self.draw_splitting_lines(self.screen)
    else:
        self.draw_sheep_forces(self.screen)

    tick_text = self.font.render(f"Tick: {state.tick}", True, TEXT_COLOR)
    self.screen.blit(tick_text, (10, 10))

  def update(self) -> bool:
    current_time = time.time()
    next_tick = False
    if not self.paused:
      time_since_last_tick = current_time - self.last_tick_time
      if time_since_last_tick >= self.tick_interval / self.simulation_speed:
        next_tick = True
        self.last_tick_time = current_time

    self.ui_manager.update(current_time - self.last_tick_time)
    return next_tick

  def run(self, steps: Iterator[SimulationState]):
    running = True
    clock = pygame.time.Clock()

    state = next(steps)

    while running:
      running = self.handle_events()
      if self.update():
        try:
          state = next(steps)
        except StopIteration:
          pass
      self.draw_frame(state)
      self.ui_manager.draw_ui(self.screen)
      pygame.display.flip()
      clock.tick(60)

    pygame.quit()

  def draw_splitting_lines(self, screen):
    if len(self.sim.shepherds) != 2 or not self.sim.sheep:
      return

    dog1, dog2 = self.sim.shepherds[0], self.sim.shepherds[1]
    barycenter = self.sim.calculate_barycenter()

    # Middle point between dogs
    mid_x = (dog1.x + dog2.x) / 2
    mid_y = (dog1.y + dog2.y) / 2

    # Convert to screen coordinates using camera
    dog1_screen = self.camera.world_to_screen((dog1.x, dog1.y), (self.screen_width, self.screen_height))
    dog2_screen = self.camera.world_to_screen((dog2.x, dog2.y), (self.screen_width, self.screen_height))

    # Draw line between dogs
    pygame.draw.line(screen, (100, 100, 100), dog1_screen, dog2_screen, 1)

    # Draw extended line from midpoint through barycenter
    dir_x = barycenter[0] - mid_x
    dir_y = barycenter[1] - mid_y
    norm = math.hypot(dir_x, dir_y)

    if norm > 0:
      # Normalize direction
      dir_x /= norm
      dir_y /= norm

      # Extend the midpoint-barycenter line across the visible area
      line_length = max(self.world_width, self.world_height) * 2

      # Line from midpoint through barycenter
      mb_start_x = mid_x - dir_x * line_length
      mb_start_y = mid_y - dir_y * line_length
      mb_end_x = mid_x + dir_x * line_length
      mb_end_y = mid_y + dir_y * line_length

      mb_start_screen = self.camera.world_to_screen((mb_start_x, mb_start_y), (self.screen_width, self.screen_height))
      mb_end_screen = self.camera.world_to_screen((mb_end_x, mb_end_y), (self.screen_width, self.screen_height))

      # Draw extended midpoint-barycenter line
      pygame.draw.line(screen, (255, 50, 255), mb_start_screen, mb_end_screen, 1)

      # Perpendicular vector for splitting line
      perp_x = -dir_y
      perp_y = dir_x

      # Extend the perpendicular visible area
      split_start_x = mid_x - perp_x * line_length
      split_start_y = mid_y - perp_y * line_length
      split_end_x = mid_x + perp_x * line_length
      split_end_y = mid_y + perp_y * line_length

      split_start_screen = self.camera.world_to_screen((split_start_x, split_start_y), (self.screen_width, self.screen_height))
      split_end_screen = self.camera.world_to_screen((split_end_x, split_end_y), (self.screen_width, self.screen_height))

      # Draw the perpendicular line
      pygame.draw.line(screen, (100, 100, 100), split_start_screen, split_end_screen, 1)

    # Draw midpoint
    self.draw_circle((mid_x, mid_y), (100, 100, 100), 1)

    # Draw barycenter
    self.draw_circle(barycenter, (100, 100, 100), 1)

  def draw_sheep_forces(self, screen):
    if not self.selected_force or not self.sim.sheep:
      return

    force_colors = {
      "social_attraction": (255, 0, 0),
      "social_alignment": (0, 255, 0),
      "social_repulsion": (0, 0, 255),
      "dog_repulsion": (255, 255, 0),
      "obstacle_repulsion": (255, 0, 255),
      "noise": (0, 255, 255),
    }

    color = force_colors.get(self.selected_force, (255, 255, 255))

    for sheep in self.sim.sheep:
      if hasattr(sheep, self.selected_force):
        force = getattr(sheep, self.selected_force)
        force_x, force_y = force

        if math.hypot(force_x, force_y) < 1e-3:
          continue

        mag = math.hypot(force_x, force_y)
        scale = min(20.0, 5.0 + 15.0 * mag)

        start_pos = (sheep.x, sheep.y)
        end_pos = (
          sheep.x + force_x / (mag + 1e-6) * scale,
          sheep.y + force_y / (mag + 1e-6) * scale
        )

        start_screen = self.camera.world_to_screen(start_pos, (self.screen_width, self.screen_height))
        end_screen = self.camera.world_to_screen(end_pos, (self.screen_width, self.screen_height))

        pygame.draw.line(screen, color, start_screen, end_screen, 1)
        self._draw_arrowhead(screen, start_screen, end_screen, color)

  def _draw_arrowhead(self, screen, start_pos, end_pos, color):
    start_x, start_y = start_pos
    end_x, end_y = end_pos

    dx = end_x - start_x
    dy = end_y - start_y
    length = math.hypot(dx, dy)

    if length < 5:
        return

    dx /= length
    dy /= length

    arrow_length = 8
    arrow_angle = 0.5

    cos_angle = math.cos(arrow_angle)
    sin_angle = math.sin(arrow_angle)

    left_x = end_x - arrow_length * (dx * cos_angle - dy * sin_angle)
    left_y = end_y - arrow_length * (dy * cos_angle + dx * sin_angle)

    right_x = end_x - arrow_length * (dx * cos_angle + dy * sin_angle)
    right_y = end_y - arrow_length * (dy * cos_angle - dx * sin_angle)

    pygame.draw.line(screen, color, end_pos, (left_x, left_y), 1)
    pygame.draw.line(screen, color, end_pos, (right_x, right_y), 1)


class SimulationRecorder(SimulationVisualizer):
  CELL_SIZE = 10

  def __init__(self, sim, world_width: int = 100, world_height: int = 100):
    os.environ['SDL_VIDEODRIVER'] = 'dummy'

    super().__init__(sim, world_width, world_height, headless=True)

    margin = 40  # For text
    self.screen_width = world_width * self.CELL_SIZE + margin * 2
    self.screen_height = world_height * self.CELL_SIZE + margin * 2

    self.screen = pygame.Surface((self.screen_width, self.screen_height))

    self.camera = Camera()
    self.camera.x = world_width / 2
    self.camera.y = world_height / 2
    self.camera.zoom = self.CELL_SIZE

    self.frames_list = []

  def capture_frame(self):
    string_image = pygame.image.tobytes(self.screen, 'RGB')
    return Image.frombytes('RGB', (self.screen_width, self.screen_height), string_image)

  def record(self, steps: Iterator[SimulationState], output_path: str, fps: int = 10):
    for state in steps:
      self.draw_frame(state)
      self.frames_list.append(self.capture_frame())

    print("Saving GIF...")
    self.frames_list[0].save(
      output_path,
      save_all=True,
      append_images=self.frames_list[1:],
      duration=1000 // fps,  # milliseconds per frame
      loop=0
    )
    print(f"Saved GIF to {output_path}")

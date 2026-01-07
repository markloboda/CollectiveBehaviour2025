import os
from dataclasses import dataclass

import pygame
import pygame_gui
import time
from typing import Tuple, Generator, Iterator

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

  def __init__(self, sim = None, world_width: int = 100, world_height: int = 100, headless=False):
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

      self.pause_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, self.screen_height - 35), (100, 30)),
        text="Pause",
        manager=self.ui_manager
      )

      self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((120, self.screen_height - 35), (200, 30)),
        start_value=1.0,
        value_range=(0.1, 500.0),
        manager=self.ui_manager
      )

      self.speed_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((330, self.screen_height - 35), (100, 40)),
        text="Speed: 1.0x",
        manager=self.ui_manager
      )

    self.paused = False
    self.simulation_speed = 1.0
    self.last_tick_time = time.time()
    self.tick_interval = 1.0  # seconds per tick

    self.camera = Camera()
    # Center camera on world and fit to screen
    self.camera.x = world_width / 2
    self.camera.y = world_height / 2
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

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == self.pause_button:
          self.paused = not self.paused
          self.pause_button.set_text("Resume" if self.paused else "Pause")

      if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
        if event.ui_element == self.speed_slider:
          self.simulation_speed = event.value
          self.speed_label.set_text(f"Speed: {self.simulation_speed:.1f}x")
        elif event.ui_element == self.progress_slider:
          self.player.tick = int(event.value * self.player.tick_count())

      self.ui_manager.process_events(event)

    return True

  def draw_circle(self, pos: Tuple[float, float], color: Tuple[int, int, int], radius=1.0, width=0):
    screen_pos = self.camera.world_to_screen(pos, (self.screen_width, self.screen_height))
    pygame.draw.circle(self.screen, color, screen_pos, radius * self.camera.zoom, width)

  def draw_grid(self):
    world_width = self.world_width
    world_height = self.world_height

    x1, y1 = self.camera.world_to_screen((0, 0), (self.screen_width, self.screen_height))
    x2, y2 = self.camera.world_to_screen((world_width, world_height), (self.screen_width, self.screen_height))

    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    world_rect = [
      left, top, width, height
    ]
    pygame.draw.rect(self.screen, GRID_COLOR, pygame.Rect(world_rect), 5)


  def draw_frame(self, state: SimulationState):
    self.screen.fill(BACKGROUND_COLOR)
    self.draw_grid()

    self.draw_circle(self.goal_pos, GOAL_COLOR, 10, 2)

    # Draw entities
    for sheep in state.sheep:
      self.draw_circle((sheep.x, sheep.y), DOG_COLOR)

    for dog in state.dogs:
      self.draw_circle((dog.x, dog.y), SHEEP_COLOR)

    # Draw tick number
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

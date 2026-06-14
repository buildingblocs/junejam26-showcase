# scenes/base_scene.py
from abc import ABC, abstractmethod

class BaseScene(ABC):
    def __init__(self, manager):
        self.manager = manager
        self.assets  = manager.assets    # shortcut so every scene can call self.assets

    @abstractmethod
    def handle_event(self, event): pass

    @abstractmethod
    def update(self, dt): pass

    @abstractmethod
    def draw(self, surface): pass
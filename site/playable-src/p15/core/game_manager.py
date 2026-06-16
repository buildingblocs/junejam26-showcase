# core/game_manager.py
from core.asset_manager import AssetManager

class GameManager:
    def __init__(self, surface):
        self.surface = surface
        self.assets  = AssetManager()
        self._stack  = []
        self._scene_map = {}
        self._register_scenes()

    def _register_scenes(self):
        from scenes.menu     import MenuScene
        from scenes.prologue import PrologueScene
        from scenes.chapter1 import Chapter1Scene
        from scenes.chapter2 import Chapter2Scene
        from scenes.chapter3 import Chapter3Scene
        from scenes.chapter4 import Chapter4Scene

        self._scene_map = {
            "menu":     MenuScene,
            "prologue": PrologueScene,
            "ch1":      Chapter1Scene,
            "ch2":      Chapter2Scene,
            "ch3":      Chapter3Scene,
            "ch4":      Chapter4Scene,
        }

    def push_scene(self, name, **kwargs):
        scene = self._scene_map[name](self, **kwargs)
        self._stack.append(scene)

    def pop_scene(self):
        if self._stack:
            self._stack.pop()

    def replace_scene(self, name, **kwargs):
        self.pop_scene()
        self.push_scene(name, **kwargs)

    def handle_event(self, event):
        if self._stack:
            self._stack[-1].handle_event(event)

    def update(self, dt):
        if self._stack:
            self._stack[-1].update(dt)

    def draw(self):
        if self._stack:
            self._stack[-1].draw(self.surface)
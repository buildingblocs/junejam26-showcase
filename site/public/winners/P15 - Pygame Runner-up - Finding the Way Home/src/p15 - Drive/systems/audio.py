# systems/audio.py
import pygame
from settings import CH_MUSIC, CH_AMBIENT, CH_SFX

class AudioManager:
    def __init__(self, assets):
        self.assets = assets
        pygame.mixer.set_num_channels(8)

    def play_music(self, name, loops=-1, volume=0.6):
        sound = self.assets.get_sound(f"music/{name}")
        if sound:
            pygame.mixer.Channel(CH_MUSIC).stop()
            pygame.mixer.Channel(CH_MUSIC).play(sound, loops=loops)
            pygame.mixer.Channel(CH_MUSIC).set_volume(volume)

    def play_ambient(self, name, loops=-1, volume=0.4):
        sound = self.assets.get_sound(f"sfx/{name}")
        if sound:
            pygame.mixer.Channel(CH_AMBIENT).play(sound, loops=loops)
            pygame.mixer.Channel(CH_AMBIENT).set_volume(volume)

    def play_sfx(self, name, volume=1.0):
        sound = self.assets.get_sound(f"sfx/{name}")
        if sound:
            pygame.mixer.Channel(CH_SFX).play(sound)
            pygame.mixer.Channel(CH_SFX).set_volume(volume)

    def duck_music(self, volume=0.1):
        """Lower music volume — use on heartbeat moment."""
        pygame.mixer.Channel(CH_MUSIC).set_volume(volume)

    def restore_music(self, volume=0.6):
        pygame.mixer.Channel(CH_MUSIC).set_volume(volume)

    def stop_all(self):
        pygame.mixer.stop()
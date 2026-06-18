import enemies
import game_state

class WaveManager:
    def __init__(self, stage_num):
        self.stage = stage_num
        self.wave = 1
        self.enemies = []
        self.is_shop_open = False
        
    def spawn_wave(self):
        # Every 2 stages add new enemy types
        # Stage 1: Charger, Stage 2: Poisoner, Stage 3: Shooter
        for _ in range(3 + self.wave):
            if self.stage >= 1: self.enemies.append(enemies.Charger(100, 100, 1, 2))
            if self.stage >= 2: self.enemies.append(enemies.Poisoner(200, 200))
            if self.stage >= 3: self.enemies.append(enemies.Shooter(800, 500))

    def check_progression(self, health_sys):
        if len(self.enemies) == 0 and not self.is_shop_open:
            self.wave += 1
            # Heal every stage transition
            health_sys.grant_boon()
            
            # Shop every 2 waves
            if self.wave % 2 == 0:
                self.is_shop_open = True
            else:
                self.spawn_wave()
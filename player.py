import pygame

class Player:
    def __init__(self, x, y, tile_size):
        self.tile_size = tile_size
        self.x = x
        self.y = y
        self.grid_x = x // tile_size
        self.grid_y = y // tile_size
        
        # Inventar
        self.inventory = {
            "Eisen": 0,
            "Kohle": 0,
            "Magnesium": 0,
            "Holz": 0
        }
        
        # Bewegungsgeschwindigkeit
        self.speed = tile_size
        
        # Farbe (8-Bit Stil - helles Blau für den Spieler)
        self.color = (0, 150, 255)
        
    def move(self, dx, dy, world):
        """Bewegt den Spieler um dx, dy Raster-Einheiten (eingerastet)"""
        if dx == 0 and dy == 0:
            return
            
        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy
        
        # Überprüfen ob die Position gültig ist
        if world.is_valid_position(new_grid_x, new_grid_y):
            self.grid_x = new_grid_x
            self.grid_y = new_grid_y
            # Position immer perfekt im Raster einrasten
            self.x = self.grid_x * self.tile_size
            self.y = self.grid_y * self.tile_size
            
    def mine_right(self, world):
        """Baut das Feld rechts neben dem Spieler ab"""
        target_x = self.grid_x + 1
        target_y = self.grid_y
        
        material = world.collect_material(target_x, target_y)
        if material:
            self.add_to_inventory(material)
            return True
        return False
            
    def add_to_inventory(self, material):
        """Fügt Material zum Inventar hinzu"""
        if material in self.inventory:
            self.inventory[material] += 1
            
    def mine_right(self, world):
        """Baut das Feld rechts neben dem Spieler ab"""
        target_x = self.grid_x + 1
        target_y = self.grid_y
        
        material = world.collect_material(target_x, target_y)
        if material:
            self.add_to_inventory(material)
            return True
        return False
            
    def draw(self, screen, camera_x, camera_y):
        """Zeichnet den Spieler auf dem Bildschirm"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Spieler als gefülltes Quadrat zeichnen
        pygame.draw.rect(screen, self.color, 
                        (screen_x, screen_y, self.tile_size, self.tile_size))
        
        # Rand um den Spieler (für bessere Sichtbarkeit)
        pygame.draw.rect(screen, (255, 255, 255), 
                        (screen_x, screen_y, self.tile_size, self.tile_size), 2)
        
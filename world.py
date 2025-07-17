import pygame
import random
import noise

class World:
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.world_size = 200  # 200x200 Raster
        
        # Material-Farben (8-Bit Stil)
        self.colors = {
            "Gras": (34, 139, 34),      # Grün
            "Eisen": (169, 169, 169),   # Grau
            "Kohle": (64, 64, 64),      # Dunkelgrau
            "Magnesium": (255, 215, 0), # Gold
            "Stein": (128, 128, 128),   # Hellgrau
            "Wald": (0, 100, 0)         # Dunkelgrün
        }
        
        # Spawn-Position in der Mitte
        self.spawn_x = (self.world_size // 2) * tile_size
        self.spawn_y = (self.world_size // 2) * tile_size
        
        # Gebäude-System
        self.buildings = {}
        
        # Welt generieren
        self.generate_world()
        
    def generate_world(self):
        """Generiert die Welt mit Perlin Noise"""
        self.tiles = {}
        
        # Seed für reproduzierbare Welten
        random.seed(42)
        
        for x in range(self.world_size):
            for y in range(self.world_size):
                # Perlin Noise für natürliche Verteilung
                noise_val = noise.pnoise2(x * 0.1, y * 0.1, octaves=4)
                
                # Material basierend auf Noise-Wert bestimmen
                if noise_val < -0.3:
                    material = "Kohle"
                elif noise_val < -0.1:
                    material = "Stein"  # Stein ist jetzt häufig
                elif noise_val > 0.4:
                    material = "Stein"  # Auch bei hohen Werten
                elif noise_val > 0.2 and noise_val <= 0.35:
                    material = "Wald"
                elif noise_val > 0.1 and noise_val <= 0.15 and random.random() < 0.3:
                    material = "Eisen"  # Eisen ist jetzt selten
                elif noise_val > 0.35 and random.random() < 0.1:
                    material = "Magnesium"  # Selten
                else:
                    material = "Gras"
                    
                self.tiles[(x, y)] = {
                    "material": material,
                    "collected": False
                }
                
    def get_tile(self, x, y):
        """Gibt das Tile an Position (x, y) zurück"""
        return self.tiles.get((x, y), None)
        
    def is_valid_position(self, x, y):
        """Überprüft ob Position gültig ist"""
        if not (0 <= x < self.world_size and 0 <= y < self.world_size):
            return False
            
        # Nur auf Gras oder gesammelte Felder kann man gehen
        tile = self.get_tile(x, y)
        if tile:
            return tile["material"] == "Gras" or tile["collected"]
        return False
        
    def collect_material(self, x, y):
        """Sammelt Material an Position (x, y)"""
        tile = self.get_tile(x, y)
        if tile and not tile["collected"] and tile["material"] != "Gras":
            tile["collected"] = True
            # Wald gibt Holz als Ressource
            if tile["material"] == "Wald":
                return "Holz"
            else:
                return tile["material"]
        return None
        
    def place_building(self, x, y, building_type):
        """Platziert ein Gebäude an Position (x, y)"""
        if self.is_valid_position(x, y):
            self.buildings[(x, y)] = {
                "type": building_type,
                "light_range": 4 if building_type == "Lagerfeuer" else 0
            }
            
    def get_light_level(self, x, y):
        """Berechnet das Lichtlevel an Position (x, y)"""
        base_light = 0.3  # Grundhelligkeit
        
        for (bx, by), building in self.buildings.items():
            if building["light_range"] > 0:
                distance = max(abs(x - bx), abs(y - by))  # Chebyshev-Distanz
                if distance <= building["light_range"]:
                    # Licht wird mit Entfernung schwächer
                    light_strength = 1.0 - (distance / building["light_range"])
                    base_light = min(1.0, base_light + light_strength * 0.7)
        
        return base_light
        
    def draw(self, screen, camera_x, camera_y, screen_width, screen_height):
        """Zeichnet die sichtbare Welt"""
        # Berechne welche Tiles sichtbar sind
        start_x = max(0, camera_x // self.tile_size)
        start_y = max(0, camera_y // self.tile_size)
        end_x = min(self.world_size, (camera_x + screen_width) // self.tile_size + 1)
        end_y = min(self.world_size, (camera_y + screen_height) // self.tile_size + 1)
        
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                tile = self.get_tile(x, y)
                if tile:
                    screen_x = x * self.tile_size - camera_x
                    screen_y = y * self.tile_size - camera_y
                    
                    # Grundfarbe
                    color = self.colors.get(tile["material"], (100, 100, 100))
                    
                    # Lichtlevel anwenden
                    light_level = self.get_light_level(x, y)
                    color = tuple(int(c * light_level) for c in color)
                    
                    # Wenn gesammelt, dunkler machen
                    if tile["collected"]:
                        color = tuple(max(0, c - 30) for c in color)
                    
                    # Tile zeichnen
                    pygame.draw.rect(screen, color,
                                   (screen_x, screen_y, self.tile_size, self.tile_size))
                    
                    # Spezielle Darstellung für Stein (geriffelt)
                    if tile["material"] == "Stein" and not tile["collected"]:
                        # Dunklere Linien für Riffel-Effekt
                        riffle_color = tuple(max(0, int(c * 0.7)) for c in color)
                        # Horizontale Linien alle 4 Pixel
                        for i in range(0, self.tile_size, 4):
                            pygame.draw.line(screen, riffle_color, 
                                           (screen_x, screen_y + i), 
                                           (screen_x + self.tile_size, screen_y + i), 1)
                        # Vertikale Linien alle 8 Pixel für Kreuzriffeln
                        for i in range(0, self.tile_size, 8):
                            pygame.draw.line(screen, riffle_color, 
                                           (screen_x + i, screen_y), 
                                           (screen_x + i, screen_y + self.tile_size), 1)
                    
                    # Spezielle Darstellung für Eisen (Metallglanz)
                    if tile["material"] == "Eisen" and not tile["collected"]:
                        # Hellere Punkte für Metallglanz
                        base_shine = tuple(min(255, c + 50) for c in self.colors["Eisen"])
                        shine_color = tuple(int(c * light_level) for c in base_shine)
                        # Diagonale Glanzpunkte
                        for i in range(4, self.tile_size - 4, 6):
                            for j in range(4, self.tile_size - 4, 6):
                                if (i + j) % 12 == 4:  # Diagonales Muster
                                    pygame.draw.circle(screen, shine_color,
                                                     (screen_x + i, screen_y + j), 1)
                    
                    # Spezielle Darstellung für Wald (Baum-Muster)
                    if tile["material"] == "Wald" and not tile["collected"]:
                        # Hellere Punkte für Baum-Textur
                        base_tree = tuple(min(255, c + 30) for c in self.colors["Wald"])
                        tree_color = tuple(int(c * light_level) for c in base_tree)
                        # Kleine Rechtecke als Bäume
                        for i in range(4, self.tile_size - 4, 8):
                            for j in range(4, self.tile_size - 4, 8):
                                pygame.draw.rect(screen, tree_color,
                                               (screen_x + i, screen_y + j, 4, 4))
                    
                    # Raster-Linien (optional, für 8-Bit Look)
                    pygame.draw.rect(screen, (50, 50, 50),
                                   (screen_x, screen_y, self.tile_size, self.tile_size), 1)
        
        # Gebäude zeichnen
        for (bx, by), building in self.buildings.items():
            if start_x <= bx < end_x and start_y <= by < end_y:
                screen_x = bx * self.tile_size - camera_x
                screen_y = by * self.tile_size - camera_y
                
                if building["type"] == "Lagerfeuer":
                    # Lagerfeuer als oranges Quadrat mit Flammen-Effekt
                    pygame.draw.rect(screen, (255, 140, 0),
                                   (screen_x, screen_y, self.tile_size, self.tile_size))
                    # Flammen-Punkte
                    for i in range(8, self.tile_size - 8, 4):
                        for j in range(8, self.tile_size - 8, 4):
                            pygame.draw.circle(screen, (255, 69, 0),
                                             (screen_x + i, screen_y + j), 2)
                            
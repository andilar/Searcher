import pygame
import sys
from player import Player
from world import World

class Game:
    def __init__(self):
        pygame.init()
        
        # Konstanten
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.TILE_SIZE = 32
        self.FPS = 60
        
        # Farben (8-Bit Stil)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        
        # Display Setup
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("8-Bit Mining Adventure")
        self.clock = pygame.time.Clock()
        
        # Font für UI
        self.font = pygame.font.Font(None, 36)
        
        # Spiel-Objekte
        self.world = World(self.TILE_SIZE)
        self.player = Player(self.world.spawn_x, self.world.spawn_y, self.TILE_SIZE)
        
        # Kamera
        self.camera_x = 0
        self.camera_y = 0
        
        # Baumenü
        self.build_menu_open = False
        self.selected_build_item = 0
        self.build_items = [
            {"name": "Lagerfeuer", "cost": {"Stein": 4, "Kohle": 4}}
        ]
        
    def update_camera(self):
        # Kamera folgt dem Spieler
        self.camera_x = self.player.x - self.SCREEN_WIDTH // 2
        self.camera_y = self.player.y - self.SCREEN_HEIGHT // 2
        
    def draw_ui(self):
        # Inventar anzeigen
        y_offset = 10
        inventory_text = self.font.render("Inventar:", True, self.WHITE)
        self.screen.blit(inventory_text, (10, y_offset))
        y_offset += 30
        
        for material, count in self.player.inventory.items():
            if count > 0:
                text = self.font.render(f"{material}: {count}", True, self.WHITE)
                self.screen.blit(text, (10, y_offset))
                y_offset += 25
                
        # Position anzeigen
        pos_text = self.font.render(f"Position: ({self.player.grid_x}, {self.player.grid_y})", True, self.WHITE)
        self.screen.blit(pos_text, (10, self.SCREEN_HEIGHT - 30))
        
        # Baumenü anzeigen
        if self.build_menu_open:
            self.draw_build_menu()
            
    def draw_build_menu(self):
        # Hintergrund für Baumenü
        menu_width = 300
        menu_height = 200
        menu_x = self.SCREEN_WIDTH - menu_width - 10
        menu_y = 10
        
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, self.WHITE, 
                        (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Titel
        title_text = self.font.render("Baumenü (B zum Schließen)", True, self.WHITE)
        self.screen.blit(title_text, (menu_x + 10, menu_y + 10))
        
        # Bauoptionen
        y_offset = menu_y + 50
        for i, item in enumerate(self.build_items):
            color = self.GREEN if i == self.selected_build_item else self.WHITE
            
            # Item Name
            item_text = self.font.render(f"{i+1}. {item['name']}", True, color)
            self.screen.blit(item_text, (menu_x + 10, y_offset))
            
            # Kosten anzeigen
            cost_y = y_offset + 25
            can_build = True
            for material, amount in item["cost"].items():
                player_amount = self.player.inventory.get(material, 0)
                cost_color = self.GREEN if player_amount >= amount else (255, 0, 0)
                if player_amount < amount:
                    can_build = False
                    
                cost_text = self.font.render(f"  {material}: {amount} ({player_amount})", True, cost_color)
                self.screen.blit(cost_text, (menu_x + 20, cost_y))
                cost_y += 20
            
            # Bauanweisung
            if i == self.selected_build_item:
                if can_build:
                    build_text = self.font.render("Drücke ENTER zum Bauen", True, self.GREEN)
                else:
                    build_text = self.font.render("Nicht genug Materialien", True, (255, 0, 0))
                self.screen.blit(build_text, (menu_x + 10, cost_y + 10))
            
            y_offset = cost_y + 40
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_b:
                    # Baumenü öffnen/schließen
                    self.build_menu_open = not self.build_menu_open
                elif self.build_menu_open:
                    # Baumenü Navigation
                    if event.key == pygame.K_1:
                        self.selected_build_item = 0
                    elif event.key == pygame.K_RETURN:
                        self.try_build_item()
                elif not self.build_menu_open:
                    # Normale Steuerung nur wenn Baumenü geschlossen
                    if event.key == pygame.K_SPACE:
                        # Feld rechts neben der Figur abbauen
                        self.player.mine_right(self.world)
                    elif event.key == pygame.K_w:
                        self.player.move(0, -1, self.world)
                    elif event.key == pygame.K_s:
                        self.player.move(0, 1, self.world)
                    elif event.key == pygame.K_a:
                        self.player.move(-1, 0, self.world)
                    elif event.key == pygame.K_d:
                        self.player.move(1, 0, self.world)
        
        return True
        
    def try_build_item(self):
        """Versucht das ausgewählte Item zu bauen"""
        if self.selected_build_item >= len(self.build_items):
            return
            
        item = self.build_items[self.selected_build_item]
        
        # Prüfen ob genug Materialien vorhanden
        can_build = True
        for material, amount in item["cost"].items():
            if self.player.inventory.get(material, 0) < amount:
                can_build = False
                break
        
        if can_build:
            # Materialien abziehen
            for material, amount in item["cost"].items():
                self.player.inventory[material] -= amount
            
            # Gebäude bauen
            if item["name"] == "Lagerfeuer":
                self.world.place_building(self.player.grid_x, self.player.grid_y, "Lagerfeuer")
            
            # Baumenü schließen
            self.build_menu_open = False
        
    def update(self):
        # Kamera aktualisieren
        self.update_camera()
        
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Welt zeichnen
        self.world.draw(self.screen, self.camera_x, self.camera_y, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Zielfläche (rechts neben dem Spieler) markieren
        target_x = self.player.grid_x + 1
        target_y = self.player.grid_y
        if self.world.is_valid_position(target_x, target_y):
            screen_x = target_x * self.TILE_SIZE - self.camera_x
            screen_y = target_y * self.TILE_SIZE - self.camera_y
            # Roten Rahmen um das Zielfeld zeichnen
            pygame.draw.rect(self.screen, (255, 0, 0), 
                           (screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE), 3)
        
        # Spieler zeichnen
        self.player.draw(self.screen, self.camera_x, self.camera_y)
        
        # UI zeichnen
        self.draw_ui()
        
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
    
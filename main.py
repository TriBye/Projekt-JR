import arcade
import time

class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(832, 624, "Plattformer")
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Tilemaps laden und Szene erstellen.
        self.tilemap = arcade.load_tilemap("karte.tmx")
        self.tilemap_2 = arcade.load_tilemap("karte_2.tmx")
        self.scene = arcade.Scene.from_tilemap(self.tilemap)

        # Spieler-Sprite erstellen und zur Szene hinzufügen.
        self.player = arcade.Sprite("player.png", scale=1.6)
        self.player.center_x = self.width // 2
        self.player.center_y = 400
        self.scene.add_sprite("Spieler", self.player)

        # Spielzustand: Zunächst ist das Spiel nicht aktiv.
        self.alive = False
        self.dimension = 1

        # Lade das Tab-Bild.
        self.tab = arcade.load_texture("tab.png")
        self.show_tab = False  # Flag, ob das Tab-Bild angezeigt werden soll.

        # Letzte gültige Position für Respawn.
        self.last_x = self.player.center_x
        self.last_y = self.player.center_y

        self.got_boot = False
        self.got_key = False
        self.coins = 0

        # Maximale Sprünge (1 bedeutet, dass nur ein Sprung möglich ist, bis der Boden berührt wird).
        self.max_jumps = 1

        self.player_speed = 2.5
        self.camera_y_fixed = 0

        # FPS-Berechnungswerte.
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

        # Plattformen abrufen und Spatial Hashing aktivieren.
        platforms = self.scene.get_sprite_list("Tile Layer 1")
        platforms.enable_spatial_hashing()

        # Physics Engine erstellen.
        self.physik = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms,
            gravity_constant=0.35,
            ladders=self.scene.get_sprite_list("leiter")
        )
        self.physik.enable_multi_jump(self.max_jumps)

        # Dictionary, um den Status der gedrückten Tasten zu speichern.
        self.keys_pressed = {}

    def reset_game(self):
        self.alive = True
        # Spielerposition und -geschwindigkeit zurücksetzen.
        self.lives = 3
        self.player.center_x = self.width // 2
        self.player.center_y = 400
        self.player.change_x = 0
        self.player.change_y = 0
        # Letzte gültige Position zurücksetzen.
        self.last_x = self.player.center_x
        self.last_y = self.player.center_y
        # Maximale Sprünge zurücksetzen.
        self.max_jumps = 1
        self.physik.enable_multi_jump(self.max_jumps)
        # Die Szene (Tilemap) wird auf die erste zurückgesetzt.
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        # Spieler-Sprite wieder zur Szene hinzufügen:
        self.scene.add_sprite("Spieler", self.player)
        # Tasteneingaben leeren.
        self.keys_pressed.clear()


    def on_key_press(self, symbol, modifiers):
        # Wenn das Spiel noch nicht aktiv ist, prüfe, ob ENTER gedrückt wird.
        if not self.alive:
            if symbol == arcade.key.ENTER:
                self.reset_game()
            return

        # Markiere die Taste als gedrückt.
        self.keys_pressed[symbol] = True

        # Aktionen, die direkt ausgelöst werden (z. B. Sprung, Teleport, etc.).
        if symbol == arcade.key.SPACE:
            if self.physik.can_jump() and not self.physik.is_on_ladder():
                self.physik.jump(5)
        elif symbol == arcade.key.W:
            if self.physik.is_on_ladder():
                self.player.change_y = 2
        elif symbol == arcade.key.S:
            if self.physik.is_on_ladder():
                self.player.change_y = -2
        elif symbol == arcade.key.R:
            self.reset_game()
        elif symbol == arcade.key.T:
            self.player.center_x = self.last_x
            self.player.center_y = self.last_y + 100
        elif symbol == arcade.key.L:
            self.max_jumps += 1
            self.physik.enable_multi_jump(self.max_jumps)
        elif symbol == arcade.key.TAB:
            self.show_tab = not self.show_tab
        elif symbol == arcade.key.PLUS:
            self.scene = arcade.Scene.from_tilemap(self.tilemap)
        elif symbol == arcade.key.MINUS:
            self.scene = arcade.Scene.from_tilemap(self.tilemap_2)

        self.update_horizontal_movement()

    def on_key_release(self, symbol, modifiers):
        if not self.alive:
            return
        # Markiere die Taste als losgelassen.
        self.keys_pressed[symbol] = False
        self.update_horizontal_movement()
        if symbol in (arcade.key.W, arcade.key.S):
            self.player.change_y = 0

    def update_horizontal_movement(self):
        if not self.alive:
            return
        a_pressed = self.keys_pressed.get(arcade.key.A, False)
        d_pressed = self.keys_pressed.get(arcade.key.D, False)
        if a_pressed and not d_pressed:
            self.player.change_x = -self.player_speed
            self.player.texture = arcade.load_texture("player-back.png")
        elif d_pressed and not a_pressed:
            self.player.change_x = self.player_speed
            self.player.texture = arcade.load_texture("player.png")
        else:
            self.player.change_x = 0

    def on_update(self, delta_time):
        if not self.alive:
            return

        self.scene.update()
        self.physik.update()

        if self.physik.can_jump():
            self.last_x = self.player.center_x
            self.last_y = self.player.center_y
        
        if self.player.center_y <= -10:
            if self.lives >= 2:
                self.lives -= 1
                self.player.center_x = self.width // 2
                self.player.center_y = 400
            else:   
                self.alive = False

    def on_draw(self):
        self.clear()
        if not self.alive:
            # Zeichne den Startbildschirm.
            arcade.draw_text("Drücke ENTER zum Starten",
                             self.width / 2,
                             self.height / 2,
                             arcade.color.WHITE,
                             20,
                             anchor_x="center",
                             anchor_y="center")
            return

        # Setze den Viewport, sodass die Kamera dem Spieler folgt.
        left = max(0, self.player.center_x - self.width // 2)
        right = left + self.width
        bottom = self.camera_y_fixed
        top = bottom + self.height
        arcade.set_viewport(left, right, bottom, top)
        self.scene.draw()

        # FPS-Berechnung.
        current_time = time.time()
        self.frame_count += 1
        if current_time - self.last_time > 1.0:
            self.fps = self.frame_count / (current_time - self.last_time)
            self.last_time = current_time
            self.frame_count = 0

        # HUD zeichnen: Viewport auf Fensterkoordinaten zurücksetzen.
        arcade.set_viewport(0, self.width, 0, self.height)
        fps_text = f"FPS: {self.fps:.1f}"
        arcade.draw_text(fps_text,
                         self.width / 2,
                         self.height - 20,
                         arcade.color.BLACK,
                         14,
                         anchor_x="center")

        arcade.draw_rectangle_filled(80, 600, 50*self.lives, 30, arcade.color.RED)
        arcade.draw_rectangle_outline(80, 600, 150, 30, arcade.color.BLACK, 3)
        arcade.draw_text(self.lives, 75, 590, arcade.color.WHITE, 20)

        # Zeichne das Tab-Bild, falls aktiviert.
        if self.show_tab:
            arcade.draw_texture_rectangle(self.width / 2,
                                          self.height / 2,
                                          self.tab.width,
                                          self.tab.height,
                                          self.tab)

def main():
    Platformer()
    arcade.run()

if __name__ == "__main__":
    main()
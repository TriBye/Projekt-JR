import arcade
import time
import os

# --- Button Class Definition ---
class Button:
    def __init__(self, left, top, width, height, text,
                 default_color, hover_color, border_color, text_color, font_size=20):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.text = text
        self.default_color = default_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.text_color = text_color
        self.font_size = font_size
        self.is_hovered = False

    def draw(self):
        center_x = self.left + self.width / 2
        center_y = self.top - self.height / 2
        color = self.hover_color if self.is_hovered else self.default_color
        arcade.draw_rectangle_filled(center_x, center_y, self.width, self.height, color)
        arcade.draw_rectangle_outline(center_x, center_y, self.width, self.height, self.border_color, 2)
        arcade.draw_text(self.text, center_x, center_y, self.text_color,
                         self.font_size, anchor_x="center", anchor_y="center")

    def is_mouse_over(self, x, y):
        return (self.left <= x <= self.left + self.width) and (self.top - self.height <= y <= self.top)

class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(832, 624, "Plattformer")
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.tilemap = arcade.load_tilemap("karte.tmx")
        self.tilemap_2 = arcade.load_tilemap("karte_2.tmx")
        self.scene = arcade.Scene.from_tilemap(self.tilemap)

        self.player = arcade.Sprite("images/player.png", scale=1.6)
        self.player.center_x = self.width // 2
        self.player.center_y = 400
        self.scene.add_sprite("Spieler", self.player)

        self.alive = False  
        self.dimension = 1

        self.tab = arcade.load_texture("images/tab.png")
        self.show_tab = False  
        self.trade = arcade.load_texture("images/trade.png")

        self.start_screen = True     # True when showing the start screen.
        self.game_over = False       # True when in game-over mode.
        self.start_screen_image = arcade.load_texture("images/start_screen.png")
        self.game_over_image = arcade.load_texture("images/game_over.png")

        # Create start screen buttons.
        self.start_buttons = []
        default_btn_color = arcade.color.WHITE
        hover_btn_color = arcade.color.GRAY
        default_btn_color_2 = (12, 192, 223)
        hover_btn_color_2 = (0, 151, 178)
        border_color = arcade.color.WHITE
        text_color = (255, 49, 49)  # #ff3131
        self.start_buttons.append(Button(166, 424, 500, 100, "Start Game",
                                           default_btn_color_2, hover_btn_color_2, border_color, (255,255,255), font_size=30))
        self.start_buttons.append(Button(166, 299, 500, 100, "Load Game",
                                           default_btn_color_2, hover_btn_color_2, border_color, (255,255,255), font_size=30))
        self.start_buttons.append(Button(166, 174, 500, 100, "Info / Credits",
                                           default_btn_color_2, hover_btn_color_2, border_color, (255,255,255), font_size=30))

        # Create game-over screen buttons.
        self.game_over_buttons = []
        self.game_over_buttons.append(Button(266, 349, 300, 50, "Respawn (R)",
                                               default_btn_color, hover_btn_color, border_color, text_color, font_size=20))
        self.game_over_buttons.append(Button(266, 280, 300, 50, "Menu",
                                               default_btn_color, hover_btn_color, border_color, text_color, font_size=20))

        # Last valid respawn position.
        self.last_x = self.player.center_x
        self.last_y = self.player.center_y

        self.got_boot = False
        self.got_key = False

        self.coins = 0
        self.coin_spawns = self.scene.get_sprite_list("Coins")

        # Trader sprite list (from the tilemap layer "Trader").
        self.trader = self.scene.get_sprite_list("Trader")

        self.lives = 3
        self.max_jumps = 1
        self.jumps = self.max_jumps

        self.player_speed = 2.5
        self.camera_y_fixed = 0
        self.camera_mode = 1

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.legit = True

        self.save_mode = False
        self.load_mode = False

        platforms = self.scene.get_sprite_list("Tile Layer 1")
        platforms.enable_spatial_hashing()

        self.safe_points = self.scene.get_sprite_list("Safe Points")
        self.safe_point = [self.player.center_x, self.player.center_y]

        self.physik = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms,
            gravity_constant=0.35,
            ladders=self.scene.get_sprite_list("leiter")
        )
        self.physik.enable_multi_jump(self.max_jumps)

        self.keys_pressed = {}

    def restart_game(self):
        """Completely restart the game (for start screen)."""
        self.alive = True
        self.game_over = False
        self.lives = 3
        self.coins = 0
        self.max_jumps = 1
        self.jumps = self.max_jumps
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        self.scene.add_sprite("Spieler", self.player)
        self.player.center_x = self.width // 2
        self.player.center_y = 400
        self.player.change_x = 0
        self.player.change_y = 0
        self.safe_point = [self.player.center_x, self.player.center_y]
        self.last_x = self.player.center_x
        self.last_y = self.player.center_y
        self.physik.enable_multi_jump(self.max_jumps)
        self.keys_pressed.clear()

    def respawn(self):
        """Respawn the player at the last safe point (without reloading the scene)."""
        self.player.center_x = self.safe_point[0]
        self.player.center_y = self.safe_point[1]
        self.player.change_x = 0
        self.player.change_y = 0
        self.physik.enable_multi_jump(self.max_jumps)
        self.jumps = self.max_jumps

    def load_game_mode(self):
        self.load_mode = True

    def save_game_mode(self):
        self.save_mode = True

    # --- Mouse Event Handlers for Start Screen and Game Over Screen ---
    def on_mouse_motion(self, x, y, dx, dy):
        if self.start_screen:
            for button in self.start_buttons:
                button.is_hovered = button.is_mouse_over(x, y)
        elif self.game_over:
            for button in self.game_over_buttons:
                button.is_hovered = button.is_mouse_over(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.start_screen:
            for btn in self.start_buttons:
                if btn.is_mouse_over(x, y):
                    if btn.text == "Start Game":
                        self.start_screen = False
                        self.alive = True
                        self.restart_game()
                    elif btn.text == "Load Game":
                        self.start_screen_image = arcade.load_texture("images/load_game.png")
                        self.start_buttons = []  # Remove buttons so only image is displayed.
                    elif btn.text == "Info / Credits":
                        # You may implement an info screen here.
                        pass
                    break
        elif self.game_over:
            for btn in self.game_over_buttons:
                if btn.is_mouse_over(x, y):
                    if btn.text == "Respawn (R)":
                        self.respawn()
                        self.alive = True
                        self.game_over = False
                    elif btn.text == "Menu":
                        self.start_screen = True
                        self.game_over = False
                        self.alive = False
                    break

    def on_key_press(self, symbol, modifiers):
        # If on the start screen, ignore normal key presses.
        if self.start_screen:
            return

        # If game over, allow respawn by pressing R.
        if self.game_over:
            if symbol == arcade.key.R:
                self.respawn()
                self.alive = True
                self.game_over = False
            return

        # If the game is not active (but not in start screen), check for ENTER to restart.
        if not self.alive:
            if symbol == arcade.key.ENTER:
                self.restart_game()
            return

        # --- Save Mode ---
        if self.save_mode:
            if not os.path.exists("saves"):
                os.makedirs("saves")
            if arcade.key.KEY_0 <= symbol <= arcade.key.KEY_9:
                digit = symbol - arcade.key.KEY_0
                filename = os.path.join("saves", f"core.txt{digit}")
                with open(filename, "w", encoding="utf-8") as datei:
                    datei.write(f"{self.coins}\n")
                    datei.write(f"{self.lives}\n")
                    datei.write(f"{self.max_jumps}\n")
                    datei.write(f"{self.player.center_x}\n")
                    datei.write(f"{self.player.center_y}\n")
                    datei.write(f"{self.legit}\n")
                self.save_mode = False
            return

        # --- Load Mode ---
        if self.load_mode:
            if not os.path.exists("saves"):
                self.load_mode = False
            else:
                if arcade.key.KEY_0 <= symbol <= arcade.key.KEY_9:
                    digit = symbol - arcade.key.KEY_0
                    filename = os.path.join("saves", f"core.txt{digit}")
                    try:
                        with open(filename, "r", encoding="utf-8") as datei:
                            lines = datei.readlines()
                        self.coins = int(lines[0].strip())
                        self.lives = int(lines[1].strip())
                        self.max_jumps = int(lines[2].strip())
                        self.jumps = self.max_jumps
                        self.player.center_x = float(lines[3].strip())
                        self.player.center_y = float(lines[4].strip())
                        self.legit = lines[5].strip() == "True"
                        self.physik.enable_multi_jump(self.max_jumps)
                    except Exception as e:
                        print("Error loading game:", e)
                    self.load_mode = False
            return

        self.keys_pressed[symbol] = True

        if symbol == arcade.key.SPACE:
            if self.physik.can_jump() and not self.physik.is_on_ladder():
                self.physik.jump(5)
                self.jumps = max(0, self.jumps - 1)
        elif symbol == arcade.key.W:
            if self.physik.is_on_ladder():
                self.player.change_y = 2
        elif symbol == arcade.key.S:
            if self.physik.is_on_ladder():
                self.player.change_y = -2
        elif symbol == arcade.key.R:
            self.respawn()
        elif symbol == arcade.key.T:
            self.legit = False
            self.player.center_x = self.last_x
            self.player.center_y = self.last_y + 100
        elif symbol == arcade.key.L:
            self.legit = False
            self.max_jumps += 1
            self.physik.enable_multi_jump(self.max_jumps)
        elif symbol == arcade.key.TAB:
            self.show_tab = not self.show_tab
        elif symbol == arcade.key.PLUS:
            self.scene = arcade.Scene.from_tilemap(self.tilemap)
        elif symbol == arcade.key.MINUS:
            self.scene = arcade.Scene.from_tilemap(self.tilemap_2)
        elif symbol == arcade.key.LCTRL:
            self.save_game_mode()
        elif symbol == arcade.key.LALT:
            self.load_game_mode()
        elif symbol == arcade.key.K:
            self.camera_mode = 2 if self.camera_mode == 1 else 1
        elif symbol == arcade.key.P:
            print(self.player.center_x, self.player.center_y)
        
        self.update_horizontal_movement()

    def on_key_release(self, symbol, modifiers):
        if not self.alive:
            return
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
            self.player.texture = arcade.load_texture("images/player-back.png")
        elif d_pressed and not a_pressed:
            self.player.change_x = self.player_speed
            self.player.texture = arcade.load_texture("images/player.png")
        else:
            self.player.change_x = 0

    def on_update(self, delta_time):
        if self.start_screen:
            return
        if not self.alive:
            return

        self.scene.update()
        self.physik.update()

        if self.physik.can_jump():
            self.last_x = self.player.center_x
            self.last_y = self.player.center_y
            self.jumps = self.max_jumps

        if self.player.center_y <= -10:
            if self.lives > 1:
                self.lives -= 1
                self.respawn()
            else:
                self.alive = False
                self.game_over = True

        if arcade.check_for_collision_with_list(self.player, self.safe_points):
            self.safe_point = [self.player.center_x, self.player.center_y]

        coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_spawns)
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.coins += 1

    def on_draw(self):
        # Draw Start Screen if active.
        if self.start_screen:
            self.clear()
            arcade.draw_texture_rectangle(self.width/2, self.height/2, self.width, self.height, self.start_screen_image)
            for btn in self.start_buttons:
                btn.draw()
            return

        # Draw Save Mode screen.
        if self.save_mode:
            self.clear(arcade.color.LIGHT_BLUE)
            arcade.draw_text("Select a Save Slot to Save!",
                             self.width/2, self.height/2,
                             arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")
            return

        # Draw Load Mode screen.
        if self.load_mode:
            self.clear(arcade.color.LIGHT_BLUE)
            arcade.draw_text("Select a Save Slot to Load!",
                             self.width/2, self.height/2,
                             arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")
            return

        # Draw Game Over screen if not alive and game_over is True.
        if not self.alive and hasattr(self, "game_over") and self.game_over:
            self.clear()
            arcade.draw_texture_rectangle(self.width/2, self.height/2, self.width, self.height, self.game_over_image)
            for btn in self.game_over_buttons:
                btn.draw()
            return

        # Normal game drawing.
        self.clear()
        if self.camera_mode == 1:
            left = max(0, self.player.center_x - self.width // 2)
            right = left + self.width
            bottom = self.camera_y_fixed
            top = bottom + self.height
        else:
            left = max(0, self.player.center_x - self.width // 4)
            right = left + self.width // 2
            bottom = max(0, self.player.center_y - self.height // 4)
            top = bottom + self.height // 2
        arcade.set_viewport(left, right, bottom, top)
        self.scene.draw()

        current_time = time.time()
        self.frame_count += 1
        if current_time - self.last_time > 1.0:
            self.fps = self.frame_count / (current_time - self.last_time)
            self.last_time = current_time
            self.frame_count = 0

        arcade.set_viewport(0, self.width, 0, self.height)
        fps_text = f"FPS: {self.fps:.1f}"
        arcade.draw_text(fps_text,
                         self.width/2,
                         self.height - 20,
                         arcade.color.BLACK,
                         14, anchor_x="center")

        arcade.draw_rectangle_filled(80, 600, 50*self.lives, 30, arcade.color.RED)
        arcade.draw_rectangle_outline(80, 600, 150, 30, arcade.color.BLACK, 3)
        arcade.draw_text(str(self.lives),
                         75, 590, arcade.color.WHITE, 20)
        
        arcade.draw_text(f"{self.coins}", 800, 600, arcade.color.WHITE, 20)

        outline_width = 500
        bar_height = 30
        bar_center_x = 416
        bar_center_y = 50
        arcade.draw_rectangle_outline(bar_center_x, bar_center_y, outline_width, bar_height, arcade.color.WHITE, 2)
        fill_ratio = self.jumps / self.max_jumps if self.max_jumps > 0 else 0
        filled_width = outline_width * fill_ratio
        arcade.draw_rectangle_filled(bar_center_x, bar_center_y, filled_width, bar_height, arcade.color.LIGHT_STEEL_BLUE)

        if self.show_tab:
            arcade.draw_texture_rectangle(self.width/2,
                                          self.height/2,
                                          self.tab.width,
                                          self.tab.height,
                                          self.tab)

        if arcade.check_for_collision_with_list(self.player, self.safe_points):
            arcade.draw_text("Spawnpoint Updated", 360, self.player.center_y + 50, arcade.color.WHITE, 10)
        
        colliding_traders = arcade.check_for_collision_with_list(self.player, self.trader)
        if colliding_traders:
            for trader_sprite in colliding_traders:
                arcade.draw_texture_rectangle(
                    trader_sprite.center_x,
                    trader_sprite.center_y + 50,
                    self.trade.width,
                    self.trade.height,
                    self.trade
                )

    def on_mouse_motion(self, x, y, dx, dy):
        if self.start_screen:
            for button in self.start_buttons:
                button.is_hovered = button.is_mouse_over(x, y)
        elif not self.alive and hasattr(self, "game_over") and self.game_over:
            for button in self.game_over_buttons:
                button.is_hovered = button.is_mouse_over(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.start_screen:
            for btn in self.start_buttons:
                if btn.is_mouse_over(x, y):
                    if btn.text == "Start Game":
                        self.start_screen = False
                        self.alive = True
                        self.game_over = False
                        self.restart_game()
                    elif btn.text == "Load Game":
                        self.load_mode = True
                        self.start_screen = False
                    elif btn.text == "Info / Credits":
                        pass
                    break
        elif not self.alive and hasattr(self, "game_over") and self.game_over:
            for btn in self.game_over_buttons:
                if btn.is_mouse_over(x, y):
                    if btn.text == "Respawn (R)":
                        self.respawn()
                        self.alive = True
                        self.game_over = False
                    elif btn.text == "Menu":
                        self.start_screen = True
                        self.game_over = False
                        self.alive = False
                    break

def main():
    Platformer()
    arcade.run()

if __name__ == "__main__":
    main()
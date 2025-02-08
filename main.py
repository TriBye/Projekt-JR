import arcade
import time
import os
import arcade.color

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

        self.last_x = self.player.center_x
        self.last_y = self.player.center_y

        self.got_boot = False
        self.got_key = False

        self.coins = 0
        self.coin_spawns = self.scene.get_sprite_list("Coins")

        self.trader = self.scene.get_sprite_list("Trader")

        self.lives = 3
        self.max_jumps = 1
        self.jumps = 1

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
        """
        Completely restart the game (reloads the tilemap, resets coins, lives, etc.).
        This is used at the start of the game.
        """
        self.alive = True
        self.lives = 3
        self.coins = 0
        self.max_jumps = 1
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
        self.player.center_x = self.safe_point[0]
        self.player.center_y = self.safe_point[1]
        self.player.change_x = 0
        self.player.change_y = 0
        self.physik.enable_multi_jump(self.max_jumps)

    def load_game(self):
        self.load_mode = True

    def save_game(self):
        self.save_mode = True

    def on_key_press(self, symbol, modifiers):
        if not self.alive:
            if symbol == arcade.key.ENTER:
                self.restart_game()
            return

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
                self.jumps -= 1
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
            self.save_game()
        elif symbol == arcade.key.LALT:
            self.load_game()
        elif symbol == arcade.key.K:
            self.camera_mode = 2 if self.camera_mode == 1 else 1
        elif symbol == arcade.key.P:
            print(self.player.center_x, self.player.center_y)
        
        elif symbol == arcade.key.ENTER and arcade.check_for_collision_with_list(self.player, self.trader):
            if self.coins >= 6:
                self.max_jumps = 3
                self.coins -= 6
            elif self.coins >= 4:
                self.max_jumps = 2
                self.coins -= 4

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
        if not self.alive:
            return

        self.scene.update()
        self.physik.update()

        if self.physik.can_jump():
            self.last_x = self.player.center_x
            self.last_y = self.player.center_y

        if self.player.center_y <= -10:
            if self.lives > 1:
                self.lives -= 1
                self.respawn()
            else:
                self.alive = False

        if arcade.check_for_collision_with_list(self.player, self.safe_points):
            self.safe_point = [self.player.center_x, self.player.center_y]

        coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_spawns)
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.coins += 1

        self.physik.enable_multi_jump(self.max_jumps)
        self.jumps = self.max_jumps

    def on_draw(self):
        if self.save_mode:
            self.clear(arcade.color.LIGHT_BLUE)
            arcade.draw_text("Select a Save Slot to Save!",
                             self.width/2, self.height/2,
                             arcade.color.WHITE, 20,
                             anchor_x="center", anchor_y="center")
            return

        if self.load_mode:
            self.clear(arcade.color.LIGHT_BLUE)
            arcade.draw_text("Select a Save Slot to Load!",
                             self.width/2, self.height/2,
                             arcade.color.WHITE, 20,
                             anchor_x="center", anchor_y="center")
            return

        if not self.alive:
            self.clear(arcade.color.LIGHT_BLUE)
            arcade.draw_text("Press ENTER to Respawn",
                             self.width/2, self.height/2,
                             arcade.color.WHITE, 20,
                             anchor_x="center", anchor_y="center")
            return

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
        
        outline_width = 500
        bar_height = 30
        bar_center_x = 416
        bar_center_y = 50

        arcade.draw_rectangle_outline(bar_center_x, bar_center_y, outline_width, bar_height, arcade.color.WHITE, 2)
        if self.jumps == 0:
            fill_ratio = 0
        else:
            fill_ratio = self.jumps / self.max_jumps   
        filled_width = outline_width * fill_ratio
        arcade.draw_rectangle_filled(bar_center_x, bar_center_y, filled_width, bar_height, arcade.color.LIGHT_STEEL_BLUE)
        
        arcade.draw_text(f"{self.coins}", 800, 600, arcade.color.WHITE, 20)

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

def main():
    Platformer()
    arcade.run()

if __name__ == "__main__":
    main()
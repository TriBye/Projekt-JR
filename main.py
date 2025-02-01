import arcade
import time

class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(832, 624, "Plattformer")

        arcade.set_background_color(arcade.color.SKY_BLUE)

        tilemap = arcade.load_tilemap("karte.tmx")
        self.scene = arcade.Scene.from_tilemap(tilemap)

        self.player = arcade.Sprite("player.png", scale=1)
        self.player.x = self.width // 2
        self.player.y = 400
        self.player.center_x = self.player.x
        self.player.center_y = self.player.y
        self.scene.add_sprite("Spieler", self.player)

        self.last_x = self.width // 2
        self.last_y = 400

        self.got_boot = False
        self.got_key = False

        self.max_jumps = 1

        self.player_speed = 2.5
        self.camera_y_fixed = 0 

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.fps_display = arcade.Text("", 10, self.height - 20, arcade.color.BLACK, 14)

        plattformen = self.scene.get_sprite_list("Tile Layer 1")
        plattformen.enable_spatial_hashing()

        self.physik = arcade.PhysicsEnginePlatformer(self.player, plattformen, 0.35, self.scene.get_sprite_list("leiter"))

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.A:
            self.player.change_x = -self.player_speed
        elif symbol == arcade.key.D:
            self.player.change_x = self.player_speed
        elif symbol == arcade.key.C:
            self.player.change_x = -1
        elif symbol == arcade.key.V:
            self.player.change_x = 1
        elif symbol == arcade.key.SPACE:
            if self.physik.can_jump() == True and self.physik.is_on_ladder() == False:
                self.player.change_y += 5
        elif symbol == arcade.key.W:
            if self.physik.is_on_ladder() == True:
                self.player.change_y = 2
        elif symbol == arcade.key.S:
            if self.physik.is_on_ladder() == True:
                self.player.change_y = -2


        if symbol == arcade.key.R:
            self.player.center_x = self.width // 2
            self.player.center_y = 400
            #self.camera.move_to((self.player.center_x - self.width // 2, self.camera_y_fixed))
            self.max_jumps = 1

        if symbol == arcade.key.T:
            self.player.center_x = self.last_x
            self.player.center_y = self.last_y + 100
            #self.camera.move_to((self.player.center_x - self.width // 2, self.camera_y_fixed))

        if symbol == arcade.key.L:
            self.max_jumps += 1
            

    def on_key_release(self, symbol, modifiers):
        if symbol in (arcade.key.A, arcade.key.D, arcade.key.C, arcade.key.V):
            self.player.change_x = 0
        if symbol in (arcade.key.W, arcade.key.S):
            self.player.change_y = 0

    def on_update(self, delta_time):
        self.scene.update()
        self.physik.update()

        #if self.player.center_x > self.width // 2 and self.player.center_y >= 0:
        #   self.camera.move_to((self.player.center_x - self.width // 2, self.camera_y_fixed))

        if self.physik.can_jump():
            self.last_x = self.player.center_x
            self.last_y = self.player.center_y
        
        self.physik.enable_multi_jump(self.max_jumps)

    def on_draw(self):
        self.clear()
        self.scene.draw()

        left = self.player.center_x - self.width // 2
        right = self.player.center_x + self.width // 2

        bottom = self.camera_y_fixed
        top = self.camera_y_fixed + self.height

        arcade.set_viewport(left, right, bottom, top)

        current_time = time.time()
        self.frame_count += 1
        if current_time - self.last_time > 1.0:
            self.fps = self.frame_count / (current_time - self.last_time)
            self.last_time = current_time
            self.frame_count = 0

        if self.player.center_x > self.width // 2 and self.player.center_y >= 0:
            self.fps_display = arcade.Text("", self.player.x - 40,self.height - 20, arcade.color.BLACK, 14)
            self.fps_display.text = f"FPS: {self.fps:.1f}"
            self.fps_display.draw()
        else:
            self.fps_display = arcade.Text("", self.width // 2 - 40,self.height - 20, arcade.color.BLACK, 14)
            self.fps_display.text = f"FPS: {self.fps:.1f}"
            self.fps_display.draw()

Platformer()
arcade.run()

#jump fixen
#map fixen
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

        self.camera = arcade.Camera(self.width, self.height)
        self.player_speed = 5
        self.gravity = -1
        self.is_on_ground = False
        self.camera_y_fixed = 0 

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.fps_display = arcade.Text("", 10, self.height - 20, arcade.color.BLACK, 14)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.A:
            self.player.change_x = -self.player_speed
        elif symbol == arcade.key.D:
            self.player.change_x = self.player_speed
        elif symbol == arcade.key.SPACE:
            if self.is_on_ground == True:
                self.player.change_y += 10


        if symbol == arcade.key.R:
            self.player.x = self.width // 2
            self.player.y = 400
            self.camera.move_to((self.player.x - self.width // 2, self.camera_y_fixed))

    def on_key_release(self, symbol, modifiers):
        if symbol in (arcade.key.A, arcade.key.D):
            self.player.change_x = 0

    def on_update(self, delta_time):
        self.player.x += self.player.change_x
        self.player.y += self.player.change_y
        self.player.center_x = self.player.x
        self.player.center_y = self.player.y


        

        if self.player.x > self.width // 2 and self.player.y >= 0:
            self.camera.move_to((self.player.x - self.width // 2, self.camera_y_fixed))

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()

        current_time = time.time()
        self.frame_count += 1
        if current_time - self.last_time > 1.0:
            self.fps = self.frame_count / (current_time - self.last_time)
            self.last_time = current_time
            self.frame_count = 0

        if self.player.x > self.width // 2 and self.player.y >= 0:
            self.fps_display = arcade.Text("", self.player.x - 40,self.height - 20, arcade.color.BLACK, 14)
            self.fps_display.text = f"FPS: {self.fps:.1f}"
            self.fps_display.draw()
        else:
            self.fps_display = arcade.Text("", self.width // 2 - 40,self.height - 20, arcade.color.BLACK, 14)
            self.fps_display.text = f"FPS: {self.fps:.1f}"
            self.fps_display.draw()
Platformer()
arcade.run()
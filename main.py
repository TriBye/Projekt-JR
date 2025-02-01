import arcade
import time

class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(832, 624, "Plattformer")
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Load tilemap and create the scene.
        tilemap = arcade.load_tilemap("karte.tmx")
        self.scene = arcade.Scene.from_tilemap(tilemap)

        # Create the player sprite and add it to the scene.
        self.player = arcade.Sprite("player.png", scale=1)
        self.player.center_x = self.width // 2
        self.player.center_y = 400
        self.scene.add_sprite("Spieler", self.player)

        # Last valid position for respawn.
        self.last_x = self.player.center_x
        self.last_y = self.player.center_y

        self.got_boot = False
        self.got_key = False

        # Maximum number of jumps (1 means only one jump until you touch the ground).
        self.max_jumps = 1

        self.player_speed = 2.5
        self.camera_y_fixed = 0 

        # FPS calculation values.
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

        # Get the platform sprites and enable spatial hashing.
        platforms = self.scene.get_sprite_list("Tile Layer 1")
        platforms.enable_spatial_hashing()

        # Create the physics engine.
        self.physik = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms,
            gravity_constant=0.35,
            ladders=self.scene.get_sprite_list("leiter")
        )
        # Enable multi-jump with the initial max_jumps count.
        self.physik.enable_multi_jump(self.max_jumps)

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
            # Only allow jump if the player can jump and is not on a ladder.
            if self.physik.can_jump() and not self.physik.is_on_ladder():
                self.player.change_y = 5
        elif symbol == arcade.key.W:
            if self.physik.is_on_ladder():
                self.player.change_y = 2
        elif symbol == arcade.key.S:
            if self.physik.is_on_ladder():
                self.player.change_y = -2

        if symbol == arcade.key.R:
            self.player.center_x = self.width // 2
            self.player.center_y = 400
            self.max_jumps = 1
            # Update the multi-jump setting upon reset.
            self.physik.enable_multi_jump(self.max_jumps)

        if symbol == arcade.key.T:
            self.player.center_x = self.last_x
            self.player.center_y = self.last_y + 100

        # Increase max jumps by 1 when L is pressed.
        if symbol == arcade.key.L:
            self.max_jumps += 1
            self.physik.enable_multi_jump(self.max_jumps)

    def on_key_release(self, symbol, modifiers):
        if symbol in (arcade.key.A, arcade.key.D, arcade.key.C, arcade.key.V):
            self.player.change_x = 0
        if symbol in (arcade.key.W, arcade.key.S):
            self.player.change_y = 0

    def on_update(self, delta_time):
        self.scene.update()
        self.physik.update()

        # When the player is on the ground, update the last valid position.
        if self.physik.can_jump():
            self.last_x = self.player.center_x
            self.last_y = self.player.center_y
        # (Do not call enable_multi_jump here, so the jump count isn't reset every frame!)

    def on_draw(self):
        self.clear()

        # --- Set the viewport so that the camera follows the player.
        # Clamp the left boundary to 0 so the camera doesn't go past the left edge.
        left = max(0, self.player.center_x - self.width // 2)
        right = left + self.width
        bottom = self.camera_y_fixed
        top = bottom + self.height

        arcade.set_viewport(left, right, bottom, top)
        self.scene.draw()

        # --- FPS calculation.
        current_time = time.time()
        self.frame_count += 1
        if current_time - self.last_time > 1.0:
            self.fps = self.frame_count / (current_time - self.last_time)
            self.last_time = current_time
            self.frame_count = 0

        # --- Draw the HUD (FPS display) centered on the screen.
        arcade.set_viewport(0, self.width, 0, self.height)
        fps_text = f"FPS: {self.fps:.1f}"
        arcade.draw_text(fps_text,
                         self.width / 2,         # x coordinate (center of the window)
                         self.height - 20,       # y coordinate near the top
                         arcade.color.BLACK,
                         14,
                         anchor_x="center")

def main():
    Platformer()
    arcade.run()

if __name__ == "__main__":
    main()  
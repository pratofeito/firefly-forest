import random
from pathlib import Path
from pyglet.math import Vec2

import arcade
from arcade.experimental import Shadertoy

import math
import os

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Ray-casting Demo"

SPRITE_SCALING = 0.4

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.2
PLAYER_MOVEMENT_SPEED = 5
COIN_COUNT = 50
COIN_SPEED = 15
PLAYING_FIELD_WIDTH = 1600
PLAYING_FIELD_HEIGHT = 1600

class Coin(arcade.Sprite):
    """
    This class represents the coins on our screen. It is a child class of
    the arcade library's "Sprite" class.
    """
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        # Flip this once the coin has been collected.
        self.followed = False

        # Current angle in radians
        self.circle_angle = 0

        # How far away from the center to orbit, in pixels
        self.circle_radius = 0

        # How fast to orbit, in radians per frame
        self.circle_speed = 0

        # Set the center of the point we will orbit around
        self.circle_center_x = 0
        self.circle_center_y = 0

        self.random_center = 0
        self.random_speed = 0

    def giro(self, player_sprite, random_center, random_speed):
        self.circle_center_x = player_sprite.center_x + random_center
        self.circle_center_y = player_sprite.center_y + random_center
        self.circle_speed = random_speed

    def update(self):

        """ Update the ball's position. """
        # Calculate a new x, y
        self.center_x = self.circle_radius * math.sin(self.circle_angle) \
            + self.circle_center_x
        self.center_y = self.circle_radius * math.cos(self.circle_angle) \
            + self.circle_center_y

        # Increase the angle in prep for the next round.
        self.circle_angle += self.circle_speed 


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)

        # The shader toy and 'channels' we'll be using
        self.shadertoy = None
        self.channel0 = None
        self.channel1 = None
        self.load_shader()

        # Sprites and sprite lists
        self.player_sprite = None
        self.wall_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.coin_list = None
        self.physics_engine = None

        # Create cameras used for scrolling
        self.camera_sprites = arcade.Camera(width, height)
        self.camera_gui = arcade.Camera(width, height)

        self.generate_sprites()

        # Our sample GUI text
        self.score = 0
        self.coin_list = arcade.SpriteList()

        for i in range(COIN_COUNT):
            # Create the coin instance
            # Coin image from kenney.nl
            coin = Coin(":resources:images/items/coinGold.png", SPRITE_SCALING / 3)

            # Position the center of the circle the coin will orbit
            coin.circle_center_x = random.randrange(SCREEN_WIDTH)
            coin.circle_center_y = random.randrange(SCREEN_HEIGHT)

            coin.random_center = random.randrange(0, 20)
            coin.random_speed = random.randrange(1, 10)/100


            # Random radius from 10 to 200
            coin.circle_radius = random.randrange(10, 50)

            # Random start angle from 0 to 2pi
            coin.circle_angle = random.random() * 2 * math.pi

            # Add the coin to the lists
            self.coin_list.append(coin)

        arcade.set_background_color(arcade.color.ARMY_GREEN)

    def load_shader(self):
        # Where is the shader file? Must be specified as a path.
        shader_file_path = Path("shader.glsl")

        # Size of the window
        window_size = self.get_size()

        # Create the shader toy
        self.shadertoy = Shadertoy.create_from_file(window_size, shader_file_path)

        # Create the channels 0 and 1 frame buffers.
        # Make the buffer the size of the window, with 4 channels (RGBA)
        self.channel0 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )
        self.channel1 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )

        # Assign the frame buffers to the channels
        self.shadertoy.channel_0 = self.channel0.color_attachments[0]
        self.shadertoy.channel_1 = self.channel1.color_attachments[0]

    def generate_sprites(self):
        # -- Set up several columns of walls
        for x in range(0, PLAYING_FIELD_WIDTH, 128):
            for y in range(0, PLAYING_FIELD_HEIGHT, int(128 * SPRITE_SCALING)):
                # Randomly skip a box so the player can find a way through
                if random.randrange(2) > 0:
                    wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", SPRITE_SCALING)
                    wall.center_x = x
                    wall.center_y = y
                    self.wall_list.append(wall)

        # Create the player
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                           scale=SPRITE_SCALING)
        self.player_sprite.center_x = 256
        self.player_sprite.center_y = 512
        self.player_list.append(self.player_sprite)

        # Physics engine, so we don't run into walls
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Start centered on the player
        self.scroll_to_player(1.0)
        self.camera_sprites.update()


    def on_draw(self):
        # Use our scrolled camera
        self.camera_sprites.use()

        # Select the channel 0 frame buffer to draw on
        self.channel0.use()
        self.channel0.clear()
        # Draw the walls
        self.wall_list.draw()

        self.channel1.use()
        self.channel1.clear()
        # Draw the bombs
        self.coin_list.draw()

        # Select this window to draw on
        self.use()
        # Clear to background color
        self.clear()

        # Calculate the light position. We have to subtract the camera position
        # from the player position to get screen-relative coordinates.
        p = (self.player_sprite.position[0] - self.camera_sprites.position[0],
             self.player_sprite.position[1] - self.camera_sprites.position[1])

        # Set the uniform data
        self.shadertoy.program['lightPosition'] = p
        self.shadertoy.program['lightSize'] = 300

        # Run the shader and render to the window
        self.shadertoy.render()

        # Draw the walls
        # self.wall_list.draw()

        # Draw the player
        self.player_list.draw()

        # Switch to the un-scrolled camera to draw the GUI with
        self.camera_gui.use()
        # Draw our sample GUI text
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()
        # Scroll the screen to the player
        self.scroll_to_player()
        self.coin_list.update()

        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        for coin in hit_list:
            coin.followed = True

        for coin in self.coin_list:
            if coin.followed == True:
             coin.giro(self.player_sprite, coin.random_center, coin.random_speed)
             coin.width = 10
             coin.height = 10

    def scroll_to_player(self, speed=CAMERA_SPEED):
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.
        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """

        position = Vec2(self.player_sprite.center_x - self.width / 2,
                        self.player_sprite.center_y - self.height / 2)
        self.camera_sprites.move_to(position, speed)

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.camera_sprites.resize(width, height)
        self.camera_gui.resize(width, height)
        self.shadertoy.resize((width, height))


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
import random
import csv
import math
from pathlib import Path
from pyglet.math import Vec2

import arcade
from arcade.experimental import Shadertoy

# Escala geral
SCALE = 0.5

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Game"
SPRITE_SCALING = SCALE

# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1

PLAYER_MOVEMENT_SPEED = 4 * SPRITE_SCALING * 2
PLAYING_FIELD_WIDTH = 1600
PLAYING_FIELD_HEIGHT = 1600


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=False, fullscreen = True)

        # The shader toy and 'channels' we'll be using
        self.shadertoy = None
        self.channel0 = None
        self.channel1 = None
        self.load_shader()

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        # Sprites and sprite lists
        self.player_sprite = None
        self.second_player = None
        self.wall_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.second_player_list = arcade.SpriteList()
        self.physics_engine = None
        self.cara = None

        # luzes
        self.player_light_status = True
        self.player_light_max_intensity = 700
        self.player_light_intensity = self.player_light_max_intensity

        # cara
        self.cara = None

        # vagalumes
        self.coin_list = None

        # Create cameras used for scrolling
        self.camera_sprites = arcade.Camera(width, height)
        self.camera_gui = arcade.Camera(width, height)

        self.generate_sprites()

        arcade.set_background_color(arcade.color.AMAZON)

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
        # Lê tiles do arquivo e coloca na matriz de posições
        with open('map.csv') as f:
            reader = csv.reader(f)
            matrix = [row for row in reader]
        
        # Desenha as paredes
        for x in range (0, len(matrix), 1):
            for y in range (0, len(matrix[0]), 1):
                if (matrix[y][x] != '-1'):
                    wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", SPRITE_SCALING)
                    wall.center_x = x * 128 * SPRITE_SCALING
                    wall.center_y = y * 128 * SPRITE_SCALING
                    self.wall_list.append(wall)

        # Create the player
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                           scale=SPRITE_SCALING)
        self.player_sprite.center_x = 2560 * SCALE
        self.player_sprite.center_y = 256 * SCALE
        self.player_list.append(self.player_sprite)

        # Cria o segundo player
        self.second_player = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                           scale=SPRITE_SCALING)
        self.second_player.center_x = 320
        self.second_player.center_y = 320
        self.second_player_list.append(self.second_player)

        # Physics engine, so we don't run into walls
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Start centered on the player
        self.scroll_to_player(1.0)
        self.camera_sprites.update()

        # cara
        self.cara = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                           scale=SPRITE_SCALING*10)

        # vagalumes e cria os vagalumes
        self.coin_list = arcade.SpriteList()
        coin_1 = Coin(":resources:images/items/coinGold.png", SPRITE_SCALING / 3)
        coin_2 = Coin(":resources:images/items/coinGold.png", SPRITE_SCALING / 3)
        
        coin_1.circle_center_x = 2560 * SCALE
        coin_1.circle_center_y = 300 * SCALE
        coin_2.circle_center_x = 2560 * SCALE
        coin_2.circle_center_y = 600 * SCALE

        coin_1.random_center = random.randrange(0, 20)
        coin_1.random_speed = random.randrange(1, 10)/100
        coin_1.circle_radius = random.randrange(30, 50)
        coin_1.circle_angle = random.random() * 2 * math.pi
        coin_2.random_center = random.randrange(0, 20)
        coin_2.random_speed = random.randrange(1, 10)/100
        coin_2.circle_radius = random.randrange(30, 50)
        coin_2.circle_angle = random.random() * 2 * math.pi

        self.coin_list.append(coin_1)
        self.coin_list.append(coin_2)

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

        # Select this window to draw on
        self.use()
        # Clear to background color
        self.clear()

        # Calculate the light position. We have to subtract the camera position
        # from the player position to get screen-relative coordinates.
        p = (self.player_sprite.position[0] - self.camera_sprites.position[0],
             self.player_sprite.position[1] - self.camera_sprites.position[1])

        p2 = (200 - self.camera_sprites.position[0],
             300 - self.camera_sprites.position[1])

        p3 = (500 - self.camera_sprites.position[0],
             300 - self.camera_sprites.position[1])
        
        p4 = (0 - self.camera_sprites.position[0],
             300 - self.camera_sprites.position[1])


        # posições dos vagalumes
        p5 = (self.coin_list[0].position[0] - self.camera_sprites.position[0],
             self.coin_list[0].position[1] - self.camera_sprites.position[1])
        p6 = (self.coin_list[1].position[0] - self.camera_sprites.position[0],
             self.coin_list[1].position[1] - self.camera_sprites.position[1])

        #diminui a intensidade da luz do player
        light_step = 50
        if (self.player_light_status == True):
            if(self.player_light_intensity != self.player_light_max_intensity):
                self.player_light_intensity += light_step
        else:
            if(self.player_light_intensity != 0):
                self.player_light_intensity -= light_step

        # Luzes do player e de teste
        self.shadertoy.program['light_1'] = p
        self.shadertoy.program['light_2'] = p2   
        self.shadertoy.program['light_3'] = p3
        self.shadertoy.program['light_4'] = p4

        # Luzes do vagalume
        self.shadertoy.program['light_5'] = p5
        self.shadertoy.program['light_6'] = p6


        self.shadertoy.program['light_size_1'] = self.player_light_intensity
        self.shadertoy.program['light_size_2'] = 100
        self.shadertoy.program['light_size_3'] = 200
        self.shadertoy.program['light_size_4'] = 50
        self.shadertoy.program['light_size_5'] = 70
        self.shadertoy.program['light_size_6'] = 70
        
        # Run the shader and render to the window
        self.shadertoy.render() # aqui !!!!

        # Draw the walls
        # self.wall_list.draw()

        # Draw the player
        self.player_list.draw()
        self.second_player_list.draw()

        # desenha os vagalumes
        self.coin_list.draw()

        # cara
        self.cara.center_x = self.camera_sprites.position[0]
        self.cara.center_y = self.camera_sprites.position[1]
        self.cara.draw()

        # Switch to the un-scrolled camera to draw the GUI with
        self.camera_gui.use()

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
        elif key == arcade.key.S:
            if (self.player_light_status == True):
                self.player_light_status = False
            else:
                self.player_light_status = True

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

        # vagalumes
        self.coin_list.update()

        # Generate a list of all sprites that collided with the player.
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


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
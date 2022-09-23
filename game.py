import random
import csv
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

        # Create cameras used for scrolling
        self.camera_sprites = arcade.Camera(width, height)
        self.camera_gui = arcade.Camera(width, height)

        self.generate_sprites()

        arcade.set_background_color(arcade.color.GRAY)

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


        #diminui a intensidade da luz do player
        light_step = 50
        if (self.player_light_status == True):
            if(self.player_light_intensity != self.player_light_max_intensity):
                self.player_light_intensity += light_step
        else:
            if(self.player_light_intensity != 0):
                self.player_light_intensity -= light_step

        # Set the uniform data
        self.shadertoy.program['light_1'] = p
        self.shadertoy.program['light_2'] = p2   
        self.shadertoy.program['light_3'] = p3
        self.shadertoy.program['light_4'] = p4
        self.shadertoy.program['light_size_1'] = self.player_light_intensity
        self.shadertoy.program['light_size_2'] = 100
        self.shadertoy.program['light_size_3'] = 200
        self.shadertoy.program['light_size_4'] = 50
        
        # Run the shader and render to the window
        self.shadertoy.render() # aqui !!!!

        # Draw the walls
        # self.wall_list.draw()

        # Draw the player
        self.player_list.draw()
        self.second_player_list.draw()

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
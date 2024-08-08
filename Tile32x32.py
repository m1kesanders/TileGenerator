from PIL import Image, ImageDraw
import os
import pygame
from pygame.locals import QUIT, KEYDOWN, K_RIGHT, K_LEFT, K_x, K_e


class CreateTileGenerator():

    def __init__ (self, width = 32, height = 32, background_color = (255, 255, 255), line_color = (0,0,0), shadow_color = (0, 0, 0, 100), output_file = "Ididntsettheoutputname.png"):
        self._width = width
        self._height = height
        self._background_color = background_color
        self._line_color = line_color
        self._shadow_color = shadow_color
        self._output_file = output_file
        self._output_path = os.path.join(os.getcwd(), "outputted_assets")
        if not os.path.exists(self._output_path):
            os.makedirs(self._output_path)
        self._frames = []
        self._img = Image.new('RGBA', (self._width, self._height), self._background_color)
        self._draw = ImageDraw.Draw(self._img)

    def __str__(self):
        return f"A tile {self._width} wide, {self._height} tall. {self._background_color} as the background, with {self._line_color} for lines. It should be saved as {self._output_file}."

    @staticmethod
    def getFrameNum():
        while True:
            try:
                num_frames = int(input("How many frames? "))
                if num_frames <= 0:
                    raise ValueError("Frames must be a positive integer.")
                return num_frames
                    
            except ValueError:
                continue
   
    @staticmethod
    def validateRGB(color):
        return isinstance(color, tuple) and len(color) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in color)
    
    @staticmethod
    def draw_bezier_curve(draw, start_point, curve_start, end_point, closed, thickness, line_color):
        prev_x, prev_y = start_point
        for t in range(101):
            t /= 100
            x = (1 - t) ** 2 * start_point[0] + 2 * (1 - t) * t * curve_start[0] + t ** 2 * end_point[0]
            y = (1 - t) ** 2 * start_point[1] + 2 * (1 - t) * t * curve_start[1] + t ** 2 * end_point[1]
            if t > 0:
                draw.line([prev_x, prev_y, x, y], fill=line_color, width=thickness)
            prev_x, prev_y = x, y

        if closed:
            draw.line([end_point[0], end_point[1], start_point[0], start_point[1]], fill=line_color, width=thickness)


    @property
    def width(self):
        return self._width
    
    @width.setter
    def width(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Width must be an integer and greater than 0.")
        self._width = value

    @property
    def height(self):
        return self._height
    
    @height.setter
    def height(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Height must be an integer and greater than 0.")
        self._height = value 
    
    @property
    def background_color(self):
        return self._background_color
    
    @background_color.setter
    def background_color(self, color):
        if self.validateRGB(color):
            self._background_color = color
        else:
            raise ValueError("background color must be an RGB tuple (255,255,255)")
    
    @property
    def line_color(self):
        return self._line_color
    
    @line_color.setter
    def line_color(self, color):
        if self.validateRGB(color):
            self._line_color = color
        else:
            raise ValueError("line color must be an RGB tuple (255,255,255)")
        
    @property
    def shadow_color(self):
        return self._shadow_color
    
    @shadow_color.setter
    def shadow_color(self, color):
        if isinstance(color, tuple) and len(color) == 4 and all(isinstance(c, int) and 0 <= c <= 255 for c in color):
            self._shadow_color = color
        else:
            raise ValueError("Shadow color must be RGBA format")
        
    @property
    def output_file(self):
        return self._output_file
    
    @output_file.setter
    def output_file(self, file):
        if isinstance(file, str) and file.endswith(".png"):
            self._output_file = file
        else:
            raise ValueError("File must be a str and end with .png")
        
    @property
    def image(self):
        return self._img
    
    @property
    def draw(self):
        return self._draw
        
    def create_shape(self, thickness, show_top = True, show_bottom = True, show_left = True, show_right = True, pop = False, animate = False, repeat = None, location = (0, 0), manual =False):
        if repeat is None:
            repeat = max(self._width, self._height)
        if manual:
            self.manualOverride()
        
        x_start, y_start = location

        if animate:
            num_frames = self.getFrameNum()
            self._frames = []
            for i in range(num_frames):
                self._img = Image.new('RGBA', (self._width, self._height), self._background_color)
                self._draw = ImageDraw.Draw(self._img)

                for y in range(y_start, self._height, thickness * repeat):
                    for x in range(x_start, self._width, thickness * repeat):
                        self._draw_line(self._draw, x, y, thickness, show_top, show_bottom, show_left, show_right, pop, line_color = None)
                
                frame_file = f"{self._output_file.split('.png')[0]}_frame_{i}.png"
                frame_path = os.path.join(self._output_path, frame_file)
                self._img.save(frame_path)
                self._frames.append(frame_path)
            
            
            self._preview_animation()
        
        else:
            img = Image.new('RGBA', (self._width, self._height), self._background_color)
            draw = ImageDraw.Draw(img)

            for y in range(y_start, self._height, thickness * repeat):
                for x in range(x_start, self._width, thickness * repeat):
                    self._draw_line(self._draw, x, y, thickness, show_top, show_bottom, show_left, show_right, pop)

            self._img.save(os.path.join(self._output_path, self._output_file))
            self._preview_image(self._img)

    def generatePositions(self, tile_size, spacing, max_position = None):
        x, y = 0, 0
        count = 0
        while True:
            if max_position and count >= max_position:
                break
            yield (x, y)
            y += spacing
            if y >= tile_size:
                y = 0
                x += spacing
                if x >= tile_size:
                    break
            count += 1

    def create_curved_shape(self, start_point, end_point, curve_start, closed = False, thickness = 2, pop = False, animate = False, repeat = None, location = (0, 0), manual = False):

        if repeat is None:
            repeat = max(self._width, self._height)
        if manual:
            self.manualOverride()

        x_start, y_start = location

        if animate:
            num_frames = self.getFrameNum()
            self._frames = []

            for i in range(num_frames):
                self._img = Image.new('RGBA', (self._width, self._height), self.background_color)
                self._draw = ImageDraw.Draw(self._img)

                for y in range(y_start, self._height, thickness * repeat):
                    for x in range(x_start, self._width, thickness * repeat):
                        self._draw_curved_shape(self._draw, start_point, end_point, curve_start, closed, thickness, pop)

                frame_file = f"{self._output_file.split('.png')[0]}_frame_{i}.png"
                frame_path = os.path.join(self._output_path, frame_file)
                self._img.save(frame_path)
                self._frames.append(frame_path)

            self._preview_animation()
        
        else:
            for y in range(y_start, self._height, thickness * repeat):
                for x in range(x_start, self._width, thickness * repeat):
                    self._draw_curved_shape(self._draw, start_point, end_point, curve_start, closed, thickness, pop)

            self._img.save(os.path.join(self._output_path, self._output_file))
            self._preview_image(self._img)

    def draw_arc(self, draw, start_point, end_point, top_point, thickness, color):
        #calculate vounding box for ellipse
        min_x = min(start_point[0], end_point[0], top_point[0]) - thickness
        max_x = max(start_point[0], end_point[0], top_point[0]) + thickness
        min_y = min(start_point[1], end_point[1], top_point[1]) - thickness
        max_y = max(start_point[1], end_point[1], top_point[1]) + thickness

        bounding_box = [min_x, max_x, min_y, max_y]
        
        #draw arc segment to desired shape
        draw.arc(bounding_box, start = 0, end = 180, fill = color, width = thickness)

    def manualOverride(self):
        try:
            x = int(input("Enter X-Coordinates: "))
            y = int(input("Enter Y-Coordinates: "))

            color_input = input("Enter color (RGB) or leave blank for default color: ")
            if color_input:
                color = tuple(map(int, color_input.split(',')))
                if not self.validateRGB(color):
                    raise ValueError("Must be RGB tuple (255, 255, 255)")
            else:
                color = self._line_color

            repeats_input = input("Enter repeats (x,y) or leave blank for default: ")
            if repeats_input:
                repeats = tuple(map(int, repeats_input.split(',')))
                if len(repeats) != 2 or any(val < 0 for val in repeats):
                    raise ValueError("Invalid input, input tuple (x, y) both greater than 0.")
            else:
                repeats = (0, 0)

            self._apply_manual_override(x, y, color, repeats)
        
        except ValueError:
            return f"Error: {ValueError}"
        
    def _apply_manual_override(self, x, y, color, repeats):
        #adjust imae based on user inputs
        for i in range(y, self.height, self.height) if repeats[1] == 0 else repeats[1]:
            for j in range(x, self.width, self.width) if repeats[0] == 0 else repeats[0]:
                #draw pixel or shape based on users input and color
                self._draw.point((j, i), fill = color)

        self._img.save(os.path.join(self._output_path, self._output_file))
    
    def _draw_line(self, draw, x, y, thickness, show_top, show_bottom, show_left, show_right, pop, line_color = None):
        shadow_offset = 5
        shadow_color = self.shadow_color
        line_color = line_color if line_color is not None else self._line_color
        
        def draw_lines(offset_x, offset_y, color):
            if show_top:
                draw.line([x + offset_x, y + offset_y, x + self._width + offset_x, y + offset_y], fill=color, width=thickness)
            if show_bottom:
                draw.line([x + offset_x, y + self._height + offset_y, x + self._width + offset_x, y + self._height + offset_y], fill=color, width=thickness)
            if show_left:
                draw.line([x + offset_x, y + offset_y, x + offset_x, y + self._height + offset_y], fill=color, width=thickness)
            if show_right:
                draw.line([x + self._width + offset_x, y + offset_y, x + self._width + offset_x, y + self._height + offset_y], fill=color, width=thickness)

        if pop:
            draw_lines(shadow_offset, shadow_offset, shadow_color)
        draw_lines(0, 0, line_color)

    def _draw_curved_shape(self, draw, start_point, end_point, curve_start, closed, thickness, pop):
        shadow_offset = 5
        shadow_color = self.shadow_color
        
        if pop:
            shadow_start = (start_point[0] + shadow_offset, start_point[1] + shadow_offset)
            shadow_curve_start = (curve_start[0] + shadow_offset, curve_start[1] + shadow_offset)
            shadow_end = (end_point[0] + shadow_offset, end_point[1] + shadow_offset)
            

            if closed:
                #draw shadow for closed curve
                self.draw_bezier_curve(draw, shadow_start, shadow_curve_start, shadow_end, closed, thickness, shadow_color)
                #draw shadow lines to complete the closed shape
                draw.line([shadow_start, shadow_end], fill = shadow_color, width = thickness)
                draw.line([shadow_end, shadow_curve_start], fill = shadow_color, width = thickness)
                draw.line([shadow_curve_start, shadow_start], fill = shadow_color, width = thickness)
                
            else:
                #draw shadow for open curve
                self.draw_bezier_curve(draw, shadow_start, shadow_curve_start, shadow_end, closed, thickness, shadow_color)
                
        
        if closed:
            #draw the closed curve
            self.draw_bezier_curve(draw, start_point, curve_start, end_point, closed, thickness, self._line_color)
            #draw lines connecting the end points to close the shape
            draw.line([start_point, end_point], fill = self._line_color, width = thickness)
            draw.line([end_point, curve_start], fill = self._line_color, width = thickness)
            draw.line([curve_start, start_point], fill = self._line_color, width = thickness)
        else:
            #draw open curve
            self.draw_bezier_curve(draw, start_point, curve_start, end_point, closed, thickness, self._line_color)
            
        
    def _preview_image(self, img):
        pygame.init()
        screen = pygame.display.set_mode((self._width, self._height))
        pygame.display.set_caption("Preview Image")
        img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            screen.blit(img, (0, 0))
            pygame.display.flip()
        pygame.quit()
    
    def _preview_animation(self):
        pygame.init()
        screen = pygame.display.set_mode((self._width, self._height))
        pygame.display.set_caption("Preview Animation")
        clock = pygame.time.Clock()

        current_frame = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        current_frame = (current_frame + 1) % len(self._frames)
                    elif event.key == K_LEFT:
                        current_frame = (current_frame - 1) % len(self._frames)
                    elif event.key == K_e:
                        self._save_frame(self._frames[current_frame])
                    elif event.key == K_x:
                        pygame.quit()
                        return

      
            # Load the current frame directly
            img = pygame.image.load(self._frames[current_frame])
            # Ensure the image is in the correct format
            img = img.convert()  # Remove specific mode to use the default one
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(10)  # Adjust the frame rate as needed

        pygame.quit()

    

            
tile_generator = CreateTileGenerator(
    background_color=(0, 128, 0),  # Darkish green
    line_color=(0, 0, 0),
    output_file="animated_grass_tile.png"
)

tile_generator.line_color = tile_generator.background_color

# Define parameters for the grass tile
thickness = 1 # Thin lines
animate = True  # Create an animation


# Create the shape
tile_generator.create_shape(
    thickness=thickness,
    animate=animate,
    
)
tile_generator.line_color = (76, 187, 23)
tile_size = 32
spacing = 4

# Create the generator
positions = tile_generator.generatePositions(tile_size, spacing)

# Define curved shape parameters
start_point = (0, 1)
end_point = (1, 0)
curve_start = (4, 3)

# Create the shapes at each position
for position in positions:
    # Create a new image for each position
    new_img = tile_generator.image
    new_draw = ImageDraw.Draw(new_img)

    tile_generator._draw_curved_shape(
        draw=new_draw,
        start_point=(start_point[0] + position[0], start_point[1] + position[1]),
        end_point=(end_point[0] + position[0], end_point[1] + position[1]),
        curve_start=(curve_start[0] + position[0], curve_start[1] + position[1]),
        closed=False,
        thickness=1,
        pop = False
    )

    # Save or append the newly generated image
    new_img.save(os.path.join(tile_generator._output_path, f"grass_tile_{position[0]}_{position[1]}.png"))
from PIL import Image, ImageDraw
import math
import os

class TileGenerator:

    def __init__(self, array =  [["."]*32 for _ in range(32)], background_color = None, line_color = None, output_file = "temp_output.png", output_directory = "temp_assets"):
        self._array = array if isinstance(array, list) else  [["."]*32 for _ in range(32)]
        self._background_color = background_color if self.validateRGBA(background_color) else None
        self._line_color = line_color if self.validateRGBA(line_color) else None
        self._output_file = output_file if isinstance(output_file, str) and output_file.endswith(".png") else "temp_output.png"
        self._output_directory = os.path.join(os.getcwd(), output_directory) if isinstance(output_directory, str) else "temp_assets"
        if not os.path.exists(self._output_directory):
            os.makedirs(self._output_directory)
        self._img = Image.new("RGBA", (len(array[0]) if array else 0, len(array)), self._background_color)
        self._draw = ImageDraw.Draw(self._img)

        if self._background_color:
            self._applyBackground()

    def __str__(self):
        return f"A Tile represented with a 2D array {self._array}, it has {self._background_color} as a background and {self._line_color} for lines. it will be saved as {self._output_file} in {self._output_directory}."

    @property
    def array(self):
        return self._array
    
    @array.setter
    def array(self, array):
        self._array = array if isinstance(array, list) else [["."]*32]*32
        self._applyBackground()

    @property
    def background_color(self):
        return self._background_color
    
    @background_color.setter
    def background_color(self, background_color):
        self._background_color = background_color if self.validateRGBA(background_color) else None
        self._applyBackground()

    @property
    def line_color(self):
        return self._line_color
    
    @line_color.setter
    def line_color(self, line_color):
        self._line_color = line_color if self.validateRGBA(line_color) else None

    @property
    def output_file(self):
        return self._output_file

    @output_file.setter
    def output_file(self, output_file):
        self._output_file = output_file if isinstance(output_file, str) and output_file.endswith(".png") else "temp_file.png" 

    @property
    def output_directory(self):
        return self._output_directory
    
    @output_directory.setter
    def output_directory(self, output_directory):
        self._output_directory = os.path.join(os.getcwd(), output_directory) if isinstance(output_directory, str) else "temp_assets"
        if not os.path.exists(self._output_directory):
            os.makedirs(self._output_directory)
   
    @staticmethod
    def validateRGBA(rgba):
        return isinstance(rgba, tuple) and (3 <= len(rgba) <= 4) and all(isinstance(c, int) and 0 <= c <= 255 for c in rgba)
    
    def _applyBackground(self):
        for y, row in enumerate(self._array):
            for x, pixel in enumerate(row):
                self._img.putpixel((x, y), self._background_color)
    
    def getSize(self):
        if self._img.size[0] > self._img.size[1]:
            return self._img.size[0]
        else:
            return self._img.size[1]

    def saveImage(self):
        self._img.save(os.path.join(self._output_directory, self._output_file))

    def deleteImage(self):
        os.remove(os.path.join(self._output_directory, self._output_file))

class PixelShape:

    def __init__(self, tile_generator, coords, color, rounded_edges = False):
        self._tile_generator = tile_generator if isinstance(tile_generator, TileGenerator) else None
        self._coords = coords if isinstance(coords, list) else [] 
        self._color = color if TileGenerator.validateRGBA(color) else None
        self._rounded_edges = rounded_edges if isinstance(rounded_edges, bool) else False

    def __str__(self):
        return f"A custom pixel shape on {self._tile_generator} at {self._coords} coordinates in {self._color} color. Rounded edges is {self._rounded_edges}"

    @property
    def coords(self):
        return self._coords
    
    @coords.setter
    def coords(self, coords):
        self._coords = coords if isinstance(coords, list) else []
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        self._color = color if self._tile_generator.validateRGBA(color) else None

    @property 
    def rounded_edges(self):
        return self._rounded_edges
    
    @rounded_edges.setter
    def rounded_edges(self, rounded_edges):
        self._rounded_edges = rounded_edges if isinstance(rounded_edges, bool) else False

    def draw(self, radius = 2):
        for coord in self.coords:
            x, y = int(coord[0] * self._tile_generator._img.size[0]), int(coord[1] * self._tile_generator._img.size[1])
            if self.rounded_edges:
                self._tile_generator._draw.ellipse([x - radius, y - radius , x + radius, y + radius], fill = self.color)
            else:
                self._tile_generator._img.putpixel((x, y), self.color)

    def repeat(self, count_x = 5, count_y = 5, spacing = (4, 4)):
        new_coords = []
        img_width, img_height = self._tile_generator._img.size
        for i in range(count_x):
            for j in range(count_y):
                for coord in self.coords:
                    new_x = coord[0] + (i * spacing[0]) / img_width
                    new_y = coord[1] + (j * spacing[1]) /img_height
                    if new_x < 1.0 and new_y < 1.0:
                        new_coords.append((new_x, new_y))
        self.coords = new_coords

    def drawPolygon(self, sides = 3, radius = 0.4, pos = (0.5, 0.5), color = (0, 0, 0), outline = (255, 255, 255)):
        if sides < 3:
            raise ValueError("Sides must have a minimum of 3")
        
        angle_step = 2 * math.pi / sides
        center_x, center_y = int(pos[0] * self._tile_generator._img.size[0]), int(pos[1] * self._tile_generator._img.size[1])
        points = []

        for i in range(sides):
            angle = i * angle_step
            x = center_x + int(radius * self._tile_generator._img.size[0] * math.cos(angle))
            y = center_y + int(radius * self._tile_generator._img.size[1] * math.sin(angle))
            points.append((x, y))
        
        if TileGenerator.validateRGBA(color):
            self._tile_generator._draw.polygon(points, fill = self._tile_generator.line_color, outline = outline if TileGenerator.validateRGBA(outline) else (0, 0, 0))
       
green_tile = TileGenerator(background_color = (0, 128,0), line_color = (34, 139, 34), output_file = "green.png")
grass_blade = PixelShape(green_tile, [(0.06, 0), (0, 0.06), (0, 0.08), (0.08, 0.06), (0.08, 0.08)], color = (124, 190, 0))
grass_shadow = PixelShape(green_tile, [(0.06, 0.06), (0.06, 0.08)], color = green_tile.line_color)
grass_shadow.repeat(count_x=32, count_y=32)
grass_blade.repeat(count_x = 32, count_y = 32)
grass_shadow.draw()
grass_blade.draw()
green_tile.saveImage()
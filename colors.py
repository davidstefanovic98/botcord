import re
from PIL import Image, ImageColor, ImageDraw
from os.path import join
from sys import argv
from tempfile import TemporaryDirectory

size = (32, 32)

tempdir = TemporaryDirectory()


def save_color_image(hex_color):
	if hex_color is None:
		raise ValueError("Color must not be none")
	if len(hex_color) == 3:
		hex_color = "{r}{r}{g}{g}{b}{b}".format(r=hex_color[0], g=hex_color[1], b=hex_color[2])
	if not hex_color.startswith("#"):
		hex_color = "#" + hex_color

	color = ImageColor.getcolor(hex_color, "RGB")

	image = Image.new(mode="RGBA", size=size, color=color)
	filename = "{}.png".format(hex_color.lstrip("#"))
	out_path = join(tempdir.name, filename)
	image.save(out_path)
	return out_path


def __get_colors(content):
	regex = re.compile(r'#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})')
	return regex.findall(content)


def get_colors(content):
	colors = __get_colors(content)
	if 0 < len(colors) < 10:
		return list(map(lambda c: ["#" + c, save_color_image(c)], colors))
	return None


if __name__ == '__main__':
	save_color_image(argv[1])

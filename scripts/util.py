import os

import pygame

BASE_IMAGE_PATH = "assets/images/"
BASE_SOUND_PATH = "assets/sfx/"
BASE_FONT_PATH = "assets/fonts/"

def load_image(path:str) -> pygame.Surface:
    img = pygame.image.load(BASE_IMAGE_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path:str) -> list[pygame.Surface]:
    images = []
    for image in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        if image.endswith(".png"):
            images.append(load_image(path + '/' + image))
    return images

def load_images_with_names(path:str) -> dict[str, pygame.Surface]:
    images = {}
    for image in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        if image.endswith(".png"):
            images[image[:-4]] = load_image(path + '/' + image)
    return images

def load_sound(path:str) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(BASE_SOUND_PATH + path)

def load_music(path:str) -> None:
    pygame.mixer.music.load(BASE_SOUND_PATH + path)
    pygame.mixer.music.play(-1)

def load_font(path:str, size:int) -> pygame.font.Font:
    return pygame.font.Font(BASE_FONT_PATH + path, size)

def set_cursor(cursor_surface: pygame.Surface):
    cursor_surface_32_32 = pygame.transform.scale(cursor_surface, (32, 32))
    hotspot = (0, 0)
    cursor = pygame.cursors.Cursor(hotspot, cursor_surface_32_32)
    pygame.mouse.set_cursor(cursor)
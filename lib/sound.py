import pygame
import pygame.mixer 

pygame.init()
pygame.mixer.music.load('sound/ubi.mp3')
pygame.mixer.music.play()
pygame.mixer.music.stop()

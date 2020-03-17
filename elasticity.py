import pygame
from pygame.locals import *
from pygame.math import Vector2

import math

BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (127,127,127)

GRAVITY = 9.8
AIR_RESISTANCE_COEFFICIENT = 0.2

resolution = [800,600]


class Box:

    def __init__(self, x, y, width, height, color, mass=1):

        self.v = Vector2(0)
        self.a = Vector2(0)
        self.fu = Vector2(0)
        self.mass = mass

        self.forces_acting = []

        self.width = width
        self.height = height

        self.color = color

        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update(self):

        self.add_force(-AIR_RESISTANCE_COEFFICIENT * self.v)
        
        self.fu = Vector2(0)
        for force in self.forces_acting:
            self.fu += force
        self.forces_acting = []

        self.a = self.fu/self.mass
        self.v += self.a
        self.rect.x += self.v.x
        self.rect.y += self.v.y

    def add_force(self, force):
        self.forces_acting.append(force)

    def reset_velocity(self):
        self.v = Vector2(0)

    def draw(self, display):
        pygame.draw.rect(display, self.color, self.rect)


class FixedElasticString:

    def __init__(self, fixed_x, fixed_y, attatched_object, modulus, natural_length, color):

        self.origin = Vector2(fixed_x, fixed_y)

        self.attatched_object = attatched_object

        self.modulus = modulus
        self.l = natural_length
        self.extension = 0
        self.tension = Vector2(0)
        self.theta = 0

        self.color = color

    def update(self):

        self.calculate_extension()
        self.calculate_theta()
        self.calculate_tension()
        self.apply_forces()

    def calculate_extension(self):
        d = (self.attatched_object.rect.center - self.origin).magnitude()
        if d == 0:
            self.extension = 0
            return
        self.extension = d - self.l

    def calculate_theta(self):

        self.theta = math.atan2(self.attatched_object.rect.centery - self.origin.y,
                                self.attatched_object.rect.centerx - self.origin.x)

    def calculate_tension(self):

        T = self.extension * self.modulus / self.l
        self.tension = Vector2(T * math.cos(self.theta), 0.5 * T * (1 + math.sin(self.theta)))

    def apply_forces(self):

        self.attatched_object.add_force(-self.tension)

    def place_attatchment_at_equilibrium(self):

        self.attatched_object.rect.center = Vector2(self.origin.x, (self.l * self.attatched_object.mass * GRAVITY / self.modulus) + self.l + self.origin.y)

    def draw(self, display):
        pygame.draw.line(display, self.color, self.origin, self.attatched_object.rect.center)


pygame.init()

display = pygame.display.set_mode(resolution)
pygame.display.set_caption("Elasticity")
clock = pygame.time.Clock()

box = Box(0, 0, 20, 20, WHITE, 10)
string = FixedElasticString(400, 10, box, 10, 30, WHITE)
string.place_attatchment_at_equilibrium()

game_exit = False

while not game_exit:
    mouse_pos = Vector2(pygame.mouse.get_pos())
    for event in pygame.event.get():
        
        if event.type == QUIT:
            game_exit = True
        
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                string.place_attatchment_at_equilibrium()
                box.reset_velocity()
                
        elif event.type == MOUSEBUTTONDOWN:
            
            if event.button == 1:
                box.rect.center = mouse_pos
                box.reset_velocity()
        

    box.add_force(Vector2(0, box.mass * GRAVITY))
    string.update()
    box.update()

    display.fill(BLACK)
    pygame.draw.line(display, GREY, (0,mouse_pos.y), (resolution[0],mouse_pos.y))
    pygame.draw.line(display, GREY, (mouse_pos.x,0), (mouse_pos.x,resolution[1]))    
    
    box.draw(display)
    string.draw(display)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

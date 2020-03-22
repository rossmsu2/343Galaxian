#!/usr/bin/env python3

import pygame
import random
import sys
import time


# this class is the background of the game
class Overlay(pygame.sprite.Sprite):

    # this function initializes the background and sets
    # the font and text
    def __init__(self):
        super(pygame.sprite.Sprite, self).__init__()
        self.image = pygame.Surface((800, 20))
        self.rect = self.image.get_rect()
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        self.render('Score: 0        Lives: 5')

    # this function takes the given text and gives it
    # the proper font and color
    def render(self, text):
        self.text = self.font.render(text, True, (255, 255, 255))
        self.image.blit(self.text, self.rect)

    # this function draws to the given screen
    def draw(self, screen):
        screen.blit(self.text, (0, 0))

    # this function updates the score and lives
    def update(self, score, lives):
        self.render('Score: ' + str(score) + '        Lives: ' + str(lives))


# this class governs the player's ship
class Ship(pygame.sprite.Sprite):

    # this function initializes the ship by giving it
    # an image and starting location
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/playerShip1_green.png')
        self.rect = self.image.get_rect()
        self.rect.x = 320
        self.rect.y = 650
        self.lose_sound = pygame.mixer.Sound('assets/lose.wav')
        self.win_sound = pygame.mixer.Sound('assets/win.wav')

    # this function draws the ship on the given screen
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    # this function plays the lose sound
    def death(self):
        self.lose_sound.play()


# this class governs the enemy ships
class Enemy(pygame.sprite.Sprite):

    # this functions initializes the ships by
    # giving them an image and a horizontal speed
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/enemyBlack2.png')
        self.rect = self.image.get_rect()
        self.vector = [1, 0]

    # this function moves the ship
    def update(self):
        self.rect.x += self.vector[0]


# this class governs the player projectiles
class Projectile(pygame.sprite.Sprite):

    # this function initializes the projectiles
    # it gives them an image, a vertical movement
    # speed and a collision sound
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/laserRed03.png')
        self.rect = self.image.get_rect()
        self.vector = [0, -7]
        self.thud_sound = pygame.mixer.Sound('assets/HITTHEM.wav')

    # this function checks for projectile collisions and
    # location. if the projectile is too high it is removed.
    # if it hits an enemy it gives the hit sound and kills
    # the enemy. it also gives you a point. then the projectile's
    # location is updated
    def update(self, game, enemies):
        if self.rect.y < 0:
            game.projectiles.remove(self)
        hitObject = pygame.sprite.spritecollideany(self, enemies)
        if hitObject:
            self.thud_sound.play()
            hitObject.kill()
            game.projectiles.remove(self)
            game.score += 1
        self.rect.y += self.vector[1]


# this class governs the enemy's projectiles
class EnemyProjectile(pygame.sprite.Sprite):

    # this function initializes the projectiles
    # it gives them an image, a vertical motion
    # and a sound
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/laserBlue03.png')
        self.rect = self.image.get_rect()
        self.vector = [0, 7]
        self.thud_sound = pygame.mixer.Sound('assets/IMHIT.wav')

    # this function checks for projectile collisions and
    # location. if the projectile is too low it is removed.
    # if it hits the player ship, the player loses a life.
    # then the projectile's location is updated
    def update(self, game, ship):
        if self.rect.y > 700:
            game.enemyProjectiles.remove(self)
        hitObject = pygame.sprite.collide_rect(self, ship)
        if hitObject:
            self.thud_sound.play()
            game.lives -= 1
            game.enemyProjectiles.remove(self)
        self.rect.y += self.vector[1]


# this class runs the actual game
class Game:

    # this function initializes the game.
    # it creates sprite groups for the enemies
    # and both types of projectiles. it sets the
    # screen size and fills it black. it sets the
    # score and lives to the default. it finally
    # sets up the enemies
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(50)
        pygame.mixer.music.load('assets/background_sound.wav')
        pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((700, 700))
        self.enemyProjectiles = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.ship = Ship()
        self.new_life_event = pygame.event.Event(pygame.USEREVENT + 1)
        self.enemies = pygame.sprite.Group()
        self.overlay = Overlay()
        self.screen.fill((0, 0, 0))
        self.score = 0
        self.lives = 5
        self.timeBetweenShots = 0
        self.canIShoot = True
        for i in range(1, 10):
            for j in range(1, 10):
                enemy = Enemy()
                enemy.rect.x = j * 40
                enemy.rect.y = i * 25
                self.enemies.add(enemy)

    # this function runs the actual game.
    def run(self):
        self.done = False
        # while the game is not over
        while not self.done:
            # reset move boolean
            move = False
            # fill the background
            self.screen.fill((0, 0, 0))
            # check if there are enemies left
            if len(self.enemies) == 0:
                # if not end the game
                self.ship.win_sound.play()
                time.sleep(4)
                pygame.quit()
                sys.exit(0)
            # check every enemy
            for enemy in self.enemies:
                # too far right we need to change movement
                if enemy.rect.x >= 680:
                    move = True
                # too far left we need to change movement
                if enemy.rect.x <= 0:
                    move = True
                # random shot check
                if random.randint(0, 1000) < 1:
                    enemyProjectile = EnemyProjectile()
                    enemyProjectile.rect.x = enemy.rect.x
                    enemyProjectile.rect.y = enemy.rect.y
                    self.enemyProjectiles.add(enemyProjectile)
                # too far down you lose
                if enemy.rect.y >= 650:
                    self.ship.lose_sound.play()
                    time.sleep(3)
                    pygame.quit()
                    sys.exit(0)
            # if we have to change movement
            if move is True:
                # switch every enemy to movement other direction
                # and move them slightly down
                for enemy in self.enemies:
                    enemy.vector[0] *= -1
                    enemy.rect.y += 25
            # check if we are dead, if so end game
            if self.lives < 1:
                self.ship.death()
                time.sleep(3)
                pygame.quit()
                sys.exit(0)
            # array of key presses
            keys = pygame.key.get_pressed()
            # SPACEBAR
            if keys[pygame.K_SPACE]:
                # if we are allowed to shoot again
                if self.canIShoot:
                    # shoot
                    projectile = Projectile()
                    projectile.rect.x = self.ship.rect.x + 10
                    projectile.rect.y = self.ship.rect.y - 10
                    self.projectiles.add(projectile)
            # LEFT ARROW
            if keys[pygame.K_LEFT]:
                # move left
                self.ship.rect.x -= 5
                # make sure not too far left
                if self.ship.rect.x <= 0:
                    self.ship.rect.x = 0
            # RIGHT ARROW
            if keys[pygame.K_RIGHT]:
                # move right
                self.ship.rect.x += 5
                # make sure not too far right
                if self.ship.rect.x >= 675:
                    self.ship.rect.x = 675
            # ESCAPE
            if keys[pygame.K_ESCAPE]:
                # end the game
                pygame.quit()
                sys.exit(0)
            # check for manual "x" on window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True

            # update everything's location and visuals
            self.projectiles.update(self, self.enemies)
            self.enemyProjectiles.update(self, self.ship)
            self.overlay.update(self.score, self.lives)
            self.enemies.update()
            self.projectiles.draw(self.screen)
            self.enemyProjectiles.draw(self.screen)
            self.ship.draw(self.screen)
            self.enemies.draw(self.screen)
            self.overlay.draw(self.screen)

            # flip to the new updated screen
            pygame.display.flip()

            # and to shot check timer
            self.timeBetweenShots += self.clock.tick(60)

            # check if we can shoot yet
            if self.timeBetweenShots < 480:
                if self.timeBetweenShots == 0:
                    self.canIShoot = True
                else:
                    self.canIShoot = False
            else:
                self.timeBetweenShots = 0
                self.canIShoot = True


# run 'er
if __name__ == "__main__":
    game = Game()
    game.run()

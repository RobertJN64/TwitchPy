import pygame
import math

def overlap(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]

    return math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2) < 30

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rot = 0

        self.moveF = False
        self.moveB = False
        self.rotL = False
        self.rotR = False

        self.radius = 15
        self.health = 5

    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,255), (self.x, self.y), self.radius)
        pygame.draw.line(screen, (0,0,0), (self.x, self.y), (self.x + math.sin(math.radians(self.rot)) * self.radius,
                        (self.y + math.cos(math.radians(self.rot + 180)) * self.radius)), width=3)


    def moveAndRotate(self, screen):
        if self.rotR:
            self.rot += 3
        if self.rotL:
            self.rot -= 3
        moveDir = 0
        if self.moveF:
            moveDir += 3
        if self.moveB:
            moveDir -= 3

        oldx = self.x
        oldy = self.y
        self.x += moveDir * math.sin(math.radians(self.rot))
        self.y += moveDir * math.cos(math.radians(self.rot + 180))
        if self.x < 0 or self.y < 0 or self.y > screen.get_rect().height or self.x > screen.get_rect().width:
            self.x = oldx
            self.y = oldy

    def shootBullet(self):
        bullet = Bullet(self.x + 10 * math.sin(math.radians(self.rot)),
                        self.y + 10 * math.cos(math.radians(self.rot + 180)),
                        self.rot)
        return bullet

    def checkOverlaps(self, bullets):
        for bullet in bullets:
            if overlap((bullet.x, bullet.y), (self.x, self.y)):
                self.health -= 1
                print(self.health)

class Bullet:
    def __init__(self, x, y, rot):
        self.x = x
        self.y = y
        self.rot = rot

        self.bounces = 0
        self.timer = 0


    def updatePos(self, screen):
        self.x += 4 * math.sin(math.radians(self.rot))
        self.y += 4 * math.cos(math.radians(self.rot + 180))

        self.rot = self.rot%360

        if self.y < 0:
            self.rot = 180 - self.rot
            self.bounces += 1

        if self.y > screen.get_rect().height:
            self.rot = 180 - self.rot
            self.bounces += 1

        if self.x < 0:
            self.rot = 360 - self.rot
            self.bounces += 1

        if self.x > screen.get_rect().width:
            self.rot = 360 - self.rot
            self.bounces += 1

        if self.bounces > 2:
            self.timer += 1
            self.bounces = 3

    def draw(self, screen):
        pygame.draw.circle(screen, (200 - self.bounces*50,0,0), (self.x, self.y), 10)

    def shouldDelete(self, playerx, playery):
        return self.timer > 20 or overlap((playerx, playery), (self.x, self.y))



def run():
    #region Reset + Init
    pygame.init()
    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
    pygame.display.set_caption("PyTwitch Arcade")
    clock = pygame.time.Clock()

    player = Player(screen.get_rect().centerx, screen.get_rect().centery)
    bullets = []
    #endregion

    done = False
    while not done:
        screen.fill((50,50,50))
        #print(clock.get_fps())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    player.moveF = True
                elif event.key == pygame.K_s:
                    player.moveB = True
                elif event.key == pygame.K_a:
                    player.rotL = True
                elif event.key == pygame.K_d:
                    player.rotR = True
                elif event.key == pygame.K_SPACE:
                    bullets.append(player.shootBullet())

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    player.moveF = False
                elif event.key == pygame.K_s:
                    player.moveB = False
                elif event.key == pygame.K_a:
                    player.rotL = False
                elif event.key == pygame.K_d:
                    player.rotR = False

        player.draw(screen)
        player.moveAndRotate(screen)
        for bullet in bullets:
            bullet.updatePos(screen)
            bullet.draw(screen)

        player.checkOverlaps(bullets)

        for i in range(len(bullets) -1, -1, -1):
            if bullets[i].shouldDelete(player.x, player.y):
                bullets.pop(i)

        pygame.display.flip()
        clock.tick(50)

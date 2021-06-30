import time
import pygame
import math
import PythonExtended.Pygame as pyg
import TwitchAPI as twitch
import threading
import random

def overlap(a, b, size=20):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]

    return math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2) < math.pow(size, 2)

#region classes
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
        bullet = Bullet(self.x + 25 * math.sin(math.radians(self.rot)),
                        self.y + 25 * math.cos(math.radians(self.rot + 180)),
                        self.rot)
        return bullet

    def checkOverlaps(self, bullets):
        for bullet in bullets:
            if overlap((bullet.x, bullet.y), (self.x, self.y)):
                self.health -= 1

    def bulletSpam(self, bullets):
        for rot in range(0, 360, 90):
            bullets.append(Bullet(self.x + 25 * math.sin(math.radians(rot + 45)),
                            self.y + 25 * math.cos(math.radians(rot + 45 + 180)), rot + 45))


class Bullet:
    def __init__(self, x, y, rot, boss=False):
        self.x = x
        self.y = y
        self.rot = rot

        self.bounces = 0
        self.timer = 0
        self.boss = boss

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
        pygame.draw.circle(screen, (200 - self.bounces*50,self.boss*100,0), (self.x, self.y), 10)

    def shouldDelete(self, playerx, playery):
        return self.timer > 20 or overlap((playerx, playery), (self.x, self.y))

class Enemy:
    def __init__(self, x, y, boss):
        self.x = x
        self.y = y
        self.boss = boss
        self.bcounter = 100
        self.health = boss * 4 + 1

    def draw(self, screen):
        if not self.boss:
            pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), 20)
        else:
            pygame.draw.circle(screen, (200,200,200), (self.x, self.y), 25)

    def checkOverlaps(self, bullets):
        for bullet in bullets:
            if overlap((bullet.x, bullet.y), (self.x, self.y), 30) and not bullet.boss:
                self.health -= 1
                return bullet
        return None

    def bulletSpam(self, bullets):
        self.bcounter += 1
        if self.bcounter >= 100:
            self.bcounter = 0
            for rot in range(0, 360, 45):
                bullets.append(Bullet(self.x + 25 * math.sin(math.radians(rot)),
                                self.y + 25 * math.cos(math.radians(rot + 180)), rot, boss=True))
#endregion

def spawnEnemy(screen, boss):
    return Enemy(random.randint(20, screen.get_rect().width - 20),
                 random.randint(20, screen.get_rect().height - 20), boss)

def run():
    print("Connecting to twitch servers...")
    s = twitch.connect()
    twitch.sendMessage(s, "#robertjn_dev", "[BOT] Connected to twitch servers! This is an interactive game.")
    twitch.sendMessage(s, "#robertjn_dev", "[BOT] Try using !enemy, !boss, !health, !powerup.")

    #region Reset + Init
    pygame.init()
    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
    pygame.display.set_caption("PyTwitch Arcade")
    clock = pygame.time.Clock()

    # region threads
    d = {}
    thread = threading.Thread(target=twitch.checkChat, args=(s, d,))
    thread.start()
    lastmessage = "Waiting for message...."
    lastsender = "Twitch chat"
    # endregion

    close = False
    while not close:
        player = Player(screen.get_rect().centerx, screen.get_rect().centery)
        bullets = []
        bulletspamcounter = 0
        score = 0
        enemies = []
        #endregion

        done = False
        while not done:
            #region threads
            if not thread.is_alive():
                if d != {}:
                    lastmessage = d["message"]
                    lastsender = d["sender"]
                    if lastmessage == "!enemy":
                        enemies.append(spawnEnemy(screen, False))
                    elif lastmessage == "!boss":
                        enemies.append(spawnEnemy(screen, True))
                    elif lastmessage == "!powerup":
                        bulletspamcounter = 200
                    elif lastmessage == "!health" and player.health < 5:
                        player.health += 1

                d = {}
                thread = threading.Thread(target=twitch.checkChat, args=(s, d,))
                thread.start()
            #endregion

            if len(enemies) == 0:
                enemies.append(spawnEnemy(screen, False))

            screen.fill((50,50,50))
            pyg.message_display(screen, "FPS: " + str(round(clock.get_fps())), (screen.get_rect().width-30,20), size=15)
            pyg.message_display(screen, "Score: " + str(round(score)), (screen.get_rect().width - 40, 40),
                                size=15)
            pyg.message_display(screen, str(lastsender) + ": " + str(lastmessage),
                                (screen.get_rect().width/2, screen.get_rect().height-20), color = (200,200,200), size=20)
            pygame.draw.rect(screen, (200,0,0), (0,0,screen.get_rect().width/5 * player.health,10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close = True
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

            if bulletspamcounter > 0:
                if bulletspamcounter%25 == 0:
                    player.bulletSpam(bullets)
                bulletspamcounter -= 1

            player.draw(screen)
            player.moveAndRotate(screen)
            for enemie in enemies:
                enemie.draw(screen)
                if enemie.boss:
                    enemie.bulletSpam(bullets)
            for bullet in bullets:
                bullet.updatePos(screen)
                bullet.draw(screen)


            player.checkOverlaps(bullets)

            for i in range(len(bullets) -1, -1, -1):
                if bullets[i].shouldDelete(player.x, player.y):
                    bullets.pop(i)

            for i in range(len(enemies) -1, -1, -1):
                bullet = enemies[i].checkOverlaps(bullets)
                if bullet is not None:
                    bullets.remove(bullet)
                    if enemies[i].health == 0:
                        if player.health < 5:
                            if enemies[i].boss:
                                score += 9
                                player.health = 5
                            elif random.randint(0, 1) == 0:
                                player.health += 1
                        enemies.pop(i)
                        score += 1



            if player.health <= 0:
                pyg.message_display(screen, "GAME OVER!", (screen.get_rect().width/2, screen.get_rect().height/2), (0,0,0),
                                    size=50)
                pygame.display.flip()
                time.sleep(2)
                done = True

            pygame.display.flip()
            clock.tick(50)

    s.close()
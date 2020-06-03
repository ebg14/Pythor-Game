import pygame as pg
import random
import math


pg.init()

screen_size = (1300, 1050)
window = pg.display.set_mode(screen_size)
pg.display.set_caption("Pythor")
screen_middle = (screen_size[0] / 2, screen_size[1] / 2)


background = pg.image.load("background.png")
mainBg = pg.image.load("mainbg.png")
pythor_img = pg.image.load("Spaceship2.png")
pythor_img = pg.transform.scale(pythor_img, (90, 108))
pythor_heart = pg.image.load("heart.png")
pythor_heart = pg.transform.scale(pythor_heart, (50, 50))
font = pg.font.Font("pixel_font.ttf", 30)
font2 = pg.font.Font("pixel_font.ttf", 200)

shootSound = pg.mixer.Sound("shoot.wav")
hitSound = pg.mixer.Sound("gotHit.wav")
correctSound = pg.mixer.Sound("correctSound.wav")
wrongSound = pg.mixer.Sound("wrongSound.wav")
enemyDeadSound = pg.mixer.Sound("deadEnemy.wav")

music = pg.mixer.music.load("Motivated.mp3")
pg.mixer.music.play(-1)

run = True
isLost = None
level = 1
stage = 1
angle = 0
enemy_list = []


class Question:
    def __init__(self, question, answers, correct_answer, question_sec_line=""):
        self.question = question
        self.answers = answers
        self.correct_answer = correct_answer
        self.question_sec_line = question_sec_line
        if len(self.question) > 50:
            words = self.question.split(" ")
            self.question = ""
            for i in range(len(words)):
                if i < 7:
                    self.question += words[i] + " "
                else:
                    self.question_sec_line += words[i] + " "


class Bullet:
    def __init__(self, x, y, speed, width, height, path):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = width
        self.height = height
        self.bullet_img = pg.image.load(path)
        self.bullet_img = pg.transform.scale(self.bullet_img, (self.width, self.height))
        self.hitbox = (self.x, self.y, self.width, self.height)

    def draw(self):
        window.blit(self.bullet_img, (self.x, self.y))

    def move(self):
        self.y -= self.speed
        self.hitbox = (self.x, self.y, self.width, self.height)


class Boss2Bullet(Bullet):
    def __init__(self, x, y, speed, width, height, path, direc=1):
        super().__init__(x, y, speed, width, height, path)
        self.direc = direc

    def move(self):
        if self.direc == 0:
            pass
        else:
            self.x = self.x - (self.speed * self.direc)
        self.y -= self.speed
        self.hitbox = (self.x, self.y, self.width, self.height)


class Level3EnemyBullet(Bullet):
    def __init__(self, x, y, speed, width, height, path, xSpeed):
        super().__init__(x, y, speed, width, height, path)
        self.xSpeed = xSpeed

    def move(self):
        if self.y < screen_middle[1]:
            self.y += self.speed
        else:
            self.y += self.speed
            self.x += self.xSpeed


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 90
        self.height = 108
        self.speed = 20
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.bullets = []
        self.bullet_cooldown = 5
        self.health = 7
        self.heart_x = 0

    def draw(self):
        self.hitbox = (self.x, self.y, self.width, self.height)
        window.blit(pythor_img, (self.x, self.y))
        for i in range(self.health):
            window.blit(pythor_heart, (self.heart_x + i * 55, 0))

    def move_and_shoot(self, pressed_keys):
        for bul in self.bullets:
            if 0 < bul.y < screen_size[1]:
                bul.move()
            else:
                self.bullets.pop(self.bullets.index(bul))

        if (pressed_keys[pg.K_a] or pressed_keys[pg.K_LEFT]) and 0 < self.x:
            self.x -= self.speed
        elif (pressed_keys[pg.K_d] or pressed_keys[pg.K_RIGHT]) and self.x < screen_size[0] - self.width:
            self.x += self.speed
        if (pressed_keys[pg.K_w] or pressed_keys[pg.K_UP]) and 0 < self.y:
            self.y -= self.speed
        elif (pressed_keys[pg.K_s] or pressed_keys[pg.K_DOWN]) and self.y < screen_size[1] - self.height:
            self.y += self.speed
        if self.bullet_cooldown == 10:
            if pressed_keys[pg.K_SPACE]:
                self.shoot()
                self.bullet_cooldown = 0
        else:
            self.bullet_cooldown += 1

    def shoot(self):
        if len(self.bullets) < 6:
            self.bullets.append(Bullet(self.x + self.width / 2, self.y, 30, 16, 48, "playerBullet.png"))
            shootSound.play()

    def get_hit(self):
        self.health -= 1
        hitSound.play()

    def get_pushed(self):
        if self.y + 100 < screen_size[1]:
            self.y += 100


class Enemy:
    def __init__(self, velocity, width, height, path, health, bullet_path, x=random.randint(0, screen_size[0] - 144), y=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.enemy_img = pg.image.load(path)
        self.enemy_img = pg.transform.scale(self.enemy_img, (self.width, self.height))
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.velocity = velocity
        self.bullets = []
        self.bullet_cooldown = 20
        self.health = health
        self.bullet_path = bullet_path

    def draw(self):
        self.hitbox = (self.x, self.y, self.width, self.height)
        window.blit(self.enemy_img, (self.x, self.y))

    def move_and_shoot(self):
        for bul in self.bullets:
            if 0 < bul.y < screen_size[1]:
                bul.move()
            else:
                self.bullets.pop(self.bullets.index(bul))

        self.x += self.velocity

        if self.bullet_cooldown == 20:
            self.shoot()
            self.bullet_cooldown = 0
        else:
            self.bullet_cooldown += 1

        if not 0 <= self.x <= screen_size[0] - self.width:
            self.velocity *= -1

    def shoot(self):
        if len(self.bullets) < 6:
            self.bullets.append(Bullet(self.x + self.width / 2, self.y + self.height, -20, 20, 40, self.bullet_path))

    def get_hit(self):
        self.health -= 1
        if self.health == 0:
            enemyDeadSound.play()


class Boss(Enemy):
    def __init__(self, velocity, width, height, path, health, bullet_path, x=random.randint(0, screen_size[0] - 144), y=0):
        super().__init__(velocity, width, height, path, health,bullet_path, x, y)
        self.finalHealth = health

    def shoot(self):
        if len(self.bullets) < 10:
            self.bullets.append(Bullet(self.x + self.width / 2, self.y + self.height, -20, 20, 40, self.bullet_path))
            self.bullets.append(Bullet(self.x + 35, self.y + self.height / 1.5, -10, 20, 40, self.bullet_path))
            self.bullets.append(Bullet(self.x + self.width-40, self.y + self.height/1.5, -10, 20, 40, self.bullet_path))

    def show_health(self):
        pg.draw.rect(window, (255, 0, 0), [screen_middle[0] - 250, 20, 500, 15])
        pg.draw.rect(window, (0, 255, 0), [screen_middle[0] - 250, 20,  self.health * (500/self.finalHealth), 15])


class Level2Enemy(Enemy):
    def __init__(self, velocity, width, height, path, health, bullet_path, direction=1,  x=random.randint(0, screen_size[0] - 144), y=0):
        super().__init__(velocity, width, height, path, health, bullet_path, x, y)
        self.direction = direction
        global angle
        angle = 0

    def move_and_shoot(self):
        # shooting
        for bul in self.bullets:
            if 0 < bul.y < screen_size[1]:
                bul.move()
            else:
                self.bullets.pop(self.bullets.index(bul))

        if self.bullet_cooldown == 30:
            self.shoot()
            self.bullet_cooldown = 0
        else:
            self.bullet_cooldown += 1
        # moving
        theta = math.radians(angle)
        if self.direction < 0:
            self.x -= self.velocity * math.cos(theta)
        else:
            self.x += self.velocity * math.cos(theta)
        self.y += self.velocity * math.sin(theta)


class Level2SmallEnemy(Enemy):
    def __init__(self, velocity, width, height, path, health, bullet_path,  x=random.randint(0, screen_size[0] - 144), y=0):
        super().__init__(velocity, width, height, path, health, bullet_path, x, y)

    def move_and_shoot(self):
        # no shooting

        # moving
        self.y += self.velocity
        if self.y > screen_size[1]:
            self.y = 0


class Level3Enemy(Enemy):
    def __init__(self, velocity, width, height, path, health, bullet_path,
                 x=random.randint(0, screen_size[0] - 144), y=0):
        super().__init__(velocity, width, height, path, health, bullet_path, x, y)

    def move_and_shoot(self):
        #shooting
        for bul in self.bullets:
            if 0 < bul.y < screen_size[1]:
                bul.move()
            else:
                self.bullets.pop(self.bullets.index(bul))

        if self.bullet_cooldown == 30:
            self.shoot()
            self.bullet_cooldown = 0
        else:
            self.bullet_cooldown += 1

        self.x += self.velocity

        if not 0 <= self.x <= screen_size[0] - self.width:
            self.velocity *= -1


    def shoot(self):
        if len(self.bullets) < 10:
            self.bullets.append(Level3EnemyBullet(self.x, self.y + self.height, 20, 100, 100, self.bullet_path, -20))
            self.bullets.append(Level3EnemyBullet(self.x + self.width, self.y + self.height, 20, 100, 100, self.bullet_path, 20))


class Boss2(Boss):
    def __init__(self, velocity, width, height, path, health, bullet_path, x=random.randint(0, screen_size[0] - 144),
                 y=0):
        super().__init__(velocity, width, height, path, health, bullet_path, x, y)
        self.yVelocity = -self.velocity
        self.bullet_cooldown = 10

    def move_and_shoot(self):
        # shoot
        for bul in self.bullets:
            if 0 < bul.y < screen_size[1]:
                bul.move()
            else:
                self.bullets.pop(self.bullets.index(bul))

        if self.bullet_cooldown == 10:
            self.shoot()
            self.bullet_cooldown = 0
        else:
            self.bullet_cooldown += 1

        # move
        self.y += self.yVelocity
        self.x += self.velocity
        if not 0 <= self.y <= screen_size[1] / 2 - self.height:
            self.yVelocity *= -1
        if not 0 <= self.x <= screen_size[0] - self.width:
            self.velocity *= -1

    def shoot(self):
        if len(self.bullets) < 15:
            self.bullets.append(Boss2Bullet(self.x + self.width / 2, self.y + self.height, -10, 20, 40, self.bullet_path, -1))
            self.bullets.append(Boss2Bullet(self.x + self.width / 2, self.y + self.height, -10, 20, 40, self.bullet_path))
            self.bullets.append(Boss2Bullet(self.x + self.width / 2, self.y + self.height, -10, 20, 40, self.bullet_path,0))


class FinalBoss(Boss2):
    def __init__(self, velocity, width, height, path, health, bullet_path, x=random.randint(0, screen_size[0] - 144),
                 y=0):
        super().__init__(velocity, width, height, path, health, bullet_path, x, y)

    def move_and_shoot(self):
        # shoot
        for bul in self.bullets:
            if 0 < bul.y < screen_size[1]:
                bul.move()
            else:
                self.bullets.pop(self.bullets.index(bul))

        if self.bullet_cooldown == 10:
            self.shoot()
            self.bullet_cooldown = 0
        else:
            self.bullet_cooldown += 1

        # move
        self.y += self.yVelocity
        self.x += self.velocity
        if not 0 <= self.y <= screen_size[1] / 2 - self.height:
            self.yVelocity *= -1
        if not 0 <= self.x <= screen_size[0] - self.width:
            self.velocity *= -1

    def shoot(self):
        if len(self.bullets) < 15:
            self.bullets.append(Boss2Bullet(self.x + self.width / 2, self.y + self.height, -10, 20, 40, self.bullet_path, -1))
            self.bullets.append(Boss2Bullet(self.x + self.width / 2, self.y + self.height, -10, 20, 40, self.bullet_path))
            self.bullets.append(Boss2Bullet(self.x + self.width - 100, self.y + self.height-100, -10, 20, 40, "bullet2.png", 0))
            self.bullets.append(Boss2Bullet(self.x + 100, self.y + self.height -100, -10, 20, 40, "bullet2blue.png", 0))
            self.bullets.append(Boss2Bullet(self.x + self.width / 2, self.y + self.height, -10, 20, 40, self.bullet_path,0))


def load_questions():
    file = open("questions.txt", "r")
    global questions
    questions = []
    for line in file:
        que = Question(line.strip(), [file.readline().strip(), file.readline().strip(), file.readline().strip(),
                                      file.readline().strip()], file.readline().strip())
        questions.append(que)
    file.close()


def show_quiz():
    question = questions.pop(random.randint(-1, len(questions) - 1))
    while True:
        pg.draw.rect(window, (220, 111, 111), (screen_size[0] / 6, 200, 900, 500))
        for evt in pg.event.get():
            if evt.type == pg.QUIT:
                return

        text = font.render(question.question, 1, (255, 255, 255))
        op1 = font.render("1)" + question.answers[0], 1, (255, 255, 255))
        op2 = font.render("3)" + question.answers[2], 1, (255, 255, 255))
        op3 = font.render("2)" + question.answers[1], 1, (255, 255, 255))
        op4 = font.render("4)" + question.answers[3], 1, (255, 255, 255))
        window.blit(text, (screen_size[0] / 5, 250))
        if question.question_sec_line != "":
            text2 = font.render(question.question_sec_line, 1, (255, 255, 255))
            window.blit(text2, (screen_size[0] / 5, 300))
        window.blit(op1, (screen_size[0] / 5, 400))
        window.blit(op2, (screen_size[0] / 5, 600))
        window.blit(op3, (screen_size[0] / 5 + 500, 400))
        window.blit(op4, (screen_size[0] / 5 + 500, 600))

        keys = pg.key.get_pressed()
        player_answer = None
        if keys[pg.K_1]:
            if question.correct_answer == question.answers[0]:
                player_answer = True
            else:
                player_answer = False
        elif keys[pg.K_2]:
            if question.correct_answer == question.answers[1]:
                player_answer = True
            else:
                player_answer = False
        elif keys[pg.K_3]:
            if question.correct_answer == question.answers[2]:
                player_answer = True
            else:
                player_answer = False
        elif keys[pg.K_4]:
            if question.correct_answer == question.answers[3]:
                player_answer = True
            else:
                player_answer = False

        if player_answer:
            correctSound.play()
            correct_text = font2.render("Correct!", 1, (0, 255, 0))
            window.blit(correct_text, (screen_size[0] / 6, 300))
            pg.display.update()
            pg.time.wait(3000)
            return True
        elif player_answer == False:
            wrongSound.play()
            wrong_text = font2.render("Wrong!", 1, (255, 0, 0))
            window.blit(wrong_text, (screen_size[0] / 4, 300))
            pg.display.update()
            pg.time.wait(3000)
            return False
        pg.display.update()


def generate_enemies(level, stage):
    enemies = []
    if level == 1 and stage == 1:
        showLevel()
        enemies.append(Enemy(8, 144, 168, "enemyShip2.png", 5, "whiteBullet.png"))
        enemies.append(Enemy(6, 144, 168, "enemyShip2.png", 5, "whiteBullet.png"))
    elif level == 1 and stage == 2:
        enemies.append(Boss(6, 288, 336, "enemyShip2.png", 8, "whiteBullet.png", screen_middle[0] - 100, 40))
    elif level == 2 and stage == 1:
        showLevel()
        enemies.append(Level2Enemy(7, 176, 136, "enemyShip1.png", 5, "blueBullet.png", 1, screen_size[0] / 4, 0))
        enemies.append(Level2Enemy(7, 176, 136, "enemyShip1.png", 5, "blueBullet.png", -1, 2 * screen_size[0] / 4, 0))
        enemies.append(Level2SmallEnemy(10, 72, 84, "enemyShip2.png", 1, "blueBullet.png", 0, 0))
        enemies.append(Level2SmallEnemy(10, 72, 84, "enemyShip2.png", 1, "blueBullet.png", screen_size[0] / 4, 0))
        enemies.append(Level2SmallEnemy(10, 72, 84, "enemyShip2.png", 1, "blueBullet.png", 2 * screen_size[0] / 4, 0))
        enemies.append(Level2SmallEnemy(10, 72, 84, "enemyShip2.png", 1, "blueBullet.png", 3 * screen_size[0] / 4, 0))
        enemies.append(Level2SmallEnemy(10, 72, 84, "enemyShip2.png", 1, "blueBullet.png", 3.8 * screen_size[0] / 4, 0))
    elif level == 2 and stage == 2:
        enemies.append(Boss2(2, 352, 272, "enemyShip1.png", 12, "blueBullet.png", screen_size[0] / 4, 0))
    elif level == 3 and stage == 1:
        showLevel()
        enemies.append(Level3Enemy(5, 144, 168, "enemy3.png", 7, "bull3.png", screen_size[0] / 4, 60))
        enemies.append(Level3Enemy(5, 144, 168, "enemy3.png", 7, "bull3.png", screen_size[0] / 12, 60))
        enemies.append(Level3Enemy(5, 144, 168, "enemy3.png", 7, "bull3.png", screen_size[0] / 6, 300))
    elif level == 3 and stage == 2:
        enemies.append(FinalBoss(2, 438, 423, "bigEnemyShip.png", 15, "bullet2green.png", 0, 40))
    return enemies


def showLevel():
    window_update()
    global level
    text = font2.render("Level " + str(level), 1, (255, 255, 255))
    window.blit(text, (screen_middle[0] -400, screen_middle[1]-200))
    pg.display.update()
    pg.time.wait(2000)


def window_update():
    window.blit(background, (0, 0))
    pythor.draw()
    for bul in pythor.bullets:
        bul.draw()
    for enmy in enemy_list:
        if type(enmy).__name__ == "Boss" or issubclass(type(enmy), Boss):
            enmy.show_health()
        enmy.draw()
        for enmyBul in enmy.bullets:
            enmyBul.draw()
    pg.display.update()


def main():
    global run, angle, enemy_list, level, stage, isLost, window
    enemy_list = generate_enemies(level, stage)
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

        keys = pg.key.get_pressed()

        for enmy in enemy_list:
            if enmy.health == 0:
                enemy_list.pop(enemy_list.index(enmy))

            enmy.move_and_shoot()
            for enmy_bul in enmy.bullets:
                if pythor.hitbox[0] < enmy_bul.x < pythor.hitbox[0] + pythor.hitbox[2] \
                        and pythor.hitbox[1] < enmy_bul.y + enmy_bul.hitbox[3] < pythor.hitbox[1] + pythor.hitbox[3]:
                    enmy.bullets.pop(enmy.bullets.index(enmy_bul))
                    pythor.get_hit()
            for plyr_bul in pythor.bullets:
                if enmy.hitbox[0] < plyr_bul.x < enmy.hitbox[0] + enmy.hitbox[2] \
                        and enmy.hitbox[1] < plyr_bul.y + plyr_bul.hitbox[3] < enmy.hitbox[1] + enmy.hitbox[3]:
                    pythor.bullets.pop(pythor.bullets.index(plyr_bul))
                    enmy.get_hit()
            if (enmy.hitbox[0] < pythor.x < enmy.hitbox[0] + enmy.hitbox[2] \
                    and enmy.hitbox[1] < pythor.y < enmy.hitbox[1] + enmy.hitbox[3]) \
                        or (pythor.hitbox[0] < enmy.x < pythor.hitbox[0] + pythor.hitbox[2] \
                    and pythor.hitbox[1] < enmy.y < pythor.hitbox[1] + pythor.hitbox[3]):
                pythor.get_hit()
                pythor.get_pushed()

        if pythor.health == 0:
            run = False
            isLost = True

        if len(enemy_list) == 0:
            if stage == 2 and level != 3:
                if show_quiz():
                    pythor.health = 7
                level += 1
                stage = 1
                enemy_list = list(generate_enemies(level, stage))
            elif level == 3 and stage == 3:
                run = False
                isLost = False
                print("You win")
            else:
                stage += 1
                enemy_list = generate_enemies(level, stage)

        angle += 1
        pythor.move_and_shoot(keys)
        window_update()


def menu_window():
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
        mouse = pg.mouse.get_pressed()
        mousePos = pg.mouse.get_pos()
        window.blit(mainBg, (0, 0))
        if mouse[0] and 360 < mousePos[0] < 930 and 650 < mousePos[1] < 880:
            return True

        pg.display.update()


if menu_window():
    pythor = Player(screen_middle[0] - 120, screen_size[1] - 144)
    load_questions()
    main()
if isLost:
    text = font2.render("Game Over!", 1, (255, 255, 255))
    window.blit(text, (screen_size[0] / 10 - 50, screen_size[1] / 2.5))
    pg.display.update()
    pg.time.wait(3000)
elif isLost == False:
    text = font2.render("YOU WIN!", 1, (255, 255, 255))
    window.blit(text, (screen_size[0] / 8, screen_size[1] / 2.5))
    pg.display.update()
    pg.time.wait(3000)
else:
    pass
pg.quit()
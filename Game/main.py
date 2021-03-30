from livewires import games, color
import random
games.init(screen_height=600, screen_width=600, fps=50)


class Square(games.Sprite):
    HID = [games.load_image("hidden.png", transparent=False), games.load_image("question.png", transparent=False), games.load_image("flag.png", transparent=False)]
    NUMS = [games.load_image("blank.png", transparent=False), games.load_image("1.png", transparent=False), games.load_image("2.png", transparent=False), games.load_image("3.png", transparent=False),
            games.load_image("4.png", transparent=False), games.load_image("5.png", transparent=False), games.load_image("6.png", transparent=False),
            games.load_image("7.png", transparent=False),
            games.load_image("8.png", transparent=False)]  # TODO write a lambda function to handle that
    MINES = [games.load_image("mine.png", transparent=False), games.load_image("mine_red.png", transparent=False), games.load_image("mine_x.png", transparent=False)]

    def __init__(self, game = None, x=200, y=200, value=0):
        super(Square, self).__init__(image=Square.HID[0], x=Game.SPACE+x*32, y=Game.SPACE+y*32)
        self.value = value
        self.posx = x
        self.posy = y
        self.flagged = False
        self.shown = False
        self.game = game

    def show(self):
        if not self.flagged and not self.shown:
            self.game.shown_counter += 1
            self.shown = True
            if self.value == -2:
                self.image = Square.MINES[1]
            elif self.value == 0:
                self.reveal(self.posx, self.posy)
                self.image = Square.NUMS[self.value]
            elif self.value > 0:
                self.image = Square.NUMS[self.value]
            elif self.value == -1:
                self.image = Square.MINES[0]
    # def showforce(self):
    #     self.shown = True
    #     if self.value == 0:
    #         self.reveal()
    #     elif self.value > 0:
    #         self.image = Square.NUMS[self.value]
    #     elif self.value == -1:
    #         self.image = Square.MINES[1]

    def flag(self):
        if not self.flagged and not self.shown:
            self.image = Square.HID[2]
            self.flagged = True
            self.game.flagmod(1)
        elif not self.shown:
            self.game.flagmod(-1)
            self.flagged = not self.flagged
            self.image = Square.HID[0]

    def reveal(self, x1, y1):
        for y2 in range(-1, 2):
            for x2 in range(-1, 2):
                if len(self.game.mapa[0]) > x1 + x2 >= 0 and len(self.game.mapa) > y1 + y2 >= 0 and self.game.mapa[y1 + y2][x1 + x2] >= 0:
                    # self.game.mapasq[y1 + y2][x1 + x2].image = Square.NUMS[self.game.mapasq[y1 + y2][x1 + x2].value]
                    # self.game.mapasq[y1 + y2][x1 + x2].shown = True
                    self.game.mapasq[y1 + y2][x1 + x2].show()


class Pointer(games.Sprite):
    IMG = games.load_image("pointer.png", transparent=False)

    def __init__(self, game):
        super(Pointer, self).__init__(image=Pointer.IMG, x=games.mouse.x, y=games.mouse.y)
        self.press = True
        self.game = game

    def update(self):
        self.x = games.mouse.x
        self.y = games.mouse.y
        if games.mouse.is_pressed(0) and self.press:  # LMB
            for i in self.overlapping_sprites:
                if i.value == -1 and i.flagged is False:
                    i.value = -2
                    self.game.lose()
                i.show()

            self.press = False
        if not games.mouse.is_pressed(0) and not games.mouse.is_pressed(2):
            self.press = True
        if games.mouse.is_pressed(2) and self.press:  # RMB
            for i in self.overlapping_sprites:
                i.flag()
            self.press = False
        if self.game.shown_counter == (len(self.game.mapa)*len(self.game.mapa[0])-self.game.mines):
            self.game.win()
            self.destroy()

class Game(object):
    SPACE = games.screen.width/4
    FLAGX = 100
    FLAGY = 100

    def __init__(self, mapa, mines):
        self.mines = mines
        self.flags = 0
        self.flag_counter = games.Text(value="Flags: " + str(self.mines), x=Game.FLAGX, y=Game.FLAGY, color=color.red, size=50)
        games.screen.add(self.flag_counter)
        self.mouse = Pointer(self)
        # sq = Square()
        # games.screen.add(sq)
        self.mapasq = [[Square() for i in range(len(mapa[0]))] for y in range(len(mapa))]
        games.screen.add(self.mouse)
        self.mapa = mapa
        self.generate(mapa=self.mapa)
        self.shown_counter = 0

    def generate(self, mapa):
        for y in range(len(mapa)):
            for x in range(len(mapa[0])):
                sq = Square(x=x, y=y, value=mapa[y][x], game=self)
                self.mapasq[y][x] = sq
                games.screen.add(self.mapasq[y][x])

    def lose(self):
        self.mouse.destroy()
        self.show()
        lose_sound = games.load_sound("lose.wav")
        lose_sound.play()
        lose_msg = games.Message(value = "YOU LOST! FUKAA UwU", size=50, color = color.red, x = 500, y = 100, after_death=games.screen.quit, lifetime=5*games.screen.fps)
        games.screen.add(lose_msg)


    def show(self):
        for y in range(len(self.mapasq)):
            for x in range(len(self.mapasq[0])):
                self.mapasq[y][x].show()

    def flagmod(self, x):
        self.flags += x
        self.flag_counter.value = "Flags: " + str(self.mines - self.flags)
        self.flag_counter.x = Game.FLAGX
        self.flag_counter.y = Game.FLAGY

    def win(self):
        #  self.show() add back if shit doesn't work
        lose_sound = games.load_sound("win.wav")
        lose_sound.play()
        win_msg = games.Message(value="YOU WIN! FUKAA UwU", size=50, color=color.dark_green, x=400, y=100, after_death=games.screen.quit, lifetime=5*games.screen.fps)
        games.screen.add(win_msg)


def make_map(y, x, mines):
    nomines = 0
    mapa = [[0 for i in range(y)] for k in range(x)]
    loop = True
    while loop:
        for z in range(y):
            for b in range(x):
                if nomines == mines:
                    loop = False
                else:
                    if random.choice(range(100)) > 98 and mapa[b][z] != -1:
                        mapa[b][z] = -1
                        nomines += 1

    num = 0
    for y1 in range(len(mapa)):
        for x1 in range(len(mapa[0])):
            if mapa[y1][x1] != -1:
                for y2 in range(-1, 2):
                    for x2 in range(-1, 2):
                        if len(mapa[0]) > x1 + x2 >= 0 and len(mapa) > y1 + y2 >= 0 and mapa[y1+y2][x1+x2] == -1:
                            num += 1
                mapa[y1][x1] = num
            num = 0
    return mapa


def main(x=10, y=10, mines=7):
    games.screen.background = games.load_image("grey.png", transparent=False)
    mapka = make_map(x, y, mines)
    print(mapka)
    gaem = Game(mapka, mines)

    games.screen.mainloop()


def start():
    wejscie = True
    while(wejscie):
        try:
            x, y = input("Wprowadz pola np. 3x2:").split("x")
            x=int(x)
            y=int(y)
            wejscie = False
        except:
            print("Źle!")

    mines = 99999999999999999
    while(mines>x*y-1):
        try:
            mines = int(input("Ile min chcesz (nie więcej niż pól-1!)? "))
        except:
            mines = 9999999999999
    main(int(x), int(y), int(mines))

start()
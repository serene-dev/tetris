
import sys, random
import sdl2, sdl2.ext, sdl2.sdlmixer

ROWS = 20
COLS = 10

TETROMINOS = [
    [[1, 0, 0, 0],
     [1, 1, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 0, 0]],
    [[1, 0, 0, 0],
     [1, 0, 0, 0],
     [1, 1, 0, 0],
     [0, 0, 0, 0]],
    [[1, 0, 0, 0],
     [1, 1, 0, 0],
     [1, 0, 0, 0],
     [0, 0, 0, 0]],
    [[1, 1, 0, 0],
     [1, 1, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],
    [[1, 0, 0, 0],
     [1, 0, 0, 0],
     [1, 0, 0, 0],
     [1, 0, 0, 0]],
]

class Tetromino:
    def __init__(self, table):
        self.table = table
        self.x = COLS // 2 - 1
        self.y = 0
        self.color = random.randrange(7)
        i = random.randrange(len(TETROMINOS))
        self.data = TETROMINOS[i]
        if i < 2 and random.random() > 0.5:
            self.data = [[l[1], l[0], 0, 0] for l in self.data]

    def can_place(self, px, py, d=None):
        if not d:
            d = self.data
        for y in range(4):
            for x in range(4):
                ix, iy = x + px, y + py
                if d[y][x] and (iy < 0 or iy >= ROWS or ix < 0 or ix >= COLS or self.table[iy][ix] >= 0):
                    return False
        return True

    def rotate(self):
        d = [l for l in self.data]
        while d[3] == [0, 0, 0, 0]:
            d.insert(0, d.pop())

        d = [[d[3 - x][y] for x in range(4)] for y in range(4)]
        if self.can_place(self.x, self.y, d):
            self.data = d
        elif self.can_place(self.x - 1, self.y, d):
            self.x-= 1
            self.data = d

    def place(self):
        for y in range(4):
            for x in range(4):
                if self.data[y][x]:
                    self.table[self.y + y][self.x + x] = self.color

    def move(self, dx, dy):
        if self.can_place(self.x + dx, self.y + dy):
            self.x+= dx
            self.y+= dy
            return True
        return False

class TetrisApp:
    sfx = {}

    def __init__(self):
        sdl2.ext.init()
        sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
        window = sdl2.ext.Window("Tetris", size=(528, 672), flags=sdl2.SDL_WINDOW_BORDERLESS | sdl2.SDL_WINDOW_ALLOW_HIGHDPI)
        window.show()
        self.renderer = sdl2.ext.Renderer(window)

        self.music = sdl2.sdlmixer.Mix_LoadMUS(b"assets/tetris_theme.ogg")

    def _play(self, name):
        sfx = self.sfx.get(name, None)
        if not sfx:
            self.sfx[name] = sfx = sdl2.sdlmixer.Mix_LoadWAV(f"assets/{name}.wav".encode())
        sdl2.sdlmixer.Mix_PlayChannel(-1, sfx, 0)

    def run(self):
        sdl2.sdlmixer.Mix_PlayMusic(self.music, -1)

        background_tex = sdl2.ext.Texture(self.renderer, sdl2.ext.load_image(b"assets/background.png"))
        blocks_tex = sdl2.ext.Texture(self.renderer, sdl2.ext.load_image(b"assets/blocks.png"))
        gameover_tex = sdl2.ext.Texture(self.renderer, sdl2.ext.load_image(b"assets/gameover.png"))
        def draw(x, y, c):
            self.renderer.blit(
                blocks_tex,
                srcrect=(c * 32, 0, 32, 32),
                dstrect=((x + 0.5) * 32, (y + 0.5) * 32)
            )

        table = [[-1 for _ in range(COLS)] for _ in range(ROWS)]
        current, next = None, Tetromino(table)
        timer, speed = 0, 300
        scan_x, scan_y = None, None
        running, gameover = True, False
        while running:
            if not current and not gameover:
                if not next.can_place(next.x, next.y):
                    gameover = True
                    sdl2.sdlmixer.Mix_PauseMusic()
                    self._play("gameover")
                else:
                    current = next
                    next = Tetromino(table)

            self.renderer.blit(background_tex)
            for y in range(ROWS):
                for x in range(COLS):
                    c = table[y][x]
                    if c >= 0:
                        draw(x, y, c)
            if current:
                for y in range(4):
                    for x in range(4):
                        if current.data[y][x]:
                            draw(current.x + x, current.y + y, current.color)
            if next:
                for y in range(4):
                    for x in range(4):
                        if next.data[y][x]:
                            draw(x + 12, y + 0.5, next.color)
            if gameover:
                self.renderer.blit(gameover_tex)

            for e in sdl2.ext.get_events():
                if e.type == sdl2.SDL_QUIT:
                    running = False
                elif e.type == sdl2.SDL_KEYDOWN and e.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    running = False
                elif current and not gameover and e.type == sdl2.SDL_KEYDOWN:
                    k = e.key.keysym.sym
                    if k == sdl2.SDLK_j:
                        current.move(0, 1)
                    elif k == sdl2.SDLK_h:
                        current.move(-1, 0)
                    elif k == sdl2.SDLK_l:
                        current.move(1, 0)
                    elif k == sdl2.SDLK_k:
                        current.rotate()
                elif gameover and e.type == sdl2.SDL_KEYDOWN and e.key.keysym.sym == sdl2.SDLK_SPACE:
                    for y in range(ROWS):
                        for x in range(COLS):
                            table[y][x] = -1
                    gameover = False
                    sdl2.sdlmixer.Mix_PlayMusic(self.music, -1)

            self.renderer.present()
            sdl2.SDL_Delay(16)

            if scan_x != None:
                if scan_x < COLS:
                    for y in scan_y:
                        table[y][scan_x] = -1
                    scan_x+= 1
                else:
                    scan_x = None
                    for y in scan_y:
                        for x in range(COLS):
                            for ty in range(y, 0, -1):
                                table[ty][x] = table[ty - 1][x]

            timer+= 16
            if current and timer >= speed:
                timer = 0
                if not current.move(0, 1):
                    current.place()
                    self._play("fall")
                    scan_y = []
                    for y in range(current.y, current.y + 4):
                        if y >= ROWS:
                            continue
                        found = True
                        for x in range(COLS):
                            if table[y][x] < 0:
                                found = False
                                break
                        if found:
                            for x in range(0, COLS):
                                table[y][x] = 7
                            scan_y.append(y)
                            if scan_x == None:
                                self._play("line")
                            scan_x = 0
                    current = None

        return 0

if __name__ == "__main__":
    sys.exit(TetrisApp().run())


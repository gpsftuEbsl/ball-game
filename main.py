import sys
import pygame # type: ignore

# 初始化 Pygame
pygame.init()

# 畫面設定
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
BLACK = (0, 0, 0)

class Player:
    def __init__(self, image_path): # 建構子
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.y = HEIGHT  # 起始在底部
        self.move_speed = 10 # 每禎移動10像素

        self.jumping = False
        self.jump_counter = 0
        self.falling = False
        self.fall_counter = 0

    def handle_input(self, keys): # 成員函數
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.move_speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.move_speed
        if keys[pygame.K_UP] and not self.jumping and not self.falling: # 如果移除 and not self.falling 條件則在下落過程中可繼續往上跳
            self.jumping = True
            self.jump_counter = 15

    def update(self): # 成員函數
        if self.jumping:
            self.rect.y -= self.move_speed
            self.jump_counter -= 1
            if self.jump_counter <= 0:
                self.jumping = False
                self.falling = True
                self.fall_counter = 15 # 共15禎 每禎移動10像素

        elif self.falling:
            self.rect.y += self.move_speed
            self.fall_counter -= 1
            if self.fall_counter <= 0:
                self.falling = False

        # 邊界限制
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Game:
    def __init__(self): # 建構子
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("小球跳躍遊戲")

        # 載入背景地圖圖像
        self.background = pygame.image.load("background_map.png")  # 地圖圖片
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        # 建立玩家
        self.player = Player("small_ball.png")

    def run(self): # 主函數 也是成員函數
        clock = pygame.time.Clock() # 建立Clock類別的變數clock

        while True:
            for event in pygame.event.get(): # 從事件清單迭帶捕捉到的所有事件
                if event.type == pygame.QUIT: # 如果事件類型是離開遊戲...
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.update()

            # 畫面更新
            self.screen.blit(self.background, (0, 0))  # 畫背景地圖
            self.player.draw(self.screen)
            pygame.display.flip()

            clock.tick(60)  # 限制為每秒 60 幀

# 主程式
if __name__ == "__main__": # Python變數__name__ 其意義是「模組名稱」 如果該檔案是被引用，其值會是模組名稱；但若該檔案是(透過命令列)直接執行，其值會是 __main__
    game = Game() # 創建一個Game類別的變數game
    game.run() # 呼叫game的成員run()

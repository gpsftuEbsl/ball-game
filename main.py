import sys
import pygame # type: ignore

# 初始化 Pygame
pygame.init()

# 畫面設定
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
BLACK = (0, 0, 0)

# 格子大小
TILE_SIZE = 64

# 計算地圖尺寸 (根據螢幕大小)
MAP_COLS = WIDTH // TILE_SIZE
MAP_ROWS = HEIGHT // TILE_SIZE

# 創建更大的地圖數據來填滿整個螢幕
def create_full_screen_map():
    """創建填滿整個螢幕的地圖"""
    map_data = []
    
    for row in range(MAP_ROWS):
        line = ""
        for col in range(MAP_COLS):
            # 在特定位置放置障礙物
            if row == MAP_ROWS - 5:  # 距離底部5格的位置
                if 3 <= col <= 6 or 12 <= col <= 15:  # 兩組障礙物
                    line += "#"
                else:
                    line += "."
            elif row == MAP_ROWS - 8:  # 距離底部8格的位置
                if 8 <= col <= 10:  # 中間的障礙物
                    line += "#"
                else:
                    line += "."
            elif row == MAP_ROWS - 12:  # 距離底部12格的位置
                if 5 <= col <= 7 or 18 <= col <= 20:  # 更多障礙物
                    line += "#"
                else:
                    line += "."
            # elif row == MAP_ROWS - 1:  # 底部邊界
            #     line += "#"  # 底部全部都是障礙物作為地面
            else:
                line += "."
        map_data.append(line)
    
    return map_data

# 生成適合螢幕大小的地圖
map_data = create_full_screen_map()

class Obstacle:
    def __init__(self, x, y, width, height, image_path=None, color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = None

        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except:
                print(f"⚠️ 無法載入圖片：{image_path}，使用顏色替代")

        self.color = color

    def draw(self, screen):
        """繪製障礙物"""
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

    def colliderect(self, other_rect):
        """檢測碰撞"""
        return self.rect.colliderect(other_rect)

    def get_rect(self):
        """取得矩形區域"""
        return self.rect

    def move(self, dx, dy):
        """移動障礙物（如果需要動態障礙物）"""
        self.rect.x += dx
        self.rect.y += dy

    def set_position(self, x, y):
        """設定障礙物位置"""
        self.rect.x = x
        self.rect.y = y

    def contains_point(self, x, y):
        """檢查點是否在障礙物內"""
        return self.rect.collidepoint(x, y)


class Player:
    def __init__(self, image_path): # 建構子
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.y = HEIGHT - 150  # 起始在地面上方
        self.rect.x = 100  # 起始在左側
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
            self.jump_counter = 30

    def update(self, obstacles): # 成員函數 - 加入障礙物碰撞檢測
        # 記錄原始位置
        old_x, old_y = self.rect.x, self.rect.y
        
        if self.jumping:
            self.rect.y -= self.move_speed
            self.jump_counter -= 1
            if self.jump_counter <= 0:
                self.jumping = False
                self.falling = True
                self.fall_counter = 30 # 共15禎 每禎移動10像素

        elif self.falling:
            self.rect.y += self.move_speed
            self.fall_counter -= 1
            if self.fall_counter <= 0:
                self.falling = False

        # 檢查與障礙物的碰撞
        for obstacle in obstacles:
            if obstacle.colliderect(self.rect):
                # 發生碰撞，恢復到原來位置
                self.rect.x, self.rect.y = old_x, old_y
                # 如果在跳躍或下落中碰撞，停止動作
                if self.jumping:
                    self.jumping = False
                    self.falling = True
                    self.fall_counter = 30
                elif self.falling:
                    self.falling = False
                break

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
        try:
            self.background = pygame.image.load("background_map.png")  # 地圖圖片
            self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        except:
            print("⚠️ 無法載入背景圖片，使用黑色背景")
            self.background = pygame.Surface((WIDTH, HEIGHT))
            self.background.fill(BLACK)

        # 建立玩家
        try:
            self.player = Player("small_ball.png")
        except:
            print("⚠️ 無法載入玩家圖片，請確保 small_ball.png 存在")
            # 建立一個簡單的矩形作為玩家
            self.player = self.create_simple_player()
        
        # 調整玩家起始位置到地面上方
        self.player.rect.y = HEIGHT - 150  # 在地面上方

        # 根據地圖數據建立障礙物
        self.obstacles = self.create_obstacles_from_map(map_data)

    def create_simple_player(self):
        """建立簡單的矩形玩家（當圖片載入失敗時使用）"""
        class SimplePlayer:
            def __init__(self):
                self.rect = pygame.Rect(100, HEIGHT - 150, 32, 32)  # 調整起始位置
                self.move_speed = 10
                self.jumping = False
                self.jump_counter = 0
                self.falling = False
                self.fall_counter = 0

            def handle_input(self, keys):
                if keys[pygame.K_LEFT]:
                    self.rect.x -= self.move_speed
                if keys[pygame.K_RIGHT]:
                    self.rect.x += self.move_speed
                if keys[pygame.K_UP] and not self.jumping and not self.falling:
                    self.jumping = True
                    self.jump_counter = 15

            def update(self, obstacles):
                old_x, old_y = self.rect.x, self.rect.y
                
                if self.jumping:
                    self.rect.y -= self.move_speed
                    self.jump_counter -= 1
                    if self.jump_counter <= 0:
                        self.jumping = False
                        self.falling = True
                        self.fall_counter = 15

                elif self.falling:
                    self.rect.y += self.move_speed
                    self.fall_counter -= 1
                    if self.fall_counter <= 0:
                        self.falling = False

                for obstacle in obstacles:
                    if obstacle.colliderect(self.rect):
                        self.rect.x, self.rect.y = old_x, old_y
                        if self.jumping:
                            self.jumping = False
                            self.falling = True
                            self.fall_counter = 15
                        elif self.falling:
                            self.falling = False
                        break

                if self.rect.left < 0:
                    self.rect.left = 0
                if self.rect.right > WIDTH:
                    self.rect.right = WIDTH
                if self.rect.top < 0:
                    self.rect.top = 0
                if self.rect.bottom > HEIGHT:
                    self.rect.bottom = HEIGHT

            def draw(self, surface):
                pygame.draw.circle(surface, (255, 255, 0), self.rect.center, 16)

        return SimplePlayer()

    def create_obstacles_from_map(self, map_data):
        """根據地圖數據建立障礙物列表"""
        obstacles = []
        
        for row_index, row in enumerate(map_data):
            for col_index, cell in enumerate(row):
                if cell == '#':  # 如果是障礙物標記
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    
                    # 建立障礙物 (可以指定圖片路徑或使用預設顏色)
                    obstacle = Obstacle(
                        x=x, 
                        y=y, 
                        width=TILE_SIZE, 
                        height=TILE_SIZE,
                        image_path=None,  # 可以改為 "obstacle.png" 如果有圖片
                        color=(139, 69, 19)  # 棕色
                    )
                    obstacles.append(obstacle)
        
        return obstacles

    def run(self): # 主函數 也是成員函數
        clock = pygame.time.Clock() # 建立Clock類別的變數clock

        while True:
            for event in pygame.event.get(): # 從事件清單迭帶捕捉到的所有事件
                if event.type == pygame.QUIT: # 如果事件類型是離開遊戲...
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.update(self.obstacles)  # 傳入障礙物列表

            # 畫面更新
            self.screen.blit(self.background, (0, 0))  # 畫背景地圖
            
            # 繪製所有障礙物
            for obstacle in self.obstacles:
                obstacle.draw(self.screen)
            
            # 繪製玩家
            self.player.draw(self.screen)
            
            pygame.display.flip()

            clock.tick(60)  # 限制為每秒 60 幀

# 主程式
if __name__ == "__main__": # Python變數__name__ 其意義是「模組名稱」 如果該檔案是被引用，其值會是模組名稱；但若該檔案是(透過命令列)直接執行，其值會是 __main__
    game = Game() # 創建一個Game類別的變數game
    game.run() # 呼叫game的成員run()
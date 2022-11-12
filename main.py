import pygame
import random
import button
import menu_button
from pygame.locals import *
from pygame import mixer

pygame.init()

clock = pygame.time.Clock()

fps = 60

# Musica de fundo
bg_song = pygame.mixer.music.load('musica/menu_song.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 5000)

#FX sounds do jogo
riven_aa = pygame.mixer.Sound('FX/riven_aa.mp3')
renek_aa = pygame.mixer.Sound('FX/renek_aa.mp3')
drink_potion = pygame.mixer.Sound('FX/drink_potion.mp3')
riven_start = pygame.mixer.Sound('FX/Riven_Select.mp3')

# Tamanho da janela do jogo
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Battle')

# Definir variaveis do jogo
current_fighter = 1  # O cavaleiro vai ser o primeiro a atacar
total_fighters = 3  # Total de lutadores
action_cooldown = 0  # Cooldown 
action_wait_time = 90 # Tempo de espera entre os turnos
attack = False
potion = False
potion_effect = 15 
clicked = False
game_over = 0
start_game = False

# Carregar os butões do menu
start_img = pygame.image.load('imagens/start_btn.png').convert_alpha()
exit_img = pygame.image.load('imagens/exit_btn.png').convert_alpha()

# Carregar as imagens do jogo
background_img = pygame.image.load('imagens/background/background.png').convert_alpha()

# Carregar as imagens do painel
panel_img = pygame.image.load('imagens/icons/panel.png').convert_alpha()

# Carregar as imagens dos butões
potion_img = pygame.image.load('imagens/icons/potion.png').convert_alpha()
restart_img = pygame.image.load('imagens/icons/restart.png').convert_alpha()

#Carregar as imagens de derrota e vitoria
victory_img = pygame.image.load('imagens/icons/victory.png')
defeat_img = pygame.image.load('imagens/icons/defeat.png')
# Carregar as imagens do painel
sword_img = pygame.image.load('imagens/icons/sword.png').convert_alpha()

# Definir as fontes
font = pygame.font.SysFont('Times New Roman', 26)

# Definir cores
red = (255, 0, 0)
green = (0, 255, 0)
black = (0, 0, 0)

# Carregar imagem de fundo
def draw_bg():
    screen.blit(background_img, (0, 0))

# Função para desenhar texto
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color) # criar a imagem pq em python tem q ser texto convertido em img
    screen.blit(img, (x, y)) # exibit na tela com as coords x y

# Carregar imagem do painel
def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    # Mostrar as stats do cavaleiro
    draw_text(f'{riven.name} HP: {riven.hp}', font, red, 100, screen_height - bottom_panel + 10)
    for count, i in enumerate(renek_list):
        # Mostrar nome e vida
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)

# Classe dos lutadores
class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potion):  # construtor
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potion = potion
        self.potion = potion
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0: idle, 1: ataque, 2: machucar, 3:morto
        self.update_time = pygame.time.get_ticks()

        # Carregar imagens de idle
        temp_list = []
        for i in range(10):
            img = pygame.image.load(f'imagens/{self.name}/idle/{i}.png')
           # img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list) # uma lista de listas

        # carregar imagens de ataque
        temp_list = []
        for i in range(15):
                img = pygame.image.load(f'imagens/{self.name}/attack/{i}.png')
               # img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
                temp_list.append(img)
        self.animation_list.append(temp_list)

        # carregar imagens qnd o player leva dano
        temp_list = []
        for i in range(3):
                img = pygame.image.load(f'imagens/{self.name}/hurt/{i}.png')
               # img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
                temp_list.append(img)
        self.animation_list.append(temp_list)

        # carregar imagens de morte
        temp_list = []
        for i in range(22):
                img = pygame.image.load(f'imagens/{self.name}/death/{i}.png')
               # img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
                temp_list.append(img)
        self.animation_list.append(temp_list) 
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100
        
        # animação
        # atualizar as imagens
        self.image = self.animation_list[self.action][self.frame_index]

        # pegue o tempo atual, tire o tempo que foi atualizado recentemente e se a diferença entre os dois for maior que 100, entao atualize a imagem
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Se a animação acabar, resetar desde o zero (idle)
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1 # ultimo frame da animação
            else:
                self.idle()

    def idle(self):
         # Resetar animação para idle
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        

    def attack(self, target):
        # Atribui dano no inimigo
        rand = random.randint(-5, 5) # entre -5 e 5 numero aleatorio o dano do jogador
        damage = self.strength + rand # dano do jogador 
        target.hp -= damage  # Dano final causado nos inimigos

        # Animação de levar dano
        target.hurt()

        # Checar se o target morreu
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()

        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)

        # Animação de ataque
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        # Animação para qnd levar o dano
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
    
    def death(self):
        # Animação da morte
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
    
    def reset(self):
        self.alive = True
        self.potion = self.start_potion
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
    
    def draw(self):
        screen.blit(self.image, self.rect)

# Classe do HP
class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self. hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        # Atualize a barra de hp
        self.hp = hp
        # Calcular o ratio do hp
        ratio = self.hp/self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))

# Classe de Texto de Dano
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
    
    def update(self):
        # Mover o texto pra cima
        self.rect.y -= 1   # Positivo = vai pra baixo / Negativo = vai pra cima
        # Deletar o texto depois de alguns segundos
        self.counter += 1
        if self.counter > 30:
            self.kill()       

damage_text_group = pygame.sprite.Group()

riven = Fighter(200, 260, 'Riven', 30, 10, 3)
renek1 = Fighter(550, 270, 'Renekton', 20, 6, 1)
renek2 = Fighter(700, 270, 'Renekton', 20, 6, 1)

renek_list = []

renek_list.append(renek1)
renek_list.append(renek2)

riven_health_bar = HealthBar(100, screen_height - bottom_panel + 40, riven.hp, riven.max_hp)
renek1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, renek1.hp, renek1.max_hp)
renek2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, renek2.hp, renek2.max_hp)

# Criar butões
potion_button = button.Button(screen, 100, screen_height - bottom_panel + 70, potion_img, 64, 64)
restart_button = button.Button(screen, 330, 120, restart_img, 120, 30)
# Butoes do menu
start_button = menu_button.Button(screen_width // 2 - 130, screen_height // 2 - 150, start_img, 1)
exit_button = menu_button.Button(screen_width // 2 - 110, screen_height // 2 + 50, exit_img, 1)


run = True
while run:

    clock.tick(fps)


    if start_game == False:
        # menu principal
        screen.fill(black)
        # Carregar musica do jogo
        # adicionar butoes
        if start_button.draw(screen):
            start_game = True
            # riven_start.play(0)
        if exit_button.draw(screen):
            run = False
    else:
        # desenhe a imagem de fundo
        draw_bg()

        # desenhe a imagem do painel
        draw_panel()

        riven_health_bar.draw(riven.hp)
        renek1_health_bar.draw(renek1.hp)
        renek2_health_bar.draw(renek2.hp)

        # desenhe o cavaleiro
        riven.update()
        riven.draw()

        for renek in renek_list:
            renek.update()
            renek.draw()

        # desenhe o texto do dano
        damage_text_group.update()
        damage_text_group.draw(screen)

        # Controlar ações do jogador
        #Resetar as variaveis de ação
        attack = False
        potion = False
        target = None

        # Deixar o cursor do mouse visivel 
        pygame.mouse.set_visible(True)
        pos = pygame.mouse.get_pos() # passar o mouse em cima do inimigo mostra o icone de espada 

        for count, renek in enumerate(renek_list):
            if renek.rect.collidepoint(pos):
                # esconder o mouse
                pygame.mouse.set_visible(False)
                # mostrar o icone da espada no lugar do cursor
                screen.blit(sword_img, pos)
                if clicked == True and renek.alive == True:
                    attack = True
                    target = renek_list[count]

        if potion_button.draw():
            potion = True

        # Mostrar quantas poções restam
        draw_text(str(riven.potion), font, red, 150, screen_height - bottom_panel + 70)

        if game_over == 0:
            # Ação do jogador
            if riven.alive == True: # Se estiver vivo
                if current_fighter == 1: # Começa a atacar
                    action_cooldown +=1 # Incrementa o tempo de ação até 90 do action_wait_time
                    if action_cooldown >= action_wait_time: # Esta pronto para atacar
                        # Procurar a ação do jogador
                        # Ataque
                        if attack == True and target != None:
                            riven.attack(target) # ataca o bandido 1 
                            current_fighter += 1  # avança para o proximo lutador
                            action_cooldown = 0 # reseta o cooldown de espera
                            riven_aa.play()
                        # Poção
                        if potion == True:
                            if riven.potion > 0:
                                # Checar se a poção vai curar mais do q a vida maxima
                                # Exemplo: se o jogador tem 30 hp, levar 5 de dano, ele vai ter 25 de hp
                                #  30  - 25 = 5 (nao eh maior que 15, entao skipa e vai pro else)
                                if riven.max_hp - riven.hp > potion_effect:
                                    heal_amount = potion_effect 
                                # So curar o restante dos 5, sem ultrapassar o HP max dele. 
                                else: 
                                    heal_amount = riven.max_hp - riven.hp
                                riven.hp += heal_amount
                                riven.potion -= 1
                                damage_text = DamageText(riven.rect.centerx, riven.rect.y, str(heal_amount), green)
                                damage_text_group.add(damage_text)
                                current_fighter += 1
                                action_cooldown = 0
                                drink_potion.play()
            else:
                game_over = -1

            # Ação do inimigo
            for count, renek in enumerate(renek_list):
                if current_fighter == 2 + count:
                    if renek.alive == True:
                        action_cooldown += 1 
                        # Poção
                        if action_cooldown >= action_wait_time:
                            # Checar se o bandido precisa curar antes de atacar
                            if (renek.hp / renek.max_hp) < 0.5 and renek.potion > 0:
                                # Checar se a poção vai curar mais do q a vida maxima
                                if renek.max_hp - renek.hp > potion_effect:
                                    heal_amount = potion_effect 
                                else: 
                                    heal_amount = renek.max_hp - renek.hp
                                renek.hp += heal_amount
                                renek.potion -= 1
                                damage_text = DamageText(renek.rect.centerx, renek.rect.y, str(heal_amount), green)
                                damage_text_group.add(damage_text)
                                current_fighter += 1
                                action_cooldown = 0
                                drink_potion.play()
                            # Ataque
                            else:
                                renek.attack(riven)
                                current_fighter += 1
                                action_cooldown = 0
                                renek_aa.play()
                    else: # Se estiver morto
                        current_fighter += 1 # passa pro proximo lutador
            if current_fighter > total_fighters:
                current_fighter = 1

        #checar se os inimigos estao mortos
        alive_reneks = 0
        for renek in renek_list:
            if renek.alive == True:
                alive_reneks += 1
        if alive_reneks == 0:
            game_over = 1 # todos mortos = vitoria


        # Checar se o jogo acabou
        if game_over != 0:
            if game_over == 1:
                screen.blit(victory_img, (250, 50))
            if game_over == -1:
                screen.blit(defeat_img, (290, 50))
            if restart_button.draw():
                riven.reset()
                for renek in renek_list:
                    renek.reset()
                current_fighter = 1
                action_cooldown = 0
                game_over = 0

    # Função pra sair do jogo
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                start_game = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False
            
    pygame.display.update()

pygame.quit()
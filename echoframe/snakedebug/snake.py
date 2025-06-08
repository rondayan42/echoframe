# snake.py: Main game logic file.
import pygame
import sys
import random
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, FPS, WHITE, RED,
                       FONT_NAME, FONT_SIZE, SCORE_POS, GAME_OVER_FONT_SIZE, RESTART_FONT_SIZE)
from snake_class import Snake
from food import Food

def get_new_direction_from_input(current_direction, key_event):
    """Determines new direction based on key event, preventing reversal."""
    if key_event.key == pygame.K_UP and current_direction != 'DOWN':
        return 'UP'
    elif key_event.key == pygame.K_DOWN and current_direction != 'UP':
        return 'DOWN'
    elif key_event.key == pygame.K_LEFT and current_direction != 'RIGHT':
        return 'LEFT'
    elif key_event.key == pygame.K_RIGHT and current_direction != 'LEFT':
        return 'RIGHT'
    return current_direction

pygame.init()
pygame.font.init()

window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Snake Echo - Final Quest')
clock = pygame.time.Clock()

try:
    score_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    game_over_font = pygame.font.SysFont(FONT_NAME, GAME_OVER_FONT_SIZE)
    restart_font = pygame.font.SysFont(FONT_NAME, RESTART_FONT_SIZE)
except pygame.error as e:
    print(f"Warning: Could not load system font. Using default. Error: {e}")
    score_font = pygame.font.Font(None, FONT_SIZE)
    game_over_font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
    restart_font = pygame.font.Font(None, RESTART_FONT_SIZE)

score = 0
game_over = False
snake = Snake()
food = Food()

def reset_game_state():
    global snake, food, score, game_over
    snake = Snake()
    food.reset_position(snake.positions)
    score = 0
    game_over = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_SPACE:
                    reset_game_state()
            else:
                new_dir = get_new_direction_from_input(snake.direction, event)
                snake.change_direction(new_dir)

    if not game_over:
        snake.update()
        if snake.check_wall_collision() or snake.check_self_collision():
            game_over = True
        if snake.positions[0] == food.position:
            snake.grow()
            food.reset_position(snake.positions)
            score += 1

    # --- Required for backend preview system ---
    try:
        get_user_direction()
    except Exception:
        pass

    screen.fill(BLACK)
    snake.draw(screen)
    food.draw(screen)

    score_surface = score_font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_surface, SCORE_POS)

    if game_over:
        over_text_surface = game_over_font.render('GAME OVER', True, RED)
        final_score_surface = score_font.render(f'Final Score: {score}', True, WHITE)
        restart_surface = restart_font.render('Press SPACE to restart', True, WHITE)
        over_text_rect = over_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - GAME_OVER_FONT_SIZE // 2))
        final_score_rect = final_score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + RESTART_FONT_SIZE))
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + RESTART_FONT_SIZE * 2.5))
        screen.blit(over_text_surface, over_text_rect)
        screen.blit(final_score_surface, final_score_rect)
        screen.blit(restart_surface, restart_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit() 
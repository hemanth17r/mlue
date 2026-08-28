"""Canonical Traditional Baseline: Imperative Pong

Standard procedural/OOP game implementation in Python to benchmark against MLUE.
"""

import time
import math


class TraditionalPongGame:
    def __init__(self, width=600, height=400):
        self.width = width
        self.height = height
        self.ball_x = width / 2
        self.ball_y = height / 2
        self.ball_vx = 200.0
        self.ball_vy = 150.0
        self.ball_radius = 8

        self.paddle_w = 12
        self.paddle_h = 60
        self.paddle_left_y = height / 2
        self.paddle_right_y = height / 2
        self.paddle_speed = 300.0

        self.score_left = 0
        self.score_right = 0

    def update(self, dt: float, left_input: float = 0.0, right_input: float = 0.0):
        # 1. Update Paddles
        self.paddle_left_y += left_input * self.paddle_speed * dt
        self.paddle_right_y += right_input * self.paddle_speed * dt
        self.paddle_left_y = max(self.paddle_h / 2, min(self.height - self.paddle_h / 2, self.paddle_left_y))
        self.paddle_right_y = max(self.paddle_h / 2, min(self.height - self.paddle_h / 2, self.paddle_right_y))

        # 2. Update Ball
        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt

        # 3. Top & Bottom Wall Collisions
        if self.ball_y - self.ball_radius <= 0:
            self.ball_y = self.ball_radius
            self.ball_vy = abs(self.ball_vy)
        elif self.ball_y + self.ball_radius >= self.height:
            self.ball_y = self.height - self.ball_radius
            self.ball_vy = -abs(self.ball_vy)

        # 4. Paddle Collisions
        # Left Paddle
        if (self.ball_x - self.ball_radius <= 30 + self.paddle_w and
            abs(self.ball_y - self.paddle_left_y) <= self.paddle_h / 2):
            self.ball_vx = abs(self.ball_vx)
            self.ball_x = 30 + self.paddle_w + self.ball_radius

        # Right Paddle
        if (self.ball_x + self.ball_radius >= self.width - 30 - self.paddle_w and
            abs(self.ball_y - self.paddle_right_y) <= self.paddle_h / 2):
            self.ball_vx = -abs(self.ball_vx)
            self.ball_x = self.width - 30 - self.paddle_w - self.ball_radius

        # 5. Goal Bounds
        if self.ball_x < 0:
            self.score_right += 1
            self.ball_x = self.width / 2
            self.ball_y = self.height / 2
            self.ball_vx = abs(self.ball_vx)
        elif self.ball_x > self.width:
            self.score_left += 1
            self.ball_x = self.width / 2
            self.ball_y = self.height / 2
            self.ball_vx = -abs(self.ball_vx)


if __name__ == "__main__":
    game = TraditionalPongGame()
    t0 = time.perf_counter()
    for _ in range(10000):
        game.update(1.0 / 60.0)
    t1 = time.perf_counter()
    print(f"Traditional Pong 10k steps executed in {t1 - t0:.4f}s ({(10000 / (t1 - t0)):,.0f} ticks/s)")

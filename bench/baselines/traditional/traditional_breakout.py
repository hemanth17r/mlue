"""Canonical Traditional Baseline: Imperative Breakout

Standard procedural/OOP game implementation in Python to benchmark against MLUE.
"""

import time
import math


class Brick:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.active = True


class TraditionalBreakoutGame:
    def __init__(self, width=600, height=400):
        self.width = width
        self.height = height
        self.ball_x = width / 2
        self.ball_y = height * 0.7
        self.ball_vx = 180.0
        self.ball_vy = -200.0
        self.ball_radius = 8

        self.paddle_w = 80
        self.paddle_h = 12
        self.paddle_x = width / 2
        self.paddle_y = height - 20
        self.paddle_speed = 350.0

        self.bricks = []
        rows = 4
        cols = 8
        b_w = 60
        b_h = 20
        pad = 8
        offset_x = (width - (cols * (b_w + pad))) / 2
        offset_y = 40

        for r in range(rows):
            for c in range(cols):
                bx = offset_x + c * (b_w + pad)
                by = offset_y + r * (b_h + pad)
                self.bricks.append(Brick(bx, by, b_w, b_h))

        self.score = 0

    def update(self, dt: float, paddle_input: float = 0.0):
        # 1. Update Paddle
        self.paddle_x += paddle_input * self.paddle_speed * dt
        self.paddle_x = max(self.paddle_w / 2, min(self.width - self.paddle_w / 2, self.paddle_x))

        # 2. Update Ball
        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt

        # 3. Wall Collisions
        if self.ball_x - self.ball_radius <= 0:
            self.ball_x = self.ball_radius
            self.ball_vx = abs(self.ball_vx)
        elif self.ball_x + self.ball_radius >= self.width:
            self.ball_x = self.width - self.ball_radius
            self.ball_vx = -abs(self.ball_vx)

        if self.ball_y - self.ball_radius <= 0:
            self.ball_y = self.ball_radius
            self.ball_vy = abs(self.ball_vy)
        elif self.ball_y + self.ball_radius >= self.height:
            # Ball lost, reset
            self.ball_x = self.width / 2
            self.ball_y = self.height * 0.7
            self.ball_vx = 180.0
            self.ball_vy = -200.0

        # 4. Paddle Collision
        if (abs(self.ball_x - self.paddle_x) <= self.paddle_w / 2 + self.ball_radius and
            abs(self.ball_y - self.paddle_y) <= self.paddle_h / 2 + self.ball_radius and
            self.ball_vy > 0):
            self.ball_vy = -abs(self.ball_vy)

        # 5. Brick Collisions
        for b in self.bricks:
            if not b.active:
                continue
            if (b.x <= self.ball_x <= b.x + b.w and
                b.y <= self.ball_y <= b.y + b.h):
                b.active = False
                self.score += 10
                self.ball_vy = -self.ball_vy
                break


if __name__ == "__main__":
    game = TraditionalBreakoutGame()
    t0 = time.perf_counter()
    for _ in range(10000):
        game.update(1.0 / 60.0)
    t1 = time.perf_counter()
    print(f"Traditional Breakout 10k steps executed in {t1 - t0:.4f}s ({(10000 / (t1 - t0)):,.0f} ticks/s)")

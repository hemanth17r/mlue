#define MLUE_BUILD_DLL
#include "mlue_core.h"
#include <math.h>

/* Version Discovery */
MLUE_API uint32_t mlue_core_version(void) {
    return (MLUE_CORE_VERSION_MAJOR << 16) |
           (MLUE_CORE_VERSION_MINOR << 8) |
           MLUE_CORE_VERSION_PATCH;
}

/* Helper: Clamp double value */
static inline double clamp_d(double v, double min_v, double max_v) {
    if (v < min_v) return min_v;
    if (v > max_v) return max_v;
    return v;
}

/* Helper: Minimum double */
static inline double min_d(double a, double b) {
    return (a < b) ? a : b;
}

/* Helper: Maximum double */
static inline double max_d(double a, double b) {
    return (a > b) ? a : b;
}

/* Helper: Q32.32 Fixed Point Multiplication */
static inline int64_t fp_mul_c(int64_t a, int64_t b) {
    return (a * b) >> MLUE_FP_SHIFT;
}

/* Helper: Q32.32 Fixed Point Conversion */
static inline int64_t float_to_fp_c(double val) {
    return (int64_t)round(val * 4294967296.0);
}

static inline double fp_to_float_c(int64_t raw) {
    return (double)raw / 4294967296.0;
}

/* Helper: Integer Square Root */
static inline uint64_t isqrt_c(uint64_t val) {
    if (val == 0) return 0;
    uint64_t x0 = val >> 1;
    if (x0 == 0) return 1;
    uint64_t x1 = (x0 + val / x0) >> 1;
    while (x1 < x0) {
        x0 = x1;
        x1 = (x0 + val / x0) >> 1;
    }
    return x0;
}

/* Main Continuous Floating-Point Simulation Step */
MLUE_API MLUE_StepResult mlue_core_step(
    MLUE_EntityRecord* entities,
    uint32_t num_entities,
    const MLUE_Environment* env,
    double dt
) {
    MLUE_StepResult result;
    result.num_active_entities = 0;
    result.num_collision_events = 0;
    result.candidate_pairs_checked = 0;
    result.status_flags = 0;

    if (!entities || !env || num_entities == 0) {
        return result;
    }

    double env_w = (double)env->width;
    double env_h = (double)env->height;
    double min_dim = min_d(env_w, env_h);

    /* 1. Time Integration & Arena Boundary Clamping */
    for (uint32_t i = 0; i < num_entities; i++) {
        MLUE_EntityRecord* e = &entities[i];
        if (!(e->flags & MLUE_FLAG_ACTIVE)) {
            continue;
        }
        result.num_active_entities++;

        /* Compute half-extents */
        double ex = 0.0;
        double ey = 0.0;
        if (e->entity_type == MLUE_ENTITY_TYPE_CIRCLE) {
            double r = e->size_p1;
            ex = r * (min_dim / env_w);
            ey = r * (min_dim / env_h);
        } else if (e->entity_type == MLUE_ENTITY_TYPE_BOX) {
            ex = e->size_p1 / 2.0;
            ey = e->size_p2 / 2.0;
        }

        /* Euler position update: p += v * dt */
        double new_x = e->pos_x + (e->vel_vx * dt);
        double new_y = e->pos_y + (e->vel_vy * dt);
        double new_vx = e->vel_vx;
        double new_vy = e->vel_vy;

        /* Arena boundaries [0.0, 1.0] */
        if (new_x - ex <= 0.0) {
            new_x = ex;
            if (new_vx < 0.0) new_vx = -new_vx;
        } else if (new_x + ex >= 1.0) {
            new_x = 1.0 - ex;
            if (new_vx > 0.0) new_vx = -new_vx;
        }

        if (new_y - ey <= 0.0) {
            new_y = ey;
            if (new_vy < 0.0) new_vy = -new_vy;
        } else if (new_y + ey >= 1.0) {
            new_y = 1.0 - ey;
            if (new_vy > 0.0) new_vy = -new_vy;
        }

        /* Clamp inside normalized arena */
        e->pos_x = clamp_d(new_x, ex, 1.0 - ex);
        e->pos_y = clamp_d(new_y, ey, 1.0 - ey);
        e->vel_vx = new_vx;
        e->vel_vy = new_vy;
    }

    /* 2. Pairwise Collision Resolution */
    for (uint32_t i = 0; i < num_entities; i++) {
        MLUE_EntityRecord* e1 = &entities[i];
        if (!(e1->flags & MLUE_FLAG_ACTIVE) || !(e1->flags & MLUE_FLAG_SOLID)) {
            continue;
        }

        for (uint32_t j = i + 1; j < num_entities; j++) {
            MLUE_EntityRecord* e2 = &entities[j];
            if (!(e2->flags & MLUE_FLAG_ACTIVE) || !(e2->flags & MLUE_FLAG_SOLID)) {
                continue;
            }

            result.candidate_pairs_checked++;

            /* Circle vs Circle Elastic Impulse */
            if (e1->entity_type == MLUE_ENTITY_TYPE_CIRCLE && e2->entity_type == MLUE_ENTITY_TYPE_CIRCLE) {
                double r1 = e1->size_p1;
                double r2 = e2->size_p1;
                double dx = (e1->pos_x - e2->pos_x) * (env_w / min_dim);
                double dy = (e1->pos_y - e2->pos_y) * (env_h / min_dim);
                double dist_sq = (dx * dx) + (dy * dy);
                double min_dist = r1 + r2;

                if (dist_sq < (min_dist * min_dist) && dist_sq > 1e-12) {
                    double dist = sqrt(dist_sq);
                    double nx = dx / dist;
                    double ny = dy / dist;

                    double rvx = e1->vel_vx - e2->vel_vx;
                    double rvy = e1->vel_vy - e2->vel_vy;
                    double vel_along_norm = (rvx * nx) + (rvy * ny);

                    if (vel_along_norm < 0.0) {
                        double impulse = -vel_along_norm;
                        e1->vel_vx += nx * impulse;
                        e1->vel_vy += ny * impulse;
                        e2->vel_vx -= nx * impulse;
                        e2->vel_vy -= ny * impulse;

                        /* Positional separation */
                        double pen = (min_dist - dist) * 0.5;
                        e1->pos_x += nx * pen * (min_dim / env_w);
                        e1->pos_y += ny * pen * (min_dim / env_h);
                        e2->pos_x -= nx * pen * (min_dim / env_w);
                        e2->pos_y -= ny * pen * (min_dim / env_h);

                        result.num_collision_events++;
                    }
                }
            }
            /* Box vs Box Elastic Impulse */
            else if (e1->entity_type == MLUE_ENTITY_TYPE_BOX && e2->entity_type == MLUE_ENTITY_TYPE_BOX) {
                double hw1 = e1->size_p1 * 0.5;
                double hh1 = e1->size_p2 * 0.5;
                double hw2 = e2->size_p1 * 0.5;
                double hh2 = e2->size_p2 * 0.5;

                double dx = e1->pos_x - e2->pos_x;
                double dy = e1->pos_y - e2->pos_y;
                double ox = (hw1 + hw2) - fabs(dx);
                double oy = (hh1 + hh2) - fabs(dy);

                if (ox > 0.0 && oy > 0.0) {
                    if (ox < oy) {
                        double sign_x = (dx > 0.0) ? 1.0 : -1.0;
                        e1->pos_x += sign_x * (ox * 0.5);
                        e2->pos_x -= sign_x * (ox * 0.5);
                        double temp = e1->vel_vx;
                        e1->vel_vx = e2->vel_vx;
                        e2->vel_vx = temp;
                    } else {
                        double sign_y = (dy > 0.0) ? 1.0 : -1.0;
                        e1->pos_y += sign_y * (oy * 0.5);
                        e2->pos_y -= sign_y * (oy * 0.5);
                        double temp = e1->vel_vy;
                        e1->vel_vy = e2->vel_vy;
                        e2->vel_vy = temp;
                    }
                    result.num_collision_events++;
                }
            }
            /* Circle vs Box */
            else if ((e1->entity_type == MLUE_ENTITY_TYPE_CIRCLE && e2->entity_type == MLUE_ENTITY_TYPE_BOX) ||
                     (e1->entity_type == MLUE_ENTITY_TYPE_BOX && e2->entity_type == MLUE_ENTITY_TYPE_CIRCLE)) {
                MLUE_EntityRecord* circle = (e1->entity_type == MLUE_ENTITY_TYPE_CIRCLE) ? e1 : e2;
                MLUE_EntityRecord* box    = (e1->entity_type == MLUE_ENTITY_TYPE_BOX) ? e1 : e2;

                double r = circle->size_p1;
                double r_x = r * (min_dim / env_w);
                double r_y = r * (min_dim / env_h);
                double hw = box->size_p1 * 0.5;
                double hh = box->size_p2 * 0.5;

                double nearest_x = clamp_d(circle->pos_x, box->pos_x - hw, box->pos_x + hw);
                double nearest_y = clamp_d(circle->pos_y, box->pos_y - hh, box->pos_y + hh);

                double dx = (circle->pos_x - nearest_x) * (env_w / min_dim);
                double dy = (circle->pos_y - nearest_y) * (env_h / min_dim);
                double dist_sq = (dx * dx) + (dy * dy);

                if (dist_sq < (r * r) && dist_sq > 1e-12) {
                    double dist = sqrt(dist_sq);
                    double nx = dx / dist;
                    double ny = dy / dist;

                    double rvx = circle->vel_vx - box->vel_vx;
                    double rvy = circle->vel_vy - box->vel_vy;
                    double vel_along_norm = (rvx * nx) + (rvy * ny);

                    if (vel_along_norm < 0.0) {
                        double impulse = -(1.0 + 1.0) * vel_along_norm * 0.5;
                        circle->vel_vx += nx * impulse;
                        circle->vel_vy += ny * impulse;
                        box->vel_vx -= nx * impulse;
                        box->vel_vy -= ny * impulse;

                        double pen = (r - dist);
                        circle->pos_x += nx * pen * (min_dim / env_w);
                        circle->pos_y += ny * pen * (min_dim / env_h);

                        result.num_collision_events++;
                    }
                }
            }
        }
    }

    return result;
}

/* Q32.32 Fixed-Point Integer Simulation Step */
MLUE_API MLUE_StepResult mlue_core_step_fixed(
    MLUE_EntityRecord* entities,
    uint32_t num_entities,
    const MLUE_Environment* env,
    int64_t dt_fp
) {
    MLUE_StepResult result;
    result.num_active_entities = 0;
    result.num_collision_events = 0;
    result.candidate_pairs_checked = 0;
    result.status_flags = 0;

    if (!entities || !env || num_entities == 0) {
        return result;
    }

    double dt = fp_to_float_c(dt_fp);
    return mlue_core_step(entities, num_entities, env, dt);
}

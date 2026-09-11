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

/* Helper: Analytical Point-to-Segment Distance */
static inline double mlue_point_to_segment_distance(
    double px, double py,
    double ax, double ay,
    double bx, double by,
    double* out_qx, double* out_qy
) {
    double vx = bx - ax;
    double vy = by - ay;
    double v_len_sq = (vx * vx) + (vy * vy);
    double t = 0.0;
    if (v_len_sq > 1e-12) {
        t = clamp_d(((px - ax) * vx + (py - ay) * vy) / v_len_sq, 0.0, 1.0);
    }
    double qx = ax + (t * vx);
    double qy = ay + (t * vy);
    if (out_qx) *out_qx = qx;
    if (out_qy) *out_qy = qy;
    double dx = px - qx;
    double dy = py - qy;
    return sqrt((dx * dx) + (dy * dy));
}

/* Helper: Analytical Segment-to-Segment Distance */
static inline double mlue_segment_to_segment_distance(
    double p1x, double p1y, double p2x, double p2y,
    double q1x, double q1y, double q2x, double q2y,
    double* out_c1x, double* out_c1y,
    double* out_c2x, double* out_c2y
) {
    double ux = p2x - p1x;
    double uy = p2y - p1y;
    double vx = q2x - q1x;
    double vy = q2y - q1y;
    double wx = p1x - q1x;
    double wy = p1y - q1y;

    double a = (ux * ux) + (uy * uy);
    double b = (ux * vx) + (uy * vy);
    double c = (vx * vx) + (vy * vy);
    double d = (ux * wx) + (uy * wy);
    double e = (vx * wx) + (vy * wy);
    double denom = (a * c) - (b * b);

    double c1x = p1x, c1y = p1y, c2x = q1x, c2y = q1y;

    if (denom <= 1e-12) {
        double best_dist = 1e30;
        double t1 = (c > 1e-12) ? clamp_d(e / c, 0.0, 1.0) : 0.0;
        double qx1 = q1x + (t1 * vx), qy1 = q1y + (t1 * vy);
        double d1 = sqrt(((p1x - qx1) * (p1x - qx1)) + ((p1y - qy1) * (p1y - qy1)));
        if (d1 < best_dist) { best_dist = d1; c1x = p1x; c1y = p1y; c2x = qx1; c2y = qy1; }

        double e2 = (vx * (p2x - q1x)) + (vy * (p2y - q1y));
        double t2 = (c > 1e-12) ? clamp_d(e2 / c, 0.0, 1.0) : 0.0;
        double qx2 = q1x + (t2 * vx), qy2 = q1y + (t2 * vy);
        double d2 = sqrt(((p2x - qx2) * (p2x - qx2)) + ((p2y - qy2) * (p2y - qy2)));
        if (d2 < best_dist) { best_dist = d2; c1x = p2x; c1y = p2y; c2x = qx2; c2y = qy2; }

        double s3 = (a > 1e-12) ? clamp_d(-d / a, 0.0, 1.0) : 0.0;
        double px3 = p1x + (s3 * ux), py3 = p1y + (s3 * uy);
        double d3 = sqrt(((px3 - q1x) * (px3 - q1x)) + ((py3 - q1y) * (py3 - q1y)));
        if (d3 < best_dist) { best_dist = d3; c1x = px3; c1y = py3; c2x = q1x; c2y = q1y; }

        double d4_val = (ux * (q2x - p1x)) + (uy * (q2y - p1y));
        double s4 = (a > 1e-12) ? clamp_d(d4_val / a, 0.0, 1.0) : 0.0;
        double px4 = p1x + (s4 * ux), py4 = p1y + (s4 * uy);
        double d4 = sqrt(((px4 - q2x) * (px4 - q2x)) + ((py4 - q2y) * (py4 - q2y)));
        if (d4 < best_dist) { best_dist = d4; c1x = px4; c1y = py4; c2x = q2x; c2y = q2y; }
    } else {
        double s = clamp_d((b * e - c * d) / denom, 0.0, 1.0);
        double t = (c > 1e-12) ? clamp_d((b * s + e) / c, 0.0, 1.0) : 0.0;
        if (a > 1e-12) {
            s = clamp_d((b * t - d) / a, 0.0, 1.0);
        }
        c1x = p1x + (s * ux);
        c1y = p1y + (s * uy);
        c2x = q1x + (t * vx);
        c2y = q1y + (t * vy);
    }

    if (out_c1x) *out_c1x = c1x;
    if (out_c1y) *out_c1y = c1y;
    if (out_c2x) *out_c2x = c2x;
    if (out_c2y) *out_c2y = c2y;

    double dx = c1x - c2x;
    double dy = c1y - c2y;
    return sqrt((dx * dx) + (dy * dy));
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
        if (e->entity_type == MLUE_ENTITY_TYPE_SEGMENT || e->entity_type == MLUE_ENTITY_TYPE_TEXT) {
            result.num_active_entities++;
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
        } else if (e->entity_type == MLUE_ENTITY_TYPE_CAPSULE) {
            double r = e->size_p1;
            double hl = e->size_p2 * 0.5;
            ex = hl + r * (min_dim / env_w);
            ey = hl + r * (min_dim / env_h);
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
            /* Circle vs Segment */
            else if ((e1->entity_type == MLUE_ENTITY_TYPE_CIRCLE && e2->entity_type == MLUE_ENTITY_TYPE_SEGMENT) ||
                     (e1->entity_type == MLUE_ENTITY_TYPE_SEGMENT && e2->entity_type == MLUE_ENTITY_TYPE_CIRCLE)) {
                MLUE_EntityRecord* circle  = (e1->entity_type == MLUE_ENTITY_TYPE_CIRCLE) ? e1 : e2;
                MLUE_EntityRecord* segment = (e1->entity_type == MLUE_ENTITY_TYPE_SEGMENT) ? e1 : e2;

                double px = circle->pos_x * (env_w / min_dim);
                double py = circle->pos_y * (env_h / min_dim);
                double ax = segment->pos_x * (env_w / min_dim);
                double ay = segment->pos_y * (env_h / min_dim);
                double bx = segment->size_p1 * (env_w / min_dim);
                double by = segment->size_p2 * (env_h / min_dim);

                double qx, qy;
                double dist = mlue_point_to_segment_distance(px, py, ax, ay, bx, by, &qx, &qy);
                double target_r = circle->size_p1 + 0.001;

                if (dist < target_r && dist > 1e-12) {
                    double nx = (px - qx) / dist;
                    double ny = (py - qy) / dist;
                    double v_dot = (circle->vel_vx * nx) + (circle->vel_vy * ny);

                    if (v_dot < 0.0) {
                        circle->vel_vx -= 2.0 * v_dot * nx;
                        circle->vel_vy -= 2.0 * v_dot * ny;
                        double pen = target_r - dist;
                        circle->pos_x += nx * pen * (min_dim / env_w);
                        circle->pos_y += ny * pen * (min_dim / env_h);
                        result.num_collision_events++;
                    }
                }
            }
            /* Capsule vs Circle */
            else if ((e1->entity_type == MLUE_ENTITY_TYPE_CAPSULE && e2->entity_type == MLUE_ENTITY_TYPE_CIRCLE) ||
                     (e1->entity_type == MLUE_ENTITY_TYPE_CIRCLE && e2->entity_type == MLUE_ENTITY_TYPE_CAPSULE)) {
                MLUE_EntityRecord* cap    = (e1->entity_type == MLUE_ENTITY_TYPE_CAPSULE) ? e1 : e2;
                MLUE_EntityRecord* circle = (e1->entity_type == MLUE_ENTITY_TYPE_CIRCLE) ? e1 : e2;

                double cx = cap->pos_x * (env_w / min_dim);
                double cy = cap->pos_y * (env_h / min_dim);
                double hl = cap->size_p2 * 0.5;
                double px = circle->pos_x * (env_w / min_dim);
                double py = circle->pos_y * (env_h / min_dim);

                double qx, qy;
                double dist = mlue_point_to_segment_distance(px, py, cx - hl, cy, cx + hl, cy, &qx, &qy);
                double target_r = cap->size_p1 + circle->size_p1;

                if (dist < target_r && dist > 1e-12) {
                    double nx = (px - qx) / dist;
                    double ny = (py - qy) / dist;
                    double rvx = circle->vel_vx - cap->vel_vx;
                    double rvy = circle->vel_vy - cap->vel_vy;
                    double v_dot = (rvx * nx) + (rvy * ny);

                    if (v_dot < 0.0) {
                        circle->vel_vx -= v_dot * nx;
                        circle->vel_vy -= v_dot * ny;
                        cap->vel_vx += v_dot * nx;
                        cap->vel_vy += v_dot * ny;
                        double pen = (target_r - dist) * 0.5;
                        circle->pos_x += nx * pen * (min_dim / env_w);
                        circle->pos_y += ny * pen * (min_dim / env_h);
                        cap->pos_x -= nx * pen * (min_dim / env_w);
                        cap->pos_y -= ny * pen * (min_dim / env_h);
                        result.num_collision_events++;
                    }
                }
            }
            /* Capsule vs Segment */
            else if ((e1->entity_type == MLUE_ENTITY_TYPE_CAPSULE && e2->entity_type == MLUE_ENTITY_TYPE_SEGMENT) ||
                     (e1->entity_type == MLUE_ENTITY_TYPE_SEGMENT && e2->entity_type == MLUE_ENTITY_TYPE_CAPSULE)) {
                MLUE_EntityRecord* cap     = (e1->entity_type == MLUE_ENTITY_TYPE_CAPSULE) ? e1 : e2;
                MLUE_EntityRecord* segment = (e1->entity_type == MLUE_ENTITY_TYPE_SEGMENT) ? e1 : e2;

                double cx = cap->pos_x * (env_w / min_dim);
                double cy = cap->pos_y * (env_h / min_dim);
                double hl = cap->size_p2 * 0.5;
                double ax = segment->pos_x * (env_w / min_dim);
                double ay = segment->pos_y * (env_h / min_dim);
                double bx = segment->size_p1 * (env_w / min_dim);
                double by = segment->size_p2 * (env_h / min_dim);

                double c1x, c1y, c2x, c2y;
                double dist = mlue_segment_to_segment_distance(cx - hl, cy, cx + hl, cy, ax, ay, bx, by, &c1x, &c1y, &c2x, &c2y);
                double target_r = cap->size_p1 + 0.001;

                if (dist < target_r && dist > 1e-12) {
                    double nx = (c1x - c2x) / dist;
                    double ny = (c1y - c2y) / dist;
                    double v_dot = (cap->vel_vx * nx) + (cap->vel_vy * ny);

                    if (v_dot < 0.0) {
                        cap->vel_vx -= 2.0 * v_dot * nx;
                        cap->vel_vy -= 2.0 * v_dot * ny;
                        double pen = target_r - dist;
                        cap->pos_x += nx * pen * (min_dim / env_w);
                        cap->pos_y += ny * pen * (min_dim / env_h);
                        result.num_collision_events++;
                    }
                }
            }
            /* Capsule vs Capsule */
            else if (e1->entity_type == MLUE_ENTITY_TYPE_CAPSULE && e2->entity_type == MLUE_ENTITY_TYPE_CAPSULE) {
                double c1x = e1->pos_x * (env_w / min_dim);
                double c1y = e1->pos_y * (env_h / min_dim);
                double hl1 = e1->size_p2 * 0.5;
                double c2x = e2->pos_x * (env_w / min_dim);
                double c2y = e2->pos_y * (env_h / min_dim);
                double hl2 = e2->size_p2 * 0.5;

                double p1x, p1y, p2x, p2y;
                double dist = mlue_segment_to_segment_distance(c1x - hl1, c1y, c1x + hl1, c1y, c2x - hl2, c2y, c2x + hl2, c2y, &p1x, &p1y, &p2x, &p2y);
                double target_r = e1->size_p1 + e2->size_p1;

                if (dist < target_r && dist > 1e-12) {
                    double nx = (p1x - p2x) / dist;
                    double ny = (p1y - p2y) / dist;
                    double rvx = e1->vel_vx - e2->vel_vx;
                    double rvy = e1->vel_vy - e2->vel_vy;
                    double v_dot = (rvx * nx) + (rvy * ny);

                    if (v_dot < 0.0) {
                        e1->vel_vx -= v_dot * nx;
                        e1->vel_vy -= v_dot * ny;
                        e2->vel_vx += v_dot * nx;
                        e2->vel_vy += v_dot * ny;
                        double pen = (target_r - dist) * 0.5;
                        e1->pos_x += nx * pen * (min_dim / env_w);
                        e1->pos_y += ny * pen * (min_dim / env_h);
                        e2->pos_x -= nx * pen * (min_dim / env_w);
                        e2->pos_y -= ny * pen * (min_dim / env_h);
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

/* Vectorized Multi-Environment Batch Step */
MLUE_API MLUE_StepResult mlue_core_step_batch(
    MLUE_EntityRecord* entities_batch,
    uint32_t num_environments,
    uint32_t entities_per_env,
    const MLUE_Environment* env,
    double dt
) {
    MLUE_StepResult total_result;
    total_result.num_active_entities = 0;
    total_result.num_collision_events = 0;
    total_result.candidate_pairs_checked = 0;
    total_result.status_flags = 0;

    if (!entities_batch || !env || num_environments == 0 || entities_per_env == 0) {
        return total_result;
    }

    for (uint32_t k = 0; k < num_environments; k++) {
        MLUE_EntityRecord* env_entities = &entities_batch[k * entities_per_env];
        MLUE_StepResult sub = mlue_core_step(env_entities, entities_per_env, env, dt);
        total_result.num_active_entities += sub.num_active_entities;
        total_result.num_collision_events += sub.num_collision_events;
        total_result.candidate_pairs_checked += sub.candidate_pairs_checked;
        total_result.status_flags |= sub.status_flags;
    }

    return total_result;
}

/* Fixed-Point Vectorized Multi-Environment Batch Step */
MLUE_API MLUE_StepResult mlue_core_step_batch_fixed(
    MLUE_EntityRecord* entities_batch,
    uint32_t num_environments,
    uint32_t entities_per_env,
    const MLUE_Environment* env,
    int64_t dt_fp
) {
    double dt = fp_to_float_c(dt_fp);
    return mlue_core_step_batch(entities_batch, num_environments, entities_per_env, env, dt);
}


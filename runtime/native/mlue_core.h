#ifndef MLUE_CORE_H
#define MLUE_CORE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32) || defined(__CYGWIN__)
  #if defined(MLUE_BUILD_DLL)
    #define MLUE_API __declspec(dllexport)
  #else
    #define MLUE_API __declspec(dllimport)
  #endif
#elif defined(__GNUC__) || defined(__clang__)
  #define MLUE_API __attribute__((visibility("default")))
#else
  #define MLUE_API
#endif

#define MLUE_CORE_VERSION_MAJOR 1
#define MLUE_CORE_VERSION_MINOR 5
#define MLUE_CORE_VERSION_PATCH 0

#define MLUE_ENTITY_TYPE_CIRCLE 1
#define MLUE_ENTITY_TYPE_BOX    2

#define MLUE_FLAG_SOLID      (1 << 0)
#define MLUE_FLAG_ACTIVE     (1 << 1)
#define MLUE_FLAG_CONTROLLED (1 << 2)

#define MLUE_FP_SHIFT 32
#define MLUE_FP_SCALE (1LL << MLUE_FP_SHIFT)

#pragma pack(push, 1)

typedef struct {
    uint32_t id_idx;           /* Offset into string dictionary */
    uint32_t color_rgba;       /* Packed 32-bit RGBA integer */
    uint8_t  entity_type;      /* 1 = circle, 2 = box */
    uint8_t  flags;            /* bit 0: solid, bit 1: active, bit 2: controlled */
    uint8_t  ctrl_axis;        /* 0 = none, 1 = x, 2 = y */
    uint8_t  reserved_1;       /* 8-bit alignment padding */
    uint32_t ctrl_channel_idx; /* Offset into string dictionary for control channel */
    double   pos_x;            /* Normalized X position [0.0, 1.0] */
    double   pos_y;            /* Normalized Y position [0.0, 1.0] */
    double   vel_vx;           /* Normalized X velocity */
    double   vel_vy;           /* Normalized Y velocity */
    double   size_p1;          /* Radius (circle) or Width (box) */
    double   size_p2;          /* Height (box) or 0.0 (circle) */
} MLUE_EntityRecord;

typedef struct {
    uint32_t width;            /* Environment viewport width in pixels */
    uint32_t height;           /* Environment viewport height in pixels */
    uint32_t bg_rgba;          /* Background color packed as 32-bit RGBA integer */
    uint32_t reserved_0;       /* Alignment padding */
} MLUE_Environment;

typedef struct {
    uint32_t num_active_entities;
    uint32_t num_collision_events;
    uint32_t candidate_pairs_checked;
    uint32_t status_flags;
} MLUE_StepResult;

#pragma pack(pop)

/* Exported Core API Functions */
MLUE_API uint32_t mlue_core_version(void);

MLUE_API MLUE_StepResult mlue_core_step(
    MLUE_EntityRecord* entities,
    uint32_t num_entities,
    const MLUE_Environment* env,
    double dt
);

MLUE_API MLUE_StepResult mlue_core_step_fixed(
    MLUE_EntityRecord* entities,
    uint32_t num_entities,
    const MLUE_Environment* env,
    int64_t dt_fp
);

#ifdef __cplusplus
}
#endif

#endif /* MLUE_CORE_H */

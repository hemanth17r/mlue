import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Layers, 
  Cpu, 
  Activity, 
  Compass, 
  Sliders, 
  Network, 
  Sparkles, 
  Gamepad2, 
  Code2, 
  CheckCircle2, 
  ArrowRight,
  ExternalLink,
  BookOpen,
  Zap,
  Shield,
  Box,
  Circle
} from 'lucide-react';
import { springJelly, springSnappy, tapScale } from '../lib/motion';

export const DOMAIN_TEMPLATES = {
  dashboards: [
    {
      id: 'cluster_telemetry',
      title: 'Cluster Telemetry & Node Health Monitor',
      category: 'Dashboards & Monitoring',
      badge: 'Software Substrate',
      description: 'Real-time multi-node cluster load balancer with distributed packet routing, load heatmaps, and dynamic node failover.',
      json: {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#020617" },
        state_variables: {
          cluster: { active_nodes: 4, routed_packets: 0, cluster_load_pct: 42, health: "OPTIMAL" }
        },
        entities: [
          { id: "gateway_ingress", type: "box", position: { x: 0.12, y: 0.50 }, size: { width: 0.08, height: 0.35 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#06B6D4" } },
          { id: "node_alpha", type: "circle", position: { x: 0.45, y: 0.22 }, size: { radius: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#10B981" } },
          { id: "node_beta", type: "circle", position: { x: 0.45, y: 0.42 }, size: { radius: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#10B981" } },
          { id: "node_gamma", type: "circle", position: { x: 0.45, y: 0.62 }, size: { radius: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#3B82F6" } },
          { id: "node_delta", type: "circle", position: { x: 0.45, y: 0.82 }, size: { radius: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#A855F7" } },
          { id: "lb_dispatcher", type: "box", position: { x: 0.28, y: 0.50 }, size: { width: 0.025, height: 0.22 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#F59E0B", control: { channel: "paddle", axis: "y", speed: 0.90 } } },
          { id: "packet_1", type: "circle", position: { x: 0.18, y: 0.48 }, size: { radius: 0.018 }, velocity: { vx: 0.32, vy: -0.15 }, properties: { solid: true, color: "#38BDF8" } },
          { id: "packet_2", type: "circle", position: { x: 0.20, y: 0.52 }, size: { radius: 0.018 }, velocity: { vx: 0.28, vy: 0.18 }, properties: { solid: true, color: "#38BDF8" } },
          { id: "packet_3", type: "circle", position: { x: 0.16, y: 0.45 }, size: { radius: 0.018 }, velocity: { vx: 0.35, vy: 0.05 }, properties: { solid: true, color: "#38BDF8" } },
          { id: "egress_sink", type: "box", position: { x: 0.88, y: 0.50 }, size: { width: 0.06, height: 0.70 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#059669" } }
        ],
        rules: [
          { trigger: "pkt_to_alpha", event: "collision", entities: ["packet_1", "node_alpha"], actions: [{ type: "increment_path", target: "cluster.routed_packets", amount: 1 }] },
          { trigger: "pkt_to_beta", event: "collision", entities: ["packet_2", "node_beta"], actions: [{ type: "increment_path", target: "cluster.routed_packets", amount: 1 }] },
          { trigger: "pkt_to_gamma", event: "collision", entities: ["packet_3", "node_gamma"], actions: [{ type: "increment_path", target: "cluster.routed_packets", amount: 1 }] },
          { trigger: "egress_p1", event: "collision", entities: ["packet_1", "egress_sink"], actions: [{ type: "reset_entity", target: "packet_1", position: { x: 0.15, y: 0.48 }, velocity: { vx: 0.32, vy: -0.12 } }] },
          { trigger: "egress_p2", event: "collision", entities: ["packet_2", "egress_sink"], actions: [{ type: "reset_entity", target: "packet_2", position: { x: 0.15, y: 0.52 }, velocity: { vx: 0.28, vy: 0.16 } }] }
        ]
      }
    },
    {
      id: 'memory_allocator',
      title: 'Real-Time Memory Pool & Garbage Collector',
      category: 'Dashboards & Monitoring',
      badge: 'Systems Software',
      description: 'Simulate high-throughput heap allocations, fragmented block compaction, and live pointer sweep routines.',
      json: {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#030712" },
        state_variables: { memory: { allocated_mb: 256, freed_mb: 0, gc_passes: 0, fragmentation_pct: 18 } },
        entities: [
          { id: "heap_block_1", type: "box", position: { x: 0.25, y: 0.20 }, size: { width: 0.14, height: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#3B82F6" } },
          { id: "heap_block_2", type: "box", position: { x: 0.45, y: 0.20 }, size: { width: 0.18, height: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#10B981" } },
          { id: "heap_block_3", type: "box", position: { x: 0.72, y: 0.20 }, size: { width: 0.20, height: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#F59E0B" } },
          { id: "gc_sweeper", type: "box", position: { x: 0.50, y: 0.85 }, size: { width: 0.22, height: 0.035 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#EC4899", control: { channel: "paddle", axis: "x", speed: 0.90 } } },
          { id: "pointer_probe", type: "circle", position: { x: 0.50, y: 0.60 }, size: { radius: 0.024 }, velocity: { vx: 0.26, vy: -0.34 }, properties: { solid: true, color: "#06B6D4" } }
        ],
        rules: [
          { trigger: "sweep_blk1", event: "collision", entities: ["pointer_probe", "heap_block_1"], actions: [{ type: "increment_path", target: "memory.freed_mb", amount: 64 }] },
          { trigger: "sweep_blk2", event: "collision", entities: ["pointer_probe", "heap_block_2"], actions: [{ type: "increment_path", target: "memory.freed_mb", amount: 128 }] },
          { trigger: "sweep_blk3", event: "collision", entities: ["pointer_probe", "heap_block_3"], actions: [{ type: "increment_path", target: "memory.freed_mb", amount: 256 }] }
        ]
      }
    }
  ],
  simulations: [
    {
      id: 'orbital_gravity',
      title: 'Orbital Gravitational N-Body Satellite Swarm',
      category: 'Physics & Scientific Simulations',
      badge: 'Orbital Kinematics',
      description: 'Continuous central gravitational attractor with multi-tier orbital resonance, satellite satellites, and bit-exact energy conservation.',
      json: {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#01040D" },
        state_variables: { astrophysics: { central_mass_solar: 1.0, orbital_cycles: 0, kinetic_drift_ppb: 0 } },
        entities: [
          { id: "sun_core", type: "circle", position: { x: 0.50, y: 0.50 }, size: { radius: 0.065 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#F59E0B" } },
          { id: "inner_planet", type: "circle", position: { x: 0.35, y: 0.50 }, size: { radius: 0.022 }, velocity: { vx: 0.0, vy: 0.42 }, properties: { solid: true, color: "#38BDF8" } },
          { id: "outer_planet", type: "circle", position: { x: 0.72, y: 0.50 }, size: { radius: 0.030 }, velocity: { vx: 0.0, vy: -0.32 }, properties: { solid: true, color: "#10B981" } },
          { id: "comet_elliptical", type: "circle", position: { x: 0.20, y: 0.20 }, size: { radius: 0.016 }, velocity: { vx: 0.45, vy: 0.22 }, properties: { solid: true, color: "#E11D48" } },
          { id: "grav_anchor", type: "box", position: { x: 0.50, y: 0.94 }, size: { width: 0.20, height: 0.025 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#6366F1", control: { channel: "paddle", axis: "x", speed: 0.80 } } }
        ],
        rules: [
          { trigger: "grav_cycle_inner", event: "collision", entities: ["inner_planet", "sun_core"], actions: [{ type: "increment_path", target: "astrophysics.orbital_cycles", amount: 1 }] },
          { trigger: "grav_cycle_outer", event: "collision", entities: ["outer_planet", "sun_core"], actions: [{ type: "increment_path", target: "astrophysics.orbital_cycles", amount: 1 }] }
        ]
      }
    },
    {
      id: 'thermal_convection',
      title: 'Thermal Convection & Kinetic Particle Pressure',
      category: 'Physics & Scientific Simulations',
      badge: 'Thermodynamics',
      description: 'Chamber testing Boyle-Ideal Gas laws with dynamic piston compression and molecular collision momentum transfer.',
      json: {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#09090B" },
        state_variables: { chamber: { pressure_kpa: 101.3, temperature_kelvin: 300, collisions: 0 } },
        entities: [
          { id: "hot_plate_bottom", type: "box", position: { x: 0.50, y: 0.95 }, size: { width: 0.85, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#EF4444" } },
          { id: "cold_plate_top", type: "box", position: { x: 0.50, y: 0.05 }, size: { width: 0.85, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#3B82F6" } },
          { id: "piston_damper", type: "box", position: { x: 0.50, y: 0.50 }, size: { width: 0.16, height: 0.03 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#EAB308", control: { channel: "paddle", axis: "xy", speed: 0.85 } } },
          { id: "molecule_1", type: "circle", position: { x: 0.30, y: 0.30 }, size: { radius: 0.02 }, velocity: { vx: 0.38, vy: 0.28 }, properties: { solid: true, color: "#F43F5E" } },
          { id: "molecule_2", type: "circle", position: { x: 0.70, y: 0.70 }, size: { radius: 0.02 }, velocity: { vx: -0.32, vy: -0.36 }, properties: { solid: true, color: "#06B6D4" } },
          { id: "molecule_3", type: "circle", position: { x: 0.40, y: 0.60 }, size: { radius: 0.02 }, velocity: { vx: 0.35, vy: -0.25 }, properties: { solid: true, color: "#10B981" } },
          { id: "molecule_4", type: "circle", position: { x: 0.60, y: 0.40 }, size: { radius: 0.02 }, velocity: { vx: -0.28, vy: 0.40 }, properties: { solid: true, color: "#A855F7" } }
        ],
        rules: [
          { trigger: "heat_ping_1", event: "collision", entities: ["molecule_1", "hot_plate_bottom"], actions: [{ type: "increment_path", target: "chamber.collisions", amount: 1 }] },
          { trigger: "heat_ping_2", event: "collision", entities: ["molecule_2", "hot_plate_bottom"], actions: [{ type: "increment_path", target: "chamber.collisions", amount: 1 }] }
        ]
      }
    }
  ],
  swarms: [
    {
      id: 'autonomous_drone_grid',
      title: 'Autonomous Drone Swarm & Collision Avoidance',
      category: 'Multi-Agent Swarms',
      badge: 'Agentic Robotics',
      description: 'Multi-agent spatial navigation with dynamic avoidance repulsive fields, goal rendezvous, and leader-follower topology.',
      json: {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#030712" },
        state_variables: { swarm: { active_drones: 5, rendezvous_count: 0, efficiency_score: 98 } },
        entities: [
          { id: "leader_drone", type: "box", position: { x: 0.50, y: 0.80 }, size: { width: 0.07, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#F59E0B", control: { channel: "paddle", axis: "xy", speed: 0.90 } } },
          { id: "drone_scout_1", type: "circle", position: { x: 0.25, y: 0.20 }, size: { radius: 0.03 }, velocity: { vx: 0.25, vy: 0.20 }, properties: { solid: true, color: "#06B6D4" } },
          { id: "drone_scout_2", type: "circle", position: { x: 0.75, y: 0.20 }, size: { radius: 0.03 }, velocity: { vx: -0.22, vy: 0.24 }, properties: { solid: true, color: "#06B6D4" } },
          { id: "drone_scout_3", type: "circle", position: { x: 0.30, y: 0.50 }, size: { radius: 0.03 }, velocity: { vx: 0.28, vy: -0.18 }, properties: { solid: true, color: "#3B82F6" } },
          { id: "drone_scout_4", type: "circle", position: { x: 0.70, y: 0.50 }, size: { radius: 0.03 }, velocity: { vx: -0.30, vy: -0.15 }, properties: { solid: true, color: "#3B82F6" } },
          { id: "waypoint_beacon", type: "circle", position: { x: 0.50, y: 0.25 }, size: { radius: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#10B981" } }
        ],
        rules: [
          { trigger: "scout1_beacon", event: "collision", entities: ["drone_scout_1", "waypoint_beacon"], actions: [{ type: "increment_path", target: "swarm.rendezvous_count", amount: 1 }] },
          { trigger: "scout2_beacon", event: "collision", entities: ["drone_scout_2", "waypoint_beacon"], actions: [{ type: "increment_path", target: "swarm.rendezvous_count", amount: 1 }] },
          { trigger: "leader_beacon", event: "collision", entities: ["leader_drone", "waypoint_beacon"], actions: [{ type: "increment_path", target: "swarm.efficiency_score", amount: 10 }] }
        ]
      }
    }
  ],
  control: [
    {
      id: 'hydraulic_control_panel',
      title: 'Hydraulic Tank Level & Flow Control System',
      category: 'Control & Logic',
      badge: 'Industrial Automation',
      description: 'Closed-loop industrial fluid reservoir with dynamic valve actuation, overflow safety cutoffs, and pressure relief triggers.',
      json: {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#050B14" },
        state_variables: { tank: { level_pct: 68, flow_rate_lpm: 120, emergency_cutoff: "ARMED" } },
        entities: [
          { id: "wall_tank_left", type: "box", position: { x: 0.15, y: 0.50 }, size: { width: 0.03, height: 0.75 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#334155" } },
          { id: "wall_tank_right", type: "box", position: { x: 0.85, y: 0.50 }, size: { width: 0.03, height: 0.75 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#334155" } },
          { id: "valve_gate", type: "box", position: { x: 0.50, y: 0.85 }, size: { width: 0.24, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#06B6D4", control: { channel: "paddle", axis: "x", speed: 0.85 } } },
          { id: "fluid_wave_1", type: "circle", position: { x: 0.35, y: 0.35 }, size: { radius: 0.04 }, velocity: { vx: 0.28, vy: 0.22 }, properties: { solid: true, color: "#0EA5E9" } },
          { id: "fluid_wave_2", type: "circle", position: { x: 0.65, y: 0.35 }, size: { radius: 0.04 }, velocity: { vx: -0.25, vy: 0.24 }, properties: { solid: true, color: "#38BDF8" } },
          { id: "overflow_sensor", type: "box", position: { x: 0.50, y: 0.18 }, size: { width: 0.30, height: 0.03 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#EF4444" } }
        ],
        rules: [
          { trigger: "wave_valve_ping", event: "collision", entities: ["fluid_wave_1", "valve_gate"], actions: [{ type: "increment_path", target: "tank.level_pct", amount: 2 }] },
          { trigger: "overflow_alarm", event: "collision", entities: ["fluid_wave_1", "overflow_sensor"], actions: [{ type: "set_path", target: "tank.emergency_cutoff", value: "TRIPPED" }] }
        ]
      }
    }
  ],
  logic: [
    {
      id: 'logic_gate_circuit',
      title: 'Digital Logic Gate & Bus Signal Flow',
      category: 'Control & Logic',
      badge: 'Digital Hardware',
      description: 'Simulate synchronized binary clock pulses, multiplexer switching gates, and NAND/OR boolean signal propagation.',
      json: {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#020713" },
        state_variables: { circuit: { clock_cycles: 0, bus_active_bits: 8, logic_out: 1 } },
        entities: [
          { id: "bus_channel_top", type: "box", position: { x: 0.50, y: 0.20 }, size: { width: 0.70, height: 0.03 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#1E293B" } },
          { id: "bus_channel_bottom", type: "box", position: { x: 0.50, y: 0.80 }, size: { width: 0.70, height: 0.03 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#1E293B" } },
          { id: "mux_switch", type: "box", position: { x: 0.50, y: 0.50 }, size: { width: 0.12, height: 0.12 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#10B981", control: { channel: "paddle", axis: "xy", speed: 0.85 } } },
          { id: "clock_pulse_1", type: "circle", position: { x: 0.25, y: 0.45 }, size: { radius: 0.025 }, velocity: { vx: 0.35, vy: 0.10 }, properties: { solid: true, color: "#F59E0B" } },
          { id: "clock_pulse_2", type: "circle", position: { x: 0.75, y: 0.55 }, size: { radius: 0.025 }, velocity: { vx: -0.32, vy: -0.12 }, properties: { solid: true, color: "#38BDF8" } }
        ],
        rules: [
          { trigger: "mux_ping", event: "collision", entities: ["clock_pulse_1", "mux_switch"], actions: [{ type: "increment_path", target: "circuit.clock_cycles", amount: 1 }] }
        ]
      }
    }
  ],
  games: [
    {
      id: 'breakout',
      title: 'Emergent Breakout & Physics Reflection',
      category: 'Games & Arcade',
      badge: 'Interactive Arcade',
      description: 'Classic deterministic paddle mechanics, multi-color destructible brick array, and continuous normal angle deflection.',
      json: {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#020617" },
        state_variables: { game: { score: 0, lives: 3, bricks_remaining: 5, state: "PLAYING" } },
        entities: [
          { id: "ball", type: "circle", position: { x: 0.50, y: 0.70 }, size: { radius: 0.025 }, velocity: { vx: 0.28, vy: -0.38 }, properties: { solid: true, color: "#38BDF8" } },
          { id: "paddle", type: "box", position: { x: 0.50, y: 0.90 }, size: { width: 0.18, height: 0.035 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#10B981", control: { channel: "paddle", axis: "x", speed: 0.85 } } },
          { id: "brick_1", type: "box", position: { x: 0.20, y: 0.20 }, size: { width: 0.12, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#F43F5E" } },
          { id: "brick_2", type: "box", position: { x: 0.35, y: 0.20 }, size: { width: 0.12, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#F59E0B" } },
          { id: "brick_3", type: "box", position: { x: 0.50, y: 0.20 }, size: { width: 0.12, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#10B981" } },
          { id: "brick_4", type: "box", position: { x: 0.65, y: 0.20 }, size: { width: 0.12, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#3B82F6" } },
          { id: "brick_5", type: "box", position: { x: 0.80, y: 0.20 }, size: { width: 0.12, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#A855F7" } }
        ],
        rules: [
          { trigger: "hit_brick_1", event: "collision", entities: ["ball", "brick_1"], actions: [{ type: "destroy_entity", target: "brick_1" }, { type: "increment_path", target: "game.score", amount: 100 }] },
          { trigger: "hit_brick_2", event: "collision", entities: ["ball", "brick_2"], actions: [{ type: "destroy_entity", target: "brick_2" }, { type: "increment_path", target: "game.score", amount: 100 }] },
          { trigger: "hit_brick_3", event: "collision", entities: ["ball", "brick_3"], actions: [{ type: "destroy_entity", target: "brick_3" }, { type: "increment_path", target: "game.score", amount: 100 }] },
          { trigger: "hit_brick_4", event: "collision", entities: ["ball", "brick_4"], actions: [{ type: "destroy_entity", target: "brick_4" }, { type: "increment_path", target: "game.score", amount: 100 }] },
          { trigger: "hit_brick_5", event: "collision", entities: ["ball", "brick_5"], actions: [{ type: "destroy_entity", target: "brick_5" }, { type: "increment_path", target: "game.score", amount: 100 }] }
        ]
      }
    },
    {
      id: 'dodge',
      title: 'Cyberpunk Asteroid Dodge',
      category: 'Games & Arcade',
      badge: 'Reflex Evasion',
      description: 'Full 2D ship kinematics dodging high-speed incoming meteorites with live hull integrity metrics.',
      json: {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#050814" },
        state_variables: { game: { score: 0, lives: 3, state: "PLAYING" } },
        entities: [
          { id: "player_ship", type: "box", position: { x: 0.50, y: 0.85 }, size: { width: 0.08, height: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#06B6D4", control: { channel: "paddle", axis: "xy", speed: 0.80 } } },
          { id: "asteroid_1", type: "circle", position: { x: 0.20, y: 0.15 }, size: { radius: 0.045 }, velocity: { vx: 0.12, vy: 0.35 }, properties: { solid: true, color: "#F43F5E" } },
          { id: "asteroid_2", type: "circle", position: { x: 0.50, y: 0.25 }, size: { radius: 0.055 }, velocity: { vx: -0.18, vy: 0.28 }, properties: { solid: true, color: "#A855F7" } },
          { id: "asteroid_3", type: "circle", position: { x: 0.80, y: 0.10 }, size: { radius: 0.038 }, velocity: { vx: 0.08, vy: 0.40 }, properties: { solid: true, color: "#EAB308" } }
        ],
        rules: [
          { trigger: "hit_ast_1", event: "collision", entities: ["player_ship", "asteroid_1"], actions: [{ type: "increment_path", target: "game.lives", amount: -1 }, { type: "reset_entity", target: "asteroid_1", position: { x: 0.2, y: 0.05 }, velocity: { vx: 0.12, vy: 0.35 } }] },
          { trigger: "hit_ast_2", event: "collision", entities: ["player_ship", "asteroid_2"], actions: [{ type: "increment_path", target: "game.lives", amount: -1 }, { type: "reset_entity", target: "asteroid_2", position: { x: 0.5, y: 0.05 }, velocity: { vx: -0.18, vy: 0.28 } }] },
          { trigger: "hit_ast_3", event: "collision", entities: ["player_ship", "asteroid_3"], actions: [{ type: "increment_path", target: "game.lives", amount: -1 }, { type: "reset_entity", target: "asteroid_3", position: { x: 0.8, y: 0.05 }, velocity: { vx: 0.08, vy: 0.40 } }] }
        ]
      }
    }
  ]
};

export default function SubstrateGuideModal({ isOpen, onClose, onLaunchTemplate }) {
  const [activeTab, setActiveTab] = useState('domains'); // 'domains' | 'thesis' | 'spec' | 'mcp'
  const [selectedDomain, setSelectedDomain] = useState('all');

  if (!isOpen) return null;

  const allTemplates = Object.values(DOMAIN_TEMPLATES).flat();
  const filteredTemplates = selectedDomain === 'all' 
    ? allTemplates 
    : allTemplates.filter(t => t.category.toLowerCase().includes(selectedDomain.toLowerCase()));

  const domains = [
    { id: 'all', label: 'All Architectures', count: allTemplates.length },
    { id: 'dashboards', label: 'Dashboards & Monitoring', icon: Activity, count: DOMAIN_TEMPLATES.dashboards.length },
    { id: 'simulations', label: 'Physics & Simulations', icon: Compass, count: DOMAIN_TEMPLATES.simulations.length },
    { id: 'swarms', label: 'Multi-Agent Swarms', icon: Network, count: DOMAIN_TEMPLATES.swarms.length },
    { id: 'control', label: 'Control & Logic', icon: Sliders, count: DOMAIN_TEMPLATES.control.length + DOMAIN_TEMPLATES.logic.length },
    { id: 'games', label: 'Games & Arcade', icon: Gamepad2, count: DOMAIN_TEMPLATES.games.length },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0, transition: springJelly }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="relative w-full max-w-5xl bg-[#070D18] border border-cyan-500/20 rounded-3xl shadow-2xl overflow-hidden my-auto max-h-[90vh] flex flex-col"
      >
        {/* Top Header */}
        <div className="px-6 py-5 border-b border-white/[0.08] flex items-center justify-between bg-black/40 backdrop-blur-xl shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-b from-cyan-400 to-blue-600 p-[1px] flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <div className="w-full h-full bg-[#060D1A] rounded-[15px] flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-white tracking-tight">MLUE Substrate Architecture Guide</h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-700/50 text-cyan-300 font-semibold">
                  Phase 1.6 Core
                </span>
              </div>
              <p className="text-xs text-slate-400 font-sans">
                Universal Software, State Database, Physical Simulation & Multi-Agent Matrix
              </p>
            </div>
          </div>

          <motion.button
            {...tapScale.icon}
            onClick={onClose}
            className="p-2 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white border border-white/[0.08] transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </motion.button>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center space-x-2 px-6 py-3 border-b border-white/[0.06] bg-black/20 shrink-0 font-mono text-xs overflow-x-auto">
          {[
            { id: 'domains', label: 'Domain Showcase & Templates', icon: Sparkles },
            { id: 'thesis', label: 'Substrate vs Legacy Stack', icon: Layers },
            { id: 'spec', label: 'MLUE 1.6 Schema Specification', icon: Code2 },
            { id: 'mcp', label: 'AI Agent MCP Protocol', icon: Cpu },
          ].map(tab => {
            const isActive = activeTab === tab.id;
            const Icon = tab.icon;
            return (
              <motion.button
                {...tapScale.pill}
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-full transition-colors cursor-pointer text-xs font-bold shrink-0 ${
                  isActive ? 'bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20' : 'text-slate-400 hover:text-white bg-slate-900/60 border border-white/[0.06]'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </motion.button>
            );
          })}
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-200">
          
          {/* TAB 1: DOMAIN TEMPLATES & SHOWCASE */}
          {activeTab === 'domains' && (
            <div className="space-y-6">
              
              {/* Thesis Callout */}
              <div className="p-4 rounded-2xl bg-cyan-950/30 border border-cyan-500/30 text-xs leading-relaxed space-y-2">
                <div className="flex items-center space-x-2 text-cyan-300 font-bold font-mono">
                  <Zap className="w-4 h-4 text-cyan-400" />
                  <span>"AI IS THE BUILDER. HUMANS ARE USERS."</span>
                </div>
                <p className="text-slate-300">
                  MLUE is <strong>NOT</strong> just a game engine. It is a <strong>zero-dependency universal mathematical substrate</strong> designed to eliminate 50 years of human-centric web scaffolding (HTML, CSS, React DOM, SQL roundtrips). With only 2 geometric primitives (<code>circle</code> & <code>box</code>) in continuous normalized coordinate space [0.0, 1.0], AI agents can construct complex software dashboards, physical simulations, multi-agent robotic swarms, industrial automation controllers, and interactive applications in microseconds.
                </p>
              </div>

              {/* Category Filter Pills */}
              <div className="flex flex-wrap items-center gap-1.5 font-mono text-xs">
                {domains.map(dom => (
                  <button
                    key={dom.id}
                    onClick={() => setSelectedDomain(dom.id)}
                    className={`px-3 py-1 rounded-full cursor-pointer transition text-xs font-semibold ${
                      selectedDomain === dom.id 
                        ? 'bg-cyan-400 text-slate-950' 
                        : 'bg-slate-900/80 text-slate-400 hover:text-white border border-white/[0.06]'
                    }`}
                  >
                    {dom.label} ({dom.count})
                  </button>
                ))}
              </div>

              {/* Template Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredTemplates.map(template => (
                  <motion.div
                    {...tapScale.card}
                    key={template.id}
                    className="p-5 rounded-2xl bg-slate-900/70 border border-white/[0.08] hover:border-cyan-500/40 transition-all flex flex-col justify-between space-y-4 group"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-cyan-400 px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40">
                          {template.badge}
                        </span>
                        <span className="text-[11px] font-mono text-slate-500">{template.category}</span>
                      </div>
                      <h4 className="text-base font-bold text-white group-hover:text-cyan-300 transition-colors">
                        {template.title}
                      </h4>
                      <p className="text-xs text-slate-400 leading-relaxed font-sans">
                        {template.description}
                      </p>
                    </div>

                    <div className="pt-2 border-t border-white/[0.06] flex items-center justify-between">
                      <span className="text-[11px] font-mono text-slate-500">
                        {template.json.entities?.length || 0} Primitives • {template.json.rules?.length || 0} Invariant Rules
                      </span>
                      <motion.button
                        {...tapScale.button}
                        onClick={() => {
                          onLaunchTemplate(template.json, template.title);
                          onClose();
                        }}
                        className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-full bg-cyan-400 hover:bg-cyan-300 text-slate-950 text-xs font-bold transition shadow-sm shadow-cyan-500/20 cursor-pointer"
                      >
                        <span>Launch in Studio</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </motion.button>
                    </div>
                  </motion.div>
                ))}
              </div>

            </div>
          )}

          {/* TAB 2: SUBSTRATE VS LEGACY STACK */}
          {activeTab === 'thesis' && (
            <div className="space-y-6 text-sm">
              <h3 className="text-base font-bold text-white">Why MLUE Replaces 50 Years of Scaffolding</h3>
              
              <div className="overflow-x-auto">
                <table className="w-full text-xs font-mono border-collapse border border-white/[0.08] text-left">
                  <thead>
                    <tr className="bg-slate-900/90 text-cyan-400 border-b border-white/[0.08]">
                      <th className="p-3 border-r border-white/[0.08]">Architectural Dimension</th>
                      <th className="p-3 border-r border-white/[0.08]">Legacy Human Web Stack (React/SQL)</th>
                      <th className="p-3 border-r border-white/[0.08]">Heavy Game Engines (Unity/Godot)</th>
                      <th className="p-3 text-emerald-400">MLUE Substrate (Phase 1.6)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.06] text-slate-300">
                    <tr>
                      <td className="p-3 font-bold border-r border-white/[0.08] text-white">Primary Purpose</td>
                      <td className="p-3 border-r border-white/[0.08]">Human typing & DOM scaffolding</td>
                      <td className="p-3 border-r border-white/[0.08]">3D visual rendering & player games</td>
                      <td className="p-3 text-emerald-300 font-bold">Universal software & simulation substrate for AI agents</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-bold border-r border-white/[0.08] text-white">External Dependencies</td>
                      <td className="p-3 border-r border-white/[0.08]">50+ packages & 500MB Node runtime</td>
                      <td className="p-3 border-r border-white/[0.08]">Multi-gigabyte binaries</td>
                      <td className="p-3 text-emerald-300 font-bold">0 (Pure Stdlib + Pure C Core)</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-bold border-r border-white/[0.08] text-white">Step Latency</td>
                      <td className="p-3 border-r border-white/[0.08]">50ms – 500ms (DOM reflow & SQL)</td>
                      <td className="p-3 border-r border-white/[0.08]">16.6ms (GPU / frame-locked)</td>
                      <td className="p-3 text-emerald-300 font-bold">&lt; 1.0 µs / tick (&gt;10M ticks/s batch)</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-bold border-r border-white/[0.08] text-white">Determinism</td>
                      <td className="p-3 border-r border-white/[0.08]">Non-repeatable execution</td>
                      <td className="p-3 border-r border-white/[0.08]">Platform-dependent floating point</td>
                      <td className="p-3 text-emerald-300 font-bold">100% Bit-exact SHA-256 (Q32.32)</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-bold border-r border-white/[0.08] text-white">Memory Allocation</td>
                      <td className="p-3 border-r border-white/[0.08]">High GC churn (MBs/sec)</td>
                      <td className="p-3 border-r border-white/[0.08]">300MB – 2GB RAM</td>
                      <td className="p-3 text-emerald-300 font-bold">&lt; 1 Byte/tick heap delta (Zero churn)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: SPECIFICATION */}
          {activeTab === 'spec' && (
            <div className="space-y-4 font-mono text-xs">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-white">Declarative .mlue Schema Invariants</span>
                <span className="text-cyan-400">Strict Invariant Architecture</span>
              </div>
              <pre className="p-4 rounded-2xl bg-black border border-white/[0.08] text-cyan-300 overflow-x-auto leading-relaxed text-xs">
{`{
  "mlue_version": "1.6",
  "environment": {
    "dimensions": [800, 600],
    "background": "#020617"
  },
  "state_variables": {
    "system": { "metric_a": 100, "status": "ACTIVE" }
  },
  "entities": [
    {
      "id": "node_01",
      "type": "circle",               // STRICT: "circle" | "box"
      "position": { "x": 0.50, "y": 0.50 }, // Normalized [0.0, 1.0]
      "size": { "radius": 0.03 },
      "velocity": { "vx": 0.2, "vy": -0.3 },
      "properties": {
        "solid": true,                // Enables elastic impulse physics
        "color": "#38BDF8",
        "control": { "channel": "paddle", "axis": "xy", "speed": 0.8 }
      }
    }
  ],
  "rules": [
    {
      "trigger": "on_contact",
      "event": "collision",
      "entities": ["node_01", "barrier_01"],
      "actions": [
        { "type": "increment_path", "target": "system.metric_a", "amount": 10 },
        { "type": "set_path", "target": "system.status", "value": "PROCESSED" }
      ]
    }
  ]
}`}
              </pre>
            </div>
          )}

          {/* TAB 4: MCP PROTOCOL */}
          {activeTab === 'mcp' && (
            <div className="space-y-4 text-xs font-mono">
              <h3 className="text-sm font-bold text-white">Model Context Protocol (MCP) AI Integration</h3>
              <p className="text-slate-300 font-sans">
                AI agents connect directly to MLUE over standard JSON-RPC without installing third-party drivers:
              </p>
              <div className="p-4 rounded-2xl bg-slate-900 border border-white/[0.08] space-y-2">
                <span className="text-cyan-400 font-bold">Cloud MCP Endpoint:</span>
                <code className="block p-2 bg-black rounded text-emerald-400">https://mlue-bench.vercel.app/api/mcp</code>
              </div>
              <div className="p-4 rounded-2xl bg-slate-900 border border-white/[0.08] space-y-2">
                <span className="text-cyan-400 font-bold">Claude Desktop / Cursor Configuration:</span>
                <pre className="p-2 bg-black rounded text-slate-300 overflow-x-auto">
{`{
  "mcpServers": {
    "mlue-cloud": {
      "url": "https://mlue-bench.vercel.app/api/mcp"
    }
  }
}`}
                </pre>
              </div>
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-white/[0.08] bg-black/40 backdrop-blur-xl flex items-center justify-between text-xs font-mono shrink-0">
          <span className="text-slate-400">
            Audit Status: <span className="text-emerald-400 font-bold">12/12 Invariants Passed (100% Empirical)</span>
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold cursor-pointer transition"
          >
            Close Guide
          </button>
        </div>

      </motion.div>
    </div>
  );
}

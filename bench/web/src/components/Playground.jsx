import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Share2, 
  Download, 
  Check, 
  Sparkles, 
  ArrowUp,
  Loader2,
  Code2,
  Send,
  X
} from 'lucide-react';
import { 
  springJelly, 
  springSnappy, 
  tapScale 
} from '../lib/motion';

const SUGGESTIONS = [
  "Cyberpunk Asteroid Dodge",
  "Neon Pinball Table",
  "Dual Bumper Pong",
  "Multi-color Brick Breaker",
  "Orbital Satellite Swarm"
];

const PRESET_SCENES = {
  breakout: {
    name: 'Emergent Breakout',
    description: 'Paddle controls, lives, and dynamic brick destruction.',
    json: {
      mlue_version: "1.6",
      environment: { dimensions: [800, 600], background: "#020617" },
      state_variables: { game: { score: 0, lives: 3, bricks_remaining: 5, state: "PLAYING" } },
      entities: [
        { id: "ball", type: "circle", position: { x: 0.50, y: 0.70 }, size: { radius: 0.025 }, velocity: { vx: 0.28, vy: -0.38 }, properties: { solid: true, color: "#38BDF8" } },
        { id: "paddle", type: "box", position: { x: 0.50, y: 0.90 }, size: { width: 0.16, height: 0.03 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#10B981", control: { channel: "paddle", axis: "x" } } },
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
  pong: {
    name: 'Emergent Dual Pong',
    description: 'Two-player paddle simulation with continuous normal reflections.',
    json: {
      mlue_version: "1.6",
      environment: { dimensions: [800, 600], background: "#090D16" },
      state_variables: { score: { p1: 0, p2: 0, rallies: 0 } },
      entities: [
        { id: "pong_ball", type: "circle", position: { x: 0.50, y: 0.50 }, size: { radius: 0.025 }, velocity: { vx: 0.35, vy: 0.22 }, properties: { solid: true, color: "#F59E0B" } },
        { id: "left_paddle", type: "box", position: { x: 0.08, y: 0.50 }, size: { width: 0.025, height: 0.20 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#3B82F6", control: { channel: "p1", axis: "y" } } },
        { id: "right_paddle", type: "box", position: { x: 0.92, y: 0.50 }, size: { width: 0.025, height: 0.20 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#EC4899", control: { channel: "p2", axis: "y" } } }
      ],
      rules: [
        { trigger: "p1_deflect", event: "collision", entities: ["pong_ball", "left_paddle"], actions: [{ type: "increment_path", target: "score.rallies", amount: 1 }] },
        { trigger: "p2_deflect", event: "collision", entities: ["pong_ball", "right_paddle"], actions: [{ type: "increment_path", target: "score.rallies", amount: 1 }] }
      ]
    }
  },
  chaos: {
    name: 'Deterministic Chaos',
    description: 'Multi-body chaotic particle collisions testing bit-exact parity.',
    json: {
      mlue_version: "1.6",
      environment: { dimensions: [800, 600], background: "#030712" },
      state_variables: { chaos: { collisions: 0 } },
      entities: [
        { id: "atom_1", type: "circle", position: { x: 0.20, y: 0.20 }, size: { radius: 0.035 }, velocity: { vx: 0.38, vy: 0.26 }, properties: { solid: true, color: "#F43F5E" } },
        { id: "atom_2", type: "circle", position: { x: 0.80, y: 0.20 }, size: { radius: 0.035 }, velocity: { vx: -0.32, vy: 0.35 }, properties: { solid: true, color: "#06B6D4" } },
        { id: "atom_3", type: "circle", position: { x: 0.20, y: 0.80 }, size: { radius: 0.035 }, velocity: { vx: 0.34, vy: -0.31 }, properties: { solid: true, color: "#10B981" } },
        { id: "atom_4", type: "circle", position: { x: 0.80, y: 0.80 }, size: { radius: 0.035 }, velocity: { vx: -0.36, vy: -0.28 }, properties: { solid: true, color: "#EAB308" } },
        { id: "center_core", type: "circle", position: { x: 0.50, y: 0.50 }, size: { radius: 0.06 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#A855F7" } }
      ],
      rules: [
        { trigger: "core_ping", event: "collision", entities: ["center_core", "atom_1"], actions: [{ type: "increment_path", target: "chaos.collisions", amount: 1 }] }
      ]
    }
  },
  orbital: {
    name: 'Orbital Satellites',
    description: 'Orbital physics with central space station and energy collection.',
    json: {
      mlue_version: "1.6",
      environment: { dimensions: [800, 600], background: "#020617" },
      state_variables: { station: { energy: 100 } },
      entities: [
        { id: "sat_1", type: "circle", position: { x: 0.25, y: 0.30 }, size: { radius: 0.03 }, velocity: { vx: 0.42, vy: 0.31 }, properties: { solid: true, color: "#38BDF8" } },
        { id: "sat_2", type: "circle", position: { x: 0.75, y: 0.30 }, size: { radius: 0.03 }, velocity: { vx: -0.31, vy: 0.42 }, properties: { solid: true, color: "#38BDF8" } },
        { id: "core_station", type: "box", position: { x: 0.50, y: 0.50 }, size: { width: 0.10, height: 0.10 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#10B981" } }
      ],
      rules: [
        { trigger: "sat1_energy", event: "collision", entities: ["core_station", "sat_1"], actions: [{ type: "increment_path", target: "station.energy", amount: 25 }] }
      ]
    }
  }
};

export default function Playground({ onOpenBenchmarks }) {
  const [activeTitle, setActiveTitle] = useState('Emergent Breakout');
  const [jsonText, setJsonText] = useState(JSON.stringify(PRESET_SCENES.breakout.json, null, 2));
  const [showCode, setShowCode] = useState(false);
  const [isPlaying, setIsPlaying] = useState(true);
  const [simSpeed, setSimSpeed] = useState(1.0);
  const [tickCount, setTickCount] = useState(0);
  const [copiedLink, setCopiedLink] = useState(false);
  
  // Minimalist AI Prompt State
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [refinePrompt, setRefinePrompt] = useState('');

  // Local Recent Builds
  const [recentBuilds, setRecentBuilds] = useState(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('mlue_recent_builds');
        return saved ? JSON.parse(saved) : [];
      } catch (e) {
        return [];
      }
    }
    return [];
  });

  const simStateRef = useRef(null);
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const keysDownRef = useRef({});
  const stageRef = useRef(null);

  // Save Scene
  const saveToRecent = useCallback((name, sceneObj) => {
    try {
      const entry = {
        id: 'build_' + Date.now(),
        name: name || 'Custom Game',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        json: sceneObj
      };
      setRecentBuilds(prev => {
        const filtered = prev.filter(b => b.name !== entry.name);
        const updated = [entry, ...filtered].slice(0, 8);
        localStorage.setItem('mlue_recent_builds', JSON.stringify(updated));
        return updated;
      });
    } catch (e) {}
  }, []);

  // Initialize Simulation
  const initSimulation = useCallback((jsonObj, saveHistory = false, historyName = '') => {
    try {
      const cloned = JSON.parse(JSON.stringify(jsonObj));
      simStateRef.current = {
        doc: cloned,
        entities: cloned.entities || [],
        state_variables: cloned.state_variables || {},
        rules: cloned.rules || [],
        env: cloned.environment || { dimensions: [800, 600], background: "#020617" },
        tick: 0
      };
      setTickCount(0);
      setErrorMsg(null);
      if (saveHistory) {
        saveToRecent(historyName || 'Custom Scene', cloned);
      }
    } catch (e) {
      setErrorMsg(e.message);
    }
  }, [saveToRecent]);

  // Mount
  useEffect(() => {
    if (window.location.hash.startsWith('#data=')) {
      try {
        const rawJson = decodeURIComponent(atob(window.location.hash.substring(6)));
        const parsed = JSON.parse(rawJson);
        setJsonText(JSON.stringify(parsed, null, 2));
        setActiveTitle('Shared Game');
        initSimulation(parsed, true, 'Shared Game');
        return;
      } catch (e) {}
    }
    initSimulation(PRESET_SCENES.breakout.json);
  }, [initSimulation]);

  // Handle Preset Select
  const handleSelectPreset = (key) => {
    const preset = PRESET_SCENES[key];
    setActiveTitle(preset.name);
    setJsonText(JSON.stringify(preset.json, null, 2));
    initSimulation(preset.json, true, preset.name);
    stageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // AI Game Generator
  const handleBuild = async (textToUse = prompt) => {
    if (!textToUse.trim()) return;
    setIsGenerating(true);
    setErrorMsg(null);

    let currentScene = null;
    try {
      currentScene = JSON.parse(jsonText);
    } catch (e) {}

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: textToUse,
          current_scene: currentScene
        })
      });

      const data = await res.json();
      if (data.success && data.scene) {
        const pretty = JSON.stringify(data.scene, null, 2);
        const gameName = textToUse.length > 28 ? textToUse.slice(0, 28) + '...' : textToUse;
        setJsonText(pretty);
        setActiveTitle(gameName);
        initSimulation(data.scene, true, gameName);
        setPrompt('');
        setRefinePrompt('');
        // Smooth scroll to stage
        setTimeout(() => {
          stageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
      } else {
        setErrorMsg(data.error || 'Could not generate game.');
      }
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  // Keyboard controls
  useEffect(() => {
    const handleKeyDown = (e) => {
      keysDownRef.current[e.key] = true;
      keysDownRef.current[e.code] = true;
    };
    const handleKeyUp = (e) => {
      keysDownRef.current[e.key] = false;
      keysDownRef.current[e.code] = false;
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  const triggerTouch = (key, isDown) => {
    keysDownRef.current[key] = isDown;
  };

  // Step Simulation
  const stepSimulation = useCallback((dt) => {
    const state = simStateRef.current;
    if (!state) return;

    const [envW, envH] = state.env.dimensions || [800, 600];
    const minDim = Math.min(envW, envH);

    // Controls
    const keys = keysDownRef.current;
    for (const ent of state.entities) {
      const ctrl = ent.properties?.control;
      if (ctrl) {
        let speed = 0.60;
        if (ctrl.channel === 'paddle' || ctrl.channel === 'p1') {
          if (ctrl.axis === 'x') {
            if (keys['ArrowLeft'] || keys['a'] || keys['KeyA']) {
              ent.velocity.vx = -speed;
            } else if (keys['ArrowRight'] || keys['d'] || keys['KeyD']) {
              ent.velocity.vx = speed;
            } else {
              ent.velocity.vx = 0.0;
            }
          } else if (ctrl.axis === 'y') {
            if (keys['ArrowUp'] || keys['w'] || keys['KeyW']) {
              ent.velocity.vy = -speed;
            } else if (keys['ArrowDown'] || keys['s'] || keys['KeyS']) {
              ent.velocity.vy = speed;
            } else {
              ent.velocity.vy = 0.0;
            }
          }
        } else if (ctrl.channel === 'p2') {
          if (keys['ArrowUp'] || keys['k']) {
            ent.velocity.vy = -speed;
          } else if (keys['ArrowDown'] || keys['j']) {
            ent.velocity.vy = speed;
          } else {
            ent.velocity.vy = 0.0;
          }
        }
      }
    }

    // Kinematics & Bounding
    for (const ent of state.entities) {
      if (ent.active === false) continue;

      let ex = 0, ey = 0;
      if (ent.type === 'circle') {
        const r = ent.size.radius;
        ex = r * (minDim / envW);
        ey = r * (minDim / envH);
      } else if (ent.type === 'box') {
        ex = ent.size.width / 2.0;
        ey = ent.size.height / 2.0;
      }

      let newX = ent.position.x + (ent.velocity.vx * dt);
      let newY = ent.position.y + (ent.velocity.vy * dt);

      if (newX - ex <= 0.0) {
        newX = ex;
        if (ent.velocity.vx < 0) ent.velocity.vx = -ent.velocity.vx;
      } else if (newX + ex >= 1.0) {
        newX = 1.0 - ex;
        if (ent.velocity.vx > 0) ent.velocity.vx = -ent.velocity.vx;
      }

      if (newY - ey <= 0.0) {
        newY = ey;
        if (ent.velocity.vy < 0) ent.velocity.vy = -ent.velocity.vy;
      } else if (newY + ey >= 1.0) {
        newY = 1.0 - ey;
        if (ent.velocity.vy > 0) ent.velocity.vy = -ent.velocity.vy;
      }

      ent.position.x = Math.max(ex, Math.min(1.0 - ex, newX));
      ent.position.y = Math.max(ey, Math.min(1.0 - ey, newY));
    }

    // Collisions
    const entities = state.entities;
    const collisionsThisFrame = [];

    for (let i = 0; i < entities.length; i++) {
      const e1 = entities[i];
      if (e1.active === false || !e1.properties?.solid) continue;

      for (let j = i + 1; j < entities.length; j++) {
        const e2 = entities[j];
        if (e2.active === false || !e2.properties?.solid) continue;

        // Circle vs Circle
        if (e1.type === 'circle' && e2.type === 'circle') {
          const r1 = e1.size.radius;
          const r2 = e2.size.radius;
          const dx = (e1.position.x - e2.position.x) * (envW / minDim);
          const dy = (e1.position.y - e2.position.y) * (envH / minDim);
          const distSq = (dx * dx) + (dy * dy);
          const minDist = r1 + r2;

          if (distSq < (minDist * minDist) && distSq > 1e-9) {
            const dist = Math.sqrt(distSq);
            const nx = dx / dist;
            const ny = dy / dist;
            const rvx = e1.velocity.vx - e2.velocity.vx;
            const rvy = e1.velocity.vy - e2.velocity.vy;
            const velAlongNorm = (rvx * nx) + (rvy * ny);

            if (velAlongNorm < 0) {
              const impulse = -velAlongNorm;
              e1.velocity.vx += nx * impulse;
              e1.velocity.vy += ny * impulse;
              e2.velocity.vx -= nx * impulse;
              e2.velocity.vy -= ny * impulse;

              const pen = (minDist - dist) * 0.5;
              e1.position.x += nx * pen * (minDim / envW);
              e1.position.y += ny * pen * (minDim / envH);
              e2.position.x -= nx * pen * (minDim / envW);
              e2.position.y -= ny * pen * (minDim / envH);

              collisionsThisFrame.push([e1.id, e2.id]);
            }
          }
        }
        // Circle vs Box
        else if ((e1.type === 'circle' && e2.type === 'box') || (e1.type === 'box' && e2.type === 'circle')) {
          const circle = e1.type === 'circle' ? e1 : e2;
          const box = e1.type === 'box' ? e1 : e2;

          const r = circle.size.radius;
          const hw = box.size.width * 0.5;
          const hh = box.size.height * 0.5;

          const nearestX = Math.max(box.position.x - hw, Math.min(box.position.x + hw, circle.position.x));
          const nearestY = Math.max(box.position.y - hh, Math.min(box.position.y + hh, circle.position.y));

          const dx = (circle.position.x - nearestX) * (envW / minDim);
          const dy = (circle.position.y - nearestY) * (envH / minDim);
          const distSq = (dx * dx) + (dy * dy);

          if (distSq < (r * r) && distSq > 1e-9) {
            const dist = Math.sqrt(distSq);
            const nx = dx / dist;
            const ny = dy / dist;
            const rvx = circle.velocity.vx - box.velocity.vx;
            const rvy = circle.velocity.vy - box.velocity.vy;
            const velAlongNorm = (rvx * nx) + (rvy * ny);

            if (velAlongNorm < 0) {
              const impulse = -(1.0 + 1.0) * velAlongNorm * 0.5;
              circle.velocity.vx += nx * impulse;
              circle.velocity.vy += ny * impulse;

              const pen = (r - dist);
              circle.position.x += nx * pen * (minDim / envW);
              circle.position.y += ny * pen * (minDim / envH);

              collisionsThisFrame.push([circle.id, box.id]);
            }
          }
        }
      }
    }

    // Rules
    if (state.rules && state.rules.length > 0) {
      for (const rule of state.rules) {
        if (rule.event === 'collision') {
          const [idA, idB] = rule.entities || [];
          const hit = collisionsThisFrame.some(([c1, c2]) => (c1 === idA && c2 === idB) || (c1 === idB && c2 === idA));
          if (hit) {
            for (const action of rule.actions || []) {
              if (action.type === 'destroy_entity') {
                const target = state.entities.find(e => e.id === action.target);
                if (target) target.active = false;
              } else if (action.type === 'increment_path') {
                const parts = action.target.split('.');
                let curr = state.state_variables;
                for (let k = 0; k < parts.length - 1; k++) {
                  curr = curr[parts[k]];
                }
                if (curr && parts.length > 0) {
                  const lastKey = parts[parts.length - 1];
                  curr[lastKey] = (curr[lastKey] || 0) + action.amount;
                }
              }
            }
          }
        }
      }
    }

    state.tick += 1;
    setTickCount(state.tick);
  }, []);

  // Canvas Render Loop
  useEffect(() => {
    let lastTime = performance.now();

    const render = (time) => {
      const canvas = canvasRef.current;
      if (canvas && simStateRef.current) {
        const ctx = canvas.getContext('2d');
        const state = simStateRef.current;
        const [envW, envH] = state.env.dimensions || [800, 600];
        const minDim = Math.min(envW, envH);

        canvas.width = envW;
        canvas.height = envH;

        if (isPlaying) {
          const rawDt = (time - lastTime) / 1000.0;
          const dt = Math.min(rawDt, 0.05) * simSpeed;
          stepSimulation(dt);
        }
        lastTime = time;

        ctx.fillStyle = state.env.background || "#020617";
        ctx.fillRect(0, 0, envW, envH);

        for (const ent of state.entities) {
          if (ent.active === false) continue;
          const color = ent.properties?.color || "#38BDF8";

          if (ent.type === 'circle') {
            const px = ent.position.x * envW;
            const py = ent.position.y * envH;
            const r = ent.size.radius * minDim;

            ctx.beginPath();
            ctx.arc(px, py, r, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.shadowColor = color;
            ctx.shadowBlur = 8;
            ctx.fill();
            ctx.shadowBlur = 0;
          } else if (ent.type === 'box') {
            const w = ent.size.width * envW;
            const h = ent.size.height * envH;
            const px = (ent.position.x * envW) - (w / 2.0);
            const py = (ent.position.y * envH) - (h / 2.0);

            ctx.fillStyle = color;
            ctx.shadowColor = color;
            ctx.shadowBlur = 6;
            ctx.fillRect(px, py, w, h);
            ctx.shadowBlur = 0;
          }
        }
      }

      animFrameRef.current = requestAnimationFrame(render);
    };

    animFrameRef.current = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animFrameRef.current);
  }, [isPlaying, simSpeed, stepSimulation]);

  // Share
  const copyShareLink = () => {
    try {
      const base64 = btoa(encodeURIComponent(jsonText));
      const url = `${window.location.origin}${window.location.pathname}#data=${base64}`;
      navigator.clipboard.writeText(url);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    } catch (e) {}
  };

  // Download
  const downloadMlue = () => {
    const blob = new Blob([jsonText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeTitle.toLowerCase().replace(/[^a-z0-9]/g, '_')}.mlue`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-16 max-w-5xl mx-auto px-2">
      
      {/* 1. HERO PROMPT SECTION: MINIMALIST, BREATHABLE, ATTRACTOR (Apple / ChatGPT Style) */}
      <section className="pt-8 pb-4 text-center max-w-3xl mx-auto space-y-6">
        
        {/* Title */}
        <div className="space-y-2">
          <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white">
            What do you want to play?
          </h1>
          <p className="text-sm text-slate-400 font-sans">
            Describe any game or simulation. Generated and simulated in native 60 FPS.
          </p>
        </div>

        {/* Spacious Floating Prompt Capsule */}
        <div className="relative pt-2">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleBuild(); }}
            className="flex items-center bg-slate-900/90 border border-white/[0.12] hover:border-cyan-500/40 focus-within:border-cyan-400 focus-within:ring-4 focus-within:ring-cyan-500/10 rounded-full p-2 pl-6 shadow-2xl transition-all backdrop-blur-xl"
          >
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Neon Pinball table with 4 targets and high score counters..."
              disabled={isGenerating}
              className="flex-1 bg-transparent text-sm sm:text-base text-slate-100 placeholder-slate-500 focus:outline-none font-sans"
            />
            <motion.button
              {...tapScale.button}
              type="submit"
              disabled={isGenerating || !prompt.trim()}
              className="w-10 h-10 sm:w-11 sm:h-11 rounded-full bg-cyan-400 hover:bg-cyan-300 text-slate-950 flex items-center justify-center transition disabled:opacity-40 shadow-md shadow-cyan-500/20 cursor-pointer shrink-0 ml-2"
            >
              {isGenerating ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <ArrowUp className="w-5 h-5 stroke-[2.5]" />
              )}
            </motion.button>
          </form>

          {/* Minimal Suggestion Chips */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-4">
            {SUGGESTIONS.map((sug, idx) => (
              <motion.button
                {...tapScale.pill}
                key={idx}
                onClick={() => handleBuild(sug)}
                disabled={isGenerating}
                className="text-xs font-sans text-slate-400 hover:text-white bg-slate-900/60 hover:bg-slate-800 border border-white/[0.08] hover:border-cyan-500/30 px-3.5 py-1.5 rounded-full cursor-pointer transition-colors"
              >
                {sug}
              </motion.button>
            ))}
          </div>

          {errorMsg && (
            <div className="mt-3 text-xs text-rose-400 font-mono">
              {errorMsg}
            </div>
          )}
        </div>

      </section>

      {/* 2. ACTIVE INTERACTIVE STAGE & CANVAS */}
      <section ref={stageRef} className="space-y-4">
        
        <div className="bg-slate-900/90 border border-white/[0.08] rounded-3xl overflow-hidden shadow-2xl backdrop-blur-xl">
          
          {/* Minimal Stage Bar */}
          <div className="px-6 py-4 border-b border-white/[0.06] flex items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <h2 className="text-sm font-bold text-white tracking-tight truncate">{activeTitle}</h2>
              <span className="text-[11px] font-mono text-slate-500 hidden sm:inline">60 FPS Native</span>
            </div>

            {/* Playback Controls */}
            <div className="flex items-center gap-2">
              <motion.button
                {...tapScale.button}
                onClick={() => setIsPlaying(!isPlaying)}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold transition cursor-pointer ${
                  isPlaying 
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' 
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                <span>{isPlaying ? 'PAUSE' : 'PLAY'}</span>
              </motion.button>

              <motion.button
                {...tapScale.button}
                onClick={() => {
                  try {
                    initSimulation(JSON.parse(jsonText));
                  } catch (e) {}
                }}
                className="p-2 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/[0.06] cursor-pointer"
                title="Reset Simulation"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </motion.button>

              <motion.button
                {...tapScale.button}
                onClick={copyShareLink}
                className="p-2 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/[0.06] cursor-pointer"
                title="Share Game"
              >
                {copiedLink ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Share2 className="w-3.5 h-3.5 text-cyan-400" />}
              </motion.button>

              <motion.button
                {...tapScale.button}
                onClick={downloadMlue}
                className="p-2 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/[0.06] cursor-pointer"
                title="Export .mlue"
              >
                <Download className="w-3.5 h-3.5 text-emerald-400" />
              </motion.button>

              <motion.button
                {...tapScale.button}
                onClick={() => setShowCode(!showCode)}
                className={`p-2 rounded-full border border-white/[0.06] transition cursor-pointer ${
                  showCode ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
                title="View Schema"
              >
                <Code2 className="w-3.5 h-3.5" />
              </motion.button>
            </div>
          </div>

          {/* Canvas Viewport */}
          <div className="relative aspect-[16/10] sm:aspect-[16/9] bg-slate-950 flex items-center justify-center p-2">
            <canvas
              ref={canvasRef}
              className="w-full h-full object-contain rounded-2xl border border-white/[0.04]"
            />

            {/* Minimal HUD (State Variables) */}
            {simStateRef.current?.state_variables && Object.keys(simStateRef.current.state_variables).length > 0 && (
              <div className="absolute top-4 left-4 bg-black/60 border border-white/[0.08] rounded-xl px-3 py-2 backdrop-blur-md font-mono text-[11px] pointer-events-none space-y-0.5">
                {Object.entries(simStateRef.current.state_variables).map(([k, v]) => (
                  <div key={k} className="text-slate-300">
                    <span className="text-cyan-400">{k}</span>: {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                  </div>
                ))}
              </div>
            )}

            {/* Keyboard Hint */}
            <div className="absolute bottom-4 right-4 hidden sm:flex bg-black/60 border border-white/[0.08] rounded-full px-3 py-1 text-[11px] text-slate-400 font-mono pointer-events-none">
              Move: <span className="text-cyan-400 font-bold mx-1">A / D</span> or <span className="text-cyan-400 font-bold ml-1">← / →</span>
            </div>
          </div>

          {/* Mobile Touch Controls */}
          <div className="flex sm:hidden items-center justify-center gap-3 bg-slate-950 border-t border-white/[0.06] p-3">
            <motion.button
              {...tapScale.button}
              onTouchStart={() => triggerTouch('ArrowLeft', true)}
              onTouchEnd={() => triggerTouch('ArrowLeft', false)}
              onMouseDown={() => triggerTouch('ArrowLeft', true)}
              onMouseUp={() => triggerTouch('ArrowLeft', false)}
              className="flex-1 py-3 bg-slate-800 active:bg-cyan-600 rounded-full font-mono text-sm font-bold text-center border border-white/[0.08] cursor-pointer"
            >
              ◀ LEFT
            </motion.button>
            <motion.button
              {...tapScale.button}
              onTouchStart={() => triggerTouch('ArrowRight', true)}
              onTouchEnd={() => triggerTouch('ArrowRight', false)}
              onMouseDown={() => triggerTouch('ArrowRight', true)}
              onMouseUp={() => triggerTouch('ArrowRight', false)}
              className="flex-1 py-3 bg-slate-800 active:bg-cyan-600 rounded-full font-mono text-sm font-bold text-center border border-white/[0.08] cursor-pointer"
            >
              RIGHT ▶
            </motion.button>
          </div>

          {/* Sleek Refinement Bar at Bottom of Stage */}
          <div className="p-3 sm:p-4 bg-slate-950/80 border-t border-white/[0.06]">
            <form 
              onSubmit={(e) => { e.preventDefault(); handleBuild(refinePrompt); }}
              className="flex items-center bg-slate-900 border border-white/[0.08] focus-within:border-cyan-400 rounded-full px-4 py-2"
            >
              <input
                type="text"
                value={refinePrompt}
                onChange={(e) => setRefinePrompt(e.target.value)}
                placeholder="Tweak this game (e.g. make the ball 2x faster, add green bricks)..."
                disabled={isGenerating}
                className="flex-1 bg-transparent text-xs text-slate-200 placeholder-slate-500 focus:outline-none font-sans"
              />
              <motion.button
                {...tapScale.icon}
                type="submit"
                disabled={isGenerating || !refinePrompt.trim()}
                className="p-1.5 bg-cyan-400 text-slate-950 rounded-full disabled:opacity-40 cursor-pointer ml-2"
              >
                {isGenerating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              </motion.button>
            </form>
          </div>

          {/* Optional Code Drawer */}
          <AnimatePresence>
            {showCode && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto', transition: springSnappy }}
                exit={{ opacity: 0, height: 0, transition: { duration: 0.15 } }}
                className="border-t border-white/[0.06] bg-slate-950 p-4"
              >
                <div className="flex items-center justify-between mb-2 text-xs font-mono text-slate-400">
                  <span>Declarative Schema (.mlue)</span>
                  <button onClick={() => setShowCode(false)} className="hover:text-white cursor-pointer"><X className="w-3.5 h-3.5" /></button>
                </div>
                <textarea
                  value={jsonText}
                  onChange={(e) => {
                    setJsonText(e.target.value);
                    try {
                      initSimulation(JSON.parse(e.target.value));
                    } catch (err) {}
                  }}
                  spellCheck={false}
                  className="w-full h-48 bg-black text-cyan-300 font-mono text-xs p-3 rounded-xl border border-white/[0.08] focus:outline-none resize-none leading-relaxed"
                />
              </motion.div>
            )}
          </AnimatePresence>

        </div>

      </section>

      {/* 3. FEATURED & RECENT CREATIONS GALLERY (Scroll to See) */}
      <section className="space-y-4 pt-4 border-t border-white/[0.06]">
        
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-bold">
            Curated Worlds & Recent Builds
          </h3>
          <span className="text-[11px] font-mono text-slate-500">Zero-Install Playable</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(PRESET_SCENES).map(([key, item]) => {
            const isSelected = activeTitle === item.name;
            return (
              <motion.button
                {...tapScale.card}
                key={key}
                onClick={() => handleSelectPreset(key)}
                className={`p-4 text-left rounded-2xl border transition-colors cursor-pointer ${
                  isSelected 
                    ? 'bg-cyan-500/10 border-cyan-500/50 shadow-lg shadow-cyan-500/5' 
                    : 'bg-slate-900/60 border-white/[0.06] hover:border-white/[0.15] text-slate-400'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className={`text-sm font-bold ${isSelected ? 'text-cyan-300' : 'text-slate-200'}`}>
                    {item.name}
                  </span>
                  {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />}
                </div>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">{item.description}</p>
              </motion.button>
            );
          })}

          {recentBuilds.map((build) => (
            <motion.button
              {...tapScale.card}
              key={build.id}
              onClick={() => {
                setActiveTitle(build.name);
                setJsonText(JSON.stringify(build.json, null, 2));
                initSimulation(build.json);
                stageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }}
              className="p-4 text-left rounded-2xl border border-emerald-500/30 bg-emerald-950/20 hover:border-emerald-500/60 text-slate-300 cursor-pointer"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm font-bold text-emerald-400 truncate">{build.name}</span>
                <span className="text-[10px] font-mono text-slate-500">{build.timestamp}</span>
              </div>
              <p className="text-xs text-slate-400 font-sans">Recent Creation</p>
            </motion.button>
          ))}
        </div>

      </section>

    </div>
  );
}

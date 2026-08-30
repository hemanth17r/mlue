import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  FastForward, 
  Upload, 
  Download, 
  Share2, 
  Check, 
  Sliders, 
  Layers, 
  Sparkles, 
  Terminal, 
  Maximize2, 
  Minimize2,
  Gamepad2
} from 'lucide-react';

// Built-in presets for instant exploration
const PRESET_SCENES = {
  breakout: {
    name: 'Emergent Breakout',
    description: 'Classic brick breaker with paddle controls, lives, and dynamic brick destruction.',
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
    description: 'Two-player paddle simulation with continuous normal reflections and score tracking.',
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
    name: 'Deterministic Chaos (Q32.32)',
    description: 'High-frequency multi-body chaotic particle collisions testing bit-exact parity.',
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
    name: 'Orbital Satellites Swarm',
    description: 'High-speed orbital physics with bounding boxes, central space station, and energy points.',
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

export default function Playground() {
  const [activePreset, setActivePreset] = useState('breakout');
  const [jsonText, setJsonText] = useState(JSON.stringify(PRESET_SCENES.breakout.json, null, 2));
  const [parseError, setParseError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [simSpeed, setSimSpeed] = useState(1.0);
  const [tickCount, setTickCount] = useState(0);
  const [copiedLink, setCopiedLink] = useState(false);
  const [activeTab, setActiveTab] = useState('canvas'); // 'canvas' or 'editor'
  
  // Live simulation state
  const simStateRef = useRef(null);
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const keysDownRef = useRef({});

  // Initialize or reset simulation state from current JSON text
  const initSimulation = useCallback((jsonObj) => {
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
      setParseError(null);
    } catch (e) {
      setParseError(e.message);
    }
  }, []);

  // On mount / URL query parameter detection
  useEffect(() => {
    // Check if URL has a ?scene= query parameter or #data= hash
    const params = new URLSearchParams(window.location.search);
    const sceneParam = params.get('scene');
    if (sceneParam && PRESET_SCENES[sceneParam]) {
      setActivePreset(sceneParam);
      setJsonText(JSON.stringify(PRESET_SCENES[sceneParam].json, null, 2));
      initSimulation(PRESET_SCENES[sceneParam].json);
      return;
    }

    if (window.location.hash.startsWith('#data=')) {
      try {
        const rawJson = decodeURIComponent(atob(window.location.hash.substring(6)));
        const parsed = JSON.parse(rawJson);
        setJsonText(JSON.stringify(parsed, null, 2));
        initSimulation(parsed);
        return;
      } catch (e) {
        console.warn("Could not decode hash state:", e);
      }
    }

    initSimulation(PRESET_SCENES.breakout.json);
  }, [initSimulation]);

  // Handle Preset Selection
  const selectPreset = (key) => {
    setActivePreset(key);
    const selected = PRESET_SCENES[key].json;
    setJsonText(JSON.stringify(selected, null, 2));
    initSimulation(selected);
  };

  // Live JSON Text Editor Change
  const handleJsonChange = (e) => {
    const text = e.target.value;
    setJsonText(text);
    try {
      const parsed = JSON.parse(text);
      setParseError(null);
      initSimulation(parsed);
    } catch (err) {
      setParseError(err.message);
    }
  };

  // Keyboard Event Listeners for Paddle / Inputs
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

  // Main Simulation Step Logic (60 FPS HTML5 Canvas Engine)
  const stepSimulation = useCallback((dt) => {
    const state = simStateRef.current;
    if (!state) return;

    const [envW, envH] = state.env.dimensions || [800, 600];
    const minDim = Math.min(envW, envH);

    // 1. Process Input Controls
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

    // 2. Integration & Boundary Clamping
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

      // Arena boundaries [0.0, 1.0]
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

    // 3. Pairwise Collisions
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

    // 4. Evaluate Declarative Rules
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

        // Handle Dynamic Resizing
        canvas.width = envW;
        canvas.height = envH;

        // Step simulation if playing
        if (isPlaying) {
          const rawDt = (time - lastTime) / 1000.0;
          const dt = Math.min(rawDt, 0.05) * simSpeed;
          stepSimulation(dt);
        }
        lastTime = time;

        // Clear Canvas
        ctx.fillStyle = state.env.background || "#020617";
        ctx.fillRect(0, 0, envW, envH);

        // Render Entities
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

  // Handle Drag and Drop of .mlue / .mlueb Files
  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const content = event.target.result;
          const parsed = JSON.parse(content);
          setJsonText(JSON.stringify(parsed, null, 2));
          initSimulation(parsed);
        } catch (err) {
          setParseError("Uploaded file is not a valid JSON document: " + err.message);
        }
      };
      reader.readAsText(file);
    }
  };

  // Copy Shareable Link to Clipboard
  const copyShareLink = () => {
    try {
      const base64 = btoa(encodeURIComponent(jsonText));
      const url = `${window.location.origin}${window.location.pathname}#data=${base64}`;
      navigator.clipboard.writeText(url);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2500);
    } catch (e) {
      console.error("Could not create share link:", e);
    }
  };

  // Download .mlue Document
  const downloadMlue = () => {
    const blob = new Blob([jsonText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activePreset || 'custom_scene'}.mlue`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div 
      className="space-y-6"
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
    >
      {/* Top Controls Header */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
            <Gamepad2 className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              MLUE Live Studio & Web Player
              <span className="text-xs bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 px-2 py-0.5 rounded font-mono font-medium">
                60 FPS Zero-Install
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Interactive playground: edit, test, play with keyboard (WASD / Arrows), and share games instantly.
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2 w-full lg:w-auto">
          <button
            onClick={copyShareLink}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3.5 py-2 rounded-lg border border-slate-700 transition"
          >
            {copiedLink ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Share2 className="w-3.5 h-3.5 text-cyan-400" />}
            {copiedLink ? 'Link Copied!' : 'Share Playable Link'}
          </button>
          
          <button
            onClick={downloadMlue}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3.5 py-2 rounded-lg border border-slate-700 transition"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            Download .mlue
          </button>
        </div>
      </div>

      {/* Preset Gallery Selector */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Object.entries(PRESET_SCENES).map(([key, item]) => (
          <button
            key={key}
            onClick={() => selectPreset(key)}
            className={`p-3 text-left rounded-xl border transition-all ${
              activePreset === key 
                ? 'bg-cyan-500/10 border-cyan-500/50 shadow-lg shadow-cyan-500/5' 
                : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 text-slate-400'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className={`text-sm font-semibold ${activePreset === key ? 'text-cyan-300' : 'text-slate-200'}`}>
                {item.name}
              </span>
              {activePreset === key && <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />}
            </div>
            <p className="text-xs text-slate-500 line-clamp-2">{item.description}</p>
          </button>
        ))}
      </div>

      {/* Main Interactive Stage & Code Editor Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: 60 FPS HTML5 Canvas Stage */}
        <div className="lg:col-span-7 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
          {/* Canvas Toolbar */}
          <div className="bg-slate-950/80 border-b border-slate-800 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  isPlaying ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                }`}
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                {isPlaying ? 'Pause' : 'Play'}
              </button>

              <button
                onClick={() => stepSimulation(0.01667)}
                disabled={isPlaying}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 disabled:opacity-40"
              >
                <FastForward className="w-3 h-3" /> Step
              </button>

              <button
                onClick={() => {
                  try {
                    initSimulation(JSON.parse(jsonText));
                  } catch (e) {}
                }}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
              >
                <RotateCcw className="w-3 h-3" /> Reset
              </button>
            </div>

            {/* Simulation Status */}
            <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
              <span>Ticks: <strong className="text-cyan-400">{tickCount}</strong></span>
              <div className="flex items-center gap-1.5">
                <span>Speed:</span>
                <select
                  value={simSpeed}
                  onChange={(e) => setSimSpeed(parseFloat(e.target.value))}
                  className="bg-slate-800 border border-slate-700 rounded px-1.5 py-0.5 text-xs text-slate-200"
                >
                  <option value={0.5}>0.5x</option>
                  <option value={1.0}>1.0x</option>
                  <option value={2.0}>2.0x</option>
                  <option value={4.0}>4.0x</option>
                </select>
              </div>
            </div>
          </div>

          {/* Interactive Canvas Viewport */}
          <div className="relative aspect-[4/3] bg-slate-950 flex items-center justify-center p-2">
            <canvas
              ref={canvasRef}
              className="w-full h-full object-contain rounded border border-slate-800/80 shadow-inner"
            />

            {/* Live HUD Overlay (State Variables) */}
            <div className="absolute top-4 left-4 bg-slate-900/85 border border-slate-700/80 rounded-lg p-2.5 backdrop-blur font-mono text-xs pointer-events-none shadow-lg">
              <div className="text-[10px] uppercase text-slate-400 font-bold tracking-wider mb-1">State Variables</div>
              {simStateRef.current && simStateRef.current.state_variables && (
                <div className="space-y-0.5">
                  {Object.entries(simStateRef.current.state_variables).map(([k, v]) => (
                    <div key={k} className="text-slate-300">
                      <span className="text-cyan-400 font-semibold">{k}</span>: {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Keyboard Control Hints */}
            <div className="absolute bottom-4 right-4 bg-slate-900/80 border border-slate-800 rounded px-2.5 py-1 text-[11px] text-slate-400 font-mono pointer-events-none">
              Controls: <span className="text-emerald-400 font-bold">A / D</span> or <span className="text-emerald-400 font-bold">← / →</span>
            </div>
          </div>
        </div>

        {/* Right Side: Live JSON Schema / Document Editor */}
        <div className="lg:col-span-5 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
          <div className="bg-slate-950/80 border-b border-slate-800 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-bold text-slate-300 font-mono">Declarative .mlue Definition</span>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">Live Hot-Reload</span>
          </div>

          <div className="p-3 flex-1 flex flex-col">
            <textarea
              value={jsonText}
              onChange={handleJsonChange}
              spellCheck={false}
              className="w-full h-80 lg:h-[420px] bg-slate-950 text-cyan-300 font-mono text-xs p-3 rounded-lg border border-slate-800 focus:border-cyan-500 focus:outline-none resize-none leading-relaxed"
            />

            {parseError && (
              <div className="mt-2 p-2.5 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400 text-xs font-mono">
                <strong>Syntax Error:</strong> {parseError}
              </div>
            )}

            <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
              <span>Drag & drop any <code>.mlue</code> file anywhere</span>
              <span>100% Client-Side Evaluation</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

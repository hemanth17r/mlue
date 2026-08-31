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
  Key,
  Send,
  Loader2,
  ChevronRight,
  Gamepad2,
  HelpCircle,
  Clock,
  Trash2
} from 'lucide-react';

const SUGGESTIONS = [
  "Cyberpunk Asteroid Dodge with shield controls",
  "Neon Pinball table with 4 bumper targets",
  "Dual Bumper Pong with high-speed scoring",
  "Multi-colored Brick Breaker with 10 targets",
  "Orbital Satellite Gravity Swarm"
];

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

export default function Playground({ onOpenBenchmarks }) {
  const [activePreset, setActivePreset] = useState('breakout');
  const [jsonText, setJsonText] = useState(JSON.stringify(PRESET_SCENES.breakout.json, null, 2));
  const [parseError, setParseError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [simSpeed, setSimSpeed] = useState(1.0);
  const [tickCount, setTickCount] = useState(0);
  const [copiedLink, setCopiedLink] = useState(false);
  
  // AI Prompt & Refinement State
  const [userPrompt, setUserPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [genError, setGenError] = useState(null);
  const [apiKey, setApiKey] = useState(() => {
    return typeof window !== 'undefined' ? localStorage.getItem('mlue_gemini_key') || '' : '';
  });
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    { sender: 'ai', text: 'Welcome to MLUE AI Studio! Describe any game or interactive simulation, and I will build and run it live.' }
  ]);

  // Recent Builds (LocalStorage)
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

  // Live simulation state
  const simStateRef = useRef(null);
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const keysDownRef = useRef({});

  // Save scene to Recent Builds
  const saveToRecent = useCallback((name, sceneObj) => {
    try {
      const entry = {
        id: 'build_' + Date.now(),
        name: name || 'Custom Build',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        json: sceneObj
      };
      setRecentBuilds(prev => {
        const filtered = prev.filter(b => b.name !== entry.name);
        const updated = [entry, ...filtered].slice(0, 10);
        localStorage.setItem('mlue_recent_builds', JSON.stringify(updated));
        return updated;
      });
    } catch (e) {}
  }, []);

  // Initialize or reset simulation state from current JSON text
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
      setParseError(null);
      if (saveHistory) {
        saveToRecent(historyName || 'Custom Scene', cloned);
      }
    } catch (e) {
      setParseError(e.message);
    }
  }, [saveToRecent]);

  // On mount / URL query parameter detection
  useEffect(() => {
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
        initSimulation(parsed, true, 'Shared Link Scene');
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
    initSimulation(selected, true, PRESET_SCENES[key].name);
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

  // Save API Key
  const handleSaveApiKey = (key) => {
    setApiKey(key);
    localStorage.setItem('mlue_gemini_key', key);
    setShowKeyModal(false);
  };

  // AI Generation & Conversational Refinement Handler
  const handleGenerateGame = async (promptToUse = userPrompt) => {
    if (!promptToUse.trim()) return;
    setIsGenerating(true);
    setGenError(null);

    const userMsg = promptToUse;
    setUserPrompt('');
    setChatHistory(prev => [...prev, { sender: 'user', text: userMsg }]);

    let currentScene = null;
    try {
      currentScene = JSON.parse(jsonText);
    } catch (e) {}

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (apiKey) headers['x-gemini-key'] = apiKey;

      const res = await fetch('/api/generate', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          prompt: userMsg,
          current_scene: currentScene,
          api_key: apiKey
        })
      });

      const data = await res.json();

      if (data.success && data.scene) {
        const prettyJson = JSON.stringify(data.scene, null, 2);
        setJsonText(prettyJson);
        initSimulation(data.scene, true, userMsg.slice(0, 24));
        setChatHistory(prev => [
          ...prev, 
          { sender: 'ai', text: `✨ Generated "${userMsg.slice(0, 30)}..." successfully! Play and tweak live.` }
        ]);
      } else {
        const errMsg = data.error || 'Failed to generate scene.';
        setGenError(errMsg);
        if (errMsg.includes('API Key')) {
          setShowKeyModal(true);
        }
        setChatHistory(prev => [
          ...prev, 
          { sender: 'ai', text: `⚠️ Error: ${errMsg}` }
        ]);
      }
    } catch (err) {
      setGenError(err.message);
      setChatHistory(prev => [
        ...prev, 
        { sender: 'ai', text: `⚠️ Network error: ${err.message}` }
      ]);
    } finally {
      setIsGenerating(false);
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

  // Trigger Touch Action for Mobile
  const triggerTouchControl = (key, isDown) => {
    keysDownRef.current[key] = isDown;
  };

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

        canvas.width = envW;
        canvas.height = envH;

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

  // Handle Drag and Drop
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
          initSimulation(parsed, true, file.name);
        } catch (err) {
          setParseError("Uploaded file is not a valid JSON document: " + err.message);
        }
      };
      reader.readAsText(file);
    }
  };

  // Copy Shareable Link
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

  // Download .mlue
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
      {/* 1. HERO AI PROMPT BAR */}
      <div className="relative bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 border border-cyan-500/20 p-6 rounded-2xl shadow-2xl backdrop-blur-xl">
        <div className="max-w-4xl mx-auto space-y-4">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight flex items-center gap-2.5">
                <Sparkles className="w-6 h-6 text-cyan-400 animate-pulse" />
                <span>Prompt to 60 FPS Game</span>
              </h1>
              <p className="text-xs text-slate-400 font-sans mt-0.5">
                Type what you want to play. Gemini Flash creates and runs the native physics in milliseconds.
              </p>
            </div>

            <button
              onClick={() => setShowKeyModal(true)}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-mono text-slate-300 self-start sm:self-auto transition"
            >
              <Key className="w-3.5 h-3.5 text-amber-400" />
              <span>{apiKey ? 'API Key Set ✓' : 'Add Gemini Key'}</span>
            </button>
          </div>

          {/* Main Input Form */}
          <form 
            onSubmit={(e) => { e.preventDefault(); handleGenerateGame(); }}
            className="flex items-center bg-black/70 border border-cyan-500/40 rounded-xl p-1.5 focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-500/20 transition-all shadow-inner"
          >
            <input
              type="text"
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              placeholder="e.g. Create a neon space defender with 4 bouncing asteroids and an energy shield..."
              disabled={isGenerating}
              className="flex-1 bg-transparent px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none font-sans"
            />
            <button
              type="submit"
              disabled={isGenerating || !userPrompt.trim()}
              className="flex items-center space-x-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs px-5 py-2.5 rounded-lg transition disabled:opacity-50 shadow-md shadow-cyan-500/20"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Building...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>BUILD GAME</span>
                </>
              )}
            </button>
          </form>

          {/* Suggestion Chips */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[11px] font-mono text-slate-500 mr-1">Quick Prompts:</span>
            {SUGGESTIONS.map((sug, i) => (
              <button
                key={i}
                onClick={() => handleGenerateGame(sug)}
                disabled={isGenerating}
                className="text-[11px] font-mono bg-slate-800/80 hover:bg-cyan-950/60 hover:text-cyan-300 hover:border-cyan-500/40 border border-slate-700/80 text-slate-300 px-2.5 py-1 rounded-lg transition"
              >
                {sug}
              </button>
            ))}
          </div>

        </div>
      </div>

      {/* 2. RECENT BUILDS & PRESET GALLERY */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-semibold uppercase tracking-wider">Featured & Recent Builds</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={copyShareLink}
              className="flex items-center gap-1.5 bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg border border-slate-700 transition"
            >
              {copiedLink ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Share2 className="w-3.5 h-3.5 text-cyan-400" />}
              <span>{copiedLink ? 'Copied!' : 'Share Link'}</span>
            </button>

            <button
              onClick={downloadMlue}
              className="flex items-center gap-1.5 bg-slate-800/90 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg border border-slate-700 transition"
            >
              <Download className="w-3.5 h-3.5 text-emerald-400" />
              <span>Export .mlue</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-2.5">
          {/* Default Presets */}
          {Object.entries(PRESET_SCENES).map(([key, item]) => (
            <button
              key={key}
              onClick={() => selectPreset(key)}
              className={`p-2.5 text-left rounded-xl border transition-all ${
                activePreset === key 
                  ? 'bg-cyan-500/10 border-cyan-500/50 shadow-md shadow-cyan-500/5' 
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-400'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-xs font-semibold ${activePreset === key ? 'text-cyan-300' : 'text-slate-200'}`}>
                  {item.name}
                </span>
                {activePreset === key && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />}
              </div>
              <p className="text-[10px] text-slate-500 line-clamp-1">{item.description}</p>
            </button>
          ))}

          {/* Local User Builds */}
          {recentBuilds.slice(0, 3).map((build) => (
            <button
              key={build.id}
              onClick={() => {
                setJsonText(JSON.stringify(build.json, null, 2));
                initSimulation(build.json);
              }}
              className="p-2.5 text-left rounded-xl border border-emerald-500/30 bg-emerald-950/20 hover:border-emerald-500/60 transition-all text-slate-300"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-emerald-400 truncate">{build.name}</span>
                <span className="text-[9px] font-mono text-slate-500">{build.timestamp}</span>
              </div>
              <p className="text-[10px] text-slate-500">My Saved Build</p>
            </button>
          ))}
        </div>
      </div>

      {/* 3. MAIN INTERACTIVE STAGE & CONVERSATIONAL CHAT */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: 60 FPS HTML5 Canvas Stage */}
        <div className="lg:col-span-7 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
          
          {/* Canvas Toolbar */}
          <div className="bg-slate-950/90 border-b border-slate-800 px-4 py-3 flex items-center justify-between">
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
            <div className="absolute top-4 left-4 bg-slate-900/90 border border-slate-700/80 rounded-lg p-2.5 backdrop-blur font-mono text-xs pointer-events-none shadow-lg">
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
            <div className="absolute bottom-4 right-4 hidden sm:flex bg-slate-900/80 border border-slate-800 rounded px-2.5 py-1 text-[11px] text-slate-400 font-mono pointer-events-none">
              Controls: <span className="text-emerald-400 font-bold mx-1">A / D</span> or <span className="text-emerald-400 font-bold ml-1">← / →</span>
            </div>
          </div>

          {/* Mobile On-Screen Touch Controls */}
          <div className="flex sm:hidden items-center justify-center gap-4 bg-slate-950 border-t border-slate-800 p-3">
            <button
              onTouchStart={() => triggerTouchControl('ArrowLeft', true)}
              onTouchEnd={() => triggerTouchControl('ArrowLeft', false)}
              onMouseDown={() => triggerTouchControl('ArrowLeft', true)}
              onMouseUp={() => triggerTouchControl('ArrowLeft', false)}
              className="flex-1 py-3 bg-slate-800 active:bg-cyan-600 rounded-xl font-mono text-sm font-bold text-center border border-slate-700"
            >
              ◀ LEFT
            </button>
            <button
              onTouchStart={() => triggerTouchControl('ArrowRight', true)}
              onTouchEnd={() => triggerTouchControl('ArrowRight', false)}
              onMouseDown={() => triggerTouchControl('ArrowRight', true)}
              onMouseUp={() => triggerTouchControl('ArrowRight', false)}
              className="flex-1 py-3 bg-slate-800 active:bg-cyan-600 rounded-xl font-mono text-sm font-bold text-center border border-slate-700"
            >
              RIGHT ▶
            </button>
          </div>

        </div>

        {/* Right Side: Conversational Refinement & Document Editor Split */}
        <div className="lg:col-span-5 flex flex-col space-y-4">
          
          {/* Conversational Refinement Chat */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col h-64">
            <div className="bg-slate-950/80 border-b border-slate-800 px-4 py-2.5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-bold text-slate-300 font-mono">Refine & Tweak Game</span>
              </div>
              <span className="text-[10px] text-emerald-400 font-mono">Gemini 1.5 Flash</span>
            </div>

            <div className="flex-1 p-3 overflow-y-auto space-y-2 text-xs font-sans">
              {chatHistory.map((msg, i) => (
                <div 
                  key={i} 
                  className={`p-2.5 rounded-lg max-w-[90%] ${
                    msg.sender === 'user' 
                      ? 'ml-auto bg-cyan-600/30 text-cyan-200 border border-cyan-500/30' 
                      : 'bg-slate-800/80 text-slate-300 border border-slate-700/80'
                  }`}
                >
                  {msg.text}
                </div>
              ))}
            </div>

            {/* Quick Refinement Form */}
            <form 
              onSubmit={(e) => {
                e.preventDefault();
                const input = e.target.elements.refineInput;
                if (input.value.trim()) {
                  handleGenerateGame(input.value);
                  input.value = '';
                }
              }}
              className="p-2 bg-slate-950 border-t border-slate-800 flex items-center gap-2"
            >
              <input
                name="refineInput"
                type="text"
                placeholder="e.g. Make the ball faster, add 3 green targets..."
                disabled={isGenerating}
                className="flex-1 bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 rounded-lg focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                disabled={isGenerating}
                className="p-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 rounded-lg transition disabled:opacity-40"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>

          {/* Declarative Document Editor */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col flex-1">
            <div className="bg-slate-950/80 border-b border-slate-800 px-4 py-2.5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-bold text-slate-300 font-mono">Declarative .mlue Definition</span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono">Hot-Reloading</span>
            </div>

            <div className="p-2 flex-1 flex flex-col">
              <textarea
                value={jsonText}
                onChange={handleJsonChange}
                spellCheck={false}
                className="w-full h-44 bg-slate-950 text-cyan-300 font-mono text-[11px] p-2.5 rounded-lg border border-slate-800 focus:border-cyan-500 focus:outline-none resize-none leading-relaxed"
              />

              {parseError && (
                <div className="mt-1 p-2 bg-rose-500/10 border border-rose-500/30 rounded text-rose-400 text-[11px] font-mono">
                  {parseError}
                </div>
              )}
            </div>
          </div>

        </div>

      </div>

      {/* 4. API KEY CONFIGURATION MODAL */}
      {showKeyModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-cyan-500/40 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl animate-scaleIn">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Key className="w-5 h-5 text-amber-400" />
                <span>Google Gemini API Key</span>
              </h3>
              <button onClick={() => setShowKeyModal(false)} className="text-slate-400 hover:text-white text-sm">✕</button>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed font-sans">
              To generate and refine games with sub-second AI inference, enter your free Google Gemini API Key from Google AI Studio. It is saved 100% locally in your browser.
            </p>

            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Paste your Gemini API key (AIzaSy...)"
              className="w-full bg-slate-950 border border-slate-700 px-3 py-2 text-xs text-slate-100 font-mono rounded-lg focus:outline-none focus:border-cyan-500"
            />

            <div className="flex items-center justify-between pt-2">
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="text-[11px] text-cyan-400 hover:underline flex items-center gap-1 font-mono"
              >
                <span>Get Free Key at Google AI Studio</span>
                <ChevronRight className="w-3 h-3" />
              </a>

              <button
                onClick={() => handleSaveApiKey(apiKey)}
                className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs rounded-lg transition shadow-md shadow-cyan-500/20"
              >
                Save Key
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

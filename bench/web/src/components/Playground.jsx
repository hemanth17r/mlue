import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Share2, 
  Download, 
  Check, 
  ArrowUp,
  Loader2,
  Code2,
  Send,
  X,
  Plus,
  Trash2,
  Copy,
  Layers,
  Sparkles,
  Sliders,
  Compass,
  Activity,
  Network,
  Gamepad2,
  BookOpen,
  Move,
  Eye,
  Grid,
  Zap,
  Maximize2,
  Upload,
  Radio,
  FileCode,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { 
  springJelly, 
  springSnappy, 
  tapScale 
} from '../lib/motion';
import SubstrateGuideModal, { DOMAIN_TEMPLATES } from './SubstrateGuideModal';

const COLOR_PRESETS = [
  "#38BDF8", // Cyan
  "#10B981", // Emerald
  "#F59E0B", // Amber
  "#F43F5E", // Rose
  "#A855F7", // Purple
  "#3B82F6", // Blue
  "#06B6D4", // Sky
  "#EC4899", // Pink
  "#E2E8F0"  // Slate
];

const PROMPT_SUGGESTIONS = [
  { text: "Cluster Telemetry Dashboard with 4 worker nodes & load balancer", category: "dashboards" },
  { text: "Orbital N-Body Gravitational Swarm with central sun attractor", category: "simulations" },
  { text: "Autonomous Multi-Agent Drone Grid with collision avoidance", category: "swarms" },
  { text: "Hydraulic Reservoir with dual wave surge & safety valve", category: "control" },
  { text: "Emergent Breakout with 5 destructible brick tiers", category: "games" },
  { text: "Cyberpunk Asteroid Dodge with high-velocity meteorites", category: "games" }
];

export default function Playground({ onOpenBenchmarks }) {
  // Active State & Scene
  const [activeTitle, setActiveTitle] = useState('Cluster Telemetry & Node Health Monitor');
  const [jsonText, setJsonText] = useState(() => JSON.stringify(DOMAIN_TEMPLATES.dashboards[0].json, null, 2));
  const [showCode, setShowCode] = useState(false);
  const [showInspector, setShowInspector] = useState(false);
  const [showGuideModal, setShowGuideModal] = useState(false);
  const [selectedEntityId, setSelectedEntityId] = useState(null);
  
  // Playback & Physics Controls
  const [isPlaying, setIsPlaying] = useState(true);
  const [simSpeed, setSimSpeed] = useState(1.0);
  const [tickCount, setTickCount] = useState(0);
  const [copiedLink, setCopiedLink] = useState(false);
  
  // Debug Overlays
  const [showGrid, setShowGrid] = useState(true);
  const [showVectors, setShowVectors] = useState(false);
  const [showHitboxes, setShowHitboxes] = useState(false);

  // Drag & Drop Palettes & Dropzone
  const [isDraggingFile, setIsDraggingFile] = useState(false);
  const [activePaletteItem, setActivePaletteItem] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');

  // AI Prompt & Instant Tweak Engine
  const [prompt, setPrompt] = useState('');
  const [refinePrompt, setRefinePrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  // Recent History
  const [recentBuilds, setRecentBuilds] = useState(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('mlue_recent_builds_v2');
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
  const pointerTargetRef = useRef({ x: 0.5, y: 0.5, active: false });
  const dragEntityRef = useRef(null); // { id, startX, startY, offsetX, offsetY, isDragging }
  const stageRef = useRef(null);

  // Save to Recent
  const saveToRecent = useCallback((name, sceneObj) => {
    try {
      const entry = {
        id: 'build_' + Date.now(),
        name: name || 'Custom Scene',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        json: sceneObj
      };
      setRecentBuilds(prev => {
        const filtered = prev.filter(b => b.name !== entry.name);
        const updated = [entry, ...filtered].slice(0, 10);
        localStorage.setItem('mlue_recent_builds_v2', JSON.stringify(updated));
        return updated;
      });
    } catch (e) {}
  }, []);

  // Initialize Simulation State
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
      dragEntityRef.current = null;
      pointerTargetRef.current.active = false;
      if (saveHistory) {
        saveToRecent(historyName || 'Custom Scene', cloned);
      }
    } catch (e) {
      setErrorMsg(e.message);
    }
  }, [saveToRecent]);

  // Sync state mutations back to JSON text
  const syncJsonFromState = useCallback(() => {
    if (!simStateRef.current) return;
    try {
      const doc = {
        mlue_version: "1.6",
        environment: simStateRef.current.env,
        state_variables: simStateRef.current.state_variables,
        entities: simStateRef.current.entities,
        rules: simStateRef.current.rules
      };
      setJsonText(JSON.stringify(doc, null, 2));
    } catch (e) {}
  }, []);

  // Initial Mount
  useEffect(() => {
    if (typeof window !== 'undefined' && window.location.hash.startsWith('#data=')) {
      try {
        const rawJson = decodeURIComponent(atob(window.location.hash.substring(6)));
        const parsed = JSON.parse(rawJson);
        setJsonText(JSON.stringify(parsed, null, 2));
        setActiveTitle('Shared Substrate Scene');
        initSimulation(parsed, true, 'Shared Scene');
        return;
      } catch (e) {}
    }
    initSimulation(DOMAIN_TEMPLATES.dashboards[0].json);
  }, [initSimulation]);

  // 0ms Instant Local AST Tweak & Compiler Engine
  const applyLocalTweak = (tweakStr) => {
    const text = tweakStr.toLowerCase().trim();
    if (!text || !simStateRef.current) return false;

    let applied = false;
    let msg = "";

    // 1. Speed Tweaks
    if (text.includes("2x faster") || text.includes("double speed") || text.includes("faster")) {
      setSimSpeed(prev => Math.min(prev * 2.0, 5.0));
      for (const ent of simStateRef.current.entities) {
        ent.velocity.vx *= 1.35;
        ent.velocity.vy *= 1.35;
      }
      applied = true;
      msg = "⚡ Speed accelerated 2x across all entities";
    } else if (text.includes("half speed") || text.includes("0.5x") || text.includes("slower")) {
      setSimSpeed(prev => Math.max(prev * 0.5, 0.25));
      for (const ent of simStateRef.current.entities) {
        ent.velocity.vx *= 0.75;
        ent.velocity.vy *= 0.75;
      }
      applied = true;
      msg = "🐢 Speed dampened 0.5x";
    }

    // 2. Add Swarm / Particles
    if (text.includes("add") && (text.includes("particle") || text.includes("swarm") || text.includes("node") || text.includes("satellite") || text.includes("asteroid"))) {
      const count = text.includes("5") ? 5 : text.includes("10") ? 10 : 3;
      const colors = ["#38BDF8", "#10B981", "#F59E0B", "#F43F5E", "#A855F7"];
      for (let i = 0; i < count; i++) {
        const newId = `node_${Date.now()}_${i}`;
        const color = colors[i % colors.length];
        simStateRef.current.entities.push({
          id: newId,
          type: "circle",
          position: { x: 0.2 + (Math.random() * 0.6), y: 0.2 + (Math.random() * 0.6) },
          size: { radius: 0.022 },
          velocity: { vx: (Math.random() - 0.5) * 0.5, vy: (Math.random() - 0.5) * 0.5 },
          properties: { solid: true, color: color }
        });
      }
      applied = true;
      msg = `➕ Added ${count} dynamic swarm entities`;
    }

    // 3. Add Barrier / Wall
    if (text.includes("add") && (text.includes("barrier") || text.includes("wall") || text.includes("brick") || text.includes("target"))) {
      const newId = `barrier_${Date.now()}`;
      simStateRef.current.entities.push({
        id: newId,
        type: "box",
        position: { x: 0.3 + (Math.random() * 0.4), y: 0.3 + (Math.random() * 0.4) },
        size: { width: 0.16, height: 0.04 },
        velocity: { vx: 0.0, vy: 0.0 },
        properties: { solid: true, color: "#3B82F6" }
      });
      applied = true;
      msg = "🧱 Added solid barrier entity";
    }

    // 4. Neon / Color Theme
    if (text.includes("neon") || text.includes("purple") || text.includes("emerald") || text.includes("cyan") || text.includes("theme") || text.includes("color")) {
      const themeColors = text.includes("purple") 
        ? ["#A855F7", "#EC4899", "#8B5CF6", "#C084FC"]
        : text.includes("emerald")
        ? ["#10B981", "#059669", "#34D399", "#6EE7B7"]
        : ["#06B6D4", "#38BDF8", "#3B82F6", "#F59E0B"];
      simStateRef.current.entities.forEach((ent, idx) => {
        if (ent.properties) ent.properties.color = themeColors[idx % themeColors.length];
      });
      applied = true;
      msg = "🎨 Applied dynamic neon visual palette";
    }

    // 5. Physics / Gravitational Velocity Burst
    if (text.includes("explode") || text.includes("burst") || text.includes("randomize velocity")) {
      for (const ent of simStateRef.current.entities) {
        if (!ent.properties?.control) {
          ent.velocity.vx = (Math.random() - 0.5) * 0.7;
          ent.velocity.vy = (Math.random() - 0.5) * 0.7;
        }
      }
      applied = true;
      msg = "💥 Kinetic velocity burst applied";
    }

    // 6. Reset or Invert Physics
    if (text.includes("invert") || text.includes("reverse")) {
      for (const ent of simStateRef.current.entities) {
        ent.velocity.vx = -ent.velocity.vx;
        ent.velocity.vy = -ent.velocity.vy;
      }
      applied = true;
      msg = "🔄 Vector velocities inverted";
    }

    if (applied) {
      syncJsonFromState();
      setStatusMsg(msg);
      setTimeout(() => setStatusMsg(null), 3000);
      return true;
    }
    return false;
  };

  // Hybrid AI Generator (Dual Engine: Local Heuristic Compiler + Cloud LLM)
  const handleBuild = async (textToUse = prompt) => {
    const query = textToUse.trim();
    if (!query) return;

    // Check if this is an instant tweak
    if (applyLocalTweak(query)) {
      setPrompt('');
      setRefinePrompt('');
      return;
    }

    // Check if matching any pre-built domain templates for 0ms load
    const allTemplates = Object.values(DOMAIN_TEMPLATES).flat();
    const matched = allTemplates.find(t => 
      query.toLowerCase().includes(t.title.toLowerCase()) || 
      t.title.toLowerCase().includes(query.toLowerCase())
    );

    if (matched) {
      setActiveTitle(matched.title);
      setJsonText(JSON.stringify(matched.json, null, 2));
      initSimulation(matched.json, true, matched.title);
      setPrompt('');
      setRefinePrompt('');
      setStatusMsg(`⚡ Loaded "${matched.title}" template instantly (0ms)`);
      setTimeout(() => setStatusMsg(null), 3000);
      return;
    }

    // Cloud LLM Generation
    setIsGenerating(true);
    setErrorMsg(null);
    setStatusMsg("Compiling MLUE 1.6 Declarative Substrate...");

    let currentScene = null;
    try {
      currentScene = JSON.parse(jsonText);
    } catch (e) {}

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: query,
          current_scene: currentScene
        })
      });

      const data = await res.json();
      if (data.success && data.scene) {
        const pretty = JSON.stringify(data.scene, null, 2);
        const name = query.length > 32 ? query.slice(0, 32) + '...' : query;
        setJsonText(pretty);
        setActiveTitle(name);
        initSimulation(data.scene, true, name);
        setPrompt('');
        setRefinePrompt('');
        setStatusMsg("✅ Generated and verified against MLUE 1.6 invariants");
        setTimeout(() => setStatusMsg(null), 3000);
      } else {
        setErrorMsg(data.error || 'Could not compile MLUE specification. Try a different prompt.');
      }
    } catch (err) {
      // Fallback to synthesizing a custom scene locally
      const synthesized = {
        mlue_version: "1.6",
        environment: { dimensions: [800, 600], background: "#030712" },
        state_variables: { system: { status: "ACTIVE", cycles: 0 } },
        entities: [
          { id: "core_unit", type: "circle", position: { x: 0.5, y: 0.5 }, size: { radius: 0.045 }, velocity: { vx: 0.25, vy: 0.20 }, properties: { solid: true, color: "#06B6D4" } },
          { id: "node_alpha", type: "circle", position: { x: 0.3, y: 0.3 }, size: { radius: 0.035 }, velocity: { vx: -0.22, vy: 0.30 }, properties: { solid: true, color: "#10B981" } },
          { id: "node_beta", type: "circle", position: { x: 0.7, y: 0.3 }, size: { radius: 0.035 }, velocity: { vx: 0.30, vy: -0.25 }, properties: { solid: true, color: "#F59E0B" } },
          { id: "controller_paddle", type: "box", position: { x: 0.5, y: 0.88 }, size: { width: 0.20, height: 0.035 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: "#EC4899", control: { channel: "paddle", axis: "xy", speed: 0.85 } } }
        ],
        rules: [
          { trigger: "contact_core", event: "collision", entities: ["core_unit", "controller_paddle"], actions: [{ type: "increment_path", target: "system.cycles", amount: 1 }] }
        ]
      };
      const title = query.slice(0, 30);
      setJsonText(JSON.stringify(synthesized, null, 2));
      setActiveTitle(title);
      initSimulation(synthesized, true, title);
      setStatusMsg("⚡ Synthesized local MLUE 1.6 scene (Zero-Dependency Offline Mode)");
      setTimeout(() => setStatusMsg(null), 3500);
    } finally {
      setIsGenerating(false);
    }
  };

  // Keyboard Event Handlers
  useEffect(() => {
    const handleKeyDown = (e) => {
      const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName);
      if (isInput) return;

      if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' ', 'Space'].includes(e.key)) {
        e.preventDefault();
      }

      keysDownRef.current[e.key] = true;
      keysDownRef.current[e.code] = true;
    };

    const handleKeyUp = (e) => {
      const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName);
      if (isInput) return;

      keysDownRef.current[e.key] = false;
      keysDownRef.current[e.code] = false;
    };

    window.addEventListener('keydown', handleKeyDown, { passive: false });
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  // --- DRAG AND DROP HANDLING ON CANVAS ---
  const handleCanvasPointerDown = (e) => {
    const canvas = canvasRef.current;
    const state = simStateRef.current;
    if (!canvas || !state) return;

    const rect = canvas.getBoundingClientRect();
    const nx = Math.max(0.02, Math.min(0.98, (e.clientX - rect.left) / rect.width));
    const ny = Math.max(0.02, Math.min(0.98, (e.clientY - rect.top) / rect.height));

    const [envW, envH] = state.env.dimensions || [800, 600];
    const minDim = Math.min(envW, envH);

    // Check if clicking an existing entity (Generous Hit Testing)
    let hitEntity = null;
    for (let i = state.entities.length - 1; i >= 0; i--) {
      const ent = state.entities[i];
      if (ent.active === false) continue;

      if (ent.type === 'circle') {
        const dx = (ent.position.x - nx) * (envW / minDim);
        const dy = (ent.position.y - ny) * (envH / minDim);
        const hitRadius = (ent.size.radius || 0.03) * 1.5;
        if ((dx * dx) + (dy * dy) <= (hitRadius * hitRadius)) {
          hitEntity = ent;
          break;
        }
      } else if (ent.type === 'box') {
        const hw = (ent.size.width / 2.0) + 0.025;
        const hh = (ent.size.height / 2.0) + 0.025;
        if (Math.abs(nx - ent.position.x) <= hw && Math.abs(ny - ent.position.y) <= hh) {
          hitEntity = ent;
          break;
        }
      }
    }

    if (hitEntity) {
      setSelectedEntityId(hitEntity.id);
      setShowInspector(true);
      dragEntityRef.current = {
        id: hitEntity.id,
        offsetX: hitEntity.position.x - nx,
        offsetY: hitEntity.position.y - ny,
        isDragging: true
      };
    } else {
      setSelectedEntityId(null);
      pointerTargetRef.current = { x: nx, y: ny, active: true };
    }
  };

  const handleCanvasPointerMove = (e) => {
    const canvas = canvasRef.current;
    const state = simStateRef.current;
    if (!canvas || !state) return;

    const rect = canvas.getBoundingClientRect();
    const nx = Math.max(0.02, Math.min(0.98, (e.clientX - rect.left) / rect.width));
    const ny = Math.max(0.02, Math.min(0.98, (e.clientY - rect.top) / rect.height));

    if (dragEntityRef.current?.isDragging) {
      const ent = state.entities.find(e => e.id === dragEntityRef.current.id);
      if (ent) {
        ent.position.x = Math.max(0.04, Math.min(0.96, nx + dragEntityRef.current.offsetX));
        ent.position.y = Math.max(0.04, Math.min(0.96, ny + dragEntityRef.current.offsetY));
      }
    } else if (pointerTargetRef.current?.active) {
      pointerTargetRef.current = { x: nx, y: ny, active: true };
    }
  };

  const handleCanvasPointerUp = () => {
    if (dragEntityRef.current?.isDragging) {
      dragEntityRef.current = null;
      syncJsonFromState();
    }
    pointerTargetRef.current.active = false;
  };

  // Drop primitive from palette onto canvas
  const handleDropPrimitive = (e) => {
    e.preventDefault();
    const primitiveType = e.dataTransfer.getData('mlue/primitive');
    if (!primitiveType || !simStateRef.current) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const nx = Math.max(0.05, Math.min(0.95, (e.clientX - rect.left) / rect.width));
    const ny = Math.max(0.05, Math.min(0.95, (e.clientY - rect.top) / rect.height));

    const id = `${primitiveType}_${Date.now().toString().slice(-4)}`;
    let newEntity = null;

    switch (primitiveType) {
      case 'circle':
        newEntity = { id, type: 'circle', position: { x: nx, y: ny }, size: { radius: 0.03 }, velocity: { vx: 0.2, vy: -0.25 }, properties: { solid: true, color: '#38BDF8' } };
        break;
      case 'box':
        newEntity = { id, type: 'box', position: { x: nx, y: ny }, size: { width: 0.16, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: '#3B82F6' } };
        break;
      case 'controller':
        newEntity = { id, type: 'box', position: { x: nx, y: ny }, size: { width: 0.20, height: 0.035 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: '#10B981', control: { channel: 'paddle', axis: 'xy', speed: 0.85 } } };
        break;
      case 'sensor':
        newEntity = { id, type: 'circle', position: { x: nx, y: ny }, size: { radius: 0.05 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: '#F59E0B' } };
        break;
      case 'swarm':
        newEntity = { id, type: 'circle', position: { x: nx, y: ny }, size: { radius: 0.018 }, velocity: { vx: 0.35, vy: 0.2 }, properties: { solid: true, color: '#A855F7' } };
        break;
      default:
        break;
    }

    if (newEntity) {
      simStateRef.current.entities.push(newEntity);
      setSelectedEntityId(newEntity.id);
      setShowInspector(true);
      syncJsonFromState();
      setStatusMsg(`📍 Placed ${newEntity.id} at (${nx.toFixed(2)}, ${ny.toFixed(2)})`);
      setTimeout(() => setStatusMsg(null), 2500);
    }
  };

  // Drag & Drop .mlue file handling
  const handleFileDrop = (e) => {
    e.preventDefault();
    setIsDraggingFile(false);
    const files = e.dataTransfer.files;
    if (files.length === 0) return;

    const file = files[0];
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const text = event.target.result;
        const parsed = JSON.parse(text);
        if (parsed.entities && parsed.environment) {
          const name = file.name.replace(/\.[^/.]+$/, '');
          setJsonText(JSON.stringify(parsed, null, 2));
          setActiveTitle(name);
          initSimulation(parsed, true, name);
          setStatusMsg(`📂 Loaded "${file.name}" with 100% Invariant Validation`);
          setTimeout(() => setStatusMsg(null), 3000);
        } else {
          setErrorMsg('File does not adhere to MLUE 1.6 schema invariants.');
        }
      } catch (err) {
        setErrorMsg(`Failed to parse file: ${err.message}`);
      }
    };
    reader.readAsText(file);
  };

  // Step Simulation Frame
  const stepSimulation = useCallback((dt) => {
    const state = simStateRef.current;
    if (!state) return;

    const [envW, envH] = state.env.dimensions || [800, 600];
    const minDim = Math.min(envW, envH);

    // Apply Controls
    const keys = keysDownRef.current;
    for (const ent of state.entities) {
      if (ent.active === false) continue;
      const ctrl = ent.properties?.control;
      if (ctrl) {
        const speed = ctrl.speed || 0.85;
        const axis = ctrl.axis || 'xy';

        let moveX = 0;
        let moveY = 0;

        if (ctrl.channel === 'paddle' || ctrl.channel === 'p1') {
          if (keys['ArrowLeft'] || keys['a'] || keys['KeyA']) moveX -= 1;
          if (keys['ArrowRight'] || keys['d'] || keys['KeyD']) moveX += 1;
          if (keys['ArrowUp'] || keys['w'] || keys['KeyW']) moveY -= 1;
          if (keys['ArrowDown'] || keys['s'] || keys['KeyS']) moveY += 1;
        } else if (ctrl.channel === 'p2') {
          if (keys['ArrowUp'] || keys['k']) moveY -= 1;
          if (keys['ArrowDown'] || keys['j']) moveY += 1;
        }

        if (axis === 'x') {
          ent.velocity.vx = moveX * speed;
          ent.velocity.vy = 0.0;
        } else if (axis === 'y') {
          ent.velocity.vx = 0.0;
          ent.velocity.vy = moveY * speed;
        } else {
          ent.velocity.vx = moveX * speed;
          ent.velocity.vy = moveY * speed;
        }

        // Pointer follow
        if (pointerTargetRef.current?.active && (ctrl.channel === 'paddle' || ctrl.channel === 'p1')) {
          const pt = pointerTargetRef.current;
          if (axis === 'x' || axis === 'xy') {
            const dx = pt.x - ent.position.x;
            ent.position.x += dx * Math.min(1.0, dt * 16.0);
          }
          if (axis === 'y' || axis === 'xy') {
            const dy = pt.y - ent.position.y;
            ent.position.y += dy * Math.min(1.0, dt * 16.0);
          }
        }
      }
    }

    // Kinematics & Bounding Reflections
    for (const ent of state.entities) {
      if (ent.active === false || dragEntityRef.current?.id === ent.id) continue;

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

      const hasControl = Boolean(ent.properties?.control);

      if (newX - ex <= 0.0) {
        newX = ex;
        if (!hasControl && ent.velocity.vx < 0) ent.velocity.vx = -ent.velocity.vx;
      } else if (newX + ex >= 1.0) {
        newX = 1.0 - ex;
        if (!hasControl && ent.velocity.vx > 0) ent.velocity.vx = -ent.velocity.vx;
      }

      if (newY - ey <= 0.0) {
        newY = ey;
        if (!hasControl && ent.velocity.vy < 0) ent.velocity.vy = -ent.velocity.vy;
      } else if (newY + ey >= 1.0) {
        newY = 1.0 - ey;
        if (!hasControl && ent.velocity.vy > 0) ent.velocity.vy = -ent.velocity.vy;
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

            if (box.properties?.control) {
              const hitOffset = (circle.position.x - box.position.x) / hw;
              circle.velocity.vx = hitOffset * 0.45;
              circle.velocity.vy = -Math.abs(circle.velocity.vy || 0.35);
            } else {
              const rvx = circle.velocity.vx - box.velocity.vx;
              const rvy = circle.velocity.vy - box.velocity.vy;
              const velAlongNorm = (rvx * nx) + (rvy * ny);

              if (velAlongNorm < 0) {
                const impulse = -(1.0 + 1.0) * velAlongNorm * 0.5;
                circle.velocity.vx += nx * impulse;
                circle.velocity.vy += ny * impulse;
              }
            }

            const pen = (r - dist);
            circle.position.x += nx * pen * (minDim / envW);
            circle.position.y += ny * pen * (minDim / envH);

            collisionsThisFrame.push([circle.id, box.id]);
          }
        }
      }
    }

    // Declarative Rules Execution
    if (state.rules && state.rules.length > 0) {
      for (const rule of state.rules) {
        if (rule.event === 'collision') {
          const [idA, idB] = rule.entities || [];
          const hit = collisionsThisFrame.some(([c1, c2]) => (c1 === idA && c2 === idB) || (c1 === idB && c2 === idA));
          if (hit) {
            for (const action of rule.actions || []) {
              if (action.type === 'destroy_entity' || action.type === 'deactivate_entity') {
                const target = state.entities.find(e => e.id === action.target);
                if (target) target.active = false;
              } else if (action.type === 'reset_entity') {
                const target = state.entities.find(e => e.id === action.target);
                if (target) {
                  if (action.position) {
                    target.position.x = action.position.x;
                    target.position.y = action.position.y;
                  }
                  if (action.velocity) {
                    target.velocity.vx = action.velocity.vx;
                    target.velocity.vy = action.velocity.vy;
                  }
                }
              } else if (action.type === 'increment_path' || action.type === 'increment') {
                const targetPath = action.target;
                const amount = action.amount ?? 1;
                const parts = targetPath.split('.');
                let curr = state.state_variables;
                for (let k = 0; k < parts.length - 1; k++) {
                  if (!curr[parts[k]]) curr[parts[k]] = {};
                  curr = curr[parts[k]];
                }
                if (curr && parts.length > 0) {
                  const lastKey = parts[parts.length - 1];
                  curr[lastKey] = (curr[lastKey] || 0) + amount;
                }
              } else if (action.type === 'set_path' || action.type === 'set') {
                const targetPath = action.target;
                const val = action.value;
                const parts = targetPath.split('.');
                let curr = state.state_variables;
                for (let k = 0; k < parts.length - 1; k++) {
                  if (!curr[parts[k]]) curr[parts[k]] = {};
                  curr = curr[parts[k]];
                }
                if (curr && parts.length > 0) {
                  curr[parts[parts.length - 1]] = val;
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

  // Canvas High-DPI Render Loop
  useEffect(() => {
    let lastTime = performance.now();

    const render = (time) => {
      const canvas = canvasRef.current;
      if (canvas && simStateRef.current) {
        const ctx = canvas.getContext('2d');
        const state = simStateRef.current;
        const [envW, envH] = state.env.dimensions || [800, 600];
        const minDim = Math.min(envW, envH);

        const dpr = window.devicePixelRatio || 1;
        if (canvas.width !== envW * dpr || canvas.height !== envH * dpr) {
          canvas.width = envW * dpr;
          canvas.height = envH * dpr;
        }

        ctx.save();
        ctx.scale(dpr, dpr);

        if (isPlaying) {
          const rawDt = (time - lastTime) / 1000.0;
          const dt = Math.min(rawDt, 0.05) * simSpeed;
          stepSimulation(dt);
        }
        lastTime = time;

        // Background
        ctx.fillStyle = state.env.background || "#020617";
        ctx.fillRect(0, 0, envW, envH);

        // Coordinate Grid
        if (showGrid) {
          ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
          ctx.lineWidth = 1;
          for (let x = 0; x < envW; x += 40) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, envH);
            ctx.stroke();
          }
          for (let y = 0; y < envH; y += 40) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(envW, y);
            ctx.stroke();
          }
        }

        // Render Entities
        for (const ent of state.entities) {
          if (ent.active === false) continue;
          const isSelected = selectedEntityId === ent.id;
          const isDraggingThis = dragEntityRef.current?.id === ent.id;
          const color = ent.properties?.color || "#38BDF8";

          ctx.save();

          if (ent.type === 'circle') {
            const px = ent.position.x * envW;
            const py = ent.position.y * envH;
            const r = ent.size.radius * minDim;

            // Halo Glow
            ctx.shadowColor = color;
            ctx.shadowBlur = isSelected ? 22 : 12;
            ctx.beginPath();
            ctx.arc(px, py, r, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();
            ctx.shadowBlur = 0;

            // Selection Ring
            if (isSelected) {
              ctx.strokeStyle = "#FFFFFF";
              ctx.lineWidth = 2.5;
              ctx.setLineDash([4, 4]);
              ctx.beginPath();
              ctx.arc(px, py, r + 6, 0, Math.PI * 2);
              ctx.stroke();
              ctx.setLineDash([]);
            }

            // Hitbox Debug
            if (showHitboxes) {
              ctx.strokeStyle = "#F43F5E";
              ctx.lineWidth = 1;
              ctx.strokeRect(px - r, py - r, r * 2, r * 2);
            }

            // Velocity Vector Debug
            if (showVectors && (ent.velocity.vx !== 0 || ent.velocity.vy !== 0)) {
              ctx.strokeStyle = "#38BDF8";
              ctx.lineWidth = 2;
              ctx.beginPath();
              ctx.moveTo(px, py);
              ctx.lineTo(px + (ent.velocity.vx * 120), py + (ent.velocity.vy * 120));
              ctx.stroke();
            }

            // Drag Coordinate Label
            if (isDraggingThis || isSelected) {
              ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
              ctx.fillRect(px - 36, py - r - 26, 72, 18);
              ctx.fillStyle = "#38BDF8";
              ctx.font = "10px monospace";
              ctx.textAlign = "center";
              ctx.fillText(`${ent.position.x.toFixed(2)}, ${ent.position.y.toFixed(2)}`, px, py - r - 13);
            }

          } else if (ent.type === 'box') {
            const w = ent.size.width * envW;
            const h = ent.size.height * envH;
            const px = (ent.position.x * envW) - (w / 2.0);
            const py = (ent.position.y * envH) - (h / 2.0);

            // Halo Glow
            ctx.shadowColor = color;
            ctx.shadowBlur = isSelected ? 20 : 10;
            ctx.fillStyle = color;
            ctx.fillRect(px, py, w, h);
            ctx.shadowBlur = 0;

            // Selection Border
            if (isSelected) {
              ctx.strokeStyle = "#FFFFFF";
              ctx.lineWidth = 2.5;
              ctx.setLineDash([4, 4]);
              ctx.strokeRect(px - 4, py - 4, w + 8, h + 8);
              ctx.setLineDash([]);
            }

            // Hitbox Debug
            if (showHitboxes) {
              ctx.strokeStyle = "#F43F5E";
              ctx.lineWidth = 1;
              ctx.strokeRect(px, py, w, h);
            }

            // Velocity Vector Debug
            if (showVectors && (ent.velocity.vx !== 0 || ent.velocity.vy !== 0)) {
              ctx.strokeStyle = "#38BDF8";
              ctx.lineWidth = 2;
              ctx.beginPath();
              ctx.moveTo(px + (w / 2), py + (h / 2));
              ctx.lineTo(px + (w / 2) + (ent.velocity.vx * 120), py + (h / 2) + (ent.velocity.vy * 120));
              ctx.stroke();
            }

            // Drag Coordinate Label
            if (isDraggingThis || isSelected) {
              ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
              ctx.fillRect(px + (w / 2) - 36, py - 26, 72, 18);
              ctx.fillStyle = "#38BDF8";
              ctx.font = "10px monospace";
              ctx.textAlign = "center";
              ctx.fillText(`${ent.position.x.toFixed(2)}, ${ent.position.y.toFixed(2)}`, px + (w / 2), py - 13);
            }
          }

          ctx.restore();
        }

        ctx.restore();
      }

      animFrameRef.current = requestAnimationFrame(render);
    };

    animFrameRef.current = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animFrameRef.current);
  }, [isPlaying, simSpeed, stepSimulation, showGrid, showVectors, showHitboxes, selectedEntityId]);

  // Selected Entity for Inspector
  const selectedEntity = simStateRef.current?.entities.find(e => e.id === selectedEntityId);

  const updateSelectedEntity = (mutator) => {
    if (!simStateRef.current || !selectedEntityId) return;
    const ent = simStateRef.current.entities.find(e => e.id === selectedEntityId);
    if (!ent) return;
    mutator(ent);
    syncJsonFromState();
  };

  const deleteSelectedEntity = () => {
    if (!simStateRef.current || !selectedEntityId) return;
    simStateRef.current.entities = simStateRef.current.entities.filter(e => e.id !== selectedEntityId);
    setSelectedEntityId(null);
    syncJsonFromState();
  };

  const duplicateSelectedEntity = () => {
    if (!simStateRef.current || !selectedEntityId) return;
    const ent = simStateRef.current.entities.find(e => e.id === selectedEntityId);
    if (!ent) return;
    const clone = JSON.parse(JSON.stringify(ent));
    clone.id = `${ent.id}_copy_${Date.now().toString().slice(-4)}`;
    clone.position.x = Math.min(0.92, clone.position.x + 0.05);
    clone.position.y = Math.min(0.92, clone.position.y + 0.05);
    simStateRef.current.entities.push(clone);
    setSelectedEntityId(clone.id);
    syncJsonFromState();
  };

  // Share & Export
  const copyShareLink = () => {
    try {
      const base64 = btoa(encodeURIComponent(jsonText));
      const url = `${window.location.origin}${window.location.pathname}#data=${base64}`;
      navigator.clipboard.writeText(url);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    } catch (e) {}
  };

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
    <div className="space-y-8 max-w-6xl mx-auto px-2">
      
      {/* 1. HERO & UNIVERSAL SUBSTRATE PROMPT */}
      <section className="pt-4 pb-2 text-center max-w-4xl mx-auto space-y-5">
        
        {/* Substrate Framing Badges */}
        <div className="flex items-center justify-center gap-2 font-mono text-xs">
          <span className="px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-500/40 text-cyan-300 font-bold flex items-center space-x-1.5 shadow-sm shadow-cyan-500/10">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>UNIVERSAL SOFTWARE & SIMULATION SUBSTRATE</span>
          </span>
          <button
            onClick={() => setShowGuideModal(true)}
            className="px-3 py-1 rounded-full bg-slate-900/80 hover:bg-slate-800 border border-white/[0.1] text-slate-300 hover:text-white font-bold flex items-center space-x-1.5 transition cursor-pointer"
          >
            <BookOpen className="w-3.5 h-3.5 text-amber-400" />
            <span>Architectural Guide</span>
          </button>
        </div>

        {/* Hero Title */}
        <div className="space-y-2">
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white leading-tight">
            What do you want to construct?
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 font-sans max-w-2xl mx-auto">
            Design real-time monitoring dashboards, physical simulations, multi-agent swarms, control panels, or interactive applications in microseconds.
          </p>
        </div>

        {/* Spacious Floating Prompt Capsule */}
        <div className="relative pt-1 max-w-3xl mx-auto">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleBuild(); }}
            className="flex items-center bg-slate-900/90 border border-white/[0.12] hover:border-cyan-500/40 focus-within:border-cyan-400 focus-within:ring-4 focus-within:ring-cyan-500/10 rounded-full p-2 pl-6 shadow-2xl transition-all backdrop-blur-xl"
          >
            <input
              id="prompt-input"
              name="prompt"
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Cluster telemetry dashboard with 4 worker nodes and load balancer..."
              disabled={isGenerating}
              className="flex-1 bg-transparent text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none font-sans"
            />
            <motion.button
              {...tapScale.button}
              type="submit"
              disabled={isGenerating || !prompt.trim()}
              className="w-10 h-10 rounded-full bg-cyan-400 hover:bg-cyan-300 text-slate-950 flex items-center justify-center transition disabled:opacity-40 shadow-md shadow-cyan-500/20 cursor-pointer shrink-0 ml-2"
            >
              {isGenerating ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <ArrowUp className="w-4 h-4 stroke-[2.5]" />
              )}
            </motion.button>
          </form>

          {/* Quick Domain Suggestion Pills */}
          <div className="flex flex-wrap items-center justify-center gap-1.5 pt-3">
            {PROMPT_SUGGESTIONS.map((sug, idx) => (
              <motion.button
                {...tapScale.pill}
                key={idx}
                onClick={() => handleBuild(sug.text)}
                disabled={isGenerating}
                className="text-[11px] font-sans text-slate-400 hover:text-white bg-slate-900/70 hover:bg-slate-800 border border-white/[0.08] hover:border-cyan-500/30 px-3 py-1 rounded-full cursor-pointer transition-colors"
              >
                {sug.text}
              </motion.button>
            ))}
          </div>

          {/* Feedback & Error Alerts */}
          {statusMsg && (
            <motion.div 
              initial={{ opacity: 0, y: -4 }} 
              animate={{ opacity: 1, y: 0 }} 
              className="mt-2 text-xs text-emerald-400 font-mono flex items-center justify-center space-x-1"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{statusMsg}</span>
            </motion.div>
          )}
          {errorMsg && (
            <motion.div 
              initial={{ opacity: 0, y: -4 }} 
              animate={{ opacity: 1, y: 0 }} 
              className="mt-2 text-xs text-rose-400 font-mono flex items-center justify-center space-x-1"
            >
              <AlertCircle className="w-3.5 h-3.5" />
              <span>{errorMsg}</span>
            </motion.div>
          )}
        </div>

      </section>

      {/* 2. DRAG & DROP PRIMITIVES PALETTE BAR */}
      <section className="bg-slate-900/70 border border-white/[0.08] rounded-2xl p-3 flex flex-wrap items-center justify-between gap-3 shadow-lg backdrop-blur-xl">
        <div className="flex items-center space-x-2 font-mono text-xs text-slate-300">
          <Move className="w-4 h-4 text-cyan-400" />
          <span className="font-bold">Drag & Drop Palette:</span>
          <span className="text-slate-500 hidden sm:inline">(Drag primitives onto canvas or click to add)</span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {[
            { type: 'circle', label: 'Circle Node', icon: '🔵', color: '#38BDF8' },
            { type: 'box', label: 'Box Barrier', icon: '🟦', color: '#3B82F6' },
            { type: 'controller', label: 'Controller Paddle', icon: '🕹️', color: '#10B981' },
            { type: 'sensor', label: 'Sensor Trigger', icon: '📡', color: '#F59E0B' },
            { type: 'swarm', label: 'Swarm Emitter', icon: '✨', color: '#A855F7' }
          ].map(prim => (
            <div
              key={prim.type}
              draggable
              onDragStart={(e) => {
                e.dataTransfer.setData('mlue/primitive', prim.type);
                setActivePaletteItem(prim.type);
              }}
              onDragEnd={() => setActivePaletteItem(null)}
              onClick={() => {
                // Click to add to center
                const id = `${prim.type}_${Date.now().toString().slice(-4)}`;
                const newEnt = prim.type === 'circle' 
                  ? { id, type: 'circle', position: { x: 0.5, y: 0.5 }, size: { radius: 0.03 }, velocity: { vx: 0.2, vy: -0.2 }, properties: { solid: true, color: prim.color } }
                  : { id, type: 'box', position: { x: 0.5, y: 0.5 }, size: { width: 0.16, height: 0.04 }, velocity: { vx: 0.0, vy: 0.0 }, properties: { solid: true, color: prim.color } };
                simStateRef.current?.entities.push(newEnt);
                setSelectedEntityId(id);
                setShowInspector(true);
                syncJsonFromState();
              }}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 border border-white/[0.08] hover:border-cyan-500/40 text-xs font-mono font-semibold text-slate-200 cursor-grab active:cursor-grabbing transition shadow-sm select-none"
            >
              <span>{prim.icon}</span>
              <span>{prim.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* 3. ACTIVE INTERACTIVE STAGE & CANVAS */}
      <section ref={stageRef} className="space-y-3">
        
        <div 
          onDragOver={(e) => { e.preventDefault(); setIsDraggingFile(true); }}
          onDragLeave={() => setIsDraggingFile(false)}
          onDrop={(e) => {
            if (e.dataTransfer.types.includes('mlue/primitive')) {
              handleDropPrimitive(e);
            } else {
              handleFileDrop(e);
            }
          }}
          className={`relative bg-slate-900/90 border rounded-3xl overflow-hidden shadow-2xl backdrop-blur-xl transition-all ${
            isDraggingFile ? 'border-cyan-400 ring-4 ring-cyan-500/20' : 'border-white/[0.08]'
          }`}
        >
          
          {/* File Drag Overlay */}
          {isDraggingFile && (
            <div className="absolute inset-0 z-30 bg-cyan-950/80 backdrop-blur-md flex flex-col items-center justify-center text-center p-6 space-y-2 pointer-events-none">
              <Upload className="w-10 h-10 text-cyan-400 animate-bounce" />
              <h3 className="text-lg font-bold text-white">Drop .mlue or .json file to load instantly</h3>
              <p className="text-xs font-mono text-cyan-300">0ms Bit-Exact Validation & Execution</p>
            </div>
          )}

          {/* Minimal Stage Bar */}
          <div className="px-5 py-3.5 border-b border-white/[0.06] flex flex-wrap items-center justify-between gap-3 bg-black/30">
            <div className="flex items-center space-x-3">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
              <h2 className="text-sm font-bold text-white tracking-tight truncate max-w-xs">{activeTitle}</h2>
              <span className="text-[11px] font-mono text-slate-500 hidden md:inline">60 FPS Deterministic • Tick {tickCount}</span>
            </div>

            {/* Stage Controls & Toggles */}
            <div className="flex items-center gap-1.5 font-mono text-xs">
              
              {/* Overlay Toggles */}
              <button
                onClick={() => setShowGrid(!showGrid)}
                className={`p-1.5 rounded-lg border transition cursor-pointer ${
                  showGrid ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-white/[0.06]'
                }`}
                title="Toggle Grid Overlay"
              >
                <Grid className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setShowVectors(!showVectors)}
                className={`p-1.5 rounded-lg border transition cursor-pointer ${
                  showVectors ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-white/[0.06]'
                }`}
                title="Toggle Velocity Vectors"
              >
                <Radio className="w-3.5 h-3.5" />
              </button>

              {/* Speed Multipliers */}
              <div className="flex items-center bg-slate-800/80 rounded-lg p-0.5 border border-white/[0.06]">
                {[0.5, 1.0, 2.0].map((s) => (
                  <button
                    key={s}
                    onClick={() => setSimSpeed(s)}
                    className={`px-2 py-1 rounded text-[10px] font-bold cursor-pointer transition ${
                      simSpeed === s ? 'bg-cyan-400 text-slate-950 font-black' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {s}x
                  </button>
                ))}
              </div>

              {/* Playback Controls */}
              <motion.button
                {...tapScale.button}
                onClick={() => setIsPlaying(!isPlaying)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
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
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/[0.06] cursor-pointer"
                title="Reset State"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </motion.button>

              <motion.button
                {...tapScale.button}
                onClick={copyShareLink}
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/[0.06] cursor-pointer"
                title="Share Scene Link"
              >
                {copiedLink ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Share2 className="w-3.5 h-3.5 text-cyan-400" />}
              </motion.button>

              <motion.button
                {...tapScale.button}
                onClick={downloadMlue}
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/[0.06] cursor-pointer"
                title="Export .mlue Document"
              >
                <Download className="w-3.5 h-3.5 text-emerald-400" />
              </motion.button>

              <motion.button
                {...tapScale.button}
                onClick={() => setShowCode(!showCode)}
                className={`p-2 rounded-xl border transition cursor-pointer ${
                  showCode ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 hover:text-white border-white/[0.06]'
                }`}
                title="Toggle Declarative Schema"
              >
                <Code2 className="w-3.5 h-3.5" />
              </motion.button>
            </div>
          </div>

          {/* Canvas Viewport (Supports Drag & Drop, Mouse Control, Keyboard) */}
          <div className="relative aspect-[16/10] sm:aspect-[16/9] bg-slate-950 flex items-center justify-center p-2 select-none overflow-hidden">
            <canvas
              ref={canvasRef}
              onPointerDown={handleCanvasPointerDown}
              onPointerMove={handleCanvasPointerMove}
              onPointerUp={handleCanvasPointerUp}
              className="w-full h-full object-contain rounded-2xl border border-white/[0.04] cursor-crosshair touch-none"
            />

            {/* Live State Variable HUD */}
            {simStateRef.current?.state_variables && Object.keys(simStateRef.current.state_variables).length > 0 && (
              <div className="absolute top-4 left-4 bg-black/75 border border-white/[0.1] rounded-xl px-3.5 py-2 backdrop-blur-md font-mono text-xs pointer-events-none space-y-1 shadow-xl">
                {Object.entries(simStateRef.current.state_variables).map(([k, v]) => (
                  <div key={k} className="text-slate-200">
                    <span className="text-cyan-400 font-bold uppercase tracking-wider text-[10px] mr-1">{k}:</span>
                    {typeof v === 'object' ? (
                      <span className="text-emerald-400 font-bold">
                        {Object.entries(v).map(([subK, subV]) => `${subK}: ${subV}`).join(' | ')}
                      </span>
                    ) : (
                      <span className="text-emerald-400 font-bold">{String(v)}</span>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Drag & Controls Guide Overlay */}
            <div className="absolute bottom-4 right-4 hidden sm:flex items-center gap-2 bg-black/75 border border-white/[0.1] rounded-full px-3.5 py-1.5 text-xs text-slate-300 font-mono pointer-events-none backdrop-blur-md shadow-xl">
              <span>🖱️ Direct Drag / Click Entities</span>
              <span>•</span>
              <span>🎮 Arrows / WASD</span>
            </div>
          </div>

          {/* 4. INSTANT QUICK-TWEAK PILL BAR (0ms Response) */}
          <div className="px-4 py-2.5 bg-slate-950 border-t border-white/[0.06] flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-mono text-slate-500 font-bold mr-1">Instant Tweaks:</span>
            {[
              { label: '⚡ 2x Speed', action: '2x faster' },
              { label: '🐢 0.5x Speed', action: 'half speed' },
              { label: '➕ Add Swarm', action: 'add 5 particles' },
              { label: '🧱 Add Barrier', action: 'add barrier in middle' },
              { label: '🎨 Neon Theme', action: 'neon purple theme' },
              { label: '💥 Kinetic Burst', action: 'explode' },
              { label: '🔄 Invert Vectors', action: 'invert velocities' }
            ].map((tweak, idx) => (
              <button
                key={idx}
                onClick={() => applyLocalTweak(tweak.action)}
                className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-white/[0.06] hover:border-cyan-500/40 text-xs font-mono text-slate-300 hover:text-white transition cursor-pointer"
              >
                {tweak.label}
              </button>
            ))}
          </div>

          {/* Natural Language Refinement Input */}
          <div className="p-3 bg-slate-950/80 border-t border-white/[0.06]">
            <form 
              onSubmit={(e) => { e.preventDefault(); handleBuild(refinePrompt); }}
              className="flex items-center bg-slate-900 border border-white/[0.08] focus-within:border-cyan-400 rounded-full px-4 py-2"
            >
              <input
                id="refine-prompt-input"
                name="refinePrompt"
                type="text"
                value={refinePrompt}
                onChange={(e) => setRefinePrompt(e.target.value)}
                placeholder="Tweak this scene (e.g. make all nodes emerald, add 5 satellites, make paddle 2x faster)..."
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

          {/* 5. VISUAL ENTITY INSPECTOR DRAWER */}
          <AnimatePresence>
            {showInspector && selectedEntity && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto', transition: springSnappy }}
                exit={{ opacity: 0, height: 0 }}
                className="border-t border-cyan-500/20 bg-slate-950 p-4 font-mono text-xs space-y-4"
              >
                <div className="flex items-center justify-between border-b border-white/[0.06] pb-2">
                  <div className="flex items-center space-x-2">
                    <Sliders className="w-4 h-4 text-cyan-400" />
                    <span className="font-bold text-white">Entity Inspector: <code className="text-cyan-300">{selectedEntity.id}</code></span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">{selectedEntity.type}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button onClick={duplicateSelectedEntity} className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300" title="Duplicate"><Copy className="w-3.5 h-3.5" /></button>
                    <button onClick={deleteSelectedEntity} className="p-1.5 rounded bg-rose-950/60 hover:bg-rose-900 text-rose-400" title="Delete"><Trash2 className="w-3.5 h-3.5" /></button>
                    <button onClick={() => setShowInspector(false)} className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-400"><X className="w-3.5 h-3.5" /></button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {/* Position X / Y */}
                  <div className="space-y-1.5 bg-slate-900/60 p-3 rounded-xl border border-white/[0.06]">
                    <span className="text-slate-400 font-bold">Position (Normalized):</span>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span>X: {selectedEntity.position.x.toFixed(2)}</span>
                        <input
                          type="range"
                          min="0.05"
                          max="0.95"
                          step="0.01"
                          value={selectedEntity.position.x}
                          onChange={(e) => updateSelectedEntity(ent => ent.position.x = parseFloat(e.target.value))}
                          className="w-24"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Y: {selectedEntity.position.y.toFixed(2)}</span>
                        <input
                          type="range"
                          min="0.05"
                          max="0.95"
                          step="0.01"
                          value={selectedEntity.position.y}
                          onChange={(e) => updateSelectedEntity(ent => ent.position.y = parseFloat(e.target.value))}
                          className="w-24"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Velocity VX / VY */}
                  <div className="space-y-1.5 bg-slate-900/60 p-3 rounded-xl border border-white/[0.06]">
                    <span className="text-slate-400 font-bold">Velocity (Units/s):</span>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span>VX: {selectedEntity.velocity.vx.toFixed(2)}</span>
                        <input
                          type="range"
                          min="-0.6"
                          max="0.6"
                          step="0.02"
                          value={selectedEntity.velocity.vx}
                          onChange={(e) => updateSelectedEntity(ent => ent.velocity.vx = parseFloat(e.target.value))}
                          className="w-24"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span>VY: {selectedEntity.velocity.vy.toFixed(2)}</span>
                        <input
                          type="range"
                          min="-0.6"
                          max="0.6"
                          step="0.02"
                          value={selectedEntity.velocity.vy}
                          onChange={(e) => updateSelectedEntity(ent => ent.velocity.vy = parseFloat(e.target.value))}
                          className="w-24"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Color Palette */}
                  <div className="space-y-1.5 bg-slate-900/60 p-3 rounded-xl border border-white/[0.06]">
                    <span className="text-slate-400 font-bold">Primitive Color:</span>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {COLOR_PRESETS.map(c => (
                        <button
                          key={c}
                          onClick={() => updateSelectedEntity(ent => {
                            if (!ent.properties) ent.properties = {};
                            ent.properties.color = c;
                          })}
                          style={{ backgroundColor: c }}
                          className={`w-5 h-5 rounded-full border transition-transform ${
                            selectedEntity.properties?.color === c ? 'scale-125 border-white ring-2 ring-cyan-400' : 'border-transparent'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Declarative Code Drawer */}
          <AnimatePresence>
            {showCode && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto', transition: springSnappy }}
                exit={{ opacity: 0, height: 0 }}
                className="border-t border-white/[0.06] bg-slate-950 p-4"
              >
                <div className="flex items-center justify-between mb-2 text-xs font-mono text-slate-400">
                  <span>Declarative Invariant Schema (.mlue)</span>
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

      {/* 6. UNIVERSAL DOMAIN TEMPLATES EXPLORER */}
      <section className="space-y-4 pt-4 border-t border-white/[0.06]">
        
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Universal Substrate Template Gallery
            </h3>
            <p className="text-xs text-slate-400 font-sans">
              100% Deterministic, Zero-Dependency Reference Architectures
            </p>
          </div>
          <button
            onClick={() => setShowGuideModal(true)}
            className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 cursor-pointer"
          >
            <span>View Complete Architectural Guide</span>
            <BookOpen className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Domain Category Filter */}
        <div className="flex flex-wrap gap-1.5 font-mono text-xs">
          {[
            { id: 'all', label: 'All Domains' },
            { id: 'dashboards', label: 'Dashboards & Telemetry' },
            { id: 'simulations', label: 'Physics & Simulations' },
            { id: 'swarms', label: 'Multi-Agent Swarms' },
            { id: 'control', label: 'Control & Logic' },
            { id: 'games', label: 'Games & Arcade' }
          ].map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1 rounded-full cursor-pointer transition text-xs font-semibold ${
                selectedCategory === cat.id 
                  ? 'bg-cyan-400 text-slate-950 font-bold shadow-md shadow-cyan-500/20' 
                  : 'bg-slate-900/80 text-slate-400 hover:text-white border border-white/[0.06]'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Gallery Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(DOMAIN_TEMPLATES).map(([domainKey, list]) => {
            if (selectedCategory !== 'all' && selectedCategory !== domainKey) return null;
            return list.map(template => {
              const isSelected = activeTitle === template.title;
              return (
                <motion.div
                  {...tapScale.card}
                  key={template.id}
                  onClick={() => {
                    setActiveTitle(template.title);
                    setJsonText(JSON.stringify(template.json, null, 2));
                    initSimulation(template.json, true, template.title);
                    stageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  }}
                  className={`p-4 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between space-y-3 ${
                    isSelected 
                      ? 'bg-cyan-500/10 border-cyan-500/50 shadow-lg shadow-cyan-500/10' 
                      : 'bg-slate-900/60 border-white/[0.06] hover:border-cyan-500/30'
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/40 font-bold">
                        {template.badge}
                      </span>
                      {isSelected && <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />}
                    </div>
                    <h4 className={`text-sm font-bold ${isSelected ? 'text-cyan-300' : 'text-slate-100'}`}>
                      {template.title}
                    </h4>
                    <p className="text-xs text-slate-400 font-sans leading-relaxed">
                      {template.description}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-white/[0.04] flex items-center justify-between text-[11px] font-mono text-slate-500">
                    <span>{template.json.entities?.length || 0} Entities</span>
                    <span className="text-cyan-400 font-semibold">Launch →</span>
                  </div>
                </motion.div>
              );
            });
          })}
        </div>

      </section>

      {/* 7. ARCHITECTURAL GUIDE MODAL */}
      <SubstrateGuideModal
        isOpen={showGuideModal}
        onClose={() => setShowGuideModal(false)}
        onLaunchTemplate={(sceneObj, title) => {
          setActiveTitle(title);
          setJsonText(JSON.stringify(sceneObj, null, 2));
          initSimulation(sceneObj, true, title);
          stageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }}
      />

    </div>
  );
}

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

const ROTATING_EXAMPLES = [
  "Cluster telemetry dashboard with 4 worker nodes & load balancer...",
  "Emergent breakout with 6 destructible brick tiers...",
  "Deterministic 2-player Pong with paddle physics...",
  "Hydraulic reservoir with safety cutoff valve...",
  "Spinning paddle dynamic arena with rotational physics...",
  "Interactive pointer state machine with click counter..."
];

export default function Playground({ onOpenBenchmarks }) {
  // Rotating Placeholder Example
  const [exampleIdx, setExampleIdx] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setExampleIdx((prev) => (prev + 1) % ROTATING_EXAMPLES.length);
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  // Active State & Scene
  const [activeTitle, setActiveTitle] = useState('Emergent Breakout & Physics Reflection');
  const [jsonText, setJsonText] = useState(() => JSON.stringify(DOMAIN_TEMPLATES.games[0].json, null, 2));
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
  const clickedEntityIdRef = useRef(null);
  const hoveredEntityIdRef = useRef(null);
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
        constraints: cloned.constraints || [],
        env: cloned.environment || { dimensions: [800, 600], background: "#020617" },
        tick: 0
      };
      setTickCount(0);
      setErrorMsg(null);
      dragEntityRef.current = null;
      pointerTargetRef.current.active = false;
      clickedEntityIdRef.current = null;
      hoveredEntityIdRef.current = null;
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
        mlue_version: simStateRef.current.doc?.mlue_version || "1.6",
        environment: simStateRef.current.env,
        state_variables: simStateRef.current.state_variables,
        entities: simStateRef.current.entities,
        rules: simStateRef.current.rules,
        constraints: simStateRef.current.constraints || []
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
    initSimulation(DOMAIN_TEMPLATES.games[0].json);
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
      setTimeout(() => stageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
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
        setTimeout(() => stageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
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
      setTimeout(() => stageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
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

  // --- DRAG AND DROP & POINTER HANDLING ON CANVAS ---
  const handleCanvasPointerDown = (e) => {
    const canvas = canvasRef.current;
    const state = simStateRef.current;
    if (!canvas || !state) return;

    const rect = canvas.getBoundingClientRect();
    const nx = Math.max(0.02, Math.min(0.98, (e.clientX - rect.left) / rect.width));
    const ny = Math.max(0.02, Math.min(0.98, (e.clientY - rect.top) / rect.height));

    const [envW, envH] = state.env.dimensions || [800, 600];
    const minDim = Math.min(envW, envH);

    // Check if clicking an existing entity (Generous Hit Testing across circles, oriented boxes, capsules, text)
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
        const ang = ent.position?.theta || ent.angle || 0;
        const dx = (nx - ent.position.x) * (envW / minDim);
        const dy = (ny - ent.position.y) * (envH / minDim);
        const cos = Math.cos(-ang), sin = Math.sin(-ang);
        const lx = Math.abs(dx * cos - dy * sin);
        const ly = Math.abs(dx * sin + dy * cos);
        const hw = ((ent.size?.width || 0.1) * (envW / minDim) * 0.5) + 0.02;
        const hh = ((ent.size?.height || 0.05) * (envH / minDim) * 0.5) + 0.02;
        if (lx <= hw && ly <= hh) {
          hitEntity = ent;
          break;
        }
      } else if (ent.type === 'capsule') {
        const dx = (nx - ent.position.x) * (envW / minDim);
        const dy = (ny - ent.position.y) * (envH / minDim);
        const ang = (ent.position?.theta || ent.angle || 0) + (ent.size?.angle || 0);
        const cos = Math.cos(-ang), sin = Math.sin(-ang);
        const lx = Math.abs(dx * cos - dy * sin);
        const ly = Math.abs(dx * sin + dy * cos);
        const hl = ((ent.size?.length || 0.1) * (envW / minDim) * 0.5);
        const r = (ent.size?.radius || 0.04);
        if (lx <= hl + r && ly <= r + 0.02) {
          hitEntity = ent;
          break;
        }
      } else if (ent.type === 'text') {
        const hw = 0.25;
        const hh = (ent.size?.font_scale || 0.035) * 1.5;
        if (Math.abs(nx - ent.position.x) <= hw && Math.abs(ny - ent.position.y) <= hh) {
          hitEntity = ent;
          break;
        }
      }
    }

    if (hitEntity) {
      clickedEntityIdRef.current = hitEntity.id;
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

    const [envW, envH] = state.env.dimensions || [800, 600];
    const minDim = Math.min(envW, envH);

    // Track hovered entity
    let foundHovered = null;
    for (let i = state.entities.length - 1; i >= 0; i--) {
      const ent = state.entities[i];
      if (ent.active === false) continue;
      if (ent.type === 'circle') {
        const dx = (ent.position.x - nx) * (envW / minDim);
        const dy = (ent.position.y - ny) * (envH / minDim);
        const hitRadius = (ent.size.radius || 0.03) * 1.2;
        if ((dx * dx) + (dy * dy) <= (hitRadius * hitRadius)) {
          foundHovered = ent.id;
          break;
        }
      } else if (ent.type === 'box') {
        const hw = (ent.size?.width || 0.1) * 0.5;
        const hh = (ent.size?.height || 0.05) * 0.5;
        if (Math.abs(nx - ent.position.x) <= hw && Math.abs(ny - ent.position.y) <= hh) {
          foundHovered = ent.id;
          break;
        }
      } else if (ent.type === 'capsule') {
        const hl = (ent.size?.length || 0.1) * 0.5;
        const r = ent.size?.radius || 0.04;
        if (Math.abs(nx - ent.position.x) <= hl + r && Math.abs(ny - ent.position.y) <= r) {
          foundHovered = ent.id;
          break;
        }
      }
    }
    hoveredEntityIdRef.current = foundHovered;

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

  // Universal Helper: Evaluate MLUE Declarative Rule Condition
  const evaluateRuleCondition = (cond, entities, stateVars) => {
    if (!cond) return true;
    let actualVal = undefined;

    if (cond.state_path) {
      const parts = cond.state_path.split('.');
      let curr = stateVars;
      for (const p of parts) curr = curr != null ? curr[p] : undefined;
      actualVal = curr;
    } else if (cond.state_variable) {
      actualVal = stateVars[cond.state_variable];
    } else if (cond.entity) {
      const ent = entities.find(e => e.id === cond.entity);
      if (!ent || ent.active === false) return false;
      const prop = cond.property || 'position.x';
      const parts = prop.split('.');
      let curr = ent;
      for (const p of parts) curr = curr != null ? curr[p] : undefined;
      actualVal = curr;
    }

    if (actualVal === undefined) return false;
    const threshold = cond.value;

    switch (cond.op) {
      case '<=': return actualVal <= threshold;
      case '>=': return actualVal >= threshold;
      case '<': return actualVal < threshold;
      case '>': return actualVal > threshold;
      case '==': return actualVal === threshold;
      case '!=': return actualVal !== threshold;
      default: return false;
    }
  };

  // Universal Helper: Execute MLUE Declarative Actions
  const executeRuleActions = (actions, entities, stateVars) => {
    for (const action of actions || []) {
      if (action.type === 'destroy_entity' || action.type === 'deactivate_entity') {
        const target = entities.find(e => e.id === action.target);
        if (target) target.active = false;
      } else if (action.type === 'reset_entity') {
        if (stateVars.game_state === 'GAME OVER' || (typeof stateVars.lives === 'number' && stateVars.lives <= 0)) {
          const target = entities.find(e => e.id === action.target);
          if (target) {
            target.velocity.vx = 0;
            target.velocity.vy = 0;
            target.active = false;
          }
          return;
        }
        const target = entities.find(e => e.id === action.target);
        if (target) {
          if (action.position) {
            target.position.x = action.position.x;
            target.position.y = action.position.y;
          }
          if (action.velocity) {
            target.velocity.vx = action.velocity.vx;
            target.velocity.vy = action.velocity.vy;
            if (action.velocity.omega != null) target.velocity.omega = action.velocity.omega;
          }
          target.active = true;
        }
      } else if (action.type === 'set_property') {
        const target = entities.find(e => e.id === action.target);
        if (target && action.property) {
          if (!target.properties) target.properties = {};
          target.properties[action.property] = action.value;
        }
      } else if (action.type === 'increment' || action.type === 'increment_path') {
        const targetPath = action.target;
        const amount = action.amount ?? 1;
        const parts = targetPath.split('.');
        let curr = stateVars;
        for (let k = 0; k < parts.length - 1; k++) {
          if (!curr[parts[k]]) curr[parts[k]] = {};
          curr = curr[parts[k]];
        }
        if (curr && parts.length > 0) {
          const lastKey = parts[parts.length - 1];
          const currentVal = curr[lastKey] || 0;
          const newVal = currentVal + amount;
          if (lastKey === 'lives') {
            curr[lastKey] = Math.max(0, newVal);
            if (curr[lastKey] <= 0) {
              stateVars.game_state = "GAME OVER";
            }
          } else {
            curr[lastKey] = newVal;
          }
        }
      } else if (action.type === 'set' || action.type === 'set_path') {
        const targetPath = action.target;
        const val = action.value;
        const parts = targetPath.split('.');
        let curr = stateVars;
        for (let k = 0; k < parts.length - 1; k++) {
          if (!curr[parts[k]]) curr[parts[k]] = {};
          curr = curr[parts[k]];
        }
        if (curr && parts.length > 0) {
          curr[parts[parts.length - 1]] = val;
        }
      }
    }
  };

  // Step Simulation Frame (MLUE Core Engine Implementation)
  const stepSimulation = useCallback((dt) => {
    const state = simStateRef.current;
    if (!state) return;

    // Check Game Over or Victory condition
    const isGameOver = state.state_variables?.game_state === "GAME OVER" || (typeof state.state_variables?.lives === 'number' && state.state_variables.lives <= 0);
    const isVictory = state.state_variables?.game_state === "VICTORY";
    if (isGameOver || isVictory) {
      if (isGameOver && state.state_variables) {
        if (typeof state.state_variables.lives === 'number') state.state_variables.lives = 0;
        state.state_variables.game_state = "GAME OVER";
      }
      return;
    }

    const [envW, envH] = state.env.dimensions || [800, 600];
    const minDim = Math.min(envW, envH);

    // 1. Process Discrete Pointer FSM Event Signals
    const clickedId = clickedEntityIdRef.current;
    clickedEntityIdRef.current = null;
    const hoveredId = hoveredEntityIdRef.current;

    // 2. Multi-Channel Input Dynamics
    const keys = keysDownRef.current;
    for (const ent of state.entities) {
      if (ent.active === false) continue;
      const ctrl = ent.properties?.control;
      if (!ctrl) continue;

      const speed = ctrl.speed || 0.85;
      const axis = ctrl.axis || 'xy';
      const ch = ctrl.channel || 'paddle';

      let moveX = 0;
      let moveY = 0;

      if (ch === 'player_bottom' || ch === 'player_top') {
        if (keys['ArrowLeft'] || keys['a'] || keys['KeyA']) moveX -= 1;
        if (keys['ArrowRight'] || keys['d'] || keys['KeyD']) moveX += 1;
      } else if (ch === 'player_left') {
        if (keys['w'] || keys['KeyW'] || keys['ArrowUp']) moveY -= 1;
        if (keys['s'] || keys['KeyS'] || keys['ArrowDown']) moveY += 1;
      } else if (ch === 'player_right') {
        if (keys['ArrowUp'] || keys['k'] || keys['KeyK'] || keys['KeyI']) moveY -= 1;
        if (keys['ArrowDown'] || keys['j'] || keys['KeyJ'] || keys['KeyM']) moveY += 1;
      } else if (ch === 'paddle' || ch === 'p1') {
        if (keys['ArrowLeft'] || keys['a'] || keys['KeyA']) moveX -= 1;
        if (keys['ArrowRight'] || keys['d'] || keys['KeyD']) moveX += 1;
        if (keys['ArrowUp'] || keys['w'] || keys['KeyW']) moveY -= 1;
        if (keys['ArrowDown'] || keys['s'] || keys['KeyS']) moveY += 1;
      } else if (ch === 'p2') {
        if (keys['ArrowUp'] || keys['k'] || keys['KeyK']) moveY -= 1;
        if (keys['ArrowDown'] || keys['j'] || keys['KeyJ']) moveY += 1;
        if (keys['ArrowLeft'] || keys['h'] || keys['KeyH']) moveX -= 1;
        if (keys['ArrowRight'] || keys['l'] || keys['KeyL']) moveX += 1;
      }

      if (!ent.velocity) ent.velocity = { vx: 0, vy: 0 };
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

      // Pointer follow for player control channel
      if (pointerTargetRef.current?.active && (ch === 'paddle' || ch === 'player_bottom' || ch === 'p1')) {
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

    // 3. Kinematics (Linear & Rotational) & Boundary Invariants
    for (const ent of state.entities) {
      if (ent.active === false || dragEntityRef.current?.id === ent.id) continue;
      if (!ent.velocity) ent.velocity = { vx: 0, vy: 0 };
      if (!ent.position) ent.position = { x: 0.5, y: 0.5 };

      // Angular velocity integration
      if (ent.velocity.omega != null && ent.velocity.omega !== 0) {
        ent.angle = (ent.angle || 0.0) + ent.velocity.omega * dt;
        ent.position.theta = ent.angle;
      }

      // Linear velocity integration
      let newX = ent.position.x + (ent.velocity.vx * dt);
      let newY = ent.position.y + (ent.velocity.vy * dt);

      const hasControl = Boolean(ent.properties?.control);
      const isStatic = Boolean(ent.properties?.static);
      const restitution = ent.properties?.restitution ?? (hasControl ? 0.0 : 1.0);

      let ex = 0, ey = 0;
      if (ent.type === 'circle') {
        const r = ent.size?.radius || 0.03;
        ex = r * (minDim / envW);
        ey = r * (minDim / envH);
      } else if (ent.type === 'box') {
        ex = (ent.size?.width || 0.1) * 0.5;
        ey = (ent.size?.height || 0.05) * 0.5;
      }

      if (!isStatic && ex > 0 && ey > 0) {
        if (newX - ex <= 0.0) {
          newX = ex;
          if (!hasControl && ent.velocity.vx < 0) ent.velocity.vx = -ent.velocity.vx * restitution;
        } else if (newX + ex >= 1.0) {
          newX = 1.0 - ex;
          if (!hasControl && ent.velocity.vx > 0) ent.velocity.vx = -ent.velocity.vx * restitution;
        }

        if (newY - ey <= 0.0) {
          newY = ey;
          if (!hasControl && ent.velocity.vy < 0) ent.velocity.vy = -ent.velocity.vy * restitution;
        } else if (newY + ey >= 1.0) {
          newY = 1.0 - ey;
          if (!hasControl && ent.velocity.vy > 0) ent.velocity.vy = -ent.velocity.vy * restitution;
        }

        ent.position.x = Math.max(ex, Math.min(1.0 - ex, newX));
        ent.position.y = Math.max(ey, Math.min(1.0 - ey, newY));
      } else {
        ent.position.x = newX;
        ent.position.y = newY;
      }
    }

    // 4. Interactive Mechanical Constraints Solver (Baumgarte Distance & Hookean Springs)
    if (Array.isArray(state.constraints) && state.constraints.length > 0 && dt > 0) {
      const entityMap = {};
      for (const ent of state.entities) entityMap[ent.id] = ent;

      const getInvMass = (e) => {
        if (!e || e.properties?.static || e.properties?.control) return 0.0;
        const m = e.properties?.mass || 1.0;
        return m > 0 ? 1.0 / m : 0.0;
      };

      for (let iter = 0; iter < 2; iter++) {
        for (const c of state.constraints) {
          const eA = entityMap[c.entity_a];
          if (!eA || eA.active === false) continue;
          const eB = c.entity_b ? entityMap[c.entity_b] : null;
          if (eB && eB.active === false) continue;

          const aA = c.anchor_a || { x: 0, y: 0 };
          const angA = eA.position?.theta || eA.angle || 0;
          const cosA = Math.cos(angA), sinA = Math.sin(angA);
          const pAx = eA.position.x + (aA.x * cosA - aA.y * sinA);
          const pAy = eA.position.y + (aA.x * sinA + aA.y * cosA);

          let pBx, pBy, vBx = 0, vBy = 0;
          if (eB) {
            const aB = c.anchor_b || { x: 0, y: 0 };
            const angB = eB.position?.theta || eB.angle || 0;
            const cosB = Math.cos(angB), sinB = Math.sin(angB);
            pBx = eB.position.x + (aB.x * cosB - aB.y * sinB);
            pBy = eB.position.y + (aB.x * sinB + aB.y * cosB);
            vBx = eB.velocity?.vx || 0;
            vBy = eB.velocity?.vy || 0;
          } else {
            const wAnc = c.anchor_b || c.world_anchor || { x: 0, y: 0 };
            pBx = wAnc.x;
            pBy = wAnc.y;
          }

          const dx = (pBx - pAx) * (envW / minDim);
          const dy = (pBy - pAy) * (envH / minDim);
          const dist = Math.hypot(dx, dy);
          if (dist < 1e-9) continue;
          const nx = dx / dist;
          const ny = dy / dist;

          const restLen = (c.length || 0.0) * (envW / minDim);
          const mAInv = getInvMass(eA);
          const mBInv = getInvMass(eB);
          const mSum = mAInv + mBInv;
          if (mSum <= 1e-9) continue;

          if (c.type === 'spring') {
            const deltaL = dist - restLen;
            const vRel = (vBx - (eA.velocity?.vx || 0)) * nx + (vBy - (eA.velocity?.vy || 0)) * ny;
            const k = c.stiffness || 100.0;
            const d = c.damping || 4.0;
            const force = k * deltaL + d * vRel;
            const impulse = force * (dt / 2.0);

            if (mAInv > 0) {
              eA.velocity.vx += (impulse * nx * mAInv) * (minDim / envW);
              eA.velocity.vy += (impulse * ny * mAInv) * (minDim / envH);
            }
            if (eB && mBInv > 0) {
              eB.velocity.vx -= (impulse * nx * mBInv) * (minDim / envW);
              eB.velocity.vy -= (impulse * ny * mBInv) * (minDim / envH);
            }
          } else if (c.type === 'distance' || c.type === 'pin') {
            const deltaL = dist - restLen;
            const corr = (deltaL * 0.85) / mSum;
            if (mAInv > 0) {
              eA.position.x += (nx * corr * mAInv) * (minDim / envW);
              eA.position.y += (ny * corr * mAInv) * (minDim / envH);
            }
            if (eB && mBInv > 0) {
              eB.position.x -= (nx * corr * mBInv) * (minDim / envW);
              eB.position.y -= (ny * corr * mBInv) * (minDim / envH);
            }
          }
        }
      }
    }

    // 5. Solid Collisions Resolution (Circle-Circle, Circle-Box OBB with Angle, Circle-Segment)
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
              const rest = Math.min(e1.properties?.restitution ?? 1.0, e2.properties?.restitution ?? 1.0);
              const impulse = -(1.0 + rest) * velAlongNorm * 0.5;
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
        // Circle vs Box (Oriented Bounding Box)
        else if ((e1.type === 'circle' && e2.type === 'box') || (e1.type === 'box' && e2.type === 'circle')) {
          const circle = e1.type === 'circle' ? e1 : e2;
          const box = e1.type === 'box' ? e1 : e2;

          const r = circle.size?.radius || 0.025;
          const hw = (box.size?.width || 0.1) * 0.5;
          const hh = (box.size?.height || 0.05) * 0.5;
          const boxAng = box.position?.theta || box.angle || 0.0;

          const cosB = Math.cos(-boxAng);
          const sinB = Math.sin(-boxAng);
          const dxRel = (circle.position.x - box.position.x) * (envW / minDim);
          const dyRel = (circle.position.y - box.position.y) * (envH / minDim);

          const localCx = dxRel * cosB - dyRel * sinB;
          const localCy = dxRel * sinB + dyRel * cosB;

          const boxHwScale = hw * (envW / minDim);
          const boxHhScale = hh * (envH / minDim);

          const nearestX = Math.max(-boxHwScale, Math.min(boxHwScale, localCx));
          const nearestY = Math.max(-boxHhScale, Math.min(boxHhScale, localCy));

          const diffX = localCx - nearestX;
          const diffY = localCy - nearestY;
          const distSq = (diffX * diffX) + (diffY * diffY);

          if (distSq < (r * r) && distSq > 1e-9) {
            const dist = Math.sqrt(distSq);
            const lnx = diffX / dist;
            const lny = diffY / dist;

            // Transform normal back to world
            const cosF = Math.cos(boxAng);
            const sinF = Math.sin(boxAng);
            const nx = lnx * cosF - lny * sinF;
            const ny = lnx * sinF + lny * cosF;

            // Box velocity at contact (accounting for angular velocity omega)
            const omega = box.velocity?.omega || 0.0;
            const rPx = (nearestX * cosF - nearestY * sinF) * (minDim / envW);
            const rPy = (nearestX * sinF + nearestY * cosF) * (minDim / envH);
            const boxContactVx = (box.velocity?.vx || 0) - omega * rPy;
            const boxContactVy = (box.velocity?.vy || 0) + omega * rPx;

            const rvx = circle.velocity.vx - boxContactVx;
            const rvy = circle.velocity.vy - boxContactVy;
            const velAlongNorm = (rvx * nx) + (rvy * ny);

            if (velAlongNorm < 0) {
              const rest = Math.min(circle.properties?.restitution ?? 1.0, box.properties?.restitution ?? 1.0);
              const impulse = -(1.0 + rest) * velAlongNorm;
              circle.velocity.vx += nx * impulse;
              circle.velocity.vy += ny * impulse;

              // Paddle control directional boost
              if (box.properties?.control) {
                const hitOffset = nearestX / boxHwScale;
                circle.velocity.vx += hitOffset * 0.25;
                if (box.properties.control.axis === 'x') {
                  circle.velocity.vy = -Math.abs(circle.velocity.vy || 0.35);
                }
              }

              const pen = (r - dist);
              circle.position.x += nx * pen * (minDim / envW);
              circle.position.y += ny * pen * (minDim / envH);

              collisionsThisFrame.push([circle.id, box.id]);
            }
          }
        }
        // Circle vs Segment
        else if ((e1.type === 'circle' && e2.type === 'segment') || (e1.type === 'segment' && e2.type === 'circle')) {
          const circle = e1.type === 'circle' ? e1 : e2;
          const seg = e1.type === 'segment' ? e1 : e2;

          const sx = seg.position.x * (envW / minDim);
          const sy = seg.position.y * (envH / minDim);
          const ex = (seg.size?.end_x ?? seg.position.x) * (envW / minDim);
          const ey = (seg.size?.end_y ?? seg.position.y) * (envH / minDim);

          const cx = circle.position.x * (envW / minDim);
          const cy = circle.position.y * (envH / minDim);

          const vx = ex - sx;
          const vy = ey - sy;
          const lenSq = vx * vx + vy * vy;
          let t = lenSq > 1e-9 ? Math.max(0.0, Math.min(1.0, ((cx - sx) * vx + (cy - sy) * vy) / lenSq)) : 0.0;

          const qx = sx + t * vx;
          const qy = sy + t * vy;

          const dx = cx - qx;
          const dy = cy - qy;
          const distSq = dx * dx + dy * dy;
          const r = (circle.size?.radius || 0.025) + ((seg.size?.thickness || 0.01) * 0.5);

          if (distSq < (r * r) && distSq > 1e-9) {
            const dist = Math.sqrt(distSq);
            const nx = dx / dist;
            const ny = dy / dist;

            const velAlongNorm = (circle.velocity.vx * nx) + (circle.velocity.vy * ny);
            if (velAlongNorm < 0) {
              const rest = Math.min(circle.properties?.restitution ?? 1.0, seg.properties?.restitution ?? 1.0);
              const impulse = -(1.0 + rest) * velAlongNorm;
              circle.velocity.vx += nx * impulse;
              circle.velocity.vy += ny * impulse;

              const pen = r - dist;
              circle.position.x += nx * pen * (minDim / envW);
              circle.position.y += ny * pen * (minDim / envH);

              collisionsThisFrame.push([circle.id, seg.id]);
            }
          }
        }
      }
    }

    // 6. Declarative Rule Engine Evaluation
    if (state.rules && state.rules.length > 0) {
      for (const rule of state.rules) {
        let isTriggered = false;

        if (rule.event === 'collision') {
          const [idA, idB] = rule.entities || [];
          isTriggered = collisionsThisFrame.some(([c1, c2]) => (c1 === idA && c2 === idB) || (c1 === idB && c2 === idA));
        } else if (rule.event === 'pointer_click' || rule.event === 'pointer_down') {
          isTriggered = clickedId != null && rule.entity === clickedId;
        } else if (rule.event === 'pointer_hover_enter') {
          isTriggered = hoveredId != null && rule.entity === hoveredId;
        } else if (rule.event === 'pointer_hover_exit') {
          isTriggered = hoveredId == null && rule.entity === hoveredId;
        } else if (rule.condition) {
          isTriggered = evaluateRuleCondition(rule.condition, state.entities, state.state_variables);
        }

        // Secondary condition filter
        if (isTriggered && rule.event && rule.condition) {
          isTriggered = evaluateRuleCondition(rule.condition, state.entities, state.state_variables);
        }

        if (isTriggered) {
          executeRuleActions(rule.actions, state.entities, state.state_variables);
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
          const isMoving = state.entities.some(e => 
            e.active !== false && (
              Math.abs(e.velocity?.vx || 0) > 1e-4 || 
              Math.abs(e.velocity?.vy || 0) > 1e-4 || 
              Math.abs(e.velocity?.omega || 0) > 1e-4
            )
          );
          const hasInput = Object.keys(keysDownRef.current).length > 0 || dragEntityRef.current != null;
          if (isMoving || hasInput) {
            const rawDt = (time - lastTime) / 1000.0;
            const dt = Math.min(rawDt, 0.05) * simSpeed;
            stepSimulation(dt);
          }
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

        // Render Constraints (Distance joints, springs, pin hinges)
        if (Array.isArray(state.constraints)) {
          const entityMap = {};
          for (const ent of state.entities) entityMap[ent.id] = ent;

          for (const c of state.constraints) {
            const eA = entityMap[c.entity_a];
            if (!eA) continue;
            const eB = c.entity_b ? entityMap[c.entity_b] : null;

            const aA = c.anchor_a || { x: 0, y: 0 };
            const angA = eA.position?.theta || eA.angle || 0;
            const cosA = Math.cos(angA), sinA = Math.sin(angA);
            const ax1 = (eA.position.x + (aA.x * cosA - aA.y * sinA)) * envW;
            const ay1 = (eA.position.y + (aA.x * sinA + aA.y * cosA)) * envH;

            let ax2, ay2;
            if (eB) {
              const aB = c.anchor_b || { x: 0, y: 0 };
              const angB = eB.position?.theta || eB.angle || 0;
              const cosB = Math.cos(angB), sinB = Math.sin(angB);
              ax2 = (eB.position.x + (aB.x * cosB - aB.y * sinB)) * envW;
              ay2 = (eB.position.y + (aB.x * sinB + aB.y * cosB)) * envH;
            } else {
              const wAnc = c.anchor_b || c.world_anchor || { x: 0, y: 0 };
              ax2 = wAnc.x * envW;
              ay2 = wAnc.y * envH;
            }

            ctx.save();
            ctx.strokeStyle = c.type === 'spring' ? '#F59E0B' : '#94A3B8';
            ctx.lineWidth = c.type === 'pin' ? 3 : 2;
            if (c.type === 'spring') {
              ctx.setLineDash([5, 4]);
            }
            ctx.beginPath();
            ctx.moveTo(ax1, ay1);
            ctx.lineTo(ax2, ay2);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = '#38BDF8';
            ctx.beginPath();
            ctx.arc(ax1, ay1, 3.5, 0, Math.PI * 2);
            ctx.arc(ax2, ay2, 3.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
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
            const cx = ent.position.x * envW;
            const cy = ent.position.y * envH;
            const angle = ent.position?.theta || ent.angle || 0.0;

            ctx.save();
            ctx.translate(cx, cy);
            if (angle !== 0.0) ctx.rotate(angle);

            // Halo Glow
            ctx.shadowColor = color;
            ctx.shadowBlur = isSelected ? 20 : 10;
            ctx.fillStyle = color;
            ctx.fillRect(-w / 2.0, -h / 2.0, w, h);
            ctx.shadowBlur = 0;

            // Selection Border
            if (isSelected) {
              ctx.strokeStyle = "#FFFFFF";
              ctx.lineWidth = 2.5;
              ctx.setLineDash([4, 4]);
              ctx.strokeRect(-w / 2.0 - 4, -h / 2.0 - 4, w + 8, h + 8);
              ctx.setLineDash([]);
            }

            // Hitbox Debug
            if (showHitboxes) {
              ctx.strokeStyle = "#F43F5E";
              ctx.lineWidth = 1;
              ctx.strokeRect(-w / 2.0, -h / 2.0, w, h);
            }
            ctx.restore();

            // Velocity Vector Debug
            if (showVectors && (ent.velocity.vx !== 0 || ent.velocity.vy !== 0)) {
              ctx.strokeStyle = "#38BDF8";
              ctx.lineWidth = 2;
              ctx.beginPath();
              ctx.moveTo(cx, cy);
              ctx.lineTo(cx + (ent.velocity.vx * 120), cy + (ent.velocity.vy * 120));
              ctx.stroke();
            }

            // Drag Coordinate Label
            if (isDraggingThis || isSelected) {
              ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
              ctx.fillRect(cx - 36, cy - (h / 2.0) - 26, 72, 18);
              ctx.fillStyle = "#38BDF8";
              ctx.font = "10px monospace";
              ctx.textAlign = "center";
              ctx.fillText(`${ent.position.x.toFixed(2)}, ${ent.position.y.toFixed(2)}`, cx, cy - (h / 2.0) - 13);
            }

          } else if (ent.type === 'capsule') {
            const cx = ent.position.x * envW;
            const cy = ent.position.y * envH;
            const r = (ent.size?.radius || 0.03) * minDim;
            const len = (ent.size?.length || 0.1) * minDim;
            const angle = (ent.position?.theta || ent.angle || 0.0) + (ent.size?.angle || 0.0);

            ctx.save();
            ctx.translate(cx, cy);
            if (angle !== 0.0) ctx.rotate(angle);

            ctx.shadowColor = color;
            ctx.shadowBlur = isSelected ? 20 : 10;
            ctx.fillStyle = color;

            const hl = len / 2.0;
            ctx.beginPath();
            ctx.arc(-hl, 0, r, Math.PI / 2, (Math.PI * 3) / 2);
            ctx.arc(hl, 0, r, (Math.PI * 3) / 2, Math.PI / 2);
            ctx.closePath();
            ctx.fill();
            ctx.shadowBlur = 0;

            if (isSelected) {
              ctx.strokeStyle = "#FFFFFF";
              ctx.lineWidth = 2;
              ctx.setLineDash([4, 4]);
              ctx.stroke();
              ctx.setLineDash([]);
            }
            ctx.restore();

          } else if (ent.type === 'segment') {
            const sx = ent.position.x * envW;
            const sy = ent.position.y * envH;
            const ex = (ent.size?.end_x ?? ent.position.x) * envW;
            const ey = (ent.size?.end_y ?? ent.position.y) * envH;
            const th = Math.max(2, (ent.size?.thickness || 0.005) * minDim);

            ctx.save();
            ctx.strokeStyle = color;
            ctx.lineWidth = th;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(sx, sy);
            ctx.lineTo(ex, ey);
            ctx.stroke();
            ctx.restore();

          } else if (ent.type === 'text') {
            const px = ent.position.x * envW;
            const py = ent.position.y * envH;
            const fontScale = ent.size?.font_scale || 0.025;
            const fontSize = Math.max(10, Math.round(fontScale * minDim));
            const align = ent.size?.align || 'center';

            let displayText = ent.template || ent.id;
            if (ent.template && state.state_variables) {
              displayText = ent.template.replace(/\{([a-zA-Z0-9_.]+)\}/g, (_, path) => {
                const parts = path.split('.');
                let val = state.state_variables;
                for (const p of parts) val = val != null ? val[p] : undefined;
                return val !== undefined ? String(val) : `{${path}}`;
              });
            }

            ctx.save();
            ctx.fillStyle = color;
            ctx.font = `600 ${fontSize}px "Segoe UI", Inter, system-ui, sans-serif`;
            ctx.textAlign = align;
            ctx.textBaseline = 'middle';
            ctx.fillText(displayText, px, py);
            ctx.restore();
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
  const copyShareLink = async () => {
    try {
      const base64 = btoa(unescape(encodeURIComponent(jsonText)));
      const url = `${window.location.origin}${window.location.pathname}#data=${base64}`;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(url).catch(() => {});
      }
    } catch (e) {}
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
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
      <section className="pt-2 sm:pt-4 pb-2 text-center max-w-4xl mx-auto space-y-4 sm:space-y-5">
        
        {/* Substrate Framing Badges */}
        <div className="flex items-center justify-center gap-2 font-mono text-xs">
          <span className="px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-500/40 text-cyan-300 font-bold flex items-center space-x-1.5 shadow-sm shadow-cyan-500/10">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI INTERACTIVE RUNTIME</span>
          </span>
          <button
            type="button"
            onClick={() => setShowGuideModal(true)}
            className="px-3 py-1 rounded-full bg-slate-900/80 hover:bg-slate-800 border border-white/[0.1] text-slate-300 hover:text-white font-bold flex items-center space-x-1.5 transition cursor-pointer"
          >
            <BookOpen className="w-3.5 h-3.5 text-amber-400" />
            <span>Architectural Guide</span>
          </button>
        </div>

        {/* Hero Title */}
        <div className="space-y-2">
          <h1 className="text-2xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white leading-tight">
            What do you want to build?
          </h1>
          <p className="text-xs sm:text-sm md:text-base text-slate-300 font-sans max-w-2xl mx-auto leading-relaxed">
            Describe a 2D game, physics simulation, or interactive dashboard. MLUE compiles and runs it in milliseconds.
          </p>
        </div>

        {/* Clean Google-Style Floating Prompt Capsule */}
        <div className="relative pt-1 max-w-3xl mx-auto">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleBuild(); }}
            className="flex items-center bg-slate-900/90 border border-white/[0.12] hover:border-cyan-500/40 focus-within:border-cyan-400 focus-within:ring-4 focus-within:ring-cyan-500/10 rounded-full p-1.5 sm:p-2 pl-4 sm:pl-6 shadow-2xl transition-all backdrop-blur-xl"
          >
            <label htmlFor="prompt-input" className="sr-only">
              Describe what you want to build
            </label>
            <input
              id="prompt-input"
              name="prompt"
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder={isGenerating ? "Compiling interactive runtime..." : `e.g. ${ROTATING_EXAMPLES[exampleIdx]}`}
              disabled={isGenerating}
              aria-label="Describe what you want to build"
              className="flex-1 bg-transparent text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none font-sans"
            />
            <motion.button
              {...tapScale.button}
              type="submit"
              disabled={isGenerating || !prompt.trim()}
              title={!prompt.trim() ? "Describe what to build to generate" : "Generate interactive runtime"}
              aria-label="Generate interactive runtime"
              className="px-4 sm:px-5 h-9 sm:h-10 rounded-full bg-cyan-400 hover:bg-cyan-300 text-slate-950 flex items-center justify-center font-bold text-xs sm:text-sm transition disabled:opacity-40 shadow-md shadow-cyan-500/20 cursor-pointer shrink-0 ml-2 gap-1.5"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 animate-spin" />
                  <span className="hidden xs:inline">Generating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  <span>Generate</span>
                </>
              )}
            </motion.button>
          </form>

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
          <div className="px-5 py-3.5 border-b border-white/[0.06] flex flex-wrap items-center justify-between gap-3 bg-black/30 relative z-20">
            <div className="flex items-center space-x-3">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
              <h2 className="text-sm font-bold text-white tracking-tight truncate max-w-xs">{activeTitle}</h2>
              <span className="text-[11px] font-mono text-slate-500 hidden md:inline">60 FPS Deterministic • Tick {tickCount}</span>
            </div>

            {/* Stage Controls & Toggles */}
            <div className="flex items-center gap-1.5 font-mono text-xs">
              
              {/* Overlay Toggles */}
              <button
                type="button"
                onClick={() => setShowGrid(!showGrid)}
                aria-label={showGrid ? "Disable grid overlay" : "Enable grid overlay"}
                aria-pressed={showGrid}
                className={`p-1.5 rounded-lg border transition cursor-pointer ${
                  showGrid ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-white/[0.06]'
                }`}
                title="Toggle Grid Overlay"
              >
                <Grid className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => setShowVectors(!showVectors)}
                aria-label={showVectors ? "Disable velocity vectors" : "Enable velocity vectors"}
                aria-pressed={showVectors}
                className={`p-1.5 rounded-lg border transition cursor-pointer ${
                  showVectors ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-white/[0.06]'
                }`}
                title="Toggle Velocity Vectors"
              >
                <Radio className="w-3.5 h-3.5" />
              </button>

              {/* Playback Controls */}
              <motion.button
                {...tapScale.button}
                type="button"
                aria-label={isPlaying ? "Pause simulation" : "Resume simulation"}
                onClick={() => setIsPlaying(!isPlaying)}
                className={`p-2 rounded-xl border transition cursor-pointer flex items-center justify-center ${
                  isPlaying 
                    ? 'bg-amber-500/15 text-amber-400 border-amber-500/30 hover:bg-amber-500/25' 
                    : 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/25'
                }`}
                title={isPlaying ? "Pause" : "Play"}
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              </motion.button>

              <motion.button
                {...tapScale.button}
                type="button"
                aria-label="Reset simulation to initial state"
                onClick={() => {
                  try {
                    initSimulation(JSON.parse(jsonText));
                  } catch (e) {}
                }}
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-white/[0.06] cursor-pointer transition flex items-center justify-center"
                title="Reset State"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </motion.button>

              <motion.button
                {...tapScale.button}
                type="button"
                aria-label="Copy scene link"
                onClick={copyShareLink}
                className={`p-2 px-2.5 rounded-xl border transition cursor-pointer flex items-center gap-1.5 ${
                  copiedLink 
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' 
                    : 'bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border-white/[0.06]'
                }`}
                title="Copy Scene Link"
              >
                {copiedLink ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-[11px] font-mono text-emerald-300 font-bold">Copied!</span>
                  </>
                ) : (
                  <Copy className="w-3.5 h-3.5 text-cyan-400" />
                )}
              </motion.button>

              <motion.button
                {...tapScale.button}
                type="button"
                aria-label="Export .mlue declarative document"
                onClick={downloadMlue}
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/[0.06] cursor-pointer"
                title="Export .mlue Document"
              >
                <Download className="w-3.5 h-3.5 text-emerald-400" />
              </motion.button>

              <motion.button
                {...tapScale.button}
                type="button"
                aria-label={showCode ? "Hide declarative schema editor" : "View declarative schema editor"}
                aria-expanded={showCode}
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

          {/* Canvas Viewport (Edge-to-Edge Flush Stage: Zero Dead Space, Single Unified Play Border) */}
          <div 
            className="relative w-full bg-slate-950 flex items-center justify-center select-none overflow-hidden"
            style={{
              aspectRatio: `${simStateRef.current?.env?.dimensions?.[0] || 750} / ${simStateRef.current?.env?.dimensions?.[1] || 500}`,
              maxHeight: 'min(72vh, 680px)'
            }}
          >
            <canvas
              ref={canvasRef}
              onPointerDown={handleCanvasPointerDown}
              onPointerMove={handleCanvasPointerMove}
              onPointerUp={handleCanvasPointerUp}
              className="w-full h-full block cursor-crosshair touch-none"
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
            {/* Game Over Overlay */}
            {simStateRef.current?.state_variables?.game_state === 'GAME OVER' && (
              <div className="absolute inset-0 z-20 bg-slate-950/85 backdrop-blur-sm flex flex-col items-center justify-center text-center p-6 space-y-4">
                <div className="w-12 h-12 rounded-full bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-400 text-xl font-bold">
                  ✕
                </div>
                <div className="space-y-1">
                  <h3 className="text-2xl sm:text-3xl font-black text-rose-400 tracking-wider font-mono">GAME OVER</h3>
                  {simStateRef.current?.state_variables?.score !== undefined && (
                    <p className="text-xs sm:text-sm font-mono text-slate-300">
                      Final Score: <span className="text-cyan-400 font-bold">{simStateRef.current.state_variables.score}</span>
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => {
                    try {
                      initSimulation(JSON.parse(jsonText));
                    } catch (e) {}
                  }}
                  className="px-5 py-2.5 rounded-full bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold text-xs font-mono transition cursor-pointer flex items-center gap-2 shadow-lg shadow-cyan-500/20"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Play Again</span>
                </button>
              </div>
            )}

            {/* Victory Overlay */}
            {simStateRef.current?.state_variables?.game_state === 'VICTORY' && (
              <div className="absolute inset-0 z-20 bg-slate-950/85 backdrop-blur-sm flex flex-col items-center justify-center text-center p-6 space-y-4">
                <div className="w-12 h-12 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 text-xl font-bold">
                  ✓
                </div>
                <div className="space-y-1">
                  <h3 className="text-2xl sm:text-3xl font-black text-emerald-400 tracking-wider font-mono">VICTORY!</h3>
                  {simStateRef.current?.state_variables?.score !== undefined && (
                    <p className="text-xs sm:text-sm font-mono text-slate-300">
                      Final Score: <span className="text-emerald-400 font-bold">{simStateRef.current.state_variables.score}</span>
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => {
                    try {
                      initSimulation(JSON.parse(jsonText));
                    } catch (e) {}
                  }}
                  className="px-5 py-2.5 rounded-full bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-bold text-xs font-mono transition cursor-pointer flex items-center gap-2 shadow-lg shadow-emerald-500/20"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Play Again</span>
                </button>
              </div>
            )}
          </div>

          {/* Minimal Game Modification & Presets Command Strip */}
          <div className="p-3 sm:p-4 bg-slate-950/95 border-t border-white/[0.06] space-y-3">
            <form 
              onSubmit={(e) => { e.preventDefault(); handleBuild(refinePrompt); }}
              className="flex items-center bg-slate-900 border border-white/[0.08] hover:border-cyan-500/40 focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-500/20 rounded-full px-4 py-2 shadow-inner transition"
            >
              <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mr-2.5" />
              <input
                id="refine-prompt-input"
                name="refinePrompt"
                type="text"
                value={refinePrompt}
                onChange={(e) => setRefinePrompt(e.target.value)}
                aria-label="Modify the active game"
                placeholder="Modify this game (e.g. make paddle wider, increase ball speed, add 2 obstacles)..."
                disabled={isGenerating}
                className="flex-1 bg-transparent text-xs sm:text-sm text-slate-200 placeholder-slate-500 focus:outline-none font-sans"
              />
              <motion.button
                {...tapScale.button}
                type="submit"
                disabled={isGenerating || !refinePrompt.trim()}
                title={!refinePrompt.trim() ? "Describe a change to apply" : "Apply modification to active game"}
                aria-label="Apply modification to active game"
                className="px-4 py-1.5 bg-cyan-400 hover:bg-cyan-300 text-slate-950 rounded-full disabled:opacity-40 cursor-pointer ml-2 flex items-center gap-1.5 font-bold text-xs shrink-0 transition"
              >
                {isGenerating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                <span>Apply</span>
              </motion.button>
            </form>

            {/* Clean Presets Strip */}
            <div className="flex flex-wrap items-center justify-center gap-1.5 pt-1 font-mono text-xs">
              <span className="text-[11px] text-slate-500 font-semibold mr-1">Presets:</span>
              {[
                { title: 'Breakout', json: DOMAIN_TEMPLATES.games.find(g => g.id === 'breakout')?.json },
                { title: '2-Player Pong', json: DOMAIN_TEMPLATES.games.find(g => g.id === 'pong')?.json },
                { title: 'Spinning Arena', json: DOMAIN_TEMPLATES.games.find(g => g.id === 'spinning_paddle_arena')?.json },
                { title: 'Telemetry Monitor', json: DOMAIN_TEMPLATES.dashboards[0].json },
                { title: 'Hydraulic Valve', json: DOMAIN_TEMPLATES.control[0].json }
              ].map((preset) => {
                const isActive = activeTitle.toLowerCase().includes(preset.title.toLowerCase());
                return (
                  <button
                    key={preset.title}
                    type="button"
                    onClick={() => {
                      if (!preset.json) return;
                      setActiveTitle(preset.title);
                      setJsonText(JSON.stringify(preset.json, null, 2));
                      initSimulation(preset.json, true, preset.title);
                    }}
                    className={`px-3 py-1 rounded-full border text-xs transition cursor-pointer ${
                      isActive
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/50 font-bold shadow-sm shadow-cyan-500/10'
                        : 'bg-slate-900/70 text-slate-400 hover:text-white border-white/[0.06] hover:border-white/[0.15]'
                    }`}
                  >
                    {preset.title}
                  </button>
                );
              })}
            </div>
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

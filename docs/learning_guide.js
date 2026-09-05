/* Activation function & visualization helpers for minGPT learning guide */

function initCodeCopyButtons() {
  document.querySelectorAll('pre').forEach((pre) => {
    if (pre.querySelector('.copy-code-button')) return;
    const code = pre.querySelector('code');
    if (!code) return;

    const button = document.createElement('button');
    button.className = 'copy-code-button';
    button.type = 'button';
    button.textContent = '复制';
    button.setAttribute('aria-label', '复制代码到剪贴板');

    button.addEventListener('click', async () => {
      const text = code.innerText;
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = '已复制';
        button.classList.add('copied');
      } catch (err) {
        const range = document.createRange();
        range.selectNodeContents(code);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = '已选中';
      }
      window.setTimeout(() => {
        button.textContent = '复制';
        button.classList.remove('copied');
      }, 1400);
    });

    pre.appendChild(button);
  });
}

function erf(x) {
  // Abramowitz & Stegun approximation
  const a1=0.254829592, a2=-0.284496736, a3=1.421413741;
  const a4=-1.453152027, a5=1.061405429, p=0.3275911;
  const sign = x < 0 ? -1 : 1;
  x = Math.abs(x);
  const t = 1 / (1 + p * x);
  const y = 1 - (((((a5*t+a4)*t)+a3)*t+a2)*t+a1)*t*Math.exp(-x*x);
  return sign * y;
}

function geluExact(x) {
  return 0.5 * x * (1 + erf(x / Math.SQRT2));
}

function geluApprox(x) {
  // NewGELU from mingpt/model.py
  return 0.5 * x * (1 + Math.tanh(Math.sqrt(2/Math.PI) * (x + 0.044715 * x*x*x)));
}

function relu(x) { return Math.max(0, x); }

function geluDeriv(x) {
  const phi = Math.exp(-0.5*x*x) / Math.sqrt(2*Math.PI);
  const Phi = 0.5 * (1 + erf(x / Math.SQRT2));
  return Phi + x * phi;
}

function reluDeriv(x) { return x > 0 ? 1 : 0; }

function softmax(arr) {
  const max = Math.max(...arr);
  const exps = arr.map(v => Math.exp(v - max));
  const sum = exps.reduce((a,b) => a+b, 0);
  return exps.map(e => e / sum);
}

function drawChart(canvasId, config) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth;
  const H = canvas.clientHeight || 320;
  canvas.width = W * dpr;
  canvas.height = H * dpr;
  ctx.scale(dpr, dpr);

  const pad = { top: 30, right: 30, bottom: 50, left: 60 };
  const plotW = W - pad.left - pad.right;
  const plotH = H - pad.top - pad.bottom;

  const { xMin, xMax, yMin, yMax, series, xLabel, yLabel, title } = config;

  const toX = x => pad.left + ((x - xMin) / (xMax - xMin)) * plotW;
  const toY = y => pad.top + plotH - ((y - yMin) / (yMax - yMin)) * plotH;

  // background
  ctx.fillStyle = '#252c3d';
  ctx.fillRect(0, 0, W, H);

  // grid
  ctx.strokeStyle = '#2e3345';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 8; i++) {
    const y = pad.top + (plotH / 8) * i;
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(pad.left + plotW, y); ctx.stroke();
  }
  for (let i = 0; i <= 10; i++) {
    const x = pad.left + (plotW / 10) * i;
    ctx.beginPath(); ctx.moveTo(x, pad.top); ctx.lineTo(x, pad.top + plotH); ctx.stroke();
  }

  // axes
  ctx.strokeStyle = '#9aa3b8';
  ctx.lineWidth = 1.5;
  if (yMin <= 0 && yMax >= 0) {
    const y0 = toY(0);
    ctx.beginPath(); ctx.moveTo(pad.left, y0); ctx.lineTo(pad.left + plotW, y0); ctx.stroke();
  }
  if (xMin <= 0 && xMax >= 0) {
    const x0 = toX(0);
    ctx.beginPath(); ctx.moveTo(x0, pad.top); ctx.lineTo(x0, pad.top + plotH); ctx.stroke();
  }

  // axis labels
  ctx.fillStyle = '#9aa3b8';
  ctx.font = '12px Segoe UI, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(xLabel || 'x', pad.left + plotW/2, H - 10);
  ctx.save();
  ctx.translate(14, pad.top + plotH/2);
  ctx.rotate(-Math.PI/2);
  ctx.fillText(yLabel || 'f(x)', 0, 0);
  ctx.restore();

  if (title) {
    ctx.fillStyle = '#e8eaf0';
    ctx.font = 'bold 14px Segoe UI, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(title, pad.left + plotW/2, 18);
  }

  // tick labels
  ctx.font = '11px Segoe UI, sans-serif';
  ctx.fillStyle = '#9aa3b8';
  for (let i = 0; i <= 5; i++) {
    const x = xMin + (xMax - xMin) * i / 5;
    ctx.textAlign = 'center';
    ctx.fillText(x.toFixed(1), toX(x), pad.top + plotH + 18);
  }
  for (let i = 0; i <= 4; i++) {
    const y = yMin + (yMax - yMin) * i / 4;
    ctx.textAlign = 'right';
    ctx.fillText(y.toFixed(1), pad.left - 8, toY(y) + 4);
  }

  // draw series
  const steps = 400;
  series.forEach(s => {
    ctx.strokeStyle = s.color;
    ctx.lineWidth = s.width || 2.5;
    if (s.dash) ctx.setLineDash(s.dash); else ctx.setLineDash([]);
    ctx.beginPath();
    for (let i = 0; i <= steps; i++) {
      const x = xMin + (xMax - xMin) * i / steps;
      const y = s.fn(x);
      const px = toX(x), py = toY(y);
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.stroke();
    ctx.setLineDash([]);
  });

  // hover crosshair
  const tooltip = document.getElementById(canvasId + '-tip');
  canvas.onmousemove = (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    if (mx < pad.left || mx > pad.left + plotW) {
      if (tooltip) tooltip.style.display = 'none';
      return;
    }
    const x = xMin + ((mx - pad.left) / plotW) * (xMax - xMin);
    let tip = `x = ${x.toFixed(2)}`;
    series.forEach(s => {
      tip += `<br><span style="color:${s.color}">●</span> ${s.label}: ${s.fn(x).toFixed(4)}`;
    });
    if (tooltip) {
      tooltip.innerHTML = tip;
      tooltip.style.display = 'block';
      tooltip.style.left = (e.clientX - rect.left + 15) + 'px';
      tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
    }
    // redraw with crosshair
    drawChart(canvasId, config);
    const ctx2 = canvas.getContext('2d');
    const cx = toX(x);
    ctx2.strokeStyle = '#6c9eff55';
    ctx2.lineWidth = 1;
    ctx2.setLineDash([4,4]);
    ctx2.beginPath(); ctx2.moveTo(cx, pad.top); ctx2.lineTo(cx, pad.top+plotH); ctx2.stroke();
    ctx2.setLineDash([]);
    series.forEach(s => {
      const cy = toY(s.fn(x));
      ctx2.fillStyle = s.color;
      ctx2.beginPath(); ctx2.arc(cx, cy, 4, 0, Math.PI*2); ctx2.fill();
    });
  };
  canvas.onmouseleave = () => { if (tooltip) tooltip.style.display = 'none'; };
}

function drawSoftmaxChart(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const logits = [2.0, 1.0, 0.1, -1.0, -2.0];
  const labels = ['token A', 'token B', 'token C', 'token D', 'token E'];
  const probs = softmax(logits);
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth;
  const H = 320;
  canvas.width = W * dpr; canvas.height = H * dpr;
  ctx.scale(dpr, dpr);

  const pad = { top: 40, right: 30, bottom: 60, left: 60 };
  const plotW = W - pad.left - pad.right;
  const plotH = H - pad.top - pad.bottom;
  const barW = plotW / logits.length * 0.6;
  const gap = plotW / logits.length;

  ctx.fillStyle = '#252c3d';
  ctx.fillRect(0, 0, W, H);

  ctx.fillStyle = '#e8eaf0';
  ctx.font = 'bold 14px Segoe UI';
  ctx.textAlign = 'center';
  ctx.fillText('Softmax: logits → 概率分布', pad.left + plotW/2, 22);

  // bars for logits (left half, normalized)
  const maxLogit = Math.max(...logits);
  const minLogit = Math.min(...logits);
  logits.forEach((v, i) => {
    const x = pad.left + gap * i + gap * 0.15;
    const h = ((v - minLogit) / (maxLogit - minLogit + 0.01)) * plotH * 0.35;
    ctx.fillStyle = '#6c9eff88';
    ctx.fillRect(x, pad.top + plotH - h, barW, h);
    ctx.fillStyle = '#6c9eff';
    ctx.font = '11px Segoe UI';
    ctx.textAlign = 'center';
    ctx.fillText(v.toFixed(1), x + barW/2, pad.top + plotH - h - 6);
  });

  ctx.fillStyle = '#9aa3b8';
  ctx.font = '12px Segoe UI';
  ctx.fillText('原始 logits', pad.left + plotW/4, pad.top + plotH + 20);

  // arrow
  ctx.fillStyle = '#a78bfa';
  ctx.font = '20px Segoe UI';
  ctx.fillText('→ softmax →', pad.left + plotW/2, pad.top + plotH/2);

  // bars for probs
  probs.forEach((v, i) => {
    const x = pad.left + gap * i + gap * 0.15;
    const h = v * plotH * 0.85;
    const grad = ctx.createLinearGradient(0, pad.top + plotH - h, 0, pad.top + plotH);
    grad.addColorStop(0, '#34d399');
    grad.addColorStop(1, '#34d39955');
    ctx.fillStyle = grad;
    ctx.fillRect(x, pad.top + plotH - h, barW, h);
    ctx.fillStyle = '#34d399';
    ctx.font = '11px Segoe UI';
    ctx.textAlign = 'center';
    ctx.fillText((v*100).toFixed(1)+'%', x + barW/2, pad.top + plotH - h - 6);
    ctx.fillStyle = '#9aa3b8';
    ctx.font = '10px Segoe UI';
    ctx.fillText(labels[i], x + barW/2, pad.top + plotH + 38);
  });

  ctx.fillStyle = '#9aa3b8';
  ctx.font = '12px Segoe UI';
  ctx.fillText('概率 (和 = 1.0)', pad.left + plotW*0.75, pad.top + plotH + 20);
}

function initCharts() {
  drawChart('chart-gelu', {
    xMin: -4, xMax: 4, yMin: -0.5, yMax: 4,
    xLabel: 'x (输入)', yLabel: 'f(x) (输出)',
    title: 'GELU vs ReLU 激活函数对比',
    series: [
      { fn: geluExact, color: '#6c9eff', label: 'GELU 精确', width: 2.5 },
      { fn: geluApprox, color: '#a78bfa', label: 'GELU 近似 (NewGELU)', width: 2, dash: [6,3] },
      { fn: relu, color: '#fb923c', label: 'ReLU', width: 2 },
    ]
  });

  drawChart('chart-gelu-deriv', {
    xMin: -4, xMax: 4, yMin: -0.2, yMax: 1.2,
    xLabel: 'x', yLabel: "f'(x)",
    title: 'GELU vs ReLU 导数对比',
    series: [
      { fn: geluDeriv, color: '#6c9eff', label: "GELU' (精确)" },
      { fn: reluDeriv, color: '#fb923c', label: "ReLU'" },
    ]
  });

  drawChart('chart-tanh', {
    xMin: -4, xMax: 4, yMin: -1.2, yMax: 1.2,
    xLabel: 'x', yLabel: 'tanh(x)',
    title: 'Tanh 函数（GELU 近似公式中使用）',
    series: [
      { fn: Math.tanh, color: '#34d399', label: 'tanh(x)' },
    ]
  });

  drawSoftmaxChart('chart-softmax');
}

document.addEventListener('DOMContentLoaded', initCharts);
window.addEventListener('resize', () => {
  clearTimeout(window._resizeTimer);
  window._resizeTimer = setTimeout(initCharts, 200);
});

// Sidebar active link on scroll
document.addEventListener('DOMContentLoaded', () => {
  const sections = document.querySelectorAll('section[id]');
  const links = document.querySelectorAll('.sidebar nav a');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        links.forEach(l => l.classList.remove('active'));
        const active = document.querySelector(`.sidebar nav a[href="#${e.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  sections.forEach(s => observer.observe(s));
});

/* ==================== Gradient Descent Interactive Canvas (Clean Working Version) ==================== */
function initGDCanvas() {
  const canvas = document.getElementById('gd-canvas');
  if (!canvas) {
    console.warn('GD canvas element not found');
    return;
  }
  const ctx = canvas.getContext('2d');

  let param = 2.2;   // current parameter
  let vel = 0;
  let running = false;
  let raf = null;

  const W = canvas.width;
  const H = canvas.height;
  const cx = W / 2;
  const baseY = H - 70;
  const xScale = 82;
  const lScale = 65;

  function loss(p) { return p * p; }
  function g(p) { return 2 * p; }

  function sx(p) { return cx + p * xScale; }
  function sy(l) { return baseY - l * lScale; }

  function draw() {
    ctx.fillStyle = '#1c2230';
    ctx.fillRect(0, 0, W, H);

    // light grid
    ctx.strokeStyle = '#2a3145';
    ctx.lineWidth = 1;
    for (let i = -3; i <= 3; i++) {
      const x = sx(i);
      ctx.beginPath(); ctx.moveTo(x, 25); ctx.lineTo(x, H-25); ctx.stroke();
    }

    // loss curve (nice bowl, low loss at bottom)
    ctx.strokeStyle = '#fb923c';
    ctx.lineWidth = 3;
    ctx.beginPath();
    for (let p = -2.9; p <= 2.9; p += 0.025) {
      const x = sx(p);
      const y = sy(loss(p));
      if (p === -2.9) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // current point
    const px = sx(param);
    const py = sy(loss(param));

    ctx.fillStyle = '#f87171';
    ctx.beginPath();
    ctx.arc(px, py, 9, 0, Math.PI * 2);
    ctx.fill();

    // gradient arrow (uphill)
    const grad = g(param);
    ctx.strokeStyle = '#34d399';
    ctx.lineWidth = 2.5;
    const ax = px + Math.sign(grad) * 26;
    const ay = py - 20;
    ctx.beginPath();
    ctx.moveTo(px, py);
    ctx.lineTo(ax, ay);
    ctx.stroke();

    // labels
    ctx.fillStyle = '#e8eaf0';
    ctx.font = '13px Segoe UI';
    ctx.fillText('x = ' + param.toFixed(2), px + 14, py - 4);
    ctx.fillText('loss = ' + loss(param).toFixed(2), px + 14, py + 16);

    ctx.fillStyle = '#9aa3b8';
    ctx.font = '11px Segoe UI';
    ctx.fillText('参数 x', cx + 140, baseY + 18);
    ctx.fillText('损失 (低 = 好)', 20, 42);
  }

  function step() {
    const lr = parseFloat(document.getElementById('gd-lr').value);
    const mom = parseFloat(document.getElementById('gd-mom').value);

    const grad = g(param);
    vel = mom * vel - lr * grad;
    param += vel;

    if (param < -2.85) param = -2.85;
    if (param > 2.85) param = 2.85;

    draw();
  }

  // Bind UI (do it every time in case of re-init)
  function bind() {
    const lrS = document.getElementById('gd-lr');
    const momS = document.getElementById('gd-mom');
    const lrV = document.getElementById('gd-lr-val');
    const momV = document.getElementById('gd-mom-val');

    if (lrS && lrV) {
      lrS.oninput = () => lrV.textContent = parseFloat(lrS.value).toFixed(2);
      lrV.textContent = parseFloat(lrS.value).toFixed(2);
    }
    if (momS && momV) {
      momS.oninput = () => momV.textContent = parseFloat(momS.value).toFixed(2);
      momV.textContent = parseFloat(momS.value).toFixed(2);
    }

    const stepB = document.getElementById('gd-step');
    if (stepB) stepB.onclick = step;

    const runB = document.getElementById('gd-run');
    if (runB) {
      runB.onclick = () => {
        running = !running;
        runB.textContent = running ? '暂停' : '连续运行';
        if (running) {
          const tick = () => {
            if (running) {
              step();
              raf = requestAnimationFrame(tick);
            }
          };
          tick();
        } else if (raf) {
          cancelAnimationFrame(raf);
        }
      };
    }

    const rst = document.getElementById('gd-reset');
    if (rst) rst.onclick = () => {
      running = false;
      if (runB) runB.textContent = '连续运行';
      if (raf) cancelAnimationFrame(raf);
      param = 2.0;
      vel = 0;
      draw();
    };
  }

  bind();
  draw();
  console.log('%c[GD Toy] Gradient descent canvas ready', 'color:#34d399');
}

// Ensure it runs
document.addEventListener('DOMContentLoaded', initGDCanvas);

/* ==================== Interactive Attention Toy (REAL computation, editable Q/K/V) ====================
   Every matrix shown is actually computed from the editable Q/K/V inputs below.
   Nothing is hard-coded: change any number and every later step recomputes instantly. */
function initAttentionToy() {
  const root = document.getElementById('attn-toy');
  if (!root || root.dataset.toyReady === '1') return;

  const matrixEl = root.querySelector('.toy-matrix');
  const logEl = root.querySelector('.toy-log');
  const stepBtn = root.querySelector('#attn-step');
  const resetBtn = root.querySelector('#attn-reset');
  if (!matrixEl || !logEl || !stepBtn || !resetBtn) return;
  root.dataset.toyReady = '1';

  const lang = (document.documentElement.getAttribute('lang') || 'zh').slice(0, 2).toLowerCase();
  const zh = {
    stepBtn: '下一步', resetBtn: '重置',
    ready: '就绪：序列 = [I, love, cats, !]  |  每个位置只能看到自己及左侧。Q/K/V 全部可以改数值，改完每一步都会实时重算。',
    s1: '步骤 1/6：输入。每个位置一个 3 维向量。Q/K/V 都是可编辑的 —— 改任何一个数字，后面所有步骤立刻重算。',
    s2: '步骤 2/6：打分 S = Q·Kᵀ。S[i][j] 是“位置 i 想找的信息”和“位置 j 提供的标签”的点积，越大越相关。',
    s3: '步骤 3/6：因果掩码。右上角（未来位置）全部设为 -∞ —— 这就是“不能偷看未来”。',
    s4: '步骤 4/6：Softmax。每一行独立归一化成注意力权重，行和 = 1；-∞ 位置的权重精确等于 0。',
    s5: '步骤 5/6：加权求和。输出[i] = Σ 权重[i][j] × V[j]，每个位置的新表示是“允许看到的位置的 V”按权重混合的结果。',
    s6: '✓ 完成！动手试试：把 Q 或 K 里的某个数字改大，再翻回第 2 步看分数和权重如何变化。真实模型中：多头并行 + 缩放 1/√d_k + 残差连接与 LayerNorm。',
    tblQ: 'Q（每个位置想找什么）', tblK: 'K（每个位置提供的标签）', tblV: 'V（每个位置真正携带的信息）',
    recap: '✓ 自注意力完成！接下来这个输出还会经过残差连接 + LayerNorm + MLP。'
  };
  const en = {
    stepBtn: 'Next Step', resetBtn: 'Reset',
    ready: 'Ready: sequence = [I, love, cats, !]  |  each position sees only itself and the left. Edit any Q/K/V number — every step recomputes live.',
    s1: 'Step 1/6: Inputs. One 3-dim vector per position. Q/K/V are editable — change any number and every later step recomputes instantly.',
    s2: 'Step 2/6: Scores S = Q·Kᵀ. S[i][j] = dot product between what position i looks for and the label position j offers. Higher = more relevant.',
    s3: 'Step 3/6: Causal mask. Future positions (upper right) become -∞ — this is “no peeking at the future”.',
    s4: 'Step 4/6: Softmax. Each row is normalized into attention weights that sum to 1; -∞ entries get exactly 0.',
    s5: 'Step 5/6: Weighted sum. output[i] = Σ weight[i][j] × V[j] — each new representation mixes the V vectors of allowed positions.',
    s6: '✓ Done! Try making one Q or K entry bigger, then step back to step 2 and watch scores/weights shift. Real model: multi-head + 1/√d_k scaling + residuals and LayerNorm.',
    tblQ: 'Q (what each position looks for)', tblK: 'K (label each position offers)', tblV: 'V (information each position carries)',
    recap: '✓ Attention done! This output then goes through residual + LayerNorm + MLP.'
  };
  const ja = {
    stepBtn: '次へ', resetBtn: 'リセット',
    ready: '準備完了：系列 = [I, love, cats, !]  |  各位置は自分と左側だけを見られます。Q/K/V の数値は編集でき、変更すると即座に再計算されます。',
    s1: 'ステップ 1/6：入力。各位置に 3 次元ベクトル。Q/K/V は編集可能 — 数値を変えると以降のステップはすべて再計算されます。',
    s2: 'ステップ 2/6：スコア S = Q·Kᵀ。S[i][j] は「位置 i が探したい情報」と「位置 j のラベル」の内積。大きいほど関連が強い。',
    s3: 'ステップ 3/6：因果マスク。未来の位置（右上）をすべて -∞ に — 「未来を覗き見しない」ためです。',
    s4: 'ステップ 4/6：Softmax。行ごとに正規化して注意重みにし、行和 = 1。-∞ の位置は正確に 0 になります。',
    s5: 'ステップ 5/6：重み付き和。出力[i] = Σ 重み[i][j] × V[j]。新しい表現は「見てよい位置の V」を重みで混ぜたものです。',
    s6: '✓ 完了！Q か K の数値を大きくしてみて、ステップ 2 でスコアと重みがどう変わるか観察しましょう。実際のモデル：マルチヘッド + 1/√d_k スケーリング + 残差と LayerNorm。',
    tblQ: 'Q（各位置が探したいもの）', tblK: 'K（各位置のラベル）', tblV: 'V（各位置が運ぶ情報）',
    recap: '✓ 注意計算完了！この出力はさらに残差 + LayerNorm + MLP へ進みます。'
  };
  const t = { zh, en, ja }[lang] || zh;

  const tokens = ['I', 'love', 'cats', '!'];
  const DIMS = ['d0', 'd1', 'd2'];
  const MAX_STEP = 6;

  const defQ = () => [[1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1]];
  const defK = () => [[1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1]];
  const defV = () => [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0.5, 0.5, 0]];
  let Q = defQ(), K = defK(), V = defV();
  let step = 0;
  let focus = null; // remember which editable cell the user is typing in

  const transpose = m => m[0].map((_, j) => m.map(row => row[j]));
  const matmul = (a, b) => a.map(ra => b[0].map((_, j) => ra.reduce((s, v, k) => s + v * b[k][j], 0)));
  const softmaxArr = arr => {
    const finite = arr.filter(Number.isFinite);
    const max = finite.length ? Math.max(...finite) : 0;
    const exps = arr.map(v => (Number.isFinite(v) ? Math.exp(v - max) : 0));
    const s = exps.reduce((x, y) => x + y, 0) || 1;
    return exps.map(e => e / s);
  };
  const fmt = v => (v === -Infinity ? '-∞' : (+v).toFixed(2).replace(/\.?0+$/, ''));

  function td(v) {
    const inf = v === -Infinity;
    const bg = inf ? '#3a2a1f' : (typeof v === 'number' && v > 0.3 ? '#14352a' : '#1a2332');
    const col = inf ? '#fb923c' : '#e8eaf0';
    return `<td style="padding:3px 7px;border:1px solid #2e3345;background:${bg};color:${col};text-align:center;min-width:34px;">${fmt(v)}</td>`;
  }

  function editableInput(store, i, j) {
    const v = store[i][j];
    return `<td style="padding:2px 4px;border:1px solid #2e3345;background:#141a28;text-align:center;">
      <input type="number" step="0.1" value="${v}" data-key="${store === Q ? 'Q' : store === K ? 'K' : 'V'}" data-i="${i}" data-j="${j}"
        style="width:52px;background:#0f1420;color:#bfdbfe;border:1px solid #334155;border-radius:3px;font-size:0.75rem;padding:1px 3px;">
    </td>`;
  }

  function matTable(m, colLabels, editableStore) {
    let html = '<table style="border-collapse:collapse;font-size:0.78rem;">';
    html += '<tr><th></th>' + colLabels.map(c => `<th style="color:#9aa3b8;font-weight:normal;padding:2px 6px;">${c}</th>`).join('') + '</tr>';
    m.forEach((row, i) => {
      html += `<tr><th style="color:#9aa3b8;font-weight:normal;padding:2px 6px;text-align:right;">${tokens[i]}</th>`;
      row.forEach((v, j) => { html += editableStore ? editableInput(editableStore, i, j) : td(v); });
      html += '</tr>';
    });
    return html + '</table>';
  }

  function labeledTable(store, label) {
    return `<div style="margin:4px 6px 4px 0;">
      <div style="color:#6c9eff;font-size:0.72rem;margin-bottom:2px;">${label}</div>
      ${matTable(store, DIMS, store)}
    </div>`;
  }

  const tokensRow = () => `<div style="display:flex;gap:6px;margin:6px 0;flex-wrap:wrap;">` +
    tokens.map((tk, i) => `<span style="padding:3px 10px;border-radius:12px;background:#1e3a5f;color:#bfdbfe;border:1px solid #6c9eff;font-size:0.78rem;">${i}: ${tk}</span>`).join('') + `</div>`;

  const trio = () => `<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:10px;border-top:1px dashed #2e3345;padding-top:8px;">
    ${labeledTable(Q, t.tblQ)}${labeledTable(K, t.tblK)}${labeledTable(V, t.tblV)}
  </div>`;

  const logs = { 0: t.ready, 1: t.s1, 2: t.s2, 3: t.s3, 4: t.s4, 5: t.s5, 6: t.s6 };

  function render() {
    const S = matmul(Q, transpose(K));
    const M = S.map((row, i) => row.map((v, j) => (j > i ? -Infinity : v)));
    const A = M.map(row => softmaxArr(row));
    const O = matmul(A, V);

    let html = tokensRow();
    if (step === 0) {
      html += `<div style="padding:8px 4px;color:#9aa3b8;">${t.ready}</div>`;
    } else if (step === 1) {
      html += trio();
    } else if (step === 2) {
      html += matTable(S, tokens) + trio();
    } else if (step === 3) {
      html += matTable(M, tokens) + trio();
    } else if (step === 4) {
      html += matTable(A, tokens) + trio();
    } else if (step === 5) {
      html += matTable(O, DIMS) + trio();
    } else {
      html += `<div style="padding:8px 4px;color:#34d399;">${t.recap}</div>`;
    }
    matrixEl.innerHTML = html;
    logEl.textContent = logs[step];

    if (focus) {
      const el = matrixEl.querySelector(`input[data-key="${focus.key}"][data-i="${focus.i}"][data-j="${focus.j}"]`);
      if (el) { el.focus(); const n = el.value.length; try { el.setSelectionRange(n, n); } catch (e) { /* not focusable */ } }
      focus = null;
    }
  }

  matrixEl.addEventListener('input', (e) => {
    const inp = e.target.closest('input[data-key]');
    if (!inp) return;
    const v = parseFloat(inp.value);
    if (!Number.isFinite(v)) return;
    const store = { Q, K, V }[inp.dataset.key];
    store[+inp.dataset.i][+inp.dataset.j] = v;
    focus = { key: inp.dataset.key, i: +inp.dataset.i, j: +inp.dataset.j };
    render();
  });

  stepBtn.onclick = () => { step = (step + 1) % (MAX_STEP + 1); render(); };
  resetBtn.onclick = () => { step = 0; Q = defQ(); K = defK(); V = defV(); render(); };

  stepBtn.textContent = t.stepBtn;
  resetBtn.textContent = t.resetBtn;
  render();
}

/* ==================== Sampler Playground (temperature + top-k) ==================== */
function initSamplerPlayground() {
  const root = document.getElementById('sampler-toy');
  if (!root) return;

  const logits = [2.8, 1.9, 0.7, -0.4, -1.6]; // fake next-token logits for 5 possible tokens
  const labels = ['the', 'a', 'cat', 'dog', 'xyz'];

  let temp = 1.0;
  let topk = 5;

  const tempSlider = root.querySelector('#temp');
  const topkSlider = root.querySelector('#topk');
  const tempVal = root.querySelector('#temp-val');
  const topkVal = root.querySelector('#topk-val');
  const beforeEl = root.querySelector('#bars-before');
  const afterEl = root.querySelector('#bars-after');
  const sampleEl = root.querySelector('#sample-result');

  function softmax(arr) {
    const m = Math.max(...arr);
    const ex = arr.map(v => Math.exp(v - m));
    const s = ex.reduce((a,b)=>a+b,0);
    return ex.map(e => e/s);
  }

  function drawBars(container, probs, highlightIdx = -1) {
    container.innerHTML = '';
    probs.forEach((p, i) => {
      const row = document.createElement('div');
      row.className = 'bar-row';
      const pct = (p * 100).toFixed(1);
      row.innerHTML = `
        <div style="width:52px;color:#9aa3b8;">${labels[i]}</div>
        <div style="flex:1;background:#2f364a;border-radius:3px;overflow:hidden;height:18px;">
          <div class="bar" style="width:${Math.max(2, p*100)}%;background:${i===highlightIdx?'#fb923c':'linear-gradient(90deg,#34d399,#6c9eff)'}"></div>
        </div>
        <div style="width:46px;text-align:right;color:#a5d6a7;">${pct}%</div>
      `;
      container.appendChild(row);
    });
  }

  function update() {
    temp = parseFloat(tempSlider.value);
    topk = parseInt(topkSlider.value, 10);
    tempVal.textContent = temp.toFixed(1);
    topkVal.textContent = topk;

    // before (raw temp=1)
    const probsRaw = softmax(logits);
    drawBars(beforeEl, probsRaw);

    // after temperature + optional top-k
    let adj = logits.map(v => v / temp);
    if (topk < 5) {
      const sorted = [...adj].sort((a,b)=>b-a);
      const cutoff = sorted[topk-1];
      adj = adj.map(v => v < cutoff ? -1e9 : v);
    }
    const probsAdj = softmax(adj);
    drawBars(afterEl, probsAdj);

    // sample one (deterministic for demo: pick argmax after adjustment, or random-ish)
    let chosen = probsAdj.indexOf(Math.max(...probsAdj));
    sampleEl.innerHTML = `最可能的结果（演示）： <strong style="color:#fb923c">${labels[chosen]}</strong> (p=${(probsAdj[chosen]*100).toFixed(1)}%)`;
  }

  tempSlider.oninput = update;
  topkSlider.oninput = update;

  root.querySelector('#sample-btn').onclick = () => {
    // real multinomial simulation in JS
    let adj = logits.map(v => v / temp);
    if (topk < 5) {
      const sorted = [...adj].sort((a,b)=>b-a);
      const cutoff = sorted[topk-1];
      adj = adj.map(v => v < cutoff ? -1e9 : v);
    }
    const probs = softmax(adj);
    // cumulative
    let r = Math.random();
    let cum = 0;
    let chosen = 0;
    for (let i=0; i<probs.length; i++) {
      cum += probs[i];
      if (r <= cum) { chosen = i; break; }
    }
    sampleEl.innerHTML = `🎲 真正随机采样：<strong style="color:#fb923c;font-size:1.05em">${labels[chosen]}</strong> (约 ${ (probs[chosen]*100).toFixed(1) }%)`;
  };

  // init
  update();
}

/* Boot the toys — each init is isolated so one failure can never break the others */
document.addEventListener('DOMContentLoaded', () => {
  [initCodeCopyButtons, initAttentionToy, initSamplerPlayground].forEach((fn) => {
    try { fn(); } catch (err) { console.error('[learning_guide] init failed:', fn.name, err); }
  });
});

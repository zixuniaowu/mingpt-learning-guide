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

/* ==================== Interactive Attention Toy (Causal) ==================== */
function initAttentionToy() {
  const root = document.getElementById('attn-toy');
  if (!root) return;

  const tokens = ['A', 'B', 'C', 'D']; // toy sequence of length 4
  let step = 0;
  const logEl = root.querySelector('.toy-log');
  const matrixEl = root.querySelector('.toy-matrix');

  function renderMatrix(mat, label) {
    let html = `<div style="color:#9aa3b8;font-size:0.75rem;margin:4px 0;">${label}</div>`;
    html += '<table style="border-collapse:collapse;font-size:0.78rem;">';
    mat.forEach(row => {
      html += '<tr>';
      row.forEach(v => {
        const bg = v === '-inf' ? '#3a2a1f' : (v > 0.3 ? '#14352a' : '#1a2332');
        const col = v === '-inf' ? '#fb923c' : '#e8eaf0';
        html += `<td style="padding:3px 7px;border:1px solid #2e3345;background:${bg};color:${col};text-align:center;min-width:32px;">${v}</td>`;
      });
      html += '</tr>';
    });
    html += '</table>';
    matrixEl.innerHTML = html;
  }

  function log(msg) {
    logEl.textContent = msg;
  }

  // initial: show input tokens
  function reset() {
    step = 0;
    matrixEl.innerHTML = `<div style="padding:8px;color:#9aa3b8;">点击“计算 Q/K/V” 开始逐步演示因果自注意力（T=4 玩具序列）</div>`;
    logEl.textContent = '就绪：序列 = [' + tokens.join(', ') + ']  |  每个位置只能看到自己及左侧';
  }

  root.querySelector('#attn-step').onclick = () => {
    step = (step + 1) % 6;
    if (step === 0) { reset(); return; }

    if (step === 1) {
      const qk = [
        [1.0, 0.2, 0.1, 0.0],
        [0.3, 1.1, 0.4, 0.2],
        [0.2, 0.5, 0.9, 0.3],
        [0.1, 0.3, 0.6, 1.2]
      ];
      renderMatrix(qk.map(r => r.map(x => x.toFixed(1))), '步骤1: 计算相关性分数 (Q 和 K 做点积)');
      log('每个位置都算了自己和前面所有位置的“匹配分数”。分数越高越相关。');
    } else if (step === 2) {
      const masked = [
        ['1.0', '-inf', '-inf', '-inf'],
        ['0.3', '1.1', '-inf', '-inf'],
        ['0.2', '0.5', '0.9', '-inf'],
        ['0.1', '0.3', '0.6', '1.2']
      ];
      renderMatrix(masked, '步骤2: 因果掩码（未来位置全部设为 -∞）');
      log('这里最关键！位置 0 完全看不到 1、2、3；位置 1 看不到 2、3。这就是“不能偷看未来”。');
    } else if (step === 3) {
      const sm = [
        [1.00, 0.00, 0.00, 0.00],
        [0.31, 0.69, 0.00, 0.00],
        [0.18, 0.24, 0.58, 0.00],
        [0.12, 0.15, 0.20, 0.53]
      ];
      renderMatrix(sm.map(r => r.map(x => x.toFixed(2))), '步骤3: Softmax 变成注意力权重（每行加起来=1）');
      log('现在分数变成了百分比。位置 0 100% 关注自己；位置 3 把注意力分配给了前面 4 个位置。');
    } else if (step === 4) {
      const out = [
        [0.82, 0.11, -0.05],
        [0.41, 0.67, 0.12],
        [0.25, 0.39, 0.55],
        [0.09, 0.28, 0.71]
      ];
      renderMatrix(out.map(r => r.map(x => x.toFixed(2))), '步骤4: 用权重加权 Value，得到这个位置的新表示');
      log('每个位置现在都“汇总”了它被允许看到的所有信息。');
    } else if (step === 5) {
      matrixEl.innerHTML = `<div style="padding:8px 4px;color:#34d399;">✓ 自注意力完成！后面还会做残差连接 + LayerNorm + MLP（前馈网络）。</div>`;
      log('演示完毕。真实模型里这 4 个位置会同时在多个头上并行计算。你可以重置再看一遍。');
    }
  };

  root.querySelector('#attn-reset').onclick = reset;
  reset();
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

/* Boot the new toys */
document.addEventListener('DOMContentLoaded', () => {
  initCodeCopyButtons();
  initAttentionToy();
  initSamplerPlayground();
});

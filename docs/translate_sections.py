# Translate ALL EN-glish sections body text to Chinese in the CN file
# Process: read EN section content, write Chinese translation, replace in CN file

with open('C:/Users/zixun/dev/minGPT/docs/learning_guide_en.html', 'r', encoding='utf-8') as f:
    en = f.read()
with open('C:/Users/zixun/dev/minGPT/docs/learning_guide.html', 'r', encoding='utf-8') as f:
    cn = f.read()

changes = 0

# ===== SECTION: ATTENTION =====
print('Translating: attention...')
attn_en = en[en.find('<section id="attention"'):en.find('</section>', en.find('<section id="attention"'))+11]
attn_cn_start = cn.find('<section id="attention"')
attn_cn_end = cn.find('</section>', attn_cn_start) + 11

# Build Chinese version
attn_zh = '''<section id="attention">
  <h3>5. 自注意力机制：Transformer 的核心</h3>

  <p>自注意力（Self-Attention）是 Transformer 区别于之前所有序列模型的根本创新。它让模型能够直接"看到"序列中任意两个位置的关系，而不需要像 RNN 那样一步步传递信息。</p>

  <h3>第一性原理：为什么需要注意力？</h3>
  <p>想象你在读一句话："我去银行存钱，因为我需要支付房租。"当你读到"支付"时，你需要回想前面的"房租"和"银行"。大脑会自动把"支付"和"房租"关联起来，把"银行"和"存钱"关联起来。</p>
  <p>RNN 只能把前面所有信息压缩成一个隐藏状态，容易丢失细节。注意力则允许每个词直接"查询"其他所有词，决定自己应该关注什么。</p>

  <h3>自注意力的计算过程（直觉 + 数学）</h3>
  <p>自注意力可以拆成三个概念：Query、Key、Value。可以这样理解：</p>
  <ul>
    <li><strong>Query (Q)</strong>：当前词"想问什么问题"？（"谁和我相关？"）</li>
    <li><strong>Key (K)</strong>：其他每个词"有什么信息"？（"我是第 3 个词，内容是 '存钱'"）</li>
    <li><strong>Value (V)</strong>：如果相关，其他词"要传递什么内容"？</li>
  </ul>
  <p>计算分为五步：</p>
  <ol>
    <li><strong>Q × K 点积</strong>：每个词和其他所有词做点积，得到一个"注意力分数"矩阵（T×T）。数值越大表示越相关。</li>
    <li><strong>缩放（Scale）</strong>：除以 sqrt(d_k)，防止维度高时点积太大把 softmax 推向极端。</li>
    <li><strong>因果掩码（Mask）</strong>：GPT 只能看左边的词，所以把未来位置设为 -inf（softmax 后变成 0）。</li>
    <li><strong>Softmax</strong>：把每一行的分数归一化成概率分布。</li>
    <li><strong>加权求和</strong>：用概率分布对 Value 做加权平均，得到每个位置的输出。</li>
  </ol>

  <p>用公式表达（单头注意力）：</p>
  <div class="formula">Attention(Q, K, V) = softmax(QK^T / √d_k) · V</div>

  <h3>多头注意力机制</h3>
  <p>与其让一个注意力"专家"处理所有关系，不如让多个专家各司其职。每个头学习不同类型的注意力：一个头可能关注语法关系（哪个形容词修饰哪个名词），另一个头关注位置关系（"他"指代前文提到的谁），还有一个头关注语义相关性（"银行"和"存钱"的关联）。</p>
  <p>计算时，Q、K、V 被分割成 n_head 份。每个头独立计算注意力，结果再拼接并通过一个线性投影合并。在 minGPT 的 gpt-nano 中：n_embd=48, n_head=4，每个头只能看到 12 维——这意味着每个头的"视野"很窄，但它们各自的贡献拼接起来后仍然有完整的表达能力。</p>

  <h3>与 RNN/LSTM 的本质对比</h3>
  <table>
    <tr><th>特性</th><th>RNN/LSTM</th><th>Transformer Self-Attention</th></tr>
    <tr><td>并行度</td><td>极差（必须一步步走）</td><td>全部位置同时计算</td></tr>
    <tr><td>长距离依赖</td><td>路径长度=序列长度的 O(1)（理论上可以，但实践中很难学到长距离依赖）</td><td>一步直达，路径长度=1</td></tr>
    <tr><td>梯度问题</td><td>严重的梯度消失/爆炸</td><td>残差连接后梯度非常稳定</td></tr>
    <tr><td>计算复杂度</td><td>O(T·d²)</td><td>O(T²·d)</td></tr>
    <tr><td>位置编码</td><td>天然有序（一步步来）</td><td>必须外加位置信息</td></tr>
    <tr><td>可解释性</td><td>隐藏状态难解释</td><td>注意力权重可直接可视化</td></tr>
  </table>

  <p>RNN 的关键弱点在于"信息瓶颈"——每个时间步只有一个隐藏状态向量，无法保存所有历史细节。注意力的核心优势在于"直接访问"——每个位置可以直接查看任何其他位置。实际上，Transformer 在许多领域的成功正是源于去除了归纳偏置（inductive biases），让模型自己从数据中发现模式。</p>

  <h3>与线性注意力 / State Space Model 的对比</h3>
  <p>最近的工作（Mamba、RWKV、RetNet）探索了替代注意力的线性复杂度架构：</p>
  <ul>
    <li><strong>线性注意力 / Mamba</strong>：用递归或状态空间模型替代 QK^T，将复杂度从 O(T²) 降到 O(T)。但代价是失去了"任意位置直接访问"的能力。</li>
    <li><strong>RWKV</strong>：结合了 Transformer 的训练便利性和 RNN 的推理效率。</li>
    <li><strong>RetNet</strong>：提出"保留机制"，在并行训练和递归推理之间优雅切换。</li>
  </ul>
  <p>这些工作的共同主题：能否在保持 Transformer 质量的同时，消除 O(T²) 的扩展瓶颈？到目前为止，对于非常长的序列（>16K token），这些替代方案确实有优势；但对于大多数 LLM 应用（4K-8K 长度），标准注意力仍然是默认选择。</p>

  <h3>注意力作为"软性字典查找"</h3>
  <p>理解注意力的另一种方式是"软性字典查询"：</p>
  <ul>
    <li>你有一个键-值字典 {key_i: value_i}。</li>
    <li>当输入一个查询 q 时，你不只找一个精确匹配的键；你对所有键都计算"兼容性分数"。</li>
    <li>结果是从所有值中插值出来的——根据与每个键的匹配程度加权平均。</li>
  </ul>
  <p>这就是为什么它被称为"软性"——它不是硬性选择某一个值，而是所有值的加权混合。softmax 的温度控制这个混合有多"尖锐"（是否接近 one-hot 选择）。</p>

  <h3>多头注意力的不同"专家"</h3>
  <p>多头注意力之所以有效，是因为不同的头可以学习到不同类型的注意力模式：</p>
  <ul>
    <li>有些头主要关注<strong>语法关系</strong>（主语-动词一致性、形容词-名词修饰）。</li>
    <li>有些头关注<strong>位置关系</strong>（相邻词、前一句的对应词）。</li>
    <li>有些头关注<strong>语义内容</strong>（"它"指代什么，"银行"在说什么语境）。</li>
    <li>有些头可能是<strong>冗余的</strong>（提供类似信息的多个视角，增加鲁棒性）。</li>
  </ul>

  <h3>与高效注意力变体的对比</h3>
  <table>
    <tr><th>变体</th><th>复杂度</th><th>关键思想</th></tr>
    <tr><td>标准注意力</td><td>O(T²·d)</td><td>每个位置关注所有位置</td></tr>
    <tr><td>FlashAttention</td><td>O(T²·d) 但快得多</td><td>分块 + 融合 softmax，IO 感知算法</td></tr>
    <tr><td>Performer (FAVOR+)</td><td>O(T·d²)</td><td>核方法近似 softmax</td></tr>
    <tr><td>GQA / MQA</td><td>O(T²·d) 但 KV 缓存小得多</td><td>多个查询头共享键/值</td></tr>
    <tr><td>Sliding Window</td><td>O(T·W·d)</td><td>每个位置只看窗口 W 内的局部邻居</td></tr>
  </table>

  <h3>因果掩码（Causal Mask）的重要性</h3>
  <p>在自回归语言模型中，因果掩码防止每个位置"偷看"未来的 token。这是 GPT 与 BERT 的核心区别之一：</p>
  <ul>
    <li>没有因果掩码：双向注意力（BERT）——每个位置看到整个序列，适合理解任务。</li>
    <li>有因果掩码：单向注意力（GPT）——每个位置只看到自己和之前的位置，适合生成任务。</li>
  </ul>
  <p>在 minGPT 中，因果掩码通过一个下三角布尔矩阵实现。代码中直接创建并缓存它：</p>
  <pre><code># causal mask to hide future tokens
self.register_buffer("bias", torch.tril(torch.ones(block_size, block_size))
                             .view(1, 1, block_size, block_size))</code></pre>

  <h3>用具体的 4-token 例子跟踪注意力</h3>
  <p>假设序列是 "I like cats"（4 个 token）。token 0="I"，token 1="like"，token 2="cats"。</p>
  <p>当我们为 token 1 计算输出时（它是第 2 个词 "like"）：</p>
  <ul>
    <li><strong>Step 1（生成 Q1）</strong>："like" 用一个投影矩阵乘以它的嵌入，生成查询向量 q1。</li>
    <li><strong>Step 2（准备 K、V）</strong>：所有三个 token 也都生成各自的键 k0、k1、k2 和值 v0、v1、v2。</li>
    <li><strong>Step 3（计算分数）</strong>：q1·k0（"like" vs "I"）= 0.7，q1·k1（"like" vs "like"）= 1.2，q1·k2（"like" vs "cats"）= -0.3。</li>
    <li><strong>Step 4（因果掩码 + Softmax）</strong>：分数 → [0.7, 1.2, -inf] → softmax → [0.38, 0.62, 0.0]。</li>
    <li><strong>Step 5（加权和）</strong>："like" 的输出 = 0.38×v0 + 0.62×v1。它完全忽略了 token 2（cats），因为因果掩码把它屏蔽了。</li>
  </ul>
  <p>这就是每一个 token 在每一层如何"关注"左边所有 token 的过程。在 4 个头的 multi-head 中，这个五步过程在 4 个不同的 Q/K/V 子空间上并行发生。</p>

  <h3>核心代码实现（mingpt/model.py）</h3>
  <pre><code>class CausalSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        assert config.n_embd % config.n_head == 0
        # key, query, value projections for all heads
        self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd)
        # output projection
        self.c_proj = nn.Linear(config.n_embd, config.n_embd)
        # regularization
        self.attn_dropout = nn.Dropout(config.attn_pdrop)
        self.resid_dropout = nn.Dropout(config.resid_pdrop)
        # causal mask
        self.register_buffer("bias", torch.tril(
            torch.ones(config.block_size, config.block_size))
            .view(1, 1, config.block_size, config.block_size))</code></pre>

  <p><code>c_attn</code> 是一个单独的线性层，一次性生成 Q、K、V（3 倍嵌入维度）。然后通过 <code>.split</code> 将它们拆开。然后进行批量矩阵乘法计算注意力分数。</p>

  <h3>minGPT 实现中的实践洞察</h3>
  <p>minGPT 的实现虽然简洁，但包含了所有核心要素：</p>
  <ul>
    <li>单头注意力在 gpt-nano 中：48 维嵌入被 4 个头分成 4×12 维。每个头只在一个 12 维子空间上计算注意力——但它们的输出拼接后恢复到完整的 48 维。</li>
    <li>因果掩码使用 <code>masked_fill</code>：将来位置设为 -inf，让 softmax 输出 0。这个操作虽然简单，但实际计算中仍然会为未来位置进行完整的 QK^T 计算——只是结果被忽略了。FlashAttention 等优化可以跳过这些计算。</li>
    <li>注意力 dropout 是在注意力权重上应用的（softmax 之后），而不是在分数上。这类似于在"软性选择"中随机丢弃一些连接。</li>
  </ul>

  <h3>交互式注意力小工具</h3>
  <p>下面的交互式工具让你逐步查看 4 个 token 的注意力过程。点击"Next Step"逐步推演，或用滑块调整某个 token 的查询向量，观察注意力分布如何变化。</p>
  <div id="attn-toy" class="toy-container"><div class="attn-grid"><div class="attn-step"><div class="step-label">Step 0: Input tokens</div><div class="token-row"><span class="token t0">I</span><span class="token t1">like</span><span class="token t2">cats</span><span class="token t3">&lt;pad&gt;</span></div></div><div class="attn-step"><div class="step-label">Step 1: QKV projection</div><div class="qkv-vis"><div class="qkv-row"><span class="qkv-label">Q</span><div class="qkv-bar" style="width:40%"></div></div><div class="qkv-row"><span class="qkv-label">K</span><div class="qkv-bar" style="width:55%"></div></div><div class="qkv-row"><span class="qkv-label">V</span><div class="qkv-bar" style="width:35%"></div></div></div></div><div class="attn-step"><div class="step-label">Step 2: Attention scores (Q·K)</div><div class="score-matrix"><div class="score-row"><span class="token-ref">I</span><span class="score s0">0.7</span><span class="score s1">0.2</span><span class="score s2">-0.1</span><span class="score s3">0.0</span></div><div class="score-row"><span class="token-ref">like</span><span class="score s0">0.3</span><span class="score s1">1.2</span><span class="score s2">0.5</span><span class="score s3">0.0</span></div><div class="score-row"><span class="token-ref">cats</span><span class="score s0">-0.2</span><span class="score s1">0.4</span><span class="score s2">0.9</span><span class="score s3">0.0</span></div><div class="score-row"><span class="token-ref">&lt;pad&gt;</span><span class="score s0">0.0</span><span class="score s1">0.0</span><span class="score s2">0.0</span><span class="score s3">0.0</span></div></div></div></div></div>
</section>'''

cn = cn[:attn_cn_start] + attn_zh + cn[attn_cn_end:]
changes += 1

# ===== SECTION: BLOCK =====
print('Translating: block...')
block_zh = '''<section id="block">
  <h3>6. Transformer Block 详解</h3>

  <p>Transformer Block 是 GPT 的基本构建单元。每个 Block 包含两个子层，每个子层周围都有残差连接和层归一化（LayerNorm）。</p>

  <div class="diagram" style="text-align:center;padding:1rem">
    <svg width="400" height="480" viewBox="0 0 400 480" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="12">
      <defs>
        <linearGradient id="b1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2f364a"/><stop offset="100%" stop-color="#1a2332"/></linearGradient>
        <marker id="arr" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto"><polygon points="0 0,7 2.5,0 5" fill="#6c9eff"/></marker>
      </defs>
      <rect x="100" y="10" width="200" height="50" rx="8" fill="url(#b1)" stroke="#6c9eff"/>
      <text x="200" y="40" text-anchor="middle" fill="#6c9eff" font-weight="bold">输入 x</text>
      <line x1="200" y1="60" x2="200" y2="90" stroke="#6c9eff" stroke-width="2"/>
      <rect x="100" y="90" width="200" height="40" rx="8" fill="url(#b1)" stroke="#f5a623"/>
      <text x="200" y="115" text-anchor="middle" fill="#f5a623">LayerNorm</text>
      <line x1="200" y1="130" x2="200" y2="155" stroke="#f5a623" stroke-width="2"/>
      <rect x="100" y="155" width="200" height="50" rx="8" fill="url(#b1)" stroke="#34d399"/>
      <text x="200" y="185" text-anchor="middle" fill="#34d399" font-weight="bold">多头注意力</text>
      <line x1="200" y1="205" x2="200" y2="230" stroke="#34d399" stroke-width="2"/>
      <rect x="100" y="230" width="80" height="30" rx="5" fill="url(#b1)" stroke="#9aa3b8"/>
      <text x="140" y="250" text-anchor="middle" fill="#9aa3b8" font-size="10">残差 +</text>
      <line x1="280" y1="35" x2="310" y2="35" stroke="#9aa3b8" stroke-width="1.5" stroke-dasharray="4"/>
      <line x1="310" y1="35" x2="310" y2="245" stroke="#9aa3b8" stroke-width="1.5" stroke-dasharray="4"/>
      <line x1="310" y1="245" x2="220" y2="245" stroke="#9aa3b8" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#arr)"/>
      <line x1="200" y1="260" x2="200" y2="290" stroke="#6c9eff" stroke-width="2"/>
      <rect x="100" y="290" width="200" height="40" rx="8" fill="url(#b1)" stroke="#f5a623"/>
      <text x="200" y="315" text-anchor="middle" fill="#f5a623">LayerNorm</text>
      <line x1="200" y1="330" x2="200" y2="355" stroke="#f5a623" stroke-width="2"/>
      <rect x="100" y="355" width="200" height="50" rx="8" fill="url(#b1)" stroke="#a78bfa"/>
      <text x="200" y="385" text-anchor="middle" fill="#a78bfa" font-weight="bold">前馈网络 (FFN)</text>
      <line x1="200" y1="405" x2="200" y2="430" stroke="#a78bfa" stroke-width="2"/>
      <rect x="100" y="430" width="80" height="30" rx="5" fill="url(#b1)" stroke="#9aa3b8"/>
      <text x="140" y="450" text-anchor="middle" fill="#9aa3b8" font-size="10">残差 +</text>
      <line x1="280" y1="315" x2="310" y2="315" stroke="#9aa3b8" stroke-width="1.5" stroke-dasharray="4"/>
      <line x1="310" y1="315" x2="310" y2="445" stroke="#9aa3b8" stroke-width="1.5" stroke-dasharray="4"/>
      <line x1="310" y1="445" x2="220" y2="445" stroke="#9aa3b8" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#arr)"/>
      <text x="200" y="475" text-anchor="middle" fill="#6c9eff" font-size="11">输出 x' = x + Sublayer(LayerNorm(x))</text>
    </svg>
  </div>

  <p>一个标准的 Transformer Block 遵循 Pre-LayerNorm 模式（GPT-2 引入）：</p>
  <div class="formula">x ← x + Attention(LayerNorm(x))
x ← x + FFN(LayerNorm(x))</div>

  <p>其中 Attention 可以是因果自注意力、交叉注意力或掩码注意力。在 GPT 的纯 decoder 架构中，所有 Block 都使用因果自注意力。</p>

  <h3>为什么 Transformer Block 要这样设计？</h3>
  <p>可以把一个 Block 类比为一场高效的会议：</p>
  <ul>
    <li><strong>LayerNorm（调节音量）</strong>：在每个人发言前，先把所有人的音量调到统一水平。LayerNorm 稳定了每个子层的输入分布，使训练更加稳健。</li>
    <li><strong>注意力（讨论环节）</strong>：每个人查看其他人说的内容，决定自己要说什么。这是信息交换的环节。</li>
    <li><strong>残差连接（保留笔记）</strong>：即使讨论跑偏了，你还有之前的笔记可以参考。这使得梯度可以直接流过整个网络，解决了深层网络的退化问题。</li>
    <li><strong>FFN（深入思考）</strong>：在获取了所有信息后，FFN 让每个位置独立地"深入思考"——将收集到的信息转换成更有用的表示。</li>
  </ul>

  <h3>FFN 的 4 倍扩展——为什么有效？</h3>
  <p>前馈网络通常将嵌入维度扩展到 4 倍：n_embd → 4×n_embd → n_embd。这样设计是因为它给模型提供了一个"暂存空间"来扩展中间表示。注意力负责收集信息（跨位置的混合），而 FFN 负责处理信息（每个位置的独立转换）。4× 倍率是实践中被证明效果良好的选择，现代架构如 LLaMA 和 Mistral 也继承了这一设计。</p>

  <h3>Block 设计演进与现代变体</h3>
  <table>
    <tr><th>架构</th><th>归一化位置</th><th>激活函数</th><th>FFN 变体</th></tr>
    <tr><td>原始 Transformer (2017)</td><td>Post-LN（每个子层之后）</td><td>ReLU</td><td>标准 FFN</td></tr>
    <tr><td>GPT-2 (2019)</td><td>Pre-LN（每个子层之前）</td><td>GELU</td><td>标准 FFN</td></tr>
    <tr><td>LLaMA (2023)</td><td>Pre-LN (RMSNorm)</td><td>SwiGLU</td><td>8/3 × 倍率的门控 FFN</td></tr>
    <tr><td>Mistral (2023)</td><td>Pre-LN (RMSNorm)</td><td>SiLU</td><td>滑动窗口注意力 + 标准 FFN</td></tr>
  </table>

  <h3>设计要点（简化版）</h3>
  <ul>
    <li><strong>为什么先 LayerNorm 再子层？</strong> GPT-2 发现 Pre-LN 更稳定——梯度可以直接通过残差路径流动。Post-LN 在深层网络中容易导致训练不稳定。</li>
    <li><strong>注意力 + FFN 的顺序重要吗？</strong> 经验表明"先注意力再 FFN"比反过来要好。注意力负责混合信息，FFN 负责独立处理——先获取上下文再深入思考更合理。</li>
    <li><strong>Dropout</strong>：在注意力权重上和残差输出上应用 dropout 作为正则化。对于小模型，dropout 很有帮助（防止过拟合）；对于大模型和大量数据，dropout 通常被关闭或设得很小。</li>
  </ul>
</section>'''

block_cn_start = cn.find('<section id="block"')
block_cn_end = cn.find('</section>', block_cn_start) + 11
cn = cn[:block_cn_start] + block_zh + cn[block_cn_end:]
changes += 1

# ===== SECTION: GPT =====
print('Translating: gpt...')
gpt_zh = '''<section id="gpt">
  <h3>7. GPT 完整架构与设计选择</h3>

  <p>现在我们将所有组件组合成完整的 GPT 模型。从嵌入层到输出层，GPT 是一个纯 decoder-only 的 Transformer 架构。</p>

  <h3>GPT 完整数据流</h3>
  <ol>
    <li><strong>Token 嵌入</strong>：输入 token ID 通过 wte（词嵌入矩阵）映射为密集向量。形状：(B, T) → (B, T, n_embd)。</li>
    <li><strong>位置嵌入</strong>：通过 wpe（位置嵌入矩阵）为每个位置添加位置信息。形状：(T,) → (T, n_embd)。广播到批次维度。</li>
    <li><strong>逐 Block 处理</strong>：通过 n_layer 个 Transformer Block 依次处理。每个 Block 保持形状 (B, T, n_embd)。</li>
    <li><strong>最终 LayerNorm</strong>：在输出到 lm_head 之前做一次归一化。</li>
    <li><strong>LM Head</strong>：将 (B, T, n_embd) 投影到 (B, T, vocab_size)，得到每个位置对词表中每个词的分数（logits）。</li>
    <li><strong>（推理时）Softmax + 采样</strong>：logits → softmax → 概率分布 → 采样下一个 token。</li>
  </ol>

  <h3>架构对比：BERT、LLaMA、Mistral 等</h3>
  <table>
    <tr><th>架构</th><th>注意力模式</th><th>归一化</th><th>激活函数</th><th>位置编码</th></tr>
    <tr><td>GPT-2</td><td>因果（decoder-only）</td><td>Pre-LN</td><td>GELU</td><td>可学习</td></tr>
    <tr><td>BERT</td><td>双向（encoder-only）</td><td>Post-LN</td><td>GELU</td><td>可学习</td></tr>
    <tr><td>LLaMA</td><td>因果 + 分组查询注意力</td><td>RMSNorm (Pre)</td><td>SwiGLU</td><td>RoPE</td></tr>
    <tr><td>Mistral</td><td>因果 + 滑动窗口</td><td>RMSNorm (Pre)</td><td>SiLU</td><td>RoPE</td></tr>
    <tr><td>GPT-3</td><td>因果 + 交替密集/稀疏</td><td>Pre-LN</td><td>GELU</td><td>可学习</td></tr>
  </table>

  <h3>为什么 Pre-LN 比 Post-LN 更稳定？</h3>
  <p>在 Post-LN 中，层归一化在残差相加之后：Output = LN(x + Sublayer(x))。这意味着归一化在残差混合之后进行，梯度的路径更长。在 Pre-LN 中：Output = x + Sublayer(LN(x))。归一化在子层之前，残差路径是完全不受干扰的——梯度可以直接流过整个网络。实验表明，Pre-LN 允许更高的学习率和更深层的网络而不爆炸。</p>

  <h3>架构演进：代码级深入解析</h3>

  <h4>RMSNorm vs LayerNorm</h4>
  <p>RMSNorm 是 LayerNorm 的简化版本——它只对均方根进行归一化，而不减去均值。LLaMA 证明了这对 Transformer 训练同样有效，且节省了约 5-10% 的归一化计算量。</p>
  <pre><code># LayerNorm: y = (x - E[x]) / sqrt(Var[x] + eps) * gamma + beta
# RMSNorm:  y = x / sqrt(mean(x^2) + eps) * gamma</code></pre>

  <h4>SwiGLU vs GELU</h4>
  <p>SwiGLU 是 Swish + GLU（门控线性单元）的组合。相比 GELU，它在相同的计算预算下通常能获得更好的质量。代价是 FFN 的参数增加了约 33%（因为门控需要额外的投影矩阵）。</p>
  <pre><code># GELU:            output = x * Phi(x)
# SwiGLU:          output = (x * sigmoid(x * beta)) * (W_gate * x)</code></pre>

  <h4>从 MHA 到 GQA：KV Cache 的演进</h4>
  <p>多头注意力（MHA）中每个头都有自己的 K 和 V。对于长序列，KV cache 变得巨大，成为推理的瓶颈。GQA（分组查询注意力）让多个查询头共享键和值头，在几乎不损失质量的情况下大幅减少了 KV cache 大小。</p>

  <div class="diagram" style="text-align:center;padding:0.5rem">
    <svg width="400" height="160" viewBox="0 0 400 160" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="10">
      <rect x="10" y="15" width="120" height="130" rx="6" fill="#2f364a" stroke="#6c9eff"/>
      <text x="70" y="35" text-anchor="middle" fill="#6c9eff" font-weight="bold">MHA</text>
      <text x="70" y="55" text-anchor="middle" fill="#e8eaf0">Q1 K1 V1</text>
      <text x="70" y="70" text-anchor="middle" fill="#e8eaf0">Q2 K2 V2</text>
      <text x="70" y="85" text-anchor="middle" fill="#f5a623">...8 heads...</text>
      <text x="70" y="105" text-anchor="middle" fill="#e8eaf0">Q8 K8 V8</text>
      <text x="70" y="130" text-anchor="middle" fill="#f87171" font-size="9">KV 大</text>
      <rect x="145" y="15" width="110" height="130" rx="6" fill="#2f364a" stroke="#34d399"/>
      <text x="200" y="35" text-anchor="middle" fill="#34d399" font-weight="bold">GQA</text>
      <text x="200" y="55" text-anchor="middle" fill="#e8eaf0">Q1 Q2 K1 V1</text>
      <text x="200" y="75" text-anchor="middle" fill="#e8eaf0">Q3 Q4 K2 V2</text>
      <text x="200" y="95" text-anchor="middle" fill="#f5a623">4 组</text>
      <text x="200" y="130" text-anchor="middle" fill="#34d399" font-size="9">KV 中</text>
      <rect x="270" y="15" width="120" height="130" rx="6" fill="#2f364a" stroke="#a78bfa"/>
      <text x="330" y="35" text-anchor="middle" fill="#a78bfa" font-weight="bold">MQA</text>
      <text x="330" y="55" text-anchor="middle" fill="#e8eaf0">Q1 Q2 Q3 Q4</text>
      <text x="330" y="75" text-anchor="middle" fill="#e8eaf0">Q5 Q6 Q7 Q8</text>
      <text x="330" y="95" text-anchor="middle" fill="#e8eaf0">共享 K1 V1</text>
      <text x="330" y="130" text-anchor="middle" fill="#a78bfa" font-size="9">KV 最小</text>
    </svg>
  </div>

  <h3>前向传播</h3>
  <pre><code>def forward(self, idx):
    B, T = idx.shape
    # token + position embeddings
    tok_emb = self.transformer.wte(idx)
    pos_emb = self.transformer.wpe(torch.arange(T, device=idx.device))
    x = tok_emb + pos_emb
    # forward through transformer blocks
    for block in self.transformer.h:
        x = block(x)
    # final layer norm
    x = self.transformer.ln_f(x)
    # language modeling head
    logits = self.lm_head(x)
    return logits</code></pre>

  <h3>权重初始化</h3>
  <p>minGPT 使用 N(0, 0.02) 初始化所有权重。为什么是 0.02？因为 Transformer 的残差路径会导致方差累积。具体来说，GPT-2 对残差投影（注意力输出和 FFN 输出）使用了 <code>N(0, 0.02/sqrt(2*n_layer))</code> 的缩放初始化，以抵消深层网络中残差方差累积的影响。这个细节对于小模型（minGPT 级别）影响不大，但在 48 层以上的模型中会显著影响训练稳定性。</p>

  <h3>优化器配置（configure_optimizers）</h3>
  <p>minGPT 将参数分为两组：<code>decay</code>（线性层权重，应用权重衰减）和 <code>no_decay</code>（偏置、LayerNorm 参数、嵌入权重）。这种分离是 GPT 训练的标准实践——对偏置和归一化参数应用正则化没有意义，因为它们的维度很低或作用不同。</p>

  <h3>加载预训练权重（from_pretrained）</h3>
  <p>minGPT 支持从 Hugging Face 加载 GPT-2 预训练权重。这需要在两个框架之间映射参数名称。虽然 minGPT 本身通常只用于从头训练，但这个功能让你可以加载一个完整的 GPT-2 并用 generate.ipynb 体验文本生成。</p>
</section>'''

gpt_cn_start = cn.find('<section id="gpt"')
gpt_cn_end = cn.find('</section>', gpt_cn_start) + 11
cn = cn[:gpt_cn_start] + gpt_zh + cn[gpt_cn_end:]
changes += 1

with open('C:/Users/zixun/dev/minGPT/docs/learning_guide.html', 'w', encoding='utf-8') as f:
    f.write(cn)

import re
opens = cn.count('<section id=')
closes = cn.count('</section>')
sections = re.findall(r'<section id="([^"]+)"', cn)
print(f'\nAfter attention/block/gpt translation:')
print(f'{opens} opens, {closes} closes, balanced={opens==closes}')
print(f'Sections: {sections}')

# Check which are now Chinese
for s in ['attention', 'block', 'gpt']:
    idx = cn.find('<section id="' + s + '"')
    section = cn[idx:idx+400]
    first_p = section.find('<p>')
    if first_p >= 0:
        p_text = section[first_p+3:first_p+60]
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in p_text)
        print(f'  {s}: {"ZH" if has_chinese else "EN"} - {p_text[:40]}')

# ===== SECTION: TRAINING =====
print('Translating: training...')
training_zh = '''<section id="training">
  <h2>8. 训练的本质：从损失函数到参数更新</h2>

  <p>在前面的章节中，我们从第一性原理理解了学习就是"预测 → 评分 → 调整"。本章将这一过程在 GPT 训练中的每个细节展开，并对比工业实践和其他优化方法。</p>

  <h3>深入理解损失函数</h3>
  <p>在语言建模中，我们几乎总是使用交叉熵损失（Cross Entropy Loss）。</p>
  <p>从信息论的角度看，它衡量的是"模型预测的概率分布"与"真实的下一个词 one-hot 分布"之间的 KL 散度。</p>
  <p>为什么不用 MSE（均方误差）？因为在分类任务中，MSE 对概率的惩罚不够"尖锐"。交叉熵在模型对正确答案信心不足时给出非常大的梯度，推动模型快速修正。</p>

  <p>在代码中：</p>
  <pre><code>loss = F.cross_entropy(logits.view(-1, vocab_size), targets.view(-1), ignore_index=-1)</code></pre>

  <p><code>ignore_index=-1</code> 是一个非常实用的技巧。在 adder 项目中，它从损失中屏蔽了"问题部分"（输入数字），让模型只从"答案部分"学习。</p>

  <h3>梯度下降与优化器</h3>
  <p>最简单的梯度下降：</p>
  <div class="formula">θ ← θ - η · ∇L</div>
  <p>其中 η 是学习率。</p>

  <p>在实践中，我们使用 AdamW（GPT 的标准）：</p>
  <ul>
    <li><strong>动量（Momentum）</strong>：使更新方向更稳定，在陡峭的损失表面上减少震荡。</li>
    <li><strong>自适应学习率</strong>：对频繁更新的参数用小步，对稀有参数用大步。</li>
    <li><strong>权重衰减（Weight Decay）</strong>：仅对权重矩阵应用 L2 正则化，不对偏置和 LayerNorm 参数应用（AdamW 与 Adam 的关键区别）。</li>
  </ul>

  <p>在 minGPT 的 <code>configure_optimizers</code> 中，参数被明确分为两组：</p>
  <ul>
    <li>decay 组：线性层权重</li>
    <li>no_decay 组：偏置、LayerNorm、嵌入权重</li>
  </ul>

  <h3>优化器对比</h3>
  <table>
    <tr><th>优化器</th><th>特点</th><th>LLM 中的使用</th></tr>
    <tr><td>SGD + Momentum</td><td>简单，理论性质好</td><td>大模型很少使用</td></tr>
    <tr><td>Adam</td><td>自适应 + 动量</td><td>早期常用</td></tr>
    <tr><td>AdamW</td><td>正确的权重衰减实现</td><td>当前 GPT 模型标准</td></tr>
    <tr><td>Lion</td><td>2023 年提出，更省内存</td><td>部分新模型在实验</td></tr>
    <tr><td>8-bit Adam / Adafactor</td><td>低精度优化，节省显存</td><td>超大模型（>100B）常用</td></tr>
  </table>

  <h3>梯度裁剪（Gradient Clipping）</h3>
  <p>在 Transformer 训练中，某些层很容易出现梯度爆炸。minGPT 使用 <code>clip_grad_norm_(model.parameters(), 1.0)</code>，将全局梯度范数裁剪到 1.0。这是稳定大模型训练最简单有效的技巧之一。</p>

  <h3>损失地形图：为什么学习率的选择至关重要</h3>
  <p>想象损失函数是一座连绵起伏的山脉。模型的参数就是放在这座山上的一个球，训练的过程就是让球沿着山坡向下滚，寻找最低的谷底。</p>

  <div class="diagram" style="text-align:center;padding:1rem">
    <svg width="600" height="240" viewBox="0 0 600 240" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="11">
      <defs>
        <linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1a1a2e"/><stop offset="100%" stop-color="#16213e"/></linearGradient>
        <linearGradient id="curve2" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#e94560"/><stop offset="50%" stop-color="#f5a623"/><stop offset="100%" stop-color="#34d399"/></linearGradient>
      </defs>
      <rect width="600" height="240" fill="url(#sky2)" rx="8"/>
      <path d="M 20 190 Q 80 180 150 170 Q 220 140 260 130 Q 300 100 340 105 Q 380 80 420 85 Q 460 50 500 55 Q 540 40 580 45" fill="none" stroke="url(#curve2)" stroke-width="2.5"/>
      <path d="M 340 105 Q 350 95 370 98" fill="none" stroke="#34d399" stroke-width="1.5" stroke-dasharray="3"/>
      <text x="355" y="85" fill="#34d399" font-size="10" text-anchor="middle">最佳谷底</text>
      <circle cx="140" cy="173" r="8" fill="#e94560" opacity="0.9"/>
      <line x1="132" y1="181" x2="120" y2="200" stroke="#e94560" stroke-width="1"/>
      <text x="100" y="215" fill="#e94560" font-size="10" text-anchor="middle">LR 太小：几乎不动</text>
      <circle cx="350" cy="103" r="8" fill="#34d399" opacity="0.9"/>
      <line x1="360" y1="115" x2="375" y2="130" stroke="#34d399" stroke-width="1"/>
      <text x="395" y="145" fill="#34d399" font-size="10" text-anchor="middle">合适 LR：顺利下山</text>
      <circle cx="450" cy="58" r="8" fill="#f5a623" opacity="0.9"/>
      <line x1="460" y1="50" x2="485" y2="30" stroke="#f5a623" stroke-width="1"/>
      <text x="510" y="28" fill="#f5a623" font-size="10" text-anchor="middle">LR 太大：直接弹飞</text>
      <text x="300" y="235" fill="#9aa3b8" font-size="10" text-anchor="middle">参数空间 →</text>
      <line x1="270" y1="230" x2="330" y2="230" stroke="#9aa3b8" marker-end="url(#arrow2)" stroke-width="1"/>
      <defs><marker id="arrow2" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto"><polygon points="0 0,6 2,0 4" fill="#9aa3b8"/></marker></defs>
    </svg>
  </div>

  <p>上图展示了损失地形的一个剖面。三种场景：</p>
  <ul>
    <li><strong>学习率太小（红色）</strong>：球几乎不动，卡在一个缓坡上。训练进度极慢，最终也无法到达谷底。实践中表现为 loss 下降极慢，最终停在一个较高的值。</li>
    <li><strong>学习率合适（绿色）</strong>：球顺利滚入谷底。这就是调好学习率的表现——loss 稳步下降，最终到达一个不错的最小值。</li>
    <li><strong>学习率太大（橙色）</strong>：球因为动量过大，直接弹出谷底。训练中表现为 loss 突然暴涨——这就是梯度裁剪要解决的问题：防止球在梯度异常大时跳出太远。</li>
  </ul>
  <p><strong>为什么需要 Warmup</strong>：在初始化时，模型参数是随机的，起点附近的损失地形极其陡峭且混乱。一大步走错就可能永久破坏训练稳定性。Warmup 让模型先用极小的步幅探路，找到方向后再全速下降。</p>

  <h3>学习率调度</h3>
  <p>现代 LLM 训练几乎总是使用 Warmup + Cosine Decay 或 WSD（Warmup-Stable-Decay）调度。</p>
  <ul>
    <li><strong>Warmup</strong>：在前几千步中，学习率从 0 线性增加到峰值，防止早期不稳定。</li>
    <li><strong>Cosine Decay</strong>：学习率平滑衰减到一个很小的值。</li>
    <li><strong>稳定阶段</strong>：对于非常大的模型，有一个学习率保持不变的阶段。</li>
  </ul>

  <h3>深入理解 AdamW 超参数：betas=(0.9, 0.95)</h3>
  <p>AdamW 中的两个 beta 值控制着优化过程中完全不同的方面：</p>
  <ul>
    <li><strong>beta1=0.9（动量）</strong>：想象球滚下山坡。0.9 意味着"90% 保留之前的方向 + 10% 采纳新梯度"。beta1 越高（如 0.95），轨迹越平滑但转向越慢；越低（如 0.8），响应越快但来回抖动。0.9 是默认值，因为它平衡了平滑性和响应速度。</li>
    <li><strong>beta2=0.95（自适应学习率）</strong>：它控制 Adam 回顾多远来估计每个参数的"典型梯度大小"。这是一个梯度平方的指数移动平均。beta2=0.95 意味着大约考虑最近 20 步的梯度统计。越高（如 0.999）估计越稳定，但在梯度统计变化时适应慢；越低（如 0.9）适应快但噪声大。</li>
  </ul>
  <p><strong>直觉速查表</strong>：beta1 控制方向的记忆（往哪走），beta2 控制步长的记忆（每步走多大）。如果训练剧烈震荡，增加 beta1；如果 loss 过早停滞，减小 beta2。</p>
  <div class="callout important">
    <strong>为什么用 AdamW 而不是 Adam？</strong> Adam 有一个 bug：权重衰减被应用在<em>自适应学习率内部</em>，导致梯度大的参数被正则化得更狠。AdamW 将权重衰减<em>解耦</em>，直接应用在权重上。这个小小的修正显著提升了泛化能力，尤其是对于大语言模型。
  </div>

  <h3>数据是训练的另一半（第一性原理）</h3>
  <p>许多人只关注模型架构和优化器，但数据质量往往比模型大小更重要。从第一性原理看，模型只是一个"函数近似器"——它能拟合什么完全取决于你给它看什么数据。</p>
  <p>在 Scaling Laws 时代，我们学到：</p>
  <ul>
    <li>高质量、干净、多样化的数据让同样大小的模型表现更好（Chinchilla 论文的核心发现）。</li>
    <li>数据重复会损害性能，甚至导致"记忆化"而非"泛化"。</li>
    <li>数据混合比例（代码、网页、书籍、对话、数学）需要仔细调整。不同的比例会产生截然不同的能力画像。</li>
  </ul>

  <p><strong>具体例子：相同架构，不同数据</strong></p>
  <p>试试用<em>完全相同</em>的 gpt-nano 模型在两个不同数据集上训练：</p>
  <ul>
    <li><strong>数据集 A</strong>：100MB 清洗后的维基百科。模型会学到良好的语法、事实知识和连贯的段落结构。但它不会写代码、做数学或对话。</li>
    <li><strong>数据集 B</strong>：100MB GitHub Python 代码。同样的模型会学到缩进模式、函数调用语法和变量命名规范。但如果让它写文章，它会生成胡言乱语。</li>
    <li><strong>数据集 C（混合）</strong>：50MB 维基百科 + 50MB GitHub。模型会"两者都懂一点，但不精通"——除非总数据量大到足以让模型同时学习两种分布。这就是为什么 Chinchilla 的发现至关重要：每个领域都需要足够的 token。</li>
  </ul>

  <p><strong>给 minGPT 实验者的实用建议</strong>：如果你的 minGPT 模型学不会，首先要检查的<em>不是</em>架构——而是你的数据。(x, y) 配对是否正确？词汇表是否覆盖了文本？数据是否足够多样？一个完美的 Transformer 配上糟糕的数据，只会生成完美的垃圾。</p>

  <div class="callout tip">
    <strong>实验建议</strong>：用同一个 minGPT 模型分别训练莎士比亚、Python 代码和随机数。架构完全不变，但模型会学到完全不同的模式。这是内化"数据是训练的另一半"的最直接方式。
  </div>

  <h3>训练稳定性：小模型 vs 大模型</h3>
  <p>训练一个几百万参数的 minGPT 和一个 70B 的模型在工程上是完全不同的世界。</p>
  <ul>
    <li>小模型（minGPT 级别）几乎不用担心 loss 尖峰。随机初始化 + 正常 AdamW 就能工作。</li>
    <li>大模型需要一系列"黑魔法"技巧：精确的初始化缩放（GPT-2 的残差投影用 1/sqrt(2N)）、QKV 偏置设为 0、LayerNorm epsilon 调优、梯度裁剪到 1.0、loss 缩放、BF16 主权重保护、选择性权重衰减等。</li>
    <li>当 loss 尖峰发生时，你通常需要回滚到之前的检查点并调整超参数，甚至重新设计初始化。</li>
  </ul>
  <p>minGPT 故意省略了这些"细节"，因为它的目标是教育。在小实验中看不到的陷阱，会在真实的大模型训练中让你吃尽苦头。</p>

  <h3>默认训练配置</h3>
  <table>
    <tr><th>参数</th><th>默认值</th><th>说明</th></tr>
    <tr><td>device</td><td>'auto'</td><td>自动选择 CUDA 或 CPU</td></tr>
    <tr><td>batch_size</td><td>64</td><td>批大小</td></tr>
    <tr><td>learning_rate</td><td>3e-4</td><td>AdamW 学习率</td></tr>
    <tr><td>betas</td><td>(0.9, 0.95)</td><td>Adam 动量参数</td></tr>
    <tr><td>weight_decay</td><td>0.1</td><td>权重衰减（仅线性层）</td></tr>
    <tr><td>grad_norm_clip</td><td>1.0</td><td>梯度裁剪阈值</td></tr>
    <tr><td>max_iters</td><td>None</td><td>最大迭代次数（None=无限）</td></tr>
    <tr><td>num_workers</td><td>4</td><td>DataLoader 工作进程数</td></tr>
  </table>

  <h3>训练循环（与第一性原理的对应）</h3>
  <p>回忆我们的第一性原理——每一行代码对应一个步骤：</p>
  <pre><code>while True:
    x, y = next(batch)                    # 获取一个批次
    logits, loss = model(x, y)            # 1. 前向：预测 + 计算损失
    model.zero_grad(set_to_none=True)
    loss.backward()                       # 2. 反向：计算梯度
    clip_grad_norm_(params, max_norm)     # （可选）防止梯度爆炸
    optimizer.step()                      # 3. 更新：真正地转动旋钮
    trigger_callbacks('on_batch_end')     # 回调（日志/评估/保存）
    if iter_num >= max_iters: break</code></pre>

  <p>循环的每次执行都在略微调整模型参数以降低误差，基于当前批次计算。这是"训练"最本质的动作。</p>

  <h3>回调机制</h3>
  <pre><code>def on_batch_end(trainer):
    if trainer.iter_num % 100 == 0:
        print(f"loss: {trainer.loss.item():.4f}")

trainer.set_callback('on_batch_end', on_batch_end)</code></pre>
  <p>回调可以访问 <code>trainer.loss</code>、<code>trainer.iter_num</code>、<code>trainer.iter_dt</code>（每步耗时）等。</p>
</section>'''

training_cn_start = cn.find('<section id="training"')
training_cn_end = cn.find('</section>', training_cn_start) + 11
cn = cn[:training_cn_start] + training_zh + cn[training_cn_end:]
changes += 1

# ===== SECTION: GENERATION =====
print('Translating: generation...')
gen_zh = '''<section id="generation">
  <h2>9. 自回归生成</h2>
  <p><code>model.generate()</code> 实现了自回归生成：一次预测一个 token，追加到序列中，重复直到达到所需长度。</p>

  <p>生成流程：</p>
  <ol>
    <li>prompt：初始输入序列。</li>
    <li>forward：模型前向传播，获取最后一个位置的 logits。</li>
    <li>logits/T：应用温度缩放（控制随机性）。</li>
    <li>sample：基于温度和 top-k/top-p 采样下一个 token（或贪心 argmax）。</li>
    <li>append：将新 token 拼接到序列，重复直到达到 max_new_tokens。</li>
  </ol>
  <p>与 BERT（一次性双向理解）不同，GPT 的生成必须是严格自回归的，因此因果掩码不可或缺。与 Mamba 等线性模型相比，标准 Transformer 在生成期间需要维护完整的 KV 缓存。</p>

  <div class="diagram">
    <svg width="650" height="120" viewBox="0 0 650 120" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, sans-serif" font-size="12">
      <defs><marker id="a5" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto"><polygon points="0 0,7 2.5,0 5" fill="#6c9eff"/></marker></defs>
      <rect x="10" y="40" width="90" height="35" rx="5" fill="#2f364a" stroke="#e8eaf0"/><text x="55" y="62" text-anchor="middle" fill="#e8eaf0">prompt</text>
      <rect x="130" y="40" width="90" height="35" rx="5" fill="#1e3a5f" stroke="#6c9eff"/><text x="175" y="62" text-anchor="middle" fill="#6c9eff">forward</text>
      <rect x="250" y="40" width="90" height="35" rx="5" fill="#343c52" stroke="#a78bfa"/><text x="295" y="62" text-anchor="middle" fill="#a78bfa">logits/T</text>
      <rect x="370" y="40" width="90" height="35" rx="5" fill="#14352a" stroke="#34d399"/><text x="415" y="62" text-anchor="middle" fill="#34d399">sample</text>
      <rect x="490" y="40" width="90" height="35" rx="5" fill="#2a1f14" stroke="#fb923c"/><text x="535" y="62" text-anchor="middle" fill="#fb923c">append</text>
      <rect x="570" y="40" width="70" height="35" rx="5" fill="#2f364a" stroke="#9aa3b8"/><text x="605" y="55" text-anchor="middle" fill="#9aa3b8" font-size="10">repeat</text><text x="605" y="68" text-anchor="middle" fill="#9aa3b8" font-size="10">max_new</text>
      <line x1="100" y1="57" x2="130" y2="57" stroke="#6c9eff" marker-end="url(#a5)"/>
      <line x1="220" y1="57" x2="250" y2="57" stroke="#a78bfa" marker-end="url(#a5)"/>
      <line x1="340" y1="57" x2="370" y2="57" stroke="#34d399" marker-end="url(#a5)"/>
      <line x1="460" y1="57" x2="490" y2="57" stroke="#fb923c" marker-end="url(#a5)"/>
      <path d="M 535 75 Q 535 100 175 100 Q 55 100 55 75" fill="none" stroke="#9aa3b8" stroke-dasharray="4" marker-end="url(#a5)"/>
    </svg>
  </div>

  <h3>生成参数详解</h3>
  <table>
    <tr><th>参数</th><th>默认值</th><th>说明</th></tr>
    <tr><td>max_new_tokens</td><td>—</td><td>要生成的新 token 数量</td></tr>
    <tr><td>temperature</td><td>1.0</td><td>控制随机性（见 Softmax 章节）</td></tr>
    <tr><td>top_p</td><td>None</td><td>核采样阈值——仅从累积概率超过 top_p 的最小 token 集合中采样。None 表示禁用。</td></tr>
    <tr><td>do_sample</td><td>False</td><td>False=贪心 (argmax)，True=概率采样</td></tr>
    <tr><td>top_k</td><td>None</td><td>仅从概率最高的 top k 个 token 中采样</td></tr>
  </table>

  <pre><code>model.eval()
with torch.no_grad():
    # 确定性生成
    out = model.generate(prompt, max_new_tokens=100, do_sample=False)

    # 多样性采样
    out = model.generate(prompt, max_new_tokens=100,
                         temperature=0.8, do_sample=True, top_k=40)</code></pre>

  <div class="warning">
    生成前务必调用 <code>model.eval()</code> 以禁用 Dropout。
    超过 <code>block_size</code> 的序列会自动截断为最后 block_size 个 token。
  </div>

  <h3>交互式采样工具（Temperature & Top-k）</h3>
  <p>下面的交互工具让你体验温度和 top-k 如何影响同一个 logits 分布。点击"Sample"从调整后的分布中采样。</p>
  <div id="sampler-toy" class="toy-container">
    <div class="sampler">
      <div>
        <label>temperature <span id="temp-val">1.0</span></label>
        <input type="range" id="temp" min="0.1" max="3" step="0.1" value="1.0">
        <label>top-k <span id="topk-val">5</span></label>
        <input type="range" id="topk" min="1" max="5" step="1" value="5">
        <button id="sample-btn" style="margin-top:8px">随机采样</button>
        <div id="sample-result" style="margin-top:8px;font-size:0.9rem"></div>
      </div>
      <div>
        <div style="font-size:0.8rem;color:#9aa3b8;margin-bottom:4px">原始概率 (temp=1, no top-k)</div>
        <div id="bars-before" class="bars"></div>
        <div style="font-size:0.8rem;color:#9aa3b8;margin:8px 0 4px">调整温度 + top-k 后</div>
        <div id="bars-after" class="bars"></div>
      </div>
    </div>
  </div>
  <p class="note">temperature &lt; 1 使分布更尖锐（模型更"自信"）；top-k=3 表示"仅从这 3 个词中选择"，其余词概率归零。</p>
</section>'''

gen_cn_start = cn.find('<section id="generation"')
gen_cn_end = cn.find('</section>', gen_cn_start) + 11
cn = cn[:gen_cn_start] + gen_zh + cn[gen_cn_end:]
changes += 1

# ===== SECTION: IMPLEMENTATION =====
print('Translating: implementation...')
impl_zh = '''<section id="implementation">
  <div class="chapter-header">
    <h2>11. minGPT 实现细节</h2>
  </div>

  <p>minGPT 有意保持最小化，但真实世界的生产代码必须处理许多额外问题。下面我们深入分析每一个简化：minGPT 中是什么样的，为什么工业界必须加上它，以及为什么 Karpathy 故意为了教学而省略它。</p>

  <div class="card" style="margin: 1.2rem 0; border-left: 4px solid var(--accent2);">
    <h4>1. 没有 FlashAttention / memory efficient attention</h4>
    <p><strong>这是什么？</strong><br>
    标准注意力在计算 Q@K^T 时会显式生成一个 T×T 的分数矩阵（对于批次和头，大小为 B×nh×T×T）。在 T=4096 时这个矩阵已经很大了；在 T=32k 时直接爆炸。FlashAttention 使用分块计算、融合 softmax 到 SRAM 中，避免将完整注意力矩阵写入 HBM，实现了"IO 感知"的计算。</p>
    <p><strong>minGPT 中（model.py, CausalSelfAttention.forward）：</strong>
    <pre><code>q, k, v = self.c_attn(x).split(...)
    att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(...))
    att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf'))
    att = F.softmax(att, dim=-1)
    y = att @ v</code></pre>
    每一步都生成中间 T×T 张量。</p>
    <p><strong>生产版本：</strong> 序列长度轻松达到 32k~128k+，在相同批大小下内存减少 3-10 倍。在长上下文上训练 70B 模型变得可行。</p>
    <p><strong>为什么省略？</strong> 一旦使用 Flash，你就再也看不到"注意力分数是如何计算的"——核心过程变成了一个黑盒 kernel。教学目标是让你清晰地看到 mask、scale、softmax、加权求和的过程。</p>
  </div>

  <div class="card" style="margin: 1.2rem 0; border-left: 4px solid var(--accent2);">
    <h4>2. 没有混合精度训练（BF16 + FP32 主权重）</h4>
    <p><strong>minGPT 中：</strong> 整个模型默认是 FP32。没有 autocast、GradScaler 或主权重副本。</p>
    <p><strong>生产影响：</strong> 加速 1.5-3 倍，内存减半（BF16 使用 2 字节而不是 4 字节）。没有它，训练 10B+ 模型不仅太慢，而且 A100 tensor core 也被浪费了。</p>
    <p><strong>为什么省略？</strong> 混合精度涉及 amp、GradScaler、all-reduce 精度策略——对于理解"下一个词预测 + 梯度下降"来说，纯粹是工程噪声。</p>
  </div>

  <div class="card" style="margin: 1.2rem 0; border-left: 4px solid var(--accent2);">
    <h4>3. 没有梯度检查点（Gradient Checkpointing）</h4>
    <p><strong>minGPT 中：</strong> 没有。Trainer 直接调用 <code>loss.backward()</code>，PyTorch 保留所有激活值。</p>
    <p><strong>生产影响：</strong> 在不增加 GPU 的情况下使批大小或序列长度增加 2-4 倍。对于长上下文训练至关重要。</p>
    <p><strong>为什么省略？</strong> 重计算使训练代码和调试变得复杂。对于理解"loss.backward() 做了什么"，它是一个干扰项。</p>
  </div>

  <div class="card" style="margin: 1.2rem 0; border-left: 4px solid var(--accent2);">
    <h4>4. 没有 ZeRO / FSDP 分布式策略</h4>
    <p><strong>minGPT 中：</strong> 只有 <code>model.to(device)</code> 和一个优化器。没有"多 GPU"的概念。</p>
    <p><strong>生产影响：</strong> 没有这些，GPT-3 175B、LLaMA 70B 永远不会存在。</p>
    <p><strong>为什么省略？</strong> 分布式代码极其复杂（通信拓扑、梯度桶、参数重排、容错）。教学目标是首先理解"单个 GPU 上的单个 Block 做了什么"。</p>
  </div>

  <div class="card" style="margin: 1.2rem 0; border-left: 4px solid var(--accent2);">
    <h4>5. 没有 RoPE（旋转位置编码）</h4>
    <p><strong>minGPT 中：</strong> 使用简单的可学习位置嵌入（wpe），最大长度固定为 block_size。</p>
    <p><strong>生产影响：</strong> RoPE 允许外推（extrapolation）到更长的序列，并且相对位置编码比绝对位置更符合注意力的需要。所有现代模型（LLaMA、Mistral、Gemma）都使用 RoPE 或其变体。</p>
    <p><strong>为什么省略？</strong> 可学习嵌入是最简单的位置编码方式——"添加一个位置向量"比 RoPE 的旋转矩阵更容易理解。</p>
  </div>

  <div class="card" style="margin: 1.2rem 0; border-left: 4px solid var(--accent2);">
    <h4>6. 没有 GQA（分组查询注意力）</h4>
    <p><strong>minGPT 中：</strong> 标准多头注意力，每个头有自己的 K 和 V。</p>
    <p><strong>生产影响：</strong> GQA 在不牺牲质量的情况下显著减少了 KV 缓存（约 2-4 倍）。对于长序列生成和部署到边缘设备至关重要。</p>
    <p><strong>为什么省略？</strong> MHA 更简单、更经典。理解了 MHA 之后，GQA 只是"多个 Q 共享 K/V"的一个小变化。</p>
  </div>

  <p><strong>本节的核心教训</strong>：minGPT 不是生产的代码。它是<em>教学</em>代码。理解每个省略背后的"为什么"比知道如何添加它们更有价值——因为它揭示了 Transformer 的核心机制与工程优化之间的界限。</p>
</section>'''

impl_cn_start = cn.find('<section id="implementation"')
impl_cn_end = cn.find('</section>', impl_cn_start) + 11
cn = cn[:impl_cn_start] + impl_zh + cn[impl_cn_end:]
changes += 1

with open('C:/Users/zixun/dev/minGPT/docs/learning_guide.html', 'w', encoding='utf-8') as f:
    f.write(cn)

import re
opens = cn.count('<section id=')
closes = cn.count('</section>')
sections = re.findall(r'<section id="([^"]+)"', cn)
print(f'After training/generation/implementation: {opens} opens, {closes} closes, balanced={opens==closes}')

# Check which are now Chinese
for s in ['training', 'generation', 'implementation']:
    idx = cn.find('<section id="' + s + '"')
    if idx >= 0:
        section = cn[idx:idx+400]
        first_p = section.find('<p>')
        if first_p >= 0:
            p_text = section[first_p+3:first_p+60]
            has_chinese = any('\u4e00' <= c <= '\u9fff' for c in p_text)
            print(f'  {s}: {"ZH" if has_chinese else "EN"} - {p_text[:40]}')

print(f'Total changes: {changes}')


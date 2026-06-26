"""
Full definition of a GPT Language Model, all of it in this single file.

References:
1) the official GPT-2 TensorFlow implementation released by OpenAI:
https://github.com/openai/gpt-2/blob/master/src/model.py
2) huggingface/transformers PyTorch implementation:
https://github.com/huggingface/transformers/blob/main/src/transformers/models/gpt2/modeling_gpt2.py
"""

# ============================================================================
# IMPORTS AND DEPENDENCIES
# ============================================================================

import math  # 用于数学常数和操作（Used for mathematical constants and operations）
             # 例如：math.sqrt() 用于计算注意力权重的缩放因子
             # Example: math.sqrt() for computing the scaling factor in attention
             # 参考：Attention is All You Need论文中的缩放点积注意力机制
             # Reference: Scaled Dot-Product Attention in "Attention is All You Need"

import torch  # PyTorch深度学习框架（Deep learning framework）
              # 提供张量操作、自动求导、神经网络层等核心功能
              # Provides tensor operations, autograd, nn modules, etc.

import torch.nn as nn  # PyTorch神经网络模块（Neural network module）
                       # 包含Layer, Linear, Embedding, Dropout等基础层
                       # Contains Linear, Embedding, LayerNorm, Dropout, etc.

from torch.nn import functional as F  # PyTorch函数式API（Functional API）
                                      # 提供激活函数(softmax, relu)和损失函数(cross_entropy)
                                      # Provides activation functions and loss functions

from mingpt.utils import CfgNode as CN  # 配置管理类（Configuration management）
                                         # 用于管理模型和训练的超参数
                                         # Used for managing hyperparameters

# -----------------------------------------------------------------------------

class NewGELU(nn.Module):
    """
    Implementation of the GELU activation function currently in Google BERT repo (identical to OpenAI GPT).
    实现Google BERT库中使用的GELU激活函数（与OpenAI GPT相同）。
    Google BERTリポジトリで現在使用されているGELU活性化関数の実装（OpenAI GPTと同じ）。
    
    GELU 全称为 Gaussian Error Linear Unit（高斯误差线性单元）
    GELU = x * Φ(x)，其中Φ(x)是高斯分布的累积分布函数(CDF)
    
    与ReLU相比：
    - ReLU: max(0, x) - 简单的截断，但梯度不平滑
    - GELU: x * Φ(x) - 平滑的非线性变换，对所有值进行加权
    
    这个实现使用泰勒展开的近似形式以提高计算效率：
    GELU(x) ≈ 0.5 * x * (1 + tanh(√(2/π) * (x + 0.044715 * x³)))
    
    优点：
    1. 比ReLU更平滑，梯度更稳定
    2. 对输入的加权而不是截断，保留更多信息
    3. 在NLP和视觉任务中表现优于ReLU
    
    论文链接：
    - GELU论文: https://arxiv.org/abs/1606.08415
    - Attention is All You Need: https://arxiv.org/abs/1706.03762 (Transformer基础)
    - GPT-2论文: https://d4mucfpksywq.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
    """
    def forward(self, x):
        # 泰勒展开的GELU近似形式：相比精确计算更高效
        # Approximation of GELU using tanh: more efficient than exact computation
        return 0.5 * x * (1.0 + torch.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * torch.pow(x, 3.0))))

class CausalSelfAttention(nn.Module):
    """
    A vanilla multi-head masked self-attention layer with a projection at the end.
    具有投影层的普通多头掩蔽自注意力层。虽然可以使用torch.nn.MultiheadAttention，
    但这里显式实现是为了展示自注意力机制其实并不复杂。
    最後に投影層を持つバニラマルチヘッドマスク付き自己注意層。
    
    === 自注意力机制 (Self-Attention Mechanism) ===
    
    核心思想：对于每个token位置，计算它与序列中其他所有token的相关性，然后根据这些相关性对信息进行加权聚合
    
    计算步骤：
    1. 投影 (Projection): 将输入X投影为Query(Q), Key(K), Value(V)三个向量
       - Q: 当前token的查询向量（"我想要什么信息"）
       - K: 所有token的键向量（"我拥有什么"）
       - V: 所有token的值向量（"我能提供什么"）
    
    2. 计算相似度 (Attention Scores):
       Scores = Q @ K^T / √(d_k)  其中d_k是每个头的维度
       - Q @ K^T 计算查询和键之间的相似度
       - 除以√(d_k) 是缩放操作，防止softmax梯度过小（梯度消失）
    
    3. 掩码 (Causal Mask - 因果掩码):
       - 在语言建模中，我们不能让当前位置看到未来的token
       - 因此将未来位置的scores设为-∞，使得softmax后概率为0
       - 这保证了自回归性：生成第t个token时只依赖前t-1个token
    
    4. 求概率 (Softmax):
       Attention = softmax(Scores)
       - 将scores转换为0-1之间的权重
       - 权重和为1，表示注意力分布
    
    5. 应用权重 (Apply Attention):
       Output = Attention @ V
       - 用权重加权所有的值向量
       - 高权重的token对输出贡献更大
    
    === 多头注意力 (Multi-Head Attention) ===
    
    为什么使用多头？
    - 单个注意力头只能学习一种相似度度量
    - 多个头可以并行学习多种不同的注意力模式
    - 例如：一个头可能关注语法关系，另一个头关注语义关系
    
    实现方式：
    - 将embedding维度n_embd分成n_head个子空间
    - 每个头在各自的子空间中进行自注意力计算
    - 最后将所有头的输出拼接并通过线性变换
    
    === 代码设计说明 ===
    
    虽然可以使用torch.nn.MultiheadAttention，但这里显式实现是为了：
    1. 教学目的：展示自注意力机制其实并不复杂
    2. 完整控制：便于添加自定义的mask、dropout等
    3. 清晰性：每一步都明确表示，便于理解和调试
    
    论文链接：
    - Attention is All You Need: https://arxiv.org/abs/1706.03762 (必读！详细介绍了自注意力机制)
    - GPT: Language Models are Unsupervised Multitask Learners: https://d4mucfpksywq.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
    """

    def __init__(self, config):
        super().__init__()
        assert config.n_embd % config.n_head == 0
        # key, query, value projections for all heads, but in a batch
        # 所有头部的key、query、value投影，但以批处理方式进行
        # すべてのヘッドの key、query、value投影（バッチ処理方式で実行）
        self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd)
        # output projection
        # 输出投影
        # 出力投影
        self.c_proj = nn.Linear(config.n_embd, config.n_embd)
        # regularization
        # 正则化
        # 正則化
        self.attn_dropout = nn.Dropout(config.attn_pdrop)
        self.resid_dropout = nn.Dropout(config.resid_pdrop)
        # causal mask to ensure that attention is only applied to the left in the input sequence
        # 因果掩码：确保注意力只应用于输入序列左侧（过去的信息）
        # 因果マスク：注意が入力シーケンスの左側（過去の情報）にのみ適用されることを保証
        self.register_buffer("bias", torch.tril(torch.ones(config.block_size, config.block_size))
                                     .view(1, 1, config.block_size, config.block_size))
        self.n_head = config.n_head
        self.n_embd = config.n_embd

    def forward(self, x):
        B, T, C = x.size() # batch size, sequence length, embedding dimensionality (n_embd)
                          # B: 批大小 | T: 序列长度 | C: 嵌入维度 (n_embd)
                          # B: バッチサイズ | T: シーケンス長 | C: 埋め込み次元 (n_embd)

        # calculate query, key, values for all heads in batch and move head forward to be the batch dim
        # 计算所有头部的查询、键、值，以批处理方式，将头部维度前置
        # すべてのヘッドのクエリ、キー、値を計算し、バッチ次元として先に移動
        q, k ,v  = self.c_attn(x).split(self.n_embd, dim=2)
        k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs)
        q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs) 重新组织维度
        v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2) # (B, nh, T, hs) ヘッド次元を前に

        # causal self-attention; Self-attend: (B, nh, T, hs) x (B, nh, hs, T) -> (B, nh, T, T)
        # 因果自注意力计算：Q @ K^T -> 注意力权重
        # 因果自己注意計算：Q @ K^T -> 注意重み
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
        att = att.masked_fill(self.bias[:,:,:T,:T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.attn_dropout(att)
        y = att @ v # (B, nh, T, T) x (B, nh, T, hs) -> (B, nh, T, hs) 用权重加权值
        y = y.transpose(1, 2).contiguous().view(B, T, C) # re-assemble all head outputs side by side
                                                          # 重新组织所有头部的输出 | すべてのヘッド出力を再結合

        # output projection
        # 输出投影
        # 出力投影
        y = self.resid_dropout(self.c_proj(y))
        return y

class Block(nn.Module):
    """ an unassuming Transformer block
    一个简朴的Transformer块：包含自注意力和前馈网络
    素朴なTransformerブロック：自己注意とフィードフォワードネットワークを含む
    
    === Transformer块的结构 (Transformer Block Architecture) ===
    
    一个Transformer块包含两个主要部分，通过残差连接(Residual Connections)连接：
    
    1. 自注意力子层 (Self-Attention Sublayer):
       - 输入 → LayerNorm → CausalSelfAttention → 残差连接 → 输出
       - 作用：每个token可以与序列中的其他token进行交互
    
    2. 前馈子层 (Feed-Forward Sublayer):
       - 输入 → LayerNorm → Linear(n_embd→4*n_embd) → GELU → Linear(4*n_embd→n_embd) → Dropout → 残差连接 → 输出
       - 作用：在每个位置单独应用非线性变换
       - 维度扩展：从n_embd扩展到4*n_embd再缩回，增加表达能力
    
    === 关键技巧说明 ===
    
    1. 残差连接 (Residual Connections):
       x_new = x_old + SubLayer(x_old)
       - 保留原始信息，只学习残差
       - 便于深层网络训练，缓解梯度消失问题
       - 使得很深的模型也能收敛
    
    2. 层标准化 (Layer Normalization):
       - 在子层之前进行（Pre-LayerNorm），比在之后进行（Post-LayerNorm）更稳定
       - 归一化激活的均值和方差，使训练更稳定
    
    3. Dropout：
       - 在自注意力和前馈后应用，进行正则化
       - 防止过拟合，在训练和推理时有不同行为
    
    4. 前馈网络中的维度扩展：
       - FFN(x) = max(0, xW₁ + b₁)W₂ + b₂  (使用GELU代替ReLU)
       - 4倍维度扩展是在GPT中证实有效的设计选择
       - 增加模型在每个位置的非线性表达能力
    
    === 为什么这个设计有效 ===
    
    Transformer块的设计经过了多项研究验证：
    1. 自注意力：捕捉长距离依赖关系
    2. 前馈网络：在每个位置的非线性变换
    3. 残差连接：便于训练深层网络
    4. 层标准化：稳定训练
    
    这些组件结合在一起，创建了表达能力很强的序列模型。
    
    论文链接：
    - Attention is All You Need (Transformer基础): https://arxiv.org/abs/1706.03762
    - Deep Residual Learning (残差连接): https://arxiv.org/abs/1512.03385
    - Layer Normalization: https://arxiv.org/abs/1607.06450
    """

    def __init__(self, config):
        super().__init__()
        self.ln_1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.n_embd)
        self.mlp = nn.ModuleDict(dict(
            c_fc    = nn.Linear(config.n_embd, 4 * config.n_embd),
            c_proj  = nn.Linear(4 * config.n_embd, config.n_embd),
            act     = NewGELU(),
            dropout = nn.Dropout(config.resid_pdrop),
        ))
        m = self.mlp
        self.mlpf = lambda x: m.dropout(m.c_proj(m.act(m.c_fc(x)))) # MLP forward

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlpf(self.ln_2(x))
        return x

class GPT(nn.Module):
    """ GPT Language Model
    GPT语言模型：一个仅解码器的Transformer用于文本生成
    GPT言語モデル：テキスト生成用のデコーダのみのTransformer
    
    === GPT模型的核心架构 (GPT Model Architecture) ===
    
    GPT = "Generative Pre-trained Transformer" 
    一个自回归的仅解码器(Decoder-Only)的Transformer模型
    
    完整架构流程：
    
    1. 输入嵌入 (Embedding Layer):
       - Token Embedding: 将输入token ID (0-50256) 映射到向量空间 (n_embd维)
         例：token_id=50 → embedding_vector (shape: 1×n_embd)
       - Position Embedding: 添加位置信息 (因为Transformer本身是permutation-invariant)
         作用：告诉模型"这个token在第几个位置"
       - 两个embedding相加作为Transformer块的输入
    
    2. Transformer块堆叠 (Stacked Transformer Blocks):
       - n_layer个相同的Block模块依次处理数据
       - 每个Block包含自注意力和前馈网络
       - 层数决定了模型的深度和学习能力
    
    3. 最终层标准化 (Final Layer Normalization):
       - 对最后一个Transformer块的输出进行标准化
       - 稳定最后的线性层
    
    4. 输出投影 (Language Model Head):
       - 将(batch, seq_len, n_embd)的特征投影到(batch, seq_len, vocab_size)
       - vocab_size个输出对应词汇表中的每个可能token
       - 输出logits，通过softmax可得到概率分布
    
    === 模型尺寸对比 ===
    
    这个实现提供了多个预配置的模型尺寸：
    
    - gpt-nano:   n_layer=3,  n_head=3,  n_embd=48      (~0.1M参数) - 学习用
    - gpt-micro:  n_layer=4,  n_head=4,  n_embd=128     (~1M参数)
    - gpt-mini:   n_layer=6,  n_head=6,  n_embd=192     (~8M参数)
    - gpt2:       n_layer=12, n_head=12, n_embd=768     (~124M参数) - 标准GPT-2
    - gpt2-large: n_layer=36, n_head=20, n_embd=1280    (~774M参数)
    - gpt2-xl:    n_layer=48, n_head=25, n_embd=1600    (~1.5B参数)
    
    === 自回归生成 (Autoregressive Generation) ===
    
    GPT采用自回归生成方式：
    1. 给定前缀序列，模型预测下一个最可能的token
    2. 将预测的token加到序列中
    3. 重复步骤1-2直到生成足够多的token或遇到结束符
    
    这保证了生成的序列在统计上是合理的，但可能有重复或不连贯。
    可以通过temperature、top-k采样等方法调节生成的多样性。
    
    === 训练目标 ===
    
    GPT的训练目标是最小化语言建模损失(Language Modeling Loss)：
    Loss = -Σ log P(token_i | token_1...token_{i-1})
    
    即：给定前面的token，正确预测当前token的概率越高，损失越小。
    这使得模型学习到token序列中的统计规律和语言知识。
    
    === 权重初始化 ===
    
    遵循GPT-2论文中的初始化策略：
    1. 大多数权重：N(0, 0.02) - 标准正态分布
    2. 残差投影：N(0, 0.02/√(2*n_layer)) - 缩放版本
       这是因为残差连接的梯度会累积，所以初始化要更小
    
    论文链接：
    - Language Models are Unsupervised Multitask Learners (GPT-2): https://d4mucfpksywq.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
    - Attention is All You Need (Transformer基础): https://arxiv.org/abs/1706.03762
    - An Image is Worth 16x16 Words (Transformer在视觉中的应用): https://arxiv.org/abs/2010.11929
    """

    @staticmethod
    def get_default_config():
        C = CN()
        # either model_type or (n_layer, n_head, n_embd) must be given in the config
        C.model_type = 'gpt'
        C.n_layer = None
        C.n_head = None
        C.n_embd =  None
        # these options must be filled in externally
        C.vocab_size = None
        C.block_size = None
        # dropout hyperparameters
        C.embd_pdrop = 0.1
        C.resid_pdrop = 0.1
        C.attn_pdrop = 0.1
        return C

    def __init__(self, config):
        super().__init__()
        assert config.vocab_size is not None
        assert config.block_size is not None
        self.block_size = config.block_size

        type_given = config.model_type is not None
        params_given = all([config.n_layer is not None, config.n_head is not None, config.n_embd is not None])
        assert type_given ^ params_given # exactly one of these (XOR)
        if type_given:
            # translate from model_type to detailed configuration
            config.merge_from_dict({
                # names follow the huggingface naming conventions
                # GPT-1
                'openai-gpt':   dict(n_layer=12, n_head=12, n_embd=768),  # 117M params
                # GPT-2 configs
                'gpt2':         dict(n_layer=12, n_head=12, n_embd=768),  # 124M params
                'gpt2-medium':  dict(n_layer=24, n_head=16, n_embd=1024), # 350M params
                'gpt2-large':   dict(n_layer=36, n_head=20, n_embd=1280), # 774M params
                'gpt2-xl':      dict(n_layer=48, n_head=25, n_embd=1600), # 1558M params
                # Gophers
                'gopher-44m':   dict(n_layer=8, n_head=16, n_embd=512),
                # (there are a number more...)
                # I made these tiny models up
                'gpt-mini':     dict(n_layer=6, n_head=6, n_embd=192),
                'gpt-micro':    dict(n_layer=4, n_head=4, n_embd=128),
                'gpt-nano':     dict(n_layer=3, n_head=3, n_embd=48),
            }[config.model_type])

        self.transformer = nn.ModuleDict(dict(
            wte = nn.Embedding(config.vocab_size, config.n_embd),
            wpe = nn.Embedding(config.block_size, config.n_embd),
            drop = nn.Dropout(config.embd_pdrop),
            h = nn.ModuleList([Block(config) for _ in range(config.n_layer)]),
            ln_f = nn.LayerNorm(config.n_embd),
        ))
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)

        # init all weights, and apply a special scaled init to the residual projections, per GPT-2 paper
        # 初始化所有权重，对残差投影应用特殊缩放初始化（按GPT-2论文）
        # すべての重みを初期化し、残差投影に特別なスケーリング初期化を適用（GPT-2論文に従う）
        self.apply(self._init_weights)
        for pn, p in self.named_parameters():
            if pn.endswith('c_proj.weight'):
                torch.nn.init.normal_(p, mean=0.0, std=0.02/math.sqrt(2 * config.n_layer))

        # report number of parameters (note we don't count the decoder parameters in lm_head)
        # 报告参数数量（注意：不计算lm_head中的解码器参数）
        # パラメータ数を報告（注：lm_headのデコーダパラメータは計算しない）
        n_params = sum(p.numel() for p in self.transformer.parameters())
        print("number of parameters: %.2fM" % (n_params/1e6,))

    def _init_weights(self, module):
        """初始化权重，遵循GPT-2论文中的策略 (Initialize weights following GPT-2 paper)
        
        权重初始化很重要，因为：
        1. 不同的初始化会导致不同的收敛速度
        2. 不良初始化会导致梯度消失/爆炸
        3. 遵循论文中的初始化有助于复现结果
        
        策略：
        - Linear层权重: N(0, 0.02) - 较小的初始化
        - Linear层偏置: 全0
        - Embedding层权重: N(0, 0.02)
        - LayerNorm权重(gamma): 全1（学习缩放因子）
        - LayerNorm偏置(beta): 全0（学习偏移量）
        """
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)

    @classmethod
    def from_pretrained(cls, model_type):
        """
        Initialize a pretrained GPT model by copying over the weights
        from a huggingface/transformers checkpoint.
        通过从huggingface/transformers检查点复制权重来初始化预训练的GPT模型。
        huggingface/transformersチェックポイントから重みをコピーして事前学習GPTモデルを初期化します。
        """
        assert model_type in {'gpt2', 'gpt2-medium', 'gpt2-large', 'gpt2-xl'}
        from transformers import GPT2LMHeadModel

        # create a from-scratch initialized minGPT model
        # 创建一个从头初始化的minGPT模型
        # ゼロから初期化されたminGPTモデルを作成
        config = cls.get_default_config()
        config.model_type = model_type
        config.vocab_size = 50257 # openai's model vocabulary
        config.block_size = 1024  # openai's model block_size
        model = GPT(config)
        sd = model.state_dict()

        # init a huggingface/transformers model
        # 初始化一个huggingface/transformers模型
        # huggingface/transformersモデルを初期化
        model_hf = GPT2LMHeadModel.from_pretrained(model_type)
        sd_hf = model_hf.state_dict()

        # copy while ensuring all of the parameters are aligned and match in names and shapes
        # 复制权重，确保所有参数名称和形状匹配
        # パラメータをコピーし、すべてのパラメータ名と形状が一致することを確認
        keys = [k for k in sd_hf if not k.endswith('attn.masked_bias')] # ignore these
        transposed = ['attn.c_attn.weight', 'attn.c_proj.weight', 'mlp.c_fc.weight', 'mlp.c_proj.weight']
        # basically the openai checkpoints use a "Conv1D" module, but we only want to use a vanilla nn.Linear.
        # this means that we have to transpose these weights when we import them
        # OpenAI检查点使用"Conv1D"模块，但我们只想使用普通的nn.Linear，所以导入时需要转置权重
        # OpenAIチェックポイントは"Conv1D"モジュールを使用していますが、普通のnn.Linearだけを使用したいため、
        # インポート時にこれらの重みを転置する必要があります
        assert len(keys) == len(sd)
        for k in keys:
            if any(k.endswith(w) for w in transposed):
                # special treatment for the Conv1D weights we need to transpose
                # 对Conv1D权重进行特殊处理：需要转置 | Conv1D重みの特別な処理：転置が必要
                assert sd_hf[k].shape[::-1] == sd[k].shape
                with torch.no_grad():
                    sd[k].copy_(sd_hf[k].t())
            else:
                # vanilla copy over the other parameters
                # 普通复制其他参数 | 他のパラメータを普通にコピー
                assert sd_hf[k].shape == sd[k].shape
                with torch.no_grad():
                    sd[k].copy_(sd_hf[k])

        return model

    def configure_optimizers(self, train_config):
        """
        配置优化器(Optimizer)，对不同类型的参数应用不同的权重衰减策略。
        
        === 为什么要区分参数？(Why separate parameters?) ===
        
        权重衰减(Weight Decay)是一种正则化技巧，用L2惩罚来减小权重：
        Loss = Original_Loss + λ * Σ(w²)
        
        但不是所有参数都应该被衰减：
        
        1. 应该衰减的参数 (decay=True):
           - Linear层的权重
           - 这些是主要的参数，衰减可以防止过拟合
           - 类比：正则化中的系数，应该被约束
        
        2. 不应该衰减的参数 (decay=False):
           - 所有的偏置(bias): 它们数量少，衰减没有显著效果
           - LayerNorm的权重和偏置: 这些是归一化参数，衰减会影响正规化效果
           - Embedding的权重: 这些是词汇表映射，衰减会改变token的语义表示
        
        === 优化器选择 ===
        
        使用AdamW优化器（Adam with Weight Decay）：
        - Adam: 自适应学习率的优化器，考虑梯度的一阶和二阶矩
        - Weight Decay: 正确的L2正则化实现（不同于L2梯度正则化）
        
        参数：
        - learning_rate: 学习率，控制更新步长
        - betas: (β₁, β₂)，分别控制一阶和二阶矩的指数平均
                 默认(0.9, 0.999)对大多数任务有效
        - weight_decay: 权重衰减系数，通常0.01-0.1之间
        
        这个长函数做的事情很简单，但代码较长且较为谨慎：
        将模型的所有参数分为两类：(1)应用权重衰减的参数，(2)不应用权重衰减的参数（偏置和层归一化/嵌入权重）。
        然后返回PyTorch优化器对象。
        
        論文参考：
        - Adam: A Method for Stochastic Optimization: https://arxiv.org/abs/1412.6980
        - Decoupled Weight Decay Regularization: https://arxiv.org/abs/1711.05101 (AdamW)
        """

        # separate out all parameters to those that will and won't experience regularizing weight decay
        # 将参数分为两类：应用和不应用权重衰减的参数
        # パラメータを2つに分ける：重み減衰が適用される/されないパラメータ
        decay = set()
        no_decay = set()
        whitelist_weight_modules = (torch.nn.Linear, )
        blacklist_weight_modules = (torch.nn.LayerNorm, torch.nn.Embedding)
        for mn, m in self.named_modules():
            for pn, p in m.named_parameters():
                fpn = '%s.%s' % (mn, pn) if mn else pn # full param name
                # random note: because named_modules and named_parameters are recursive
                # we will see the same tensors p many many times. but doing it this way
                # 随机注意：由于named_modules和named_parameters是递归的，我们会多次看到相同的张量p。
                # 但这样做允许我们知道任何张量p属于哪个父模块。
                # ランダムな注意：named_modulesとnamed_parametersは再帰的なので、同じテンソルpを何度も見ます。
                # しかし、このようにすることで、任意のテンソルpがどの親モジュールに属しているかを知ることができます。
                # allows us to know which parent module any tensor p belongs to...
                if pn.endswith('bias'):
                    # all biases will not be decayed
                    # 所有偏置不会衰减 | すべてのバイアスは減衰しません
                    no_decay.add(fpn)
                elif pn.endswith('weight') and isinstance(m, whitelist_weight_modules):
                    # weights of whitelist modules will be weight decayed
                    # 白名单模块的权重会衰减 | ホワイトリストモジュールの重みは減衰します
                    decay.add(fpn)
                elif pn.endswith('weight') and isinstance(m, blacklist_weight_modules):
                    # weights of blacklist modules will NOT be weight decayed
                    # 黑名单模块的权重不会衰减 | ブラックリストモジュールの重みは減衰しません
                    no_decay.add(fpn)

        # validate that we considered every parameter
        # 验证我们考虑了每个参数
        # すべてのパラメータを考慮していることを検証
        param_dict = {pn: p for pn, p in self.named_parameters()}
        inter_params = decay & no_decay
        union_params = decay | no_decay
        assert len(inter_params) == 0, "parameters %s made it into both decay/no_decay sets!" % (str(inter_params), )
        assert len(param_dict.keys() - union_params) == 0, "parameters %s were not separated into either decay/no_decay set!" \
                                                    % (str(param_dict.keys() - union_params), )

        # create the pytorch optimizer object
        # 创建PyTorch优化器对象
        # PyTorchオプティマイザオブジェクトを作成
        optim_groups = [
            {"params": [param_dict[pn] for pn in sorted(list(decay))], "weight_decay": train_config.weight_decay},
            {"params": [param_dict[pn] for pn in sorted(list(no_decay))], "weight_decay": 0.0},
        ]
        optimizer = torch.optim.AdamW(optim_groups, lr=train_config.learning_rate, betas=train_config.betas)
        return optimizer

    def forward(self, idx, targets=None):
        """前向传播：从token ID到logits和可选的损失
        
        参数说明：
        - idx: 输入token ID, shape (batch_size, seq_len)
               每个值在[0, vocab_size)范围内
        - targets: 目标token ID（用于训练）, shape (batch_size, seq_len)
                  如果为None，则只计算logits不计算损失（推理模式）
        
        返回值：
        - logits: 模型的原始输出, shape (batch_size, seq_len, vocab_size)
                 对应每个位置每个token的得分(未经softmax)
        - loss: 交叉熵损失(训练时使用)，标量值
               如果targets为None则返回None
        
        === 前向传播步骤详解 ===
        """
        device = idx.device
        b, t = idx.size()  # b: batch_size, t: sequence_length
        assert t <= self.block_size, f"Cannot forward sequence of length {t}, block size is only {self.block_size}"
        
        # 生成位置索引：(1, 2, 3, ..., t)
        # 用于获取位置嵌入向量
        pos = torch.arange(0, t, dtype=torch.long, device=device).unsqueeze(0)  # shape (1, t)

        # ========== 嵌入层 ==========
        # forward the GPT model itself
        # 通过GPT模型前向传播 | GPTモデルを前向き通過
        
        # 1. Token嵌入：将离散的token ID转换为连续向量
        tok_emb = self.transformer.wte(idx)  # shape: (b, t, n_embd)
                                             # token embeddings of shape (b, t, n_embd)
        
        # 2. 位置嵌入：添加位置信息（因为Transformer没有建立顺序信息）
        pos_emb = self.transformer.wpe(pos)  # shape: (1, t, n_embd)
                                             # position embeddings of shape (1, t, n_embd)
                                             # 广播到(b, t, n_embd)
        
        # 3. 融合嵌入并应用dropout
        x = self.transformer.drop(tok_emb + pos_emb)  # shape: (b, t, n_embd)
        
        # ========== Transformer层堆叠 ==========
        # 每个Block包含：
        # - 多头自注意力（Multi-Head Self-Attention）
        # - 前馈网络（Feed-Forward Network）
        # - 残差连接和层标准化
        for block in self.transformer.h:
            x = block(x)  # 通过n_layer个Block，逐层处理
        
        # ========== 输出处理 ==========
        # 4. 最后的层标准化
        x = self.transformer.ln_f(x)  # shape: (b, t, n_embd)
        
        # 5. 投影到词汇表大小
        logits = self.lm_head(x)  # shape: (b, t, vocab_size)
                                  # 每个位置每个token的原始得分(logits)

        # ========== 损失计算（仅在训练时） ==========
        # if we are given some desired targets also calculate the loss
        # 如果提供了目标，则计算损失 | ターゲットが提供されている場合は損失を計算
        loss = None
        if targets is not None:
            # 交叉熵损失：-Σ log(softmax(logits))
            # 衡量预测的概率分布与真实标签的差异
            # ignore_index=-1：忽略填充token的损失
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),  # (b*t, vocab_size)
                targets.view(-1),                   # (b*t,)
                ignore_index=-1                     # 忽略-1标记的位置
            )

        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, do_sample=False, top_k=None):
        """
        自回归文本生成：给定前缀序列，逐个生成新的token直到达到长度限制
        
        参数说明：
        - idx: 初始token序列, shape (batch_size, current_seq_len)
               例如：[50256, 464, 25] 对应三个token
        - max_new_tokens: 要生成的新token数量
        - temperature: 控制生成的随机性
                      < 1.0: 更确定（高概率token被选中）
                      = 1.0: 正常概率
                      > 1.0: 更随机（所有token概率更均匀）
        - do_sample: 采样方式
                    True: 从概率分布中随机采样（多样）
                    False: 总是选择概率最高的token（贪心）
        - top_k: Top-K采样，只从概率最高的k个token中采样
                例如top_k=40表示只考虑概率最高的40个token
        
        返回值：
        - 完成后的token序列, shape (batch_size, current_seq_len + max_new_tokens)
        
        === 生成算法步骤 ===
        
        循环max_new_tokens次：
        1. 获取当前序列（最多block_size个token）
        2. 前向传播获得下一位置的logits
        3. 应用temperature缩放logits
        4. 可选：使用top_k限制候选token
        5. 使用softmax获得概率分布
        6. 采样（或贪心）获得下一个token
        7. 追加到序列中
        
        === 生成参数的影响 ===
        
        Temperature缩放公式：logits_scaled = logits / temperature
        - temperature=0.1: logits会被放大10倍，softmax后差异变大，生成确定
        - temperature=1.0: 不改变logits，正常概率分布
        - temperature=2.0: logits被缩小2倍，所有token概率更接近，生成随机
        
        Top-K采样：
        - 找出概率最高的k个token
        - 将其他token的logits设为-∞（概率为0）
        - 只从这k个中采样，避免选中很低概率的奇怪token
        
        === 典型用法 ===
        
        # 贪心生成（确定性）
        model.eval()
        generated = model.generate(prompt, max_new_tokens=100, temperature=0.1, do_sample=False)
        
        # 多样性采样
        generated = model.generate(prompt, max_new_tokens=100, temperature=0.8, do_sample=True, top_k=40)
        
        以条件索引序列idx (LongTensor，形状为(b,t))开始，通过max_new_tokens次迭代来完成序列，
        每次将预测结果反馈回模型。通常需要确保模型处于eval()模式。
        条件付きインデックスシーケンスidx（LongTensor、形状(b,t)）から開始して、
        max_new_tokens回の反復を通じてシーケンスを完成させます。通常、モデルがeval()モードであることを確認する必要があります。
        """
        for _ in range(max_new_tokens):
            # if the sequence context is growing too long we must crop it at block_size
            # 如果序列上下文过长，需要在block_size处截断 | シーケンスコンテキストが長すぎる場合はblock_sizeで切断
            idx_cond = idx if idx.size(1) <= self.block_size else idx[:, -self.block_size:]
            # forward the model to get the logits for the index in the sequence
            # 通过模型获取序列中索引的logits值 | シーケンスのインデックスのlogit値を取得するためにモデルを通す
            logits, _ = self(idx_cond)
            # pluck the logits at the final step and scale by desired temperature
            # 获取最后一步的logits值并按温度缩放 | 最後のステップのlogit値を取得し、温度でスケーリング
            logits = logits[:, -1, :] / temperature
            # optionally crop the logits to only the top k options
            # 可选：将logits裁剪为仅前k个选项 | オプション：logitをトップkオプションのみに切り取る
            if top_k is not None:
                v, _ = torch.topk(logits, top_k)
                logits[logits < v[:, [-1]]] = -float('Inf')
            # apply softmax to convert logits to (normalized) probabilities
            # 应用softmax将logits转换为（归一化的）概率 | softmaxを適用してlogitを(正規化された)確率に変換
            probs = F.softmax(logits, dim=-1)
            # either sample from the distribution or take the most likely element
            # 从分布中采样或取最可能的元素 | 分布からサンプリングするか、最も可能性の高い要素を取得
            if do_sample:
                idx_next = torch.multinomial(probs, num_samples=1)
            else:
                _, idx_next = torch.topk(probs, k=1, dim=-1)
            # append sampled index to the running sequence and continue
            # 将采样的索引附加到运行序列并继续 | サンプリングされたインデックスを実行中のシーケンスに追加して続行
            idx = torch.cat((idx, idx_next), dim=1)

        return idx

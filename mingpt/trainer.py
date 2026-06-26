"""
Simple training loop; Boilerplate that could apply to any arbitrary neural network,
so nothing in this file really has anything to do with GPT specifically.
简单的训练循环；上済样板代码，適用于任意神经网络，
所以这个文件并没有与GPT特殊相关的业务。
粗い訓練ループ；任意のニューラルネットワークに適用可能な定定文句コード，
そのためこのファイルはGPTに特定したものは真に何もありません。
"""

import time
from collections import defaultdict

import torch
from torch.utils.data.dataloader import DataLoader
from mingpt.utils import CfgNode as CN

class Trainer:

    @staticmethod
    def get_default_config():
        C = CN()
        # device to train on
        # 训练设备 | 訓練デバイス
        C.device = 'auto'
        # dataloder parameters
        # 数据加载器参数 | データローダパラメータ
        C.num_workers = 4
        # optimizer parameters
        # 优化器参数 | オプティマイザパラメータ
        C.max_iters = None
        C.batch_size = 64
        C.learning_rate = 3e-4
        C.betas = (0.9, 0.95)
        C.weight_decay = 0.1 # only applied on matmul weights
        C.grad_norm_clip = 1.0
        return C

    def __init__(self, config, model, train_dataset):
        self.config = config
        self.model = model
        self.optimizer = None
        self.train_dataset = train_dataset
        self.callbacks = defaultdict(list)

        # determine the device we'll train on
        # 确定训练设备 | 訓練に使用するデバイスを決定
        if config.device == 'auto':
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = config.device
        self.model = self.model.to(self.device)
        print("running on device", self.device)

        # variables that will be assigned to trainer class later for logging and etc
        # 便于程序记录等活动里会稍后于训练类的变量 | 計姆などの穰会遐臨いを画描する場所で訓練クラスに割り当てられる変数
        self.iter_num = 0
        self.iter_time = 0.0
        self.iter_dt = 0.0

    def add_callback(self, onevent: str, callback):
        self.callbacks[onevent].append(callback)

    def set_callback(self, onevent: str, callback):
        self.callbacks[onevent] = [callback]

    def trigger_callbacks(self, onevent: str):
        for callback in self.callbacks.get(onevent, []):
            callback(self)

    def run(self):
        model, config = self.model, self.config

        # setup the optimizer
        # 设置优化器 | オプティマイザを設定
        self.optimizer = model.configure_optimizers(config)

        # setup the dataloader
        # 设置数据加载器 | データローダを設定
        train_loader = DataLoader(
            self.train_dataset,
            sampler=torch.utils.data.RandomSampler(self.train_dataset, replacement=True, num_samples=int(1e10)),
            shuffle=False,
            pin_memory=True,
            batch_size=config.batch_size,
            num_workers=config.num_workers,
        )

        model.train()
        self.iter_num = 0
        self.iter_time = time.time()
        data_iter = iter(train_loader)
        while True:

            # fetch the next batch (x, y) and re-init iterator if needed
            # 取上一个批次(x, y)并在必要时重新初始化迭代器 | 次のバッチ(x, y)を取得し、必要に応じて迭代子を再初期化
            try:
                batch = next(data_iter)
            except StopIteration:
                data_iter = iter(train_loader)
                batch = next(data_iter)
            batch = [t.to(self.device) for t in batch]
            x, y = batch

            # forward the model
            # 前向传播模型 | モデルを前向き通す
            logits, self.loss = model(x, y)

            # backprop and update the parameters
            # 优化参数的反向传播和更新 | パラメータを逆傳播で更新
            model.zero_grad(set_to_none=True)
            self.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.grad_norm_clip)
            self.optimizer.step()

            self.trigger_callbacks('on_batch_end')
            self.iter_num += 1
            tnow = time.time()
            self.iter_dt = tnow - self.iter_time
            self.iter_time = tnow

            # termination conditions
            # 终止条件 | 終汲条件
            if config.max_iters is not None and self.iter_num >= config.max_iters:
                break

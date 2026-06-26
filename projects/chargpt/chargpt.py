"""
Trains a character-level language model.
训练一个字符级的语言模型。
文字レベルの言語モデルを訓練します。
"""

import os
import sys

import torch
from torch.utils.data import Dataset
from torch.utils.data.dataloader import DataLoader

from mingpt.model import GPT
from mingpt.trainer import Trainer
from mingpt.utils import set_seed, setup_logging, CfgNode as CN

# -----------------------------------------------------------------------------

def get_config():

    C = CN()

    # system
    # 系统配置 | システム構成
    C.system = CN()
    C.system.seed = 3407
    C.system.work_dir = './out/chargpt'

    # data
    # 数据配置 | データ設定
    C.data = CharDataset.get_default_config()

    # model
    # 模型配置 | モデル設定
    C.model = GPT.get_default_config()
    C.model.model_type = 'gpt-mini'

    # trainer
    # 训练器配置 | トレーナー設定
    C.trainer = Trainer.get_default_config()
    C.trainer.learning_rate = 5e-4 # the model we're using is so small that we can go a bit faster
                                   # 我们使用的模型太小，可以快一点 | 使用しているモデルは非常に小さいので、少し速くできます

    return C

# -----------------------------------------------------------------------------

class CharDataset(Dataset):
    """
    Emits batches of characters
    发送批量字符
    文字のバッチを出力する
    """

    @staticmethod
    def get_default_config():
        C = CN()
        C.block_size = 128
        return C

    def __init__(self, config, data):
        self.config = config

        # 从数据中获取所有唯一字符 | データからすべての一意の文字を取得する
        chars = sorted(list(set(data)))
        data_size, vocab_size = len(data), len(chars)
        print('data has %d characters, %d unique.' % (data_size, vocab_size))

        # 创建字符到索引的映射 | 文字からインデックスへのマッピングを作成する
        self.stoi = { ch:i for i,ch in enumerate(chars) }
        self.itos = { i:ch for i,ch in enumerate(chars) }
        self.vocab_size = vocab_size
        self.data = data

    def get_vocab_size(self):
        return self.vocab_size

    def get_block_size(self):
        return self.config.block_size

    def __len__(self):
        return len(self.data) - self.config.block_size

    def __getitem__(self, idx):
        # grab a chunk of (block_size + 1) characters from the data
        # 从数据中获取(block_size + 1)个字符的块 | データから(block_size + 1)個の文字のチャンクをつかみます
        chunk = self.data[idx:idx + self.config.block_size + 1]
        # encode every character to an integer
        # 将每个字符编码为整数 | すべての文字を整数にエンコードします
        dix = [self.stoi[s] for s in chunk]
        # return as tensors
        # 作为张量返回 | テンソルとして返す
        x = torch.tensor(dix[:-1], dtype=torch.long)
        y = torch.tensor(dix[1:], dtype=torch.long)
        return x, y

# -----------------------------------------------------------------------------

if __name__ == '__main__':

    # get default config and overrides from the command line, if any
    # 获取默认配置和来自命令行的覆盖（如果有）| デフォルト設定とコマンドラインからのオーバーライドを取得します（ある場合）
    config = get_config()
    config.merge_from_args(sys.argv[1:])
    print(config)
    setup_logging(config)
    set_seed(config.system.seed)

    # construct the training dataset
    # 构建训练数据集 | 訓練データセットを構築します
    text = open('input.txt', 'r').read() # don't worry we won't run out of file handles
                                         # 不用担心，我们不会跑出文件句柄 | 心配せず、ファイルハンドルが足りなくなることはありません
    train_dataset = CharDataset(config.data, text)

    # construct the model
    # 构建模型 | モデルを構築します
    config.model.vocab_size = train_dataset.get_vocab_size()
    config.model.block_size = train_dataset.get_block_size()
    model = GPT(config.model)

    # construct the trainer object
    # 构建训练器对象 | トレーナーオブジェクトを構築します
    trainer = Trainer(config.trainer, model, train_dataset)

    # iteration callback
    # 迭代回调 | 追代ことにになるコールバック
    def batch_end_callback(trainer):

        if trainer.iter_num % 10 == 0:
            # 每10次迭代打印一次训练损失 | 10回の追代ごとに訓練損失を出力します
            print(f"iter_dt {trainer.iter_dt * 1000:.2f}ms; iter {trainer.iter_num}: train loss {trainer.loss.item():.5f}")

        if trainer.iter_num % 500 == 0:
            # evaluate both the train and test score
            # 评估训练和测试抄中 | 訓練の佐旋rawテストスコアを計算します
            model.eval()
            with torch.no_grad():
                # sample from the model...
                # 从模型中采样... | モデルからサンプリングしまし...
                context = "O God, O God!"
                x = torch.tensor([train_dataset.stoi[s] for s in context], dtype=torch.long)[None,...].to(trainer.device)
                y = model.generate(x, 500, temperature=1.0, do_sample=True, top_k=10)[0]
                completion = ''.join([train_dataset.itos[int(i)] for i in y])
                print(completion)
            # save the latest model
            # 保存最新模型 | 最新模形を保存します
            print("saving model")
            ckpt_path = os.path.join(config.system.work_dir, "model.pt")
            torch.save(model.state_dict(), ckpt_path)
            # revert model to training mode
            # 宗休模型到程式訓练程式 | モデルを訓練モードに戻します
            model.train()

    trainer.set_callback('on_batch_end', batch_end_callback)

    # run the optimization
    # 运行优化 | 最適化を実行します
    trainer.run()

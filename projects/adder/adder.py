"""
Trains a GPT to add n-digit numbers.
训练GPT来相加n位数字。
n桁の数字を足すようにGPTを訓練します。
"""

import os
import sys
import json

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
    C.system.work_dir = './out/adder'

    # data
    # 数据配置 | データ設定
    C.data = AdditionDataset.get_default_config()

    # model
    # 模型配置 | モデル設定
    C.model = GPT.get_default_config()
    C.model.model_type = 'gpt-nano'

    # trainer
    # 训练器配置 | トレーナー設定
    C.trainer = Trainer.get_default_config()
    C.trainer.learning_rate = 5e-4 # the model we're using is so small that we can go a bit faster
                                   # 我们使用的模型太小，可以快一点 | 使用しているモデルは非常に小さいので、少し速くできます

    return C

# -----------------------------------------------------------------------------

class AdditionDataset(Dataset):
    """
    Creates n-digit addition problems. For example, if n=2, then an example
    addition problem would be to add 85 + 50 = 135. This problem would be
    represented as the following string for the GPT:

    "8550531"

    创建n位数加法问题。例如，如果n=2，则一个加法问题示例
    将是相加85 + 50 = 135。此问题将用以下字符串表示
    GPT的:

    "8550531"

    n桁の加算問題を作成します。たとえば、n = 2の場合、加算の例
    問題は85 + 50 = 135を追加することでした。この問題は
    GPTの次の文字列で表されます:

    "8550531"

    This is because:
    - we are discarding the + and =, which are not necessary. We just encode the digits
      of the input numbers concatenated together.
    - the result 135 is encoded backwards to make the addition easier to learn for the
      GPT model, because of how the addition algorithm works.

    这是因为:
    - 我们丢弃了+和=，这不是必需的。我们只是编码输入
      数字的连接在一起。
    - 结果135向后编码，使加法更容易被学习
      GPT模型，因为加法算法的工作方式。

    理由は:
    - +と=を破棄しています。これは必要ありません。数字をエンコードするだけです
      入力数値が連結された
    - 結果135は逆向きにエンコードされ、加算がより学習しやすくなります
      GPTモデル、加算アルゴリズムの動作方法のため。

    As one more example, the problem 6 + 39 = 45 would be encoded as:

    "0639054"

    もう1つの例として、問題6 + 39 = 45は次のようにエンコードされます:

    "0639054"

    where you will notice that we are padding with zeros to make sure that we always
    produce strings of the exact same size: n + n + (n + 1). When n=2, this is 7.
    At test time, we will feed in an addition problem by giving the first 2n digits,
    and hoping that the GPT model completes the sequence with the next (n+1) digits
    correctly.

    您会注意到我们使用零进行填充，以确保我们总是
    生成大小完全相同的字符串: n + n + (n + 1)。当n = 2时，这是7。
    在测试时，我们将通过给出前2n个数字来提供加法问题，
    并希望GPT模型使用接下来的(n + 1)个数字完成序列
    正确。

    ご注意ください。ゼロでパディングしています。常に確保するため
    正確に同じサイズの文字列を生成します: n + n + (n + 1)。n = 2の場合、これは7です。
    テスト時に、加算問題を最初の2n桁を指定して入力します。
    GPTモデルが次の(n + 1)桁で配列を完成させることを期待
    正しく。
    """

    @staticmethod
    def get_default_config():
        C = CN()
        C.ndigit = 2
        return C

    def __init__(self, config, split):
        self.config = config
        self.split = split # train/test

        # split up all addition problems into either training data or test data
        # 将所有加法问题分为训练数据或测试数据 | すべての加算問題を訓練データまたはテストデータに分割
        ndigit = self.config.ndigit
        assert ndigit <= 3, "the lines below would be very memory inefficient, in future maybe refactor to support"
        num = (10**ndigit)**2 # total number of possible addition problems with ndigit numbers
                               # n位数可能的加法问题总数 | n桁数の可能な加算問題の総数
        rng = torch.Generator()
        rng.manual_seed(1337)
        perm = torch.randperm(num, generator=rng)
        num_test = min(int(num*0.2), 500) # 20% of the whole dataset, or only up to 500
                                          # 整个数据集的20%，或仅最多500个 | データセット全体の20%、または最大500個
        self.ixes = perm[:num_test] if split == 'test' else perm[num_test:]

    def get_vocab_size(self):
        return 10 # digits 0..9

    def get_block_size(self):
        # a,b,a+b, and +1 due to potential carry overflow,
        # but then also -1 because very last digit doesn't ever plug back
        # as there is no explicit <EOS> token to predict, it is implied
        # a、b、a + b，以及由于潜在的进位溢出而+ 1，
        # 但由于最后一个数字从不插回，也要-1
        # 因为没有明确的<EOS>标记来预测，这是隐含的
        # a, b, a + b，および潜在的なキャリオーバーフローによる+ 1、
        # しかし、最後の桁が決して差し込まれないため、-1です
        # 予測する明示的な<EOS>トークンはありません。これは暗黙です
        return 3*self.config.ndigit + 1 - 1

    def __len__(self):
        return self.ixes.nelement()

    def __getitem__(self, idx):
        ndigit = self.config.ndigit
        # given a problem index idx, first recover the associated a + b
        # 给定问题索引idx，首先恢复关联的a + b | 問題インデックスidxが与えられた場合、最初に関連するa + bを復元します
        idx = self.ixes[idx].item()
        nd = 10**ndigit
        a = idx // nd
        b = idx %  nd
        # calculate the "label" of the addition problem a + b
        # 计算加法问题a + b的"标签" | 加算問題a + bの"ラベル"を計算します
        c = a + b
        # encode the digits of a, b, c into strings
        # 将a、b、c的数字编码为字符串 | a、b、cの数字を文字列にエンコードします
        astr = f'%0{ndigit}d' % a
        bstr = f'%0{ndigit}d' % b
        cstr = (f'%0{ndigit+1}d' % c)[::-1] # reverse c to make addition easier
                                             # 反向c以使加法更容易 | 加算を簡単にするためにcを反転します
        render = astr + bstr + cstr
        dix = [int(s) for s in render] # convert each character to its token index
                                       # 将每个字符转换为其令牌索引 | 各文字をトークンインデックスに変換します
        # x will be input to GPT and y will be the associated expected outputs
        # x将是对GPT的输入，y将是相关的预期输出 | xはGPTへの入力であり、yは関連する予期される出力です
        x = torch.tensor(dix[:-1], dtype=torch.long)
        y = torch.tensor(dix[1:], dtype=torch.long) # predict the next token in the sequence
                                                    # 预测序列中的下一个令牌 | シーケンス内の次のトークンを予測します
        y[:ndigit*2-1] = -1 # we will only train in the output locations. -1 will mask loss to zero
                            # 我们将仅在输出位置进行训练。-1将掩码损失为零 | 出力位置でのみトレーニングします。-1は損失をゼロにマスクします
        return x, y

# -----------------------------------------------------------------------------

if __name__ == '__main__':

    # get default config and overrides from the command line, if any
    # 获取默认配置和来自命令行的覆盖（如果有） | デフォルト設定とコマンドラインからのオーバーライドを取得します（存在する場合）
    config = get_config()
    config.merge_from_args(sys.argv[1:])
    print(config)
    setup_logging(config)
    set_seed(config.system.seed)

    # construct train and test datasets
    # 构建训练和测试数据集 | 訓練とテストデータセットを構築します
    train_dataset = AdditionDataset(config.data, split='train')
    test_dataset  = AdditionDataset(config.data, split='test')

    # construct the model
    # 构建模型 | モデルを構築します
    config.model.vocab_size = train_dataset.get_vocab_size()
    config.model.block_size = train_dataset.get_block_size()
    model = GPT(config.model)

    # construct the trainer object
    # 构建训练器对象 | トレーナーオブジェクトを構築します
    trainer = Trainer(config.trainer, model, train_dataset)

    # helper function for the evaluation of a model
    def eval_split(trainer, split, max_batches=None):
        dataset = {'train':train_dataset, 'test':test_dataset}[split]
        ndigit = config.data.ndigit
        results = []
        mistakes_printed_already = 0
        factors = torch.tensor([[10**i for i in range(ndigit+1)][::-1]]).to(trainer.device)
        loader = DataLoader(dataset, batch_size=100, num_workers=0, drop_last=False)
        for b, (x, y) in enumerate(loader):
            x = x.to(trainer.device)
            # isolate the first two digits of the input sequence alone
            d1d2 = x[:, :ndigit*2]
            # let the model sample the rest of the sequence
            d1d2d3 = model.generate(d1d2, ndigit+1, do_sample=False) # using greedy argmax, not sampling
            # isolate the last digit of the sampled sequence
            d3 = d1d2d3[:, -(ndigit+1):]
            d3 = d3.flip(1) # reverse the digits to their "normal" order
            # decode the integers from individual digits
            d1i = (d1d2[:,:ndigit] * factors[:,1:]).sum(1)
            d2i = (d1d2[:,ndigit:ndigit*2] * factors[:,1:]).sum(1)
            d3i_pred = (d3 * factors).sum(1)
            d3i_gt = d1i + d2i # manually calculate the ground truth
            # evaluate the correctness of the results in this batch
            correct = (d3i_pred == d3i_gt).cpu() # Software 1.0 vs. Software 2.0 fight RIGHT on this line haha
            for i in range(x.size(0)):
                results.append(int(correct[i]))
                if not correct[i] and mistakes_printed_already < 5: # only print up to 5 mistakes to get a sense
                    mistakes_printed_already += 1
                    print("GPT claims that %d + %d = %d but gt is %d" % (d1i[i], d2i[i], d3i_pred[i], d3i_gt[i]))
            if max_batches is not None and b+1 >= max_batches:
                break
        rt = torch.tensor(results, dtype=torch.float)
        print("%s final score: %d/%d = %.2f%% correct" % (split, rt.sum(), len(results), 100*rt.mean()))
        return rt.sum()

    # iteration callback
    top_score = 0
    def batch_end_callback(trainer):
        global top_score

        if trainer.iter_num % 10 == 0:
            print(f"iter_dt {trainer.iter_dt * 1000:.2f}ms; iter {trainer.iter_num}: train loss {trainer.loss.item():.5f}")

        if trainer.iter_num % 500 == 0:
            # evaluate both the train and test score
            train_max_batches = {1: None, 2: None, 3: 5}[config.data.ndigit] # if ndigit=2 we can afford the whole train set, ow no
            model.eval()
            with torch.no_grad():
                train_score = eval_split(trainer, 'train', max_batches=train_max_batches)
                test_score  = eval_split(trainer, 'test',  max_batches=None)
            score = train_score + test_score
            # save the model if this is the best score we've seen so far
            if score > top_score:
                top_score = score
                print(f"saving model with new top score of {score}")
                ckpt_path = os.path.join(config.system.work_dir, "model.pt")
                torch.save(model.state_dict(), ckpt_path)
            # revert model to training mode
            model.train()

    trainer.set_callback('on_batch_end', batch_end_callback)

    # run the optimization
    trainer.run()

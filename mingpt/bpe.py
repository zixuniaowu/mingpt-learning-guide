"""
bpe is short for Byte Pair Encoder. It translates arbitrary utf-8 strings into
sequences of integers, where each integer represents small chunks of commonly
occuring characters. This implementation is based on openai's gpt2 encoder.py:
https://github.com/openai/gpt-2/blob/master/src/encoder.py
but was mildly modified because the original implementation is a bit confusing.
I also tried to add as many comments as possible, my own understanding of what's
going on.

bpe是字节对编码（Byte Pair Encoder）的缩写。它把任意utf-8字符串中
整数序列中，每个整数代表非常常见一小块文字。此实现既然openai的gpt2编码器。py网址:
https://github.com/openai/gpt-2/blob/master/src/encoder.py
或是可能粗略修改，因为原始实现有一些不清晰。
我也试着尽可能增加注释，我性上也明白了是什么一回事。

bpe是バイトペアエンコーダーの略です。それはニニ整数utf-8文字列を
整数序列、つまり各整数が粗流れく出現文字チャンク を表す。この実装既然openai の gpt2 編码器。py网址:
https://github.com/openai/gpt-2/blob/master/src/encoder.py
しかし、元々の実装めらくで気怠を起こしたため男だけ修正しました。
コメントをできるだけ追加しよう としています、私性上も明白了は什么一回事。
"""

import os
import json
import regex as re
import requests

import torch

# -----------------------------------------------------------------------------

def bytes_to_unicode():
    """
    Every possible byte (really an integer 0..255) gets mapped by OpenAI to a unicode
    每个可能的字节（实际上是整数0..255）由OpenAI映射到一个unicode字符
    每个可能なバイト（実際には整数0..255）は、OpenAIによってunicode文字にマップされます
    
    character that represents it visually. Some bytes have their appearance preserved
    它在视觉上代表它。有些字节保持其外观不变
    視覚的にそれを表すキャラクター。一部のバイトは外観が保たれています
    
    because they don't cause any trouble. These are defined in list bs. For example:
    因为他们不会造成任何麻烦。这些在list bs中定义。例如：
    彼らは問題を引き起こさないため。これらはリストbsで定義されています。例えば：
    
    chr(33) returns "!", so in the returned dictionary we simply have d[33] -> "!".
    chr(33)返回"!"，所以在返回的字典中我们只有d[33] -> "!"。
    chr(33)は"!"を返すため、返されたディクショナリではd[33] -> "!"になります。
    
    However, chr(0), for example, is '\x00', which looks ugly. So OpenAI maps these
    但是，例如chr(0)是'\x00'，看起来很丑。所以OpenAI映射这些
    しかし、たとえばchr(0)は'\x00'で、見た目が悪いです。そこでOpenAIはこれらをマップします
    
    bytes, into new characters in a range where chr() returns a single nice character.
    字节转换为一个范围内的新字符，其中chr()返回一个好看的字符。
    バイトを、chr()が単一の素敵な文字を返す範囲内の新しい文字に変換します。
    
    So in the final dictionary we have d[0] -> 'Ā' instead, which is just chr(0 + 2**8).
    所以在最终字典中，我们有d[0] -> 'Ā'，这只是chr(0 + 2**8)。
    したがって、最終的なディクショナリではd[0] -> 'Ā'があり、これはchr(0 + 2**8)です。
    
    In particular, the space character is 32, which we can see by ord(' '). Instead,
    特别是，空格字符是32，我们可以通过ord(' ')看到。相反，
    特に、スペース文字は32で、ord(' ')で見ることができます。代わりに、
    
    this function will shift space (32) by 256 to 288, so d[32] -> 'Ġ'.
    此函数将空格(32)移位256到288，所以d[32] -> 'Ġ'。
    この関数は空間(32)を256から288にシフトするため、d[32] -> 'Ġ'。
    
    So this is just a simple one-to-one mapping of bytes 0..255 into unicode characters
    所以这只是字节0..255到unicode字符的简单一一对应映射
    これは単にバイト0..255からunicode文字への単純な1対1マッピングです
    
    that "look nice", either in their original form, or a funny shifted character
    看起来"很好看"，要么是原始形式，要么是有趣的移位字符
    「見た目が良い」、元の形式か、面白いシフト文字のいずれか
    
    like 'Ā', or 'Ġ', etc.
    如'Ā'或'Ġ'等。
    「Ā」または「Ġ」など。
    """
    # the 188 integers that render fine in their original form and need no shifting
    # 188个整数在其原始形式中呈现良好，不需要移位 | 188個の整数は元の形式で正常にレンダリングされ、シフトを必要としません
    bs = list(range(ord("!"), ord("~")+1))+list(range(ord("¡"), ord("¬")+1))+list(range(ord("®"), ord("ÿ")+1))
    cs = bs[:] # all integers b in bs will simply map to chr(b) in the output dict
    # bs中的所有整数b将简单地映射到输出字典中的chr(b) | bs内のすべての整数bは、出力辞書内のchr(b)に単純にマップされます
    # now get the representations of the other 68 integers that do need shifting
    # 现在获取其他68个需要移动的整数的表示形式 | 他の68個の移動が必要な整数の表現を取得します
    # each will get mapped chr(256 + n), where n will grow from 0...67 in the loop
    # 每个都会映射到chr(256 + n)，其中n在循环中会从0...67增长 | 各々はchr(256 + n)にマップされます。ここでnはループで0...67から成長します
    n = 0
    for b in range(2**8):
        if b not in bs:
            # if this byte is "ugly" then map it to the next available "nice" character
            # 如果此字节"不好看"，则将其映射到下一个可用的"好看"字符 | このバイトが「醜い」場合は、次に利用可能な「素敵な」文字にマップします
            bs.append(b)
            cs.append(2**8+n)
            n += 1
    cs = [chr(n) for n in cs]
    d = dict(zip(bs, cs))
    return d

def get_pairs(word):
    """
    Return all bigrams as a set of tuples, of consecutive elements in the iterable word.
    """
    pairs = set()
    prev_char = word[0]
    for char in word[1:]:
        pairs.add((prev_char, char))
        prev_char = char
    return pairs

class Encoder:

    def __init__(self, encoder, bpe_merges):
        # byte encoder/decoder
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder = {v:k for k, v in self.byte_encoder.items()}
        # bpe token encoder/decoder
        self.encoder = encoder
        self.decoder = {v:k for k,v in self.encoder.items()}
        # bpe merge list that defines the bpe "tree", of tuples (a,b) that are to merge to token ab
        self.bpe_ranks = dict(zip(bpe_merges, range(len(bpe_merges))))
        # the splitting pattern used for pre-tokenization
        # 用于预标记化的分割模式 | 事前トークン化に使用される分割パターン
        # Should haved added re.IGNORECASE so BPE merges can happen for capitalized versions of contractions
        # 应该添加re.IGNORECASE，以便BPE合并可以发生在缩写词的大写版本上
        # 大文字の縮約形バージョンで発生するBPEマージのためにre.IGNORECASEを追加する必要がありました
        """
        ok so what is this regex looking for, exactly?
        这个regex到底在寻找什么? | このregexは正確に何を探していますか?
        python re reference: https://docs.python.org/3/library/re.html
        - the vertical bars | is OR, so re.findall will chunk text as the pieces match, from left to right
        - 竖杠|是OR，所以re.findall会根据左到右的匹配来分块文本 | 縦棒|はORなので、re.findallは左から右へのマッチに基づいてテキストをチャンク化します
        - '\'s' would split up things like Andrej's -> (Andrej, 's)
        - '\\'s'会将Andrej's之类的东西分割为(Andrej，'s) | '\'s'はAndrej'sのようなものを(Andrej、's)に分割します
        - ' ?\p{L}': optional space followed by 1+ unicode code points in the category "letter"
        - ' ?\p{L}'：可选空格后跟1+个"letter"类别中的unicode代码点 | ' ?\p{L}'：オプションのスペースの後に「letter」カテゴリ内の1+ unicode code点が続きます
        - ' ?\p{N}': optional space followed by 1+ unicode code points in the category "number"
        - ' ?\p{N}'：可选空格后跟1+个"number"类别中的unicode代码点 | ' ?\p{N}'：オプションのスペースの後に「number」カテゴリ内の1+ unicode code点が続きます
        - ' ?[^\s\p{L}\p{N}]+': optional space, then 1+ things that are NOT a whitespace, letter or number
        - ' ?[^\s\p{L}\p{N}]+'：可选空格，然后是1+个不是空格、字母或数字的东西 | ' ?[^\s\p{L}\p{N}]+'：オプションのスペース、その後空白、文字、または数字ではない1+の事柄
        - '\s+(?!\S)': 1+ whitespace characters (e.g. space or tab or etc) UNLESS they are followed by non-whitespace
        - '\s+(?!\S)'：1+个空白字符（例如空格或制表符等），除非后面跟着非空白字符 | '\s+(?!\S)'：1+個の空白文字（スペース、タブなど）ただし、後ろに非空白文字がない場合
                       so this will consume whitespace characters in a sequence but exclude the last whitespace in
                       因此这将在序列中消费空白字符，但排除该序列中的最后一个空白字符
                       したがって、これはシーケンス内の空白文字を消費しますが、そのシーケンス内の最後の空白を除外します
                       that sequence. that last whitespace has the opportunity to then match the optional ' ?' in
                       那个序列。最后一个空白有机会在较早的模式中匹配可选的" ?" | そのシーケンス。最後の空白には、その後、早期のパターンでオプションの ' ?'とマッチする機会があります
                       earlier patterns.
        - '\s+': 1+ whitespace characters, intended probably to catch a full trailing sequence of whitespaces at end of string
        - '\s+'：1+个空白字符，可能意在捕获字符串末尾的完整尾随空白序列 | '\s+'：1+個の空白文字。文字列の末尾にある空白の完全な末尾シーケンスをキャッチすることを目的としています
        So TLDR:
        所以简单来说： | つまり、一言で言えば：
        - we are special casing a few common apostrophe constructs ('s, 't, 're, ...) and making those into separate tokens
        - 我们特殊处理了一些常见的撇号构造（'s，'t，'re，...）并将其制成单独的令牌 | 一般的なアポストロフィ構造（'s、't、're、...）を特殊なケースにし、それらを個別のトークンにします
        - we then separate out strings into consecutive chunks of 1) letters, 2) numbers, 3) non-letter-numbers, 4) whitespaces
        - 然后我们将字符串分离为连续的块：1）字母，2）数字，3）非字母数字，4）空白 | その後、文字列を連続したチャンクに分離します：1）文字、2）数字、3）非文字数字、4）空白
        """
        self.pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")
        self.cache = {}

    def bpe(self, token):
        """
        this function uses self.bpe_ranks to iteratively merge all the possible bpe tokens
        此函数使用self.bpe_ranks迭代合并所有可能的bpe令牌
        この関数はself.bpe_ranksを使用してすべての可能なbpeトークンを反復的にマージします
        up the tree. token is a string of one individual 'word' (after regex tokenization)
        树上。token是一个单独'word'的字符串（在正则表达式标记化之后）
        ツリー。tokenはregex tokenization後の単一の「word」の文字列です
        and after byte encoding, e.g. 'Ġthere'.
        字节编码后，例如'Ġthere'。
        バイトエンコード後、例えば'Ġthere'。
        """
        # token is a string of one individual 'word', after byte encoding, e.g. 'Ġthere'
        # token是一个单独'word'的字符串，字节编码后，例如'Ġthere' | tokenはバイトエンコード後の単一の「word」の文字列、例えば'Ġthere'です

        # memoization, for efficiency
        # 记忆化，为了效率 | メモ化、効率のため
        if token in self.cache:
            return self.cache[token]

        word = tuple(token) # individual characters that make up the token, in a tuple
        # 组成token的各个字符，在一个元组中 | tokenを構成する個々の文字をタプルで保持

        pairs = get_pairs(word) # get all bigrams
        # 获取所有双字母组 | すべての二語のペアを取得

        if not pairs:
            return token

        while True:
            # find the next lowest rank bigram that can be merged
            # 找到可以合并的下一个最低等级的二字组 | マージできる次の最低ランクの二語ペアを見つけます
            bigram = min(pairs, key = lambda pair: self.bpe_ranks.get(pair, float('inf')))
            # 从pairs中找出bpe_ranks中排名最低的那个二元组
            # pairs からbpe_ranksのランクが最も低い二元組を見つけます
            if bigram not in self.bpe_ranks:
                break # no more bigrams are eligible to be merged
                # 没有更多的双字母组可以合并 | マージできるもう二語がありません

            first, second = bigram

            # we will now replace all occurences of (first, second) in the list of current
            # words into one merged token first_second, in the output list new_words
            # 我们现在将用一个合并的令牌first_second替换当前单词列表中(first, second)的所有出现
            # 現在、現在の単語リスト内の(first、second)のすべての出現を、マージされたトークンfirst_secondで置き換えます
            new_word = []
            i = 0
            while i < len(word):

                # find the next occurence of first in the sequence of current words
                # 在当前单词序列中找到第一个出现 | 現在の単語シーケンス内でfirstの次の出現を見つけます
                try:
                    j = word.index(first, i)
                    new_word.extend(word[i:j])
                    i = j
                except:
                    new_word.extend(word[i:])
                    break

                # if this occurence is also followed by second, then merge them into one
                # 如果这个出现后面也跟着second，那么将它们合并为一个 | この出現がsecondに続いている場合は、それらを1つにマージします
                if word[i] == first and i < len(word)-1 and word[i+1] == second:
                    new_word.append(first+second)
                    # 将first和second合并成一个新token | firstとsecondを1つの新しいトークンにマージします
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1

            # all occurences of (first, second) have been merged to first_second
            # (first, second)的所有出现都已合并到first_second | (first、second)のすべての出現がfirst_secondにマージされました
            new_word = tuple(new_word)
            word = new_word
            if len(word) == 1:
                break
            else:
                pairs = get_pairs(word)
                # 为下一次迭代重新计算pairs | 次のイテレーション用にpairsを再計算

        # concat all words into a string, and use ' ' as the separator. Note that
        # 将所有单词连接成一个字符串，并使用' '作为分隔符。请注意
        # by now all characters have been byte encoded, guaranteeing that ' ' is
        # 到现在为止，所有字符都已被字节编码，保证了' '
        # not used in the actual data and is a 'special' delimiter character
        # 在实际数据中未被使用，是一个"特殊"分隔符
        # すべての単語を文字列に連結し、' 'を区切り文字として使用します。これまでに
        # すべての文字はバイトエンコードされているため、' 'が実際のデータに使用されず、「特殊」区切り文字です
        word = ' '.join(word)

        # cache the result and return
        # 缓存结果并返回 | 結果をキャッシュして戻します
        self.cache[token] = word
        return word

    def encode(self, text):
        """ 
        string goes in, list of integers comes out 
        字符串进入，整数列表出来 | 文字列が入り、整数のリストが出ます
        """
        bpe_idx = []
        # pre-tokenize the input text into string tokens (words, roughly speaking)
        # 将输入文本预标记化为字符串tokens（粗略来说是单词）| 入力テキストを文字列トークン（大まかに言えば単語）に事前トークン化します
        tokens = re.findall(self.pat, text)
        # process each token into BPE integers
        # 将每个token处理为BPE整数 | 各トークンをBPE整数に処理します
        for token in tokens:
            # encode the token as a bytes (b'') object
            # 将token编码为bytes (b'') 对象 | トークンをbytes（b''）オブジェクトにエンコードします
            token_bytes = token.encode('utf-8')
            # translate all bytes to their unicode string representation and flatten
            # 将所有字节转换为其unicode字符串表示并展平 | すべてのバイトをそのunicode文字列表現に変換してフラット化します
            token_translated = ''.join(self.byte_encoder[b] for b in token_bytes)
            # perform all the applicable bpe merges according to self.bpe_ranks
            # 根据self.bpe_ranks执行所有适用的bpe合并 | self.bpe_ranksに従ってすべての適用可能なbpeマージを実行します
            token_merged = self.bpe(token_translated).split(' ')
            # translate all bpe tokens to integers
            # 将所有bpe tokens翻译为整数 | すべてのbpeトークンを整数に変換します
            token_ix = [self.encoder[bpe_token] for bpe_token in token_merged]
            # extend our running list of all output integers
            # 扩展所有输出整数的运行列表 | すべての出力整数の実行中のリストを拡張します
            bpe_idx.extend(token_ix)
        return bpe_idx

    def encode_and_show_work(self, text):
        """ 
        debugging function, same as encode but returns all intermediate work 
        调试函数，与encode相同但返回所有中间工作 | デバッグ関数、encodeと同じですがすべての中間作業を返します
        """
        bpe_idx = []
        parts = []
        tokens = re.findall(self.pat, text)
        # 使用预编译的正则表达式模式进行预标记化 | 事前コンパイルされた正規表現パターンを使用して事前トークン化します
        for token in tokens:
            token_bytes = token.encode('utf-8')
            # 将token编码为UTF-8字节 | トークンをUTF-8バイトにエンコードします
            token_translated = ''.join(self.byte_encoder[b] for b in token_bytes)
            # 使用byte_encoder将每个字节转换为unicode字符 | byte_encoderを使用して各バイトをunicode文字に変換します
            token_merged = self.bpe(token_translated).split(' ')
            # 应用BPE合并，然后按空格分割回令牌 | BPEマージを適用し、スペースで分割してトークンに戻します
            token_ix = [self.encoder[bpe_token] for bpe_token in token_merged]
            # 将merged tokens翻译为对应的整数索引 | マージされたトークンを対応する整数インデックスに変換します
            bpe_idx.extend(token_ix)
            # 将此token的整数添加到最终输出列表 | このトークンの整数を最終出力リストに追加します
            parts.append({
                'token': token,
                # 原始token字符串 | 元のトークン文字列
                'token_bytes': token_bytes,
                # token的UTF-8字节表示 | トークンのUTF-8バイト表現
                'token_translated': token_translated,
                # 字节转换为unicode后的字符串 | バイトをunicodeに変換した後の文字列
                'token_merged': token_merged,
                # BPE合并后的tokens | BPEマージ後のトークン
                'token_ix': token_ix,
                # 最终的整数索引 | 最終的な整数インデックス
            })
        out = {
            'bpe_idx': bpe_idx, # the actual output sequence
            # 实际的输出序列 | 実際の出力シーケンス
            'tokens': tokens, # result of pre-tokenization
            # 预标记化的结果 | 事前トークン化の結果
            'parts': parts, # intermediates for each token part
            # 每个token部分的中间值 | 各トークン部分の中間値
        }
        return out

    def decode(self, bpe_idx):
        """ 
        list of integers comes in, string comes out 
        整数列表进入，字符串出来 | 整数リストが入り、文字列が出ます
        """
        # inverse map the integers to get the tokens
        # 反向映射整数以获取tokens | 整数を逆マップしてトークンを取得します
        tokens_merged = [self.decoder[token] for token in bpe_idx]
        # inverse the byte encoder, e.g. recovering 'Ġ' -> ' ', and get the bytes
        # 反向byte编码器，例如恢复'Ġ' -> ' '，并获取字节 | byte エンコーダーを逆にし、例えば'Ġ' -> ' 'を復旧してバイトを取得します
        tokens_flat = ''.join(tokens_merged)
        # 将所有merged tokens连接成一个长字符串 | すべてのマージされたトークンを1つの長い文字列に連結します
        tokens_bytes = bytearray([self.byte_decoder[c] for c in tokens_flat])
        # 使用byte_decoder将unicode字符转换回原始字节 | byte_decoderを使用してunicode文字を元のバイトに変換します
        # recover the full utf-8 string
        # 恢复完整的UTF-8字符串 | 完全なUTF-8文字列を復旧します
        text = tokens_bytes.decode('utf-8', errors='replace')
        # 使用UTF-8解码字节序列，如果有无法解码的字节就用替代字符 | バイトシーケンスをUTF-8でデコードし、解码できないバイトがあれば置換文字を使用します
        return text

def get_file(local_file, remote_file):
    """ 
    downloads remote_file to local_file if necessary 
    如果必要，将remote_file下载到local_file | 必要に応じてremote_fileをlocal_fileにダウンロードします
    """
    if not os.path.isfile(local_file):
        # 检查local_file是否已经存在 | local_fileが既に存在するかチェックします
        print(f"downloading {remote_file} to {local_file}")
        response = requests.get(remote_file)
        # 从远程URL获取文件内容 | リモートURLからファイル内容を取得します
        open(local_file, "wb").write(response.content)
        # 将下载的内容保存到本地文件 | ダウンロードされた内容をローカルファイルに保存します

def get_encoder():
    """
    Returns an instance of the GPT BPE Encoder/Decoder
    and handles caching of "database" files.
    GPT BPEエンコーダー/デコーダーのインスタンスを返し、
    "データベース"ファイルのキャッシュを処理します
    """
    home_dir = os.path.expanduser('~')
    # 获取用户主目录 | ユーザーのホームディレクトリを取得します
    cache_dir = os.path.join(home_dir, '.cache', 'mingpt')
    # 创建mingpt缓存目录的路径 | mingptキャッシュディレクトリのパスを作成します
    os.makedirs(cache_dir, exist_ok=True)
    # 创建缓存目录，如果不存在的话 | キャッシュディレクトリを作成します（存在しない場合）

    # load encoder.json that has the raw mappings from token -> bpe index
    # 加载encoder.json，其中包含token -> bpe索引的原始映射
    # token->bpe索引の生のマッピングを持つencoder.jsonをロードします
    encoder_local_file = os.path.join(cache_dir, 'encoder.json')
    encoder_remote_file = 'https://openaipublic.blob.core.windows.net/gpt-2/models/124M/encoder.json'
    get_file(encoder_local_file, encoder_remote_file)
    with open(encoder_local_file, 'r') as f:
        encoder = json.load(f)
        # 加载encoder.json中的映射：token字符串 -> 整数索引
        # encoder.jsonのマッピングをロード：トークン文字列->整数インデックス
    assert len(encoder) == 50257 # 256 individual byte tokens, 50,000 merged tokens, and 1 special <|endoftext|> token
    # 验证encoder包含正确的token数量 | encoderに正しいトークン数が含まれていることを確認します

    # load vocab.bpe that contains the bpe merges, i.e. the bpe tree structure
    # 加载vocab.bpe，其中包含bpe合并，即bpe树结构
    # vocab.bpeをロードします。これにはbpe merge、つまりbpeツリー構造が含まれます
    # in the form tuples (a, b), that indicate that (a, b) is to be merged to one token ab
    # (a, b)形式的元组，表示(a, b)要合并成一个token ab
    # (a, b)形式のタプル。(a、b)を1つのトークンabにマージすることを示します
    vocab_local_file = os.path.join(cache_dir, 'vocab.bpe')
    vocab_remote_file = 'https://openaipublic.blob.core.windows.net/gpt-2/models/124M/vocab.bpe'
    get_file(vocab_local_file, vocab_remote_file)
    with open(vocab_local_file, 'r', encoding="utf-8") as f:
        bpe_data = f.read()
        # 读取vocab.bpe文件内容 | vocab.bpeファイルの内容を読み込みます
    # light postprocessing: strip the version on first line and the last line is a blank
    # 轻量级后处理：去掉第一行的版本和最后一行的空行
    # 軽量な後処理：最初の行のバージョンと最後の行のブランクを削除します
    bpe_merges = [tuple(merge_str.split()) for merge_str in bpe_data.split('\n')[1:-1]]
    # 将BPE merge数据解析为(token1, token2)元组列表
    # BPE mergeデータを(token1、token2)タプルのリストに解析します
    assert len(bpe_merges) == 50000 # 50,000 merged tokens

    # construct the Encoder object and return
    # 构造Encoder对象并返回 | Encoderオブジェクトを構成して戻します
    enc = Encoder(encoder, bpe_merges)
    return enc

# -----------------------------------------------------------------------------

class BPETokenizer:
    """ 
    PyTorch-aware class that wraps the Encoder above 
    PyTorch感知的类，包装上面的Encoder | 上記のEncoderをラップするPyTorch認識クラス
    """

    def __init__(self):
        # 初始化BPETokenizer，并加载或下载GPT-2编码器
        # BPETokenizerを初期化し、GPT-2エンコーダーをロードまたはダウンロードします
        self.encoder = get_encoder()

    def __call__(self, text, return_tensors='pt'):
        # PyTorch only; here because we want to match huggingface/transformers interface
        # 仅PyTorch；这里是为了匹配huggingface/transformers接口
        # PyTorchのみ。huggingface/transformersインターフェースと一致させたいのでここにあります
        assert return_tensors == 'pt'
        # single string input for now, in the future potentially a list of strings
        # 目前是单个字符串输入，将来可能是字符串列表
        # 今のところ単一の文字列入力、将来的には文字列のリストの可能性があります
        assert isinstance(text, str)
        # encode and create a "batch dimension" of 1
        # 编码并创建batch维度1 | エンコードしてバッチ次元1を作成します
        idx = [self.encoder.encode(text)]
        # 使用Encoder的encode方法将文本转换为整数列表，然后放入列表中以创建batch维度
        # Encoderのencodeメソッドを使用してテキストを整数リストに変換し、バッチ次元を作成するリストに入れます
        # wrap into PyTorch tensor
        # 包装成PyTorch张量 | PyTorchテンソルでラップします
        out = torch.tensor(idx, dtype=torch.long)
        return out

    def decode(self, idx):
        # ensure a simple 1D tensor for now
        # 确保现在是一个简单的1D张量 | 今のところは単純な1Dテンソルであることを確認してください
        assert idx.ndim == 1
        # decode indices to text
        # 将索引解码为文本 | インデックスをテキストにデコードします
        text = self.encoder.decode(idx.tolist())
        # 使用Encoder的decode方法将整数列表转换回文本
        # Encoderのdecodeメソッドを使用して整数リストをテキストに変換します
        return text


if __name__ == '__main__':

    # here is an encoding example
    # 这是一个编码示例 | これはエンコード例です
    text = "Hello!! I'm Andrej Karpathy. It's 2022. w00t :D 🤗"
    e = get_encoder()
    # 获取GPT-2 BPE编码器 | GPT-2 BPEエンコーダーを取得します
    r = e.encode_and_show_work(text)
    # 使用encode_and_show_work获取所有中间步骤 | encode_and_show_workを使用してすべての中間ステップを取得します

    print("Original text is:")
    print(text)
    # 打印原始文本 | 元のテキストを印刷します
    print("First the text gets pre-tokenized, broken up into chunks, the outcome is:")
    print(r['tokens'])
    # 首先文本被预标记化，分成块 | 最初、テキストは事前トークン化され、チャンクに分割されます
    # ['Hello', '!!', ' I', "'m", ' Andrej', ' Karpathy', '.', ' It', "'s", ' 2022', '.', ' w', '00', 't', ' :', 'D', ' 🤗']
    print("Then we iterate over each chunk and process them in turn...")
    # 然后我们迭代每个块并依次处理它们 | 次に、各チャンクを反復処理し、順番に処理します
    for part in r['parts']:
        print(part)
        # 打印每个token的处理步骤 | 各トークンの処理ステップを印刷します
    # {'token': 'Hello', 'token_bytes': b'Hello', 'token_translated': 'Hello', 'token_merged': ['Hello'], 'token_ix': [15496]}
    # {'token': '!!', 'token_bytes': b'!!', 'token_translated': '!!', 'token_merged': ['!!'], 'token_ix': [3228]}
    # {'token': ' I', 'token_bytes': b' I', 'token_translated': 'ĠI', 'token_merged': ['ĠI'], 'token_ix': [314]}
    # {'token': "'m", 'token_bytes': b"'m", 'token_translated': "'m", 'token_merged': ["'m"], 'token_ix': [1101]}
    # {'token': ' Andrej', 'token_bytes': b' Andrej', 'token_translated': 'ĠAndrej', 'token_merged': ['ĠAndre', 'j'], 'token_ix': [10948, 73]}
    # {'token': ' Karpathy', 'token_bytes': b' Karpathy', 'token_translated': 'ĠKarpathy', 'token_merged': ['ĠK', 'arp', 'athy'], 'token_ix': [509, 5117, 10036]}
    # {'token': '.', 'token_bytes': b'.', 'token_translated': '.', 'token_merged': ['.'], 'token_ix': [13]}
    # {'token': ' It', 'token_bytes': b' It', 'token_translated': 'ĠIt', 'token_merged': ['ĠIt'], 'token_ix': [632]}
    # {'token': "'s", 'token_bytes': b"'s", 'token_translated': "'s", 'token_merged': ["'s"], 'token_ix': [338]}
    # {'token': ' 2022', 'token_bytes': b' 2022', 'token_translated': 'Ġ2022', 'token_merged': ['Ġ2022'], 'token_ix': [33160]}
    # {'token': '.', 'token_bytes': b'.', 'token_translated': '.', 'token_merged': ['.'], 'token_ix': [13]}
    # {'token': ' w', 'token_bytes': b' w', 'token_translated': 'Ġw', 'token_merged': ['Ġw'], 'token_ix': [266]}
    # {'token': '00', 'token_bytes': b'00', 'token_translated': '00', 'token_merged': ['00'], 'token_ix': [405]}
    # {'token': 't', 'token_bytes': b't', 'token_translated': 't', 'token_merged': ['t'], 'token_ix': [83]}
    # {'token': ' :', 'token_bytes': b' :', 'token_translated': 'Ġ:', 'token_merged': ['Ġ:'], 'token_ix': [1058]}
    # {'token': 'D', 'token_bytes': b'D', 'token_translated': 'D', 'token_merged': ['D'], 'token_ix': [35]}
    # {'token': ' 🤗', 'token_bytes': b' \xf0\x9f\xa4\x97', 'token_translated': 'ĠðŁ¤Ĺ', 'token_merged': ['ĠðŁ', '¤', 'Ĺ'], 'token_ix': [12520, 97, 245]}
    # (refer to the code inside Encoder.encode for what these intermediates are)
    # (参考Encoder.encode内的代码了解这些中间值是什么) | (Encoder.encode内のコードを参照して、これらの中間値が何であるかを確認してください)
    print("and the final outcome is concatenating and flattening all the token_ix:")
    # 最终结果是连接和展平所有token_ix | 最終結果は、すべてのtoken_ixを連結してフラット化することです
    print(r['bpe_idx'])
    # [15496, 3228, 314, 1101, 10948, 73, 509, 5117, 10036, 13, 632, 338, 33160, 13, 266, 405, 83, 1058, 35, 12520, 97, 245]
    # this would then become the integer input sequence to the transformer
    # 这将成为transformer的整数输入序列 | これはtransformerの整数入力シーケンスになります
    print("ready to feed into a Transformer!")
    # 准备好输入到Transformer中 | Transformerに入力する準備ができました

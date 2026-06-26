with open('C:/Users/zixun/dev/minGPT/docs/learning_guide.html', encoding='utf-8') as f:
    cn = f.read()
import re
sections = re.findall(r'<section id="([^"]+)"', cn)
for s in sections:
    idx = cn.find('<section id="' + s + '"')
    section = cn[idx:idx+800]
    first_p = section.find('<p>')
    if first_p >= 0:
        p_text = section[first_p+3:first_p+150]
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in p_text)
        print(f'  {s}: {"ZH" if has_chinese else "EN"}')

"""Regenerates _build/pages/privacy-policy.html and terms-of-use.html from the
plain-text sources in this folder (copied word-for-word from the live site).
Syntax: '## ' = section heading, '- ' = bullet, '-- ' = bullet with 20px spacing, **bold**. Run: python3 _build/legal/gen.py"""
import html,os,re,sys
HERE=os.path.dirname(os.path.abspath(__file__)); PAGES=os.path.join(HERE,'..','pages')
def esc(t):
    # escape text but keep the explicit <br> and <a ...> we put in the source
    keep=[]
    def k(m): keep.append(m.group(0)); return f'\x00{len(keep)-1}\x00'
    t=re.sub(r'<br>|<a [^>]+>|</a>',k,t)
    t=html.escape(t,quote=False)
    t=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',t)
    return re.sub(r'\x00(\d+)\x00',lambda m:keep[int(m.group(1))],t)
def build(src,title,updated):
    out=[f'<section class="legal">\n  <div class="container">\n    <div class="legal-body">\n      <h1>{title}</h1>\n      <p class="legal-updated">Updated: {updated}</p>']
    ul=False
    for line in open(src,encoding='utf-8').read().strip().split('\n'):
        if line.startswith('-- ') or line.startswith('- '):
            spaced=line.startswith('-- '); txt=line[3:] if spaced else line[2:]
            if not ul: out.append('      <ul class="spaced">' if spaced else '      <ul>'); ul=True
            out.append(f'        <li>{esc(txt)}</li>'); continue
        if ul: out.append('      </ul>'); ul=False
        if line.startswith('## '): out.append(f'      <h2 class="legal-h">{esc(line[3:])}</h2>')
        else: out.append(f'      <p>{esc(line)}</p>')
    if ul: out.append('      </ul>')
    out.append('    </div>\n  </div>\n</section>\n')
    return '\n'.join(out)
open(os.path.join(PAGES,'privacy-policy.html'),'w',encoding='utf-8').write(build(os.path.join(HERE,'privacy.txt'),'Consumer Privacy Policy','11/05/23'))
open(os.path.join(PAGES,'terms-of-use.html'),'w',encoding='utf-8').write(build(os.path.join(HERE,'terms.txt'),'Terms of Use','11/05/23'))
print('ok')

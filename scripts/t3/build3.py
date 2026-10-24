import json, re, subprocess
R='/Users/saga/reels-montage/'; FF=R+'node_modules/ffmpeg-static/ffmpeg'
FILES={'1878':'IMG_1878 2.MOV','1876':'IMG_1876 2.MOV'}
DURS={'1878':104.12,'1876':227.38}
# ---------- silences
sil={}
for n in FILES:
    out=subprocess.run([FF,'-hide_banner','-i',R+f'cache/t3/a{n}.wav','-af','silencedetect=noise=-45dB:d=0.2','-f','null','-'],capture_output=True,text=True).stderr
    L=[];s=None
    for l in out.splitlines():
        m=re.search(r'silence_start: ([\d.]+)',l)
        if m: s=float(m.group(1))
        m=re.search(r'silence_end: ([\d.]+)',l)
        if m and s is not None: L.append((s,float(m.group(1)))); s=None
    if s is not None: L.append((s,DURS[n]))
    sil[n]=L
# ---------- corrected words
w78=json.load(open(R+'cache/t3/words1878_raw.json')); w76=json.load(open(R+'cache/t3/words1876_raw.json'))
fix78={13:['акне.'],29:['Юта'],35:['Nolla'],48:['сканируете'],49:['своё'],51:['а'],52:['потом'],54:['интеллект'],57:['акне'],
 106:['карт-бланш'],107:None,120:['ограничена'],122:None,123:['восемью']}
fix76={152:None,156:None,181:['машины.'],212:['счёт?']}
def apply(words,fix,keep_idx=None):
    out=[]
    for i,x in enumerate(words):
        if keep_idx is not None and i not in keep_idx: continue
        if i in fix:
            if fix[i] is None: continue
            n=len(fix[i]); d=(x['end']-x['start'])/n
            for k,t in enumerate(fix[i]): out.append({'word':t,'start':round(x['start']+k*d,3),'end':round(x['start']+(k+1)*d,3),'prob':x['prob']})
        else: out.append(dict(x))
    return out
# special merges
w78[36]['word']='Derm.'
w76[151]['word']='отвечать-то,'; w76[155]['word']='какая-то'
keep76=set(list(range(144,164))+list(range(169,182))+list(range(182,189))+list(range(208,222)))
words={'1878':apply(w78,fix78),'1876':apply(w76,fix76,keep76)}
# fix typos in merged tokens (a '-то' word was replaced above by None)
def subtract(iv,cuts):
    res=[iv]
    for c0,c1 in cuts:
        new=[]
        for a,b in res:
            if c1<=a or c0>=b: new.append((a,b)); continue
            if c0>a: new.append((a,c0))
            if c1<b: new.append((c1,b))
        res=new
    return res
# ---------- units: contiguous runs of words per file; pauses are found from the words themselves
def run(f,idx_ranges):
    allw=apply(w78 if f=='1878' else w76, fix78 if f=='1878' else fix76, set(i for a,b in idx_ranges for i in range(a,b+1)))
    return allw
units=[('1878',run('1878',[(0,152)]))]
for rng in [(144,163),(169,181),(182,188),(208,221)]:
    units.append(('1876',run('1876',[rng])))
segs=[];t=0.0;kept_words={'1878':[],'1876':[]}
for f,ws in units:
    a=max(0,ws[0]['start']-0.15); b=min(DURS[f],ws[-1]['end']+0.25)
    cuts=[]
    for x,y in zip(ws,ws[1:]):
        if y['start']-x['end']>0.5: cuts.append((x['end']+0.12,y['start']-0.12))
    for p_,q_ in subtract((a,b),cuts):
        if q_-p_>=0.12:
            segs.append({'file':f,'src_start':round(p_,3),'src_end':round(q_,3)})
    kept_words[f]+=ws
m=[]
for s_ in segs:
    if m and m[-1]['file']==s_['file'] and abs(s_['src_start']-m[-1]['src_end'])<0.03: m[-1]['src_end']=s_['src_end']
    else: m.append(dict(s_))
t=0
for s_ in m:
    d=s_['src_end']-s_['src_start']; s_['out_start']=round(t,3); t+=d; s_['out_end']=round(t,3)
segs=m
before=sum(DURS.values())
json.dump({'before_files':DURS,'after':round(t,2),'segments':segs},open(R+'cache/t3/cuts.json','w'),indent=1)
words=kept_words
# ---------- remap words
out=[]
for f in ('1878','1876'):
    for x in words[f]:
        c=(x['start']+x['end'])/2
        for s in segs:
            if s['file']==f and s['src_start']-0.02<=c<=s['src_end']+0.02:
                o=s['out_start']-s['src_start']
                out.append({'word':x['word'],'start':round(max(s['out_start'],x['start']+o),3),'end':round(min(s['out_end'],x['end']+o),3),'prob':x['prob'],'src':f}); break
out.sort(key=lambda x:x['start'])
json.dump(out,open(R+'cache/t3/words_cut.json','w'),ensure_ascii=False,indent=0)
print('segments',len(segs),'after',round(t,1),'s  (was',round(before,1),'across two files; best take alone 104.1)')
sent=[];cur=[]
for x in out:
    cur.append(x['word'])
    if x['word'][-1] in '.?!': sent.append(' '.join(cur));cur=[]
if cur: sent.append(' '.join(cur))
print('\n'.join(sent))
print('LOW',[(x['word'],round(x['start'],1)) for x in out if x['prob']<0.55])

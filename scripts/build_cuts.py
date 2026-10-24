import json, re, subprocess
R='/Users/saga/reels-montage/'
FF=R+'node_modules/ffmpeg-static/ffmpeg'
raw=json.load(open(R+'cache/words_raw2.json'))
DUR=194.14

# --- 1. corrected words (index -> replacement text); None = drop word
fix={30:'каждое',31:'пятно',39:'Прыщ,',43:'покраснение',80:'пятен',81:'пигментных,',134:'тоник',
     121:'появляются',126:'вызывают',193:'что-то',108:'Первое,',214:'Пятое,',274:'Пять',
     159:None}
words=[]
for i,x in enumerate(raw):
    x=dict(x)
    if i in fix:
        if fix[i] is None: continue
        x['word']=fix[i]
    if i==116:  # Микро + травмы -> Микротравмы
        x['word']='Микротравмы,'; x['end']=raw[117]['end']
    if i==117: continue
    if i==181:  # Проводавливать -> Про выдавливание
        mid=round((x['start']+x['end'])/2,3)
        words.append({'word':'Про','start':x['start'],'end':mid,'prob':x['prob'],'i':i})
        x['word']='выдавливание'; x['start']=mid
    if i==108: x['start']=79.55; x['end']=79.96
    if i==234: x['start']=151.52; x['end']=151.66
    if i==213: x['word']='и'; x['start']=143.74; x['end']=143.9
    x['i']=i
    words.append(x)

# --- 2. real silences from the audio
out=subprocess.run([FF,'-hide_banner','-i',R+'cache/audio.wav','-af','silencedetect=noise=-45dB:d=0.2','-f','null','-'],capture_output=True,text=True).stderr
sil=[];s=None
for l in out.splitlines():
    m=re.search(r'silence_start: ([\d.]+)',l)
    if m: s=float(m.group(1))
    m=re.search(r'silence_end: ([\d.]+)',l)
    if m and s is not None: sil.append((s,float(m.group(1)))); s=None
if s is not None: sil.append((s,DUR))

# --- 3. snap word edges out of silence
for x in words:
    for a,b in sil:
        if a<=x['start']<b and x['end']>b: x['start']=round(b,3)
        if a<x['end']<=b and x['start']<a: x['end']=round(a,3)
    if x['end']<=x['start']: x['end']=round(x['start']+0.05,3)
json.dump([{k:v for k,v in x.items() if k!='i'} for x in words],open(R+'cache/words.json','w'),ensure_ascii=False,indent=0)

# --- 4. cuts
spans=[(0.0,50.2),(79.4,187.5),(190.28,DUR)]
def snap(sp):
    a,b=sp
    for x,y in sil:
        if x<=a<y: a=y-0.1
        if x<b<=y: b=x+0.1
    return (round(a,3),round(b,3))
spans=[snap(sp) for sp in spans]      # 50.2-79.4: first failed take + 18 s pause; 187.5-190.28: duplicate outro line
filler_idx={191,192,199,207,208,209,236,237}
removed_words=[(x['start'],x['end']) for x in words if x['i'] in filler_idx]
def subtract(iv, cuts):
    res=[iv]
    for c0,c1 in cuts:
        new=[]
        for a,b in res:
            if c1<=a or c0>=b: new.append((a,b)); continue
            if c0>a: new.append((a,c0))
            if c1<b: new.append((c1,b))
        res=new
    return res
pause_cuts=[(a+0.1,b-0.1) for a,b in sil if b-a>0.5]
keep=[]
for sp in spans:
    parts=subtract(sp,pause_cuts+removed_words)
    keep+= [(round(a,3),round(b,3)) for a,b in parts if b-a>=0.2]
# merge tiny gaps (<0.03s)
merged=[]
for a,b in keep:
    if merged and a-merged[-1][1]<0.03: merged[-1]=(merged[-1][0],b)
    else: merged.append((a,b))
keep=[(a,b) for a,b in merged if any(a-0.01<=(x['start']+x['end'])/2<=b+0.01 for x in words if x['i'] not in filler_idx)]
t=0;segs=[]
for a,b in keep:
    segs.append({'src_start':a,'src_end':b,'out_start':round(t,3),'out_end':round(t+b-a,3)}); t+=b-a
cuts={'source':'input/IMG_0948.MOV','duration_before':DUR,'duration_after':round(t,2),'segments':segs}
json.dump(cuts,open(R+'cache/cuts.json','w'),indent=1)

# --- 5. words on new timeline
def remap(x):
    for sg in segs:
        c=(x['start']+x['end'])/2
        if sg['src_start']-0.01<=c<=sg['src_end']+0.01:
            o=sg['out_start']-sg['src_start']
            return {'word':x['word'],'start':round(max(sg['out_start'],x['start']+o),3),'end':round(min(sg['out_end'],x['end']+o),3),'prob':x['prob']}
    return None
wc=[r for r in (remap(x) for x in words if x['i'] not in filler_idx) if r]
json.dump(wc,open(R+'cache/words_cut.json','w'),ensure_ascii=False,indent=0)
print('segments',len(segs),'before',DUR,'after',round(t,2))
# text of what remains, by sentence
line=[];
for x in wc:
    line.append(x['word'])
print(' '.join(line))
low=[(x['word'],x['start']) for x in words if x['prob']<0.55]
print('LOW',low)

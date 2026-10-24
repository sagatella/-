import json,re
R='/Users/saga/reels-montage/'
SPEED=1.12
w=json.load(open(R+'cache/words_cut.json'))
cuts=json.load(open(R+'cache/cuts.json'))
actual=json.load(open(R+'cache/seg_actual.json'))   # real length of every sped-up segment (frames/30)
SEG=[]; t_=0.0
for sg,d in zip(cuts['segments'],actual):
    SEG.append((sg['out_start'],sg['out_end'],t_)); t_+=d      # 1x start, 1x end, real final start
TOTAL=round(t_,3)
def tf(t):
    """1x-timeline seconds -> real position in the sped-up rough.mp4"""
    for a,b,f in SEG:
        if a-1e-6<=t<=b+1e-6: return round(f+(t-a)/SPEED,3)
    if t<SEG[0][0]: return round(SEG[0][2],3)
    # in a cut-out gap: snap to the next segment start
    for a,b,f in SEG:
        if t<a: return round(f,3)
    return TOTAL
for x in w:
    c_=(x['start']+x['end'])/2
    for a,b,f in SEG:
        if a-0.02<=c_<=b+0.02:
            x['start']=round(f+max(0,x['start']-a)/SPEED,3); x['end']=round(f+min(b-a,x['end']-a)/SPEED,3); break
for i_,sg in enumerate(cuts['segments']):
    sg['out_start']=round(SEG[i_][2],3); sg['out_end']=round(SEG[i_][2]+actual[i_],3)
cuts['duration_after']=TOTAL
# fix tiny overlaps
for a,b in zip(w,w[1:]):
    if a['end']>b['start']: a['end']=max(a['start']+0.05,b['start'])
def clean(s): return re.sub(r'[^\w-]','',s.lower())
# merge "когда" + "-то"
mw=[]
for x in w:
    if x['word'].startswith('-') and mw:
        mw[-1]['word']+=x['word']; mw[-1]['end']=x['end']
    else: mw.append(dict(x))
w=mw
# sentences
sents=[];cur=[]
for x in w:
    cur.append(x)
    if x['word'][-1] in '.?!': sents.append(cur); cur=[]
if cur: sents.append(cur)
FN={'и','в','на','а','же','то','как','не','с','от','для','через','мы','у','что','по','за','к','из','но','или','одно','один','две','этих','нашу','наше','своё','тот','вообще','еще'}
FS=78; F=0.72; LINE_W=876
def nlines(ws):
    cur=0; n=1
    for x in ws:
        wpx=len(x['word'])*F*FS
        add=wpx+(0.26*FS if cur>0 else 0)
        if cur+add>LINE_W: n+=1; cur=wpx
        else: cur+=add
    return n
def chunk(sent):
    n=len(sent)
    if n<=5:
        txt=' '.join(y['word'] for y in sent)
        if nlines(sent)<=2 and len(txt)<=34: return [sent]
        if n<4: return [sent]
        # too many characters for two lines: split in two, as even by characters as possible
        best=None
        for k in range(2,n-1):
            a_=' '.join(y['word'] for y in sent[:k]); b_=' '.join(y['word'] for y in sent[k:])
            m_=max(len(a_),len(b_))
            if best is None or m_<best[0]: best=(m_,k)
        k=best[1] if best else n//2
        return [sent[:k],sent[k:]]
    best={0:(0,[])}
    for i in range(1,n+1):
        cand=None
        for k in (2,3,4,5):
            j=i-k
            if j<0 or j not in best: continue
            ws=sent[j:i]; txt=' '.join(y['word'] for y in ws)
            cost=best[j][0]+0.3*(k-4)**2+(10 if (len(txt)>34 or nlines(ws)>2) else 0)+(0 if ws[-1]['word'][-1] in ',.?!' or i==n else 1.0)+(2.5 if i<n and clean(ws[-1]['word']) in FN else 0)+(2.5 if i<n and clean(sent[i]['word']) in ('же','недели') else 0)
            if cand is None or cost<cand[0]: cand=(cost,best[j][1]+[ws])
        if cand: best[i]=cand
    return best[n][1] if n in best else [sent]
# 1-word sentence ("Четвёртое.") joins the next one
ms=[]
for s_ in sents:
    if ms and len(ms[-1])==1: ms[-1]=ms[-1]+s_
    else: ms.append(s_)
sents=ms
groups=[]
for s_ in sents: groups+=chunk(s_)
# accents: priority ordinals + a few key words, min gap 10 words
ordinals={'первое','второе','третье','четвёртое','пятое'}
keys={'пигмент','воспалением','пятно','скраб','воспаление','тоник','руками','снимка','профиле','фото'}
n=len(w); acc=set()
cand=[i for i,x in enumerate(w) if clean(x['word']) in ordinals]
for i in cand: acc.add(i)
for i,x in enumerate(w):
    if clean(x['word']) in keys and i not in acc and all(abs(i-j)>=10 for j in acc): acc.add(i)
idx=0;caps=[]
for gi,g in enumerate(groups):
    ws=[]
    for x in g:
        ws.append({'w':x['word'],'s':x['start'],'e':x['end'],'accent':idx in acc}); idx+=1
    start=g[0]['start']; last_end=g[-1]['end']
    nxt=groups[gi+1][0]['start'] if gi+1<len(groups) else None
    end=min(nxt,last_end+0.3) if nxt is not None and nxt-last_end<0.35 else last_end+0.2
    caps.append({'start':round(start,3),'end':round(end,3),'words':ws})
def I(a,b,**k): return dict(start=tf(a),end=tf(b),**k)
INSERTS=[
 I(5.6,7.6,kind='image',src='ins/IMG_0951.jpg',position='50% 55%'),
 I(9.4,11.4,kind='image',src='ins/IMG_0954.jpg',position='50% 35%'),
 I(13.3,15.3,kind='image',src='ins/IMG_0952.jpg',position='50% 40%'),
 I(19.2,21.7,kind='video',src='ins/melanocyte.mp4',trimFrom=0.2,position='50% 70%'),
 I(29.9,32.4,kind='scheme',scheme={'type':'chain','steps':['Воспаление','Пигмент','Новые пятна'],'at':[0,0.5,1.1]}),
 I(35.3,37.6,kind='image',src='ins/stock_scrub.jpg',position='50% 30%'),
 I(41.3,43.8,kind='scheme',scheme={'type':'chain','steps':['Абразивные частички','Микротравмы','Воспаление'],'at':[0,0.5,1.2]}),
 I(44.7,47.0,kind='image',src='ins/stock_toner.jpg',position='50% 35%'),
 I(48.6,51.1,kind='scheme',scheme={'type':'contrast','title':'Спиртовой тоник','left':{'label':'Сужает поры?','verdict':'НЕТ'},'right':{'label':'Раздражает кожу?','verdict':'ДА'},'at':[0.1,1.4]}),
 I(60.0,62.4,kind='image',src='ins/IMG_0953.jpg',position='50% 55%'),
 I(74.5,76.5,kind='image',src='ins/IMG_0955.jpg',position='50% 45%'),
 I(81.0,83.5,kind='scheme',scheme={'type':'timeline','from':{'title':'Сегодня','sub':'фото 1'},'to':{'title':'Через 2 недели','sub':'фото 2'},'note':'Одно окно · один свет · одно время','at':[0,0.5,1.0]}),
 I(89.6,92.1,kind='scheme',scheme={'type':'contrast','title':'Сравниваем с чем?','left':{'label':'С воспоминанием','verdict':'ОБМАН'},'right':{'label':'Со снимком','verdict':'ФАКТ'},'at':[0.1,1.3]}),
 I(94.9,96.6,kind='image',src='ins/IMG_0950.jpg',position='50% 40%'),
]
# automatic punch-ins where the picture would stay unchanged too long
hook_end=3.6
ev=[0.0,hook_end]+[sg['out_start'] for sg in cuts['segments']][1:]
for i in INSERTS: ev+=[i['start'],i['end']]
punches=[]
def gaps(e):
    e=sorted(set(round(x,3) for x in e if x<cuts['duration_after']))
    return [(b-a,a,b) for a,b in zip(e,e[1:])]
while True:
    bad=[g for g in gaps(ev+punches) if g[0]>(2.5 if g[1]<15 else 4.5)]
    if not bad: break
    g=max(bad); punches.append(round((g[1]+g[2])/2,2))
punches=sorted(punches)
data={'fps':30,'duration':cuts['duration_after'],'segments':[{'start':s['out_start'],'end':s['out_end']} for s in cuts['segments']],'captions':caps,'hook':{'text':'Сделайте это\nсегодня, если\nхотите, чтобы\nу вас была чистая\nкожа без пятен.','start':0.0,'end':3.6},'inserts':INSERTS,'punches':punches}
import os; os.makedirs(R+'src/data',exist_ok=True)
json.dump(data,open(R+'src/data/talkinghead.json','w'),ensure_ascii=False,indent=1)
acc_words=[w[i]['word'] for i in sorted(acc)]
print('duration',cuts['duration_after'],'punches',punches);print('groups',len(caps),'accents',acc_words)
for c in caps: print(f"{c['start']:6.2f}-{c['end']:6.2f}", ' '.join(('*'+x['w']+'*') if x['accent'] else x['w'] for x in c['words']))

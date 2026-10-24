import json, re
R='/Users/saga/reels-montage/'
SPEED=1.12
cuts=json.load(open(R+'cache/t3/cuts.json')); actual=json.load(open(R+'cache/t3/seg_actual.json'))
w=json.load(open(R+'cache/t3/words_cut.json'))
SEG=[];t_=0.0
for sg,d in zip(cuts['segments'],actual): SEG.append((sg['out_start'],sg['out_end'],t_)); t_+=d
TOTAL=round(t_,3)
for x in w:
    c=(x['start']+x['end'])/2
    for a,b,f in SEG:
        if a-0.02<=c<=b+0.02:
            x['start']=round(f+max(0,x['start']-a)/SPEED,3); x['end']=round(f+min(b-a,x['end']-a)/SPEED,3); break
segs_fast=[{'start':round(f,3),'end':round(f+d,3)} for (a,b,f),d in zip(SEG,actual)]
for a,b in zip(w,w[1:]):
    if a['end']>b['start']: a['end']=max(a['start']+0.05,b['start'])
def clean(s): return re.sub(r'[^\w-]','',s.lower())
FS=78;F=0.72;LINE_W=876
def nlines(ws):
    cur=0;n=1
    for x in ws:
        wpx=len(x['word'])*F*FS; add=wpx+(0.26*FS if cur>0 else 0)
        if cur+add>LINE_W: n+=1;cur=wpx
        else: cur+=add
    return n
FN={'и','в','на','а','же','то','как','не','с','от','для','что','это','я','вот','при','его','они','мы','ему','вам','по','из','но','ли','бы'}
def chunk(sent):
    n=len(sent)
    if n<=5 and nlines(sent)<=2 and len(' '.join(y['word'] for y in sent))<=34: return [sent]
    best={0:(0,[])}
    for i in range(1,n+1):
        cand=None
        for k in (2,3,4,5):
            j=i-k
            if j<0 or j not in best: continue
            ws=sent[j:i]; txt=' '.join(y['word'] for y in ws)
            cost=best[j][0]+0.3*(k-4)**2+(10 if (len(txt)>34 or nlines(ws)>2) else 0)+(0 if ws[-1]['word'][-1] in ',.?!' or i==n else 1.0)+(2.5 if i<n and clean(ws[-1]['word']) in FN else 0)
            if cand is None or cost<cand[0]: cand=(cost,best[j][1]+[ws])
        if cand: best[i]=cand
    return best[n][1] if n in best else [sent]
sents=[];cur=[]
for x in w:
    cur.append(x)
    if x['word'][-1] in '.?!': sents.append(cur);cur=[]
if cur: sents.append(cur)
ms=[]
for s_ in sents:
    if ms and len(ms[-1])==1: ms[-1]=ms[-1]+s_
    else: ms.append(s_)
groups=[]
for s_ in ms: groups+=chunk(s_)
want=['акне.','Nolla','восьми','врач','карт-бланш','восемью','завтра?','отвечать-то,','машины.']
acc=set();pos=0
for target in want:
    for i in range(pos,len(w)):
        if w[i]['word']==target and all(abs(i-j)>=10 for j in acc): acc.add(i);pos=i+1;break
idx=0;caps=[]
for gi,g in enumerate(groups):
    ws=[]
    for x in g: ws.append({'w':x['word'],'s':x['start'],'e':x['end'],'accent':idx in acc}); idx+=1
    last_end=g[-1]['end']; nxt=groups[gi+1][0]['start'] if gi+1<len(groups) else None
    end=min(nxt,last_end+0.3) if nxt is not None and nxt-last_end<0.35 else last_end+0.2
    caps.append({'start':round(g[0]['start'],3),'end':round(end,3),'words':ws})
def at(token,after=0):
    for i in range(after,len(w)):
        if w[i]['word']==token: return w[i]['start']
    raise SystemExit('token not found: '+token)
INS=[]
import os
if os.path.exists(R+'public/ins/IMG_1900.jpg'):
    t=at('Nolla'); INS.append({'start':round(t-0.2,3),'end':round(t+2.3,3),'kind':'image','src':'ins/IMG_1900.jpg','position':'50% 72%'})
t=at('сначала'); INS.append({'start':round(t-0.1,3),'end':round(t+3.9,3),'kind':'scheme','scheme':{'type':'chain','steps':['Отвечаете на вопросы','Сканируете лицо','ИИ подбирает лечение'],'at':[0,1.3,2.6]}})
t=at('Стоимость'); INS.append({'start':round(t-0.05,3),'end':round(t+5.0,3),'kind':'scheme','scheme':{'type':'update','title':'ПОМЕТКА ПРИ МОНТАЖЕ','from':'4,99 $','to':'9,99 $','label':'На момент монтажа ролика мы обнаружили: стоимость ежемесячной оплаты приложения выросла и теперь начинается с 9,99 $','at':[0.1,1.0,1.7]}})
t=at('врач'); INS.append({'start':round(t-0.1,3),'end':round(t+2.5,3),'kind':'scheme','scheme':{'type':'stat','value':'НЕ ОБЯЗАН','label':'врач проверять каждый рецепт','at':[0.15]}})
t=at('ограничена'); INS.append({'start':round(t,3),'end':round(t+2.5,3),'kind':'scheme','scheme':{'type':'stat','value':'8','label':'наружных препаратов, и всё','at':[0.15]}})
INS.sort(key=lambda x:x['start'])
HOOK={'text':'ИИ уже выписывает\nлекарства без врача','start':0.0,'end':3.6}
ev=[0.0,HOOK['end']]+[s['start'] for s in segs_fast][1:]
for i in INS: ev+=[i['start'],i['end']]
punches=[]
def gaps(e):
    e=sorted(set(round(x,3) for x in e if x<TOTAL)); return [(b-a,a,b) for a,b in zip(e,e[1:])]
while True:
    bad=[g for g in gaps(ev+punches) if g[0]>(2.5 if g[1]<15 else 4.5)]
    if not bad: break
    g=max(bad); punches.append(round((g[1]+g[2])/2,2))
data={'fps':30,'duration':round(TOTAL-0.05,2),'segments':segs_fast,'captions':caps,'hook':HOOK,'inserts':INS,'punches':sorted(punches)}
os.makedirs(R+'src/data',exist_ok=True)
json.dump(data,open(R+'src/data/th2.json','w'),ensure_ascii=False,indent=1)
# sound cues
cues={'riser':[0.0],'camera':[i['start'] for i in INS if i['kind']=='image'],
 'whoosh':[i['start'] for i in INS if i['kind']=='scheme' and i['scheme']['type']!='chain'],
 'ding':[round(i['start']+(i['scheme']['at'][1] if i['scheme']['type']=='update' else i['scheme']['at'][-1])+0.15,3) for i in INS if i['kind']=='scheme'],
 'typewriter':[at('Что')+0.0 if False else [x['start'] for x in w if x['word']=='Что'][-1]]}
json.dump(cues,open(R+'cache/t3/sfx_cues.json','w'),indent=1)
print('duration',data['duration'],'groups',len(caps),'3line',sum(1 for g in groups if nlines(g)>2))
print('accents',[w[i]['word'] for i in sorted(acc)])
print('inserts',[(i['kind'],i['start'],i['end']) for i in INS])
print('punches',punches); print('cues',cues)

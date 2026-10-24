import json, re
R='/Users/saga/reels-montage/'
w=json.load(open(R+'cache/r2/words_fast.json'))
DUR=102.3
def clean(s): return re.sub(r'[^\w-]','',s.lower())
FS=78;F=0.72;LINE_W=876
def nlines(ws):
    cur=0;n=1
    for x in ws:
        wpx=len(x['word'])*F*FS; add=wpx+(0.26*FS if cur>0 else 0)
        if cur+add>LINE_W: n+=1;cur=wpx
        else: cur+=add
    return n
FN={'и','в','на','а','же','то','как','не','с','от','для','через','мы','у','что','по','за','к','из','но','или','я','это','его','им','вот','ведь','при','они','мне','меня'}
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
# accents: product names, spaced >=10 words apart
want=['SEVI','Emansi,','Адаклин.','Restorer.','SPF,','SEVI','Angiopharm','восемь','косметичка']
acc=set();pos=0
for target in want:
    for i in range(pos,len(w)):
        if w[i]['word']==target and all(abs(i-j)>=10 for j in acc): acc.add(i);pos=i+1;break
idx=0;caps=[]
for gi,g in enumerate(groups):
    ws=[]
    for x in g:
        ws.append({'w':x['word'],'s':x['start'],'e':x['end'],'accent':idx in acc}); idx+=1
    last_end=g[-1]['end']; nxt=groups[gi+1][0]['start'] if gi+1<len(groups) else None
    end=min(nxt,last_end+0.3) if nxt is not None and nxt-last_end<0.35 else last_end+0.2
    caps.append({'start':round(g[0]['start'],3),'end':round(end,3),'words':ws})
HOOK={'text':'Вы не поверите,\nно это всё, что я\nберу с собой\nв дорогу как\nкосметолог с фарм\nобразованием','start':0.0,'end':4.4}
# price cards: (start,end,title,sub,price)   price None = still to be told by the user
PRICES=[
 {'start':17.2,'end':19.9,'title':'Мусс SEVI, Arkadia','sub':'','price':'2 200 ₽'},
 {'start':28.3,'end':31.0,'title':'Сыворотка Emansi для тела, 200 мл','sub':'средняя цена по России','price':'≈ 3 950 ₽'},
 {'start':36.9,'end':39.6,'title':'Адаклин 0,1%, 30 г','sub':'средняя цена по России','price':'≈ 1 070 ₽'},
 {'start':44.8,'end':47.5,'title':'Restorer, крем 50 мл','sub':'средняя цена по России','price':'≈ 2 800 ₽'},
 {'start':64.4,'end':67.1,'title':'Гель SEVI с энзимами граната, 400 мл','sub':'средняя цена по России','price':'≈ 2 400 ₽'},
 {'start':74.3,'end':76.75,'title':'Angiopharm Antioxidant Vitamin Cream, 50 мл','sub':'средняя цена по России','price':'≈ 2 600 ₽'},
 {'start':76.95,'end':79.6,'title':'Пилинг Emansi с салицилатом, 50 мл','sub':'средняя цена по России','price':'≈ 2 850 ₽'},
]
INSERTS=[{'start':14.85,'end':17.1,'kind':'image','src':'ins/IMG_1674.jpg','position':'50% 50%'}]
data={'fps':30,'duration':DUR,'captions':caps,'hook':HOOK,'prices':PRICES,'inserts':INSERTS}
import os; os.makedirs(R+'src/data',exist_ok=True)
json.dump(data,open(R+'src/data/packing.json','w'),ensure_ascii=False,indent=1)
print('duration',DUR,'frames',round(DUR*30),'groups',len(caps),'3-line',[1 for g in groups if nlines(g)>2])
print('accents',[w[i]['word'] for i in sorted(acc)])

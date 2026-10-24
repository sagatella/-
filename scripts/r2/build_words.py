import json, subprocess
R='/Users/saga/reels-montage/'; FF=R+'node_modules/ffmpeg-static/ffmpeg'
cuts=json.load(open(R+'cache/r2/cuts.json'))
FILES={'voice7':R+'input/voice/Новая запись 7.m4a','voice6':R+'input/voice/Новая запись 6.m4a'}
# ---- 1. rough voice
inputs=[];chains=[];labs=[]
for k,f in enumerate(FILES.values()): inputs+=['-i',f]
idx={'voice7':0,'voice6':1}
for i,s in enumerate(cuts['segments']):
    chains.append(f"[{idx[s['file']]}:a]atrim=start={s['src_start']}:end={s['src_end']},asetpts=PTS-STARTPTS,afade=t=in:d=0.006,afade=t=out:st={round(s['src_end']-s['src_start']-0.006,3)}:d=0.006,aformat=sample_rates=48000:channel_layouts=mono[a{i}]")
    labs.append(f'[a{i}]')
filt=';'.join(chains)+';'+''.join(labs)+f"concat=n={len(labs)}:v=0:a=1[a]"
r=subprocess.run([FF,'-y','-loglevel','error']+inputs+['-filter_complex',filt,'-map','[a]','-c:a','pcm_s16le',R+'cache/r2/voice_rough.wav'],capture_output=True,text=True)
print('audio',r.returncode,r.stderr[-300:])
# ---- 2. corrected words
w7=json.load(open(R+'cache/v/words7_raw.json')); w6=json.load(open(R+'cache/v/words6_raw.json'))
fill={55,65,91,107,116,217}
fix={9:['в'],10:['поездку.'],45:['SEVI'],47:['Arkadia.'],68:['в'],78:['включая'],93:['редким'],94:['исключением.'],
 97:['Сыворотка'],98:['Emansi,'],99:['которая'],120:['поездки.'],133:['Адаклин.'],153:['Restorer.'],
 227:None,231:['гель','SEVI','с','энзимами'],233:None,234:['Даёт'],254:['всегда'],255:['под','актуальную'],
 257:['С','собой'],260:['антиоксидантная'],262:['Angiopharm'],264:['салициловый'],265:['пилинг','Emansi'],
 277:['не','в'],278:['родной'],287:['флакон'],289:['шампуня'],300:['всё,'],301:['восемь'],306:['десяти'],203:['всё'],215:['средство'],216:['плохое,'],232:['граната.'],106:['что'],315:['средств,'],324:['каждое']}
words=[]
for i,x in enumerate(w7):
    if i in fill: continue
    if i in fix:
        if fix[i] is None: continue
        n=len(fix[i]); d=(x['end']-x['start'])/n
        for k,t in enumerate(fix[i]): words.append({'file':'voice7','word':t,'start':round(x['start']+k*d,3),'end':round(x['start']+(k+1)*d,3),'prob':x['prob']})
        continue
    words.append({'file':'voice7','word':x['word'],'start':x['start'],'end':x['end'],'prob':x['prob']})
# merge "только" + "-только"
m=[]
for x in words:
    if x['word'].startswith('-') and m: m[-1]['word']+=x['word']; m[-1]['end']=x['end']
    else: m.append(x)
words=m
# voice6
f6={'также':['так','же']}
for x in w6:
    if x['word'].lower() in f6:
        n=2; d=(x['end']-x['start'])/n
        for k,t in enumerate(f6[x['word'].lower()]): words.append({'file':'voice6','word':t,'start':round(x['start']+k*d,3),'end':round(x['start']+(k+1)*d,3),'prob':x['prob']})
    else: words.append({'file':'voice6','word':x['word'],'start':x['start'],'end':x['end'],'prob':x['prob']})
# ---- 3. remap to the rough timeline
out=[]
for x in words:
    c=(x['start']+x['end'])/2
    for s in cuts['segments']:
        if s['file']==x['file'] and s['src_start']-0.01<=c<=s['src_end']+0.01:
            o=s['out_start']-s['src_start']
            out.append({'word':x['word'],'start':round(max(s['out_start'],x['start']+o),3),'end':round(min(s['out_end'],x['end']+o),3),'prob':x['prob']}); break
json.dump(out,open(R+'cache/r2/words_cut.json','w'),ensure_ascii=False,indent=0)
print(len(out),'words; last end',out[-1]['end'])
print(' '.join(x['word'] for x in out))

import json
from faster_whisper import WhisperModel
R='/Users/saga/reels-montage/'
m=WhisperModel('small',device='cpu',compute_type='int8',download_root=R+'cache/whisper')
for n in ('1876','1878'):
    segs,info=m.transcribe(R+f'cache/t3/a{n}.wav',word_timestamps=True,beam_size=8,temperature=0.0,condition_on_previous_text=False,language='ru')
    words=[]
    for s in segs:
        for w in (s.words or []):
            words.append({'word':w.word.strip(),'start':round(w.start,3),'end':round(w.end,3),'prob':round(w.probability,3)})
    json.dump(words,open(R+f'cache/t3/words{n}_raw.json','w'),ensure_ascii=False)
    print('FILE',n,'WORDS',len(words),'DUR',round(info.duration,1),flush=True)
print('ALL_DONE',flush=True)

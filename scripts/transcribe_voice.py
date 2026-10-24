import json,sys
from faster_whisper import WhisperModel
m = WhisperModel('small', device='cpu', compute_type='int8', download_root='/Users/saga/reels-montage/cache/whisper')
for n in ('6','7'):
    segs, info = m.transcribe(f'/Users/saga/reels-montage/cache/v/voice{n}.wav', word_timestamps=True, beam_size=8, temperature=0.0, condition_on_previous_text=False)
    words=[]
    for s in segs:
        for w in (s.words or []):
            words.append({"word": w.word.strip(), "start": round(w.start,3), "end": round(w.end,3), "prob": round(w.probability,3)})
    json.dump(words, open(f'/Users/saga/reels-montage/cache/v/words{n}_raw.json','w'), ensure_ascii=False)
    print("FILE",n,"LANG",info.language,"WORDS",len(words),"DUR",info.duration)

import json
from faster_whisper import WhisperModel
m = WhisperModel('small', device='cpu', compute_type='int8', download_root='/Users/saga/reels-montage/cache/whisper')
segs, info = m.transcribe('/Users/saga/reels-montage/cache/audio.wav', word_timestamps=True, beam_size=8, temperature=0.0,
    condition_on_previous_text=False,
    initial_prompt='Пигментные пятна, воспаление, скраб с абразивными частичками, СПФ, тоник, косметолог.')
words = []
for s in segs:
    for w in (s.words or []):
        words.append({"word": w.word.strip(), "start": round(w.start,3), "end": round(w.end,3), "prob": round(w.probability,3)})
json.dump(words, open('/Users/saga/reels-montage/cache/words_raw2.json','w'), ensure_ascii=False)
print("LANG", info.language, "WORDS", len(words))

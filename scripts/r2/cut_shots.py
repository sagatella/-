import json,subprocess,time
R='/Users/saga/reels-montage/'; FF=R+'node_modules/ffmpeg-static/ffmpeg'
shots=json.load(open(R+'cache/r2/shots.json'))
t0=time.time()
for i,s in enumerate(shots):
    dur=round(s['t1']-s['t0'],3); src_len=round(dur*s['speed'],3)
    vf=("crop=ih*9/16:ih,scale=1080:1920:flags=lanczos," if s.get('landscape') else "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,")
    vf+=f"setpts=PTS/{s['speed']},fps=30,format=yuv420p"
    out=f"{R}cache/r2/seg/s{i:02d}.mp4"
    r=subprocess.run([FF,'-y','-loglevel','error','-ss',str(s['ss']),'-i',R+'input/'+s['clip'],'-t',str(src_len),'-an','-vf',vf,'-t',str(dur),
        '-c:v','libx264','-preset','veryfast','-crf','15','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',out],capture_output=True,text=True)
    print(i,s['note'],dur,round(time.time()-t0),'s',r.stderr[:120],flush=True)
print('ALL_DONE',flush=True)

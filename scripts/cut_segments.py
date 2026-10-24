import json,subprocess,time
S=1.12
R='/Users/saga/reels-montage/'
FF=R+'node_modules/ffmpeg-static/ffmpeg'
c=json.load(open(R+'cache/cuts.json'))
t0=time.time()
for i,s in enumerate(c['segments']):
    a,b=s['src_start'],s['src_end']; d=round(b-a,3); od=d/S
    out=f"{R}cache/seg/s{i:02d}.mov"
    cmd=[FF,'-y','-loglevel','error','-ss',str(a),'-t',str(d),'-i',R+'input/IMG_0948.MOV',
         '-vf',f'setpts=PTS/{S},fps=30,scale=1080:1920:flags=lanczos,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','14',
         '-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',
         '-af',f'atempo={S},afade=t=in:d=0.008,afade=t=out:st={round(od-0.008,3)}:d=0.008','-c:a','pcm_s16le','-ar','48000',out]
    r=subprocess.run(cmd,capture_output=True,text=True)
    print(i,f'{od:.2f}s',round(time.time()-t0),'s',r.stderr[:100],flush=True)
print('ALL_DONE',flush=True)

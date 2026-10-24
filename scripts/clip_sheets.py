import subprocess, json, glob, os
R='/Users/saga/reels-montage/'
FF=R+'node_modules/ffmpeg-static/ffmpeg'; FP='/Users/saga/.local/bin/ffprobe'
clips=sorted(glob.glob(R+'input/clips/*.MOV'))
info=[]
os.makedirs(R+'cache/cs',exist_ok=True)
for c in clips:
    o=json.loads(subprocess.run([FP,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,duration:stream_side_data=rotation','-of','json',c],capture_output=True,text=True).stdout)['streams'][0]
    d=float(o['duration']); rot=(o.get('side_data_list') or [{}])[0].get('rotation')
    info.append({'file':os.path.basename(c),'dur':round(d,2),'w':o['width'],'h':o['height'],'fps':o['r_frame_rate'],'rot':rot})
    n=5
    for i in range(n):
        t=d*(i+0.5)/n
        subprocess.run([FF,'-y','-loglevel','error','-ss',f'{t:.2f}','-i',c,'-frames:v','1','-vf','scale=192:-2',f"{R}cache/cs/{os.path.basename(c)[:-4]}_{i}.png"])
json.dump(info,open(R+'cache/clips_info.json','w'),ensure_ascii=False,indent=1)
for i in info: print(i)

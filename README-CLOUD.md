# reels-montage в облаке

Это копия монтажной для вертикальных рилсов. Главные правила монтажа: `AGENTS.md` (читай первым).

## Как запустить среду с нуля (каждый новый облачный чат)
1. `npm install` (Remotion, ffmpeg-static, шрифты).
2. Python: `python3 -m venv .venv && .venv/bin/pip install -U faster-whisper`; модель `small` скачивается при первом запуске (около 460 МБ) в `cache/whisper`.
3. Папки: `mkdir -p input/voice input/clips input/brand assets cache output/qa`.
4. Видео бери по ссылке на Яндекс Диск (публичный API: `cloud-api.yandex.net/v1/disk/public/resources/download`, качай через `curl`, не через питон urllib: он зависает), только с разрешения человека.
5. Звуки: `assets/sfx/*.mp3`, громкости в AGENTS.md, шаг 6.
6. Скрипты предыдущих роликов лежат в `scripts/` как образцы (резка, субтитры, цены, звук).

Фото, скрины и видео человека сюда не кладутся: они приходят каждый раз заново.

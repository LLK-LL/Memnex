---
name: sound-fx-for-video
description: "鐢ㄤ簬瑙嗛鍒朵綔涓殑闊虫晥鏂规锛氭悳绱笅杞藉厤璐归煶鏁堛€乄eb Audio API 鍚堟垚闊虫晥銆佷互鍙婂湪 HyperFrames/Remotion/HTML5 瑙嗛涓殑闊抽闆嗘垚銆傝Е鍙戣瘝鍖呮嫭锛氶煶鏁堛€丼FX銆侀厤涔愩€丅GM銆亀hoosh銆乧lick銆乼ransition銆乮mpact銆乼yping 绛夈€?
---

# 瑙嗛闊虫晥鍒朵綔 Skill

瑙嗛闇€瑕佸０闊炽€傝繖浠?Skill 瑕嗙洊涓ゆ潯涓昏矾寰勶細
1. **鎼滅储骞朵笅杞?* 鍏嶈垂闊虫晥绱犳潗
2. **鍚堟垚鐢熸垚** 鑷畾涔夐煶鏁堬紙Web Audio API锛屾棤闇€澶栭儴鏂囦欢锛?
鎸夐渶姹傞€夋嫨璺緞锛屽疄闄呴」鐩€氬父浼氭贩鍚堜娇鐢ㄣ€?
---

## 璺緞涓€锛氭悳绱㈠苟涓嬭浇鍏嶈垂闊虫晥

### 鎺ㄨ崘鏉ユ簮

| Source | URL | License | API | Best For |
|--------|-----|---------|-----|----------|
| Freesound | freesound.org | CC licenses (check per-file) | REST API (key required) | Huge library, specific sounds |
| Mixkit | mixkit.co/free-sound-effects | Free, no attribution | No | Quick grabs, curated quality |
| Pixabay | pixabay.com/sound-effects | Free, no attribution | No | Clean UI, good variety |
| BBC SFX | bbcsfx.acropolis.org.uk | Free for personal/educational | No | Premium BBC quality |
| ZapSplat | zapsplat.com | Free with attribution | No | Game/comedy/cartoon sounds |
| SoundBible | soundbible.com | Mixed (check per-file) | No | Quick one-off downloads |

### 鎼滅储绛栫暐

1. **鍏抽敭璇嶈鍏蜂綋銆?*  
   宸細`click sound`  
   濂斤細`mouse click sharp UI feedback`  
   宸細`whoosh`  
   濂斤細`fast whoosh air sweep transition`

2. **缁勫悎鍏抽敭璇嶆悳绱細**
   - Object + action: "glass shatter", "paper crumple"
   - Mood + type: "cinematic impact bass", "playful pop notification"
   - Context: "UI button click feedback", "slide transition whoosh"

3. **甯歌闊虫晥鍒嗙被涓庢悳绱㈣瘝锛?*

   | Category | Search Terms |
   |----------|-------------|
   | Transitions | whoosh, sweep, swoosh, riser, dive |
   | UI feedback | click, tap, pop, blip, notification, ding |
   | Impacts | boom, hit, slam, thud, punch, bass drop |
   | Typing | keyboard, typing, keystroke, mechanical |
   | Reveals | shimmer, sparkle, magic, chime, glow |
   | Movement | slide, swoop, flutter, bounce, elastic |
   | Atmosphere | ambient, drone, hum, tension, pulse |

### 绋嬪簭鍖栦笅杞?
**Freesound API** (best for automation):

```bash
# 1. Get API key from https://freesound.org/apiv2/apply/
# 2. Search
# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
curl -o whoosh.mp3 "https://freesound.org/data/previews/ID_ID_preview.mp3"

# REDACTED: sensitive-looking memory line
```

**Simple curl download** (sources with direct links):

```bash
# Pixabay (find the download URL from browser network tab)
curl -L -o click.mp3 "https://cdn.pixabay.com/audio/..."

# Mixkit
curl -L -o transition.wav "https://assets.mixkit.co/active_storage/sfx/..."
```

**Python helper** (for batch downloads):

```python
import urllib.request
import json

# REDACTED: sensitive-looking memory line

def search_sfx(query, max_results=5):
# REDACTED: sensitive-looking memory line
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())["results"][:max_results]

def download_preview(sound_id, filename):
    url = f"https://freesound.org/data/previews/{sound_id//1000}/{sound_id}_{sound_id}_preview.mp3"
    urllib.request.urlretrieve(url, filename)
```

### 鐗堟潈妫€鏌?
鍙戝竷鍓嶅繀椤绘鏌ユ巿鏉冨崗璁細
- **CC0**: Use freely, no attribution
- **CC-BY**: Use with attribution (add to video description)
- **CC-BY-NC**: Non-commercial only 鈥?do NOT use for monetized videos
- **CC-BY-SA**: Derivatives must share same license

---

## 璺緞浜岋細浣跨敤 Web Audio API 鍚堟垚闊虫晥

鏃犻渶闊抽鏂囦欢锛岀洿鎺ュ湪娴忚鍣ㄤ腑瀹炴椂鍚堟垚锛岄€傚悎浠ｇ爜椹卞姩瑙嗛娴佺▼锛圚yperFrames銆丷emotion銆丠TML5锛夈€?
### 蹇€熷弬鑰冿細甯歌瑙嗛闊虫晥妯″紡

#### UI Click / Tap
```javascript
function playClick(audioCtx) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.connect(gain).connect(audioCtx.destination);
  osc.frequency.setValueAtTime(1200, audioCtx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(600, audioCtx.currentTime + 0.05);
  gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
  osc.start(); osc.stop(audioCtx.currentTime + 0.08);
}
```

#### Notification Pop / Ding
```javascript
function playPop(audioCtx) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = 'sine';
  osc.connect(gain).connect(audioCtx.destination);
  osc.frequency.setValueAtTime(880, audioCtx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.05);
  gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);
  osc.start(); osc.stop(audioCtx.currentTime + 0.2);
}
```

#### Whoosh / Transition Sweep
```javascript
function playWhoosh(audioCtx) {
  const bufferSize = audioCtx.sampleRate * 0.4;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / bufferSize, 2);
  }
  const source = audioCtx.createBufferSource();
  source.buffer = buffer;
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'bandpass'; filter.Q.value = 5;
  filter.frequency.setValueAtTime(200, audioCtx.currentTime);
  filter.frequency.exponentialRampToValueAtTime(4000, audioCtx.currentTime + 0.2);
  filter.frequency.exponentialRampToValueAtTime(200, audioCtx.currentTime + 0.4);
  const gain = audioCtx.createGain();
  gain.gain.setValueAtTime(0, audioCtx.currentTime);
  gain.gain.linearRampToValueAtTime(0.5, audioCtx.currentTime + 0.1);
  gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.4);
  source.connect(filter).connect(gain).connect(audioCtx.destination);
  source.start();
}
```

#### Impact / Bass Hit
```javascript
function playImpact(audioCtx) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = 'sine';
  osc.connect(gain).connect(audioCtx.destination);
  osc.frequency.setValueAtTime(150, audioCtx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(30, audioCtx.currentTime + 0.3);
  gain.gain.setValueAtTime(1, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
  osc.start(); osc.stop(audioCtx.currentTime + 0.4);
  // Add noise burst layer
  const bufferSize = audioCtx.sampleRate * 0.1;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) data[i] = (Math.random() * 2 - 1);
  const noise = audioCtx.createBufferSource();
  noise.buffer = buffer;
  const noiseGain = audioCtx.createGain();
  noiseGain.gain.setValueAtTime(0.5, audioCtx.currentTime);
  noiseGain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
  noise.connect(noiseGain).connect(audioCtx.destination);
  noise.start();
}
```

#### Typing / Keystroke
```javascript
function playKey(audioCtx) {
  const bufferSize = audioCtx.sampleRate * 0.03;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / bufferSize, 4);
  }
  const source = audioCtx.createBufferSource();
  source.buffer = buffer;
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'highpass'; filter.frequency.value = 2000;
  const gain = audioCtx.createGain();
  gain.gain.value = 0.15;
  source.connect(filter).connect(gain).connect(audioCtx.destination);
  source.start();
}
```

#### Rise / Tension Builder
```javascript
function playRise(audioCtx, duration = 1.5) {
  const osc = audioCtx.createOscillator();
  osc.type = 'sawtooth';
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'lowpass'; filter.Q.value = 8;
  const gain = audioCtx.createGain();
  osc.connect(filter).connect(gain).connect(audioCtx.destination);
  filter.frequency.setValueAtTime(100, audioCtx.currentTime);
  filter.frequency.exponentialRampToValueAtTime(3000, audioCtx.currentTime + duration);
  gain.gain.setValueAtTime(0.01, audioCtx.currentTime);
  gain.gain.linearRampToValueAtTime(0.3, audioCtx.currentTime + duration);
  osc.start(); osc.stop(audioCtx.currentTime + duration);
}
```

#### Sparkle / Shimmer
```javascript
function playSparkle(audioCtx) {
  const notes = [261.63, 329.63, 392.00, 523.25, 659.25]; // C5 E5 G5 C6 E6
  notes.forEach((freq, i) => {
    const osc = audioCtx.createOscillator();
    osc.type = 'sine';
    const gain = audioCtx.createGain();
    osc.connect(gain).connect(audioCtx.destination);
    const start = audioCtx.currentTime + i * 0.06;
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0, start);
    gain.gain.linearRampToValueAtTime(0.2, start + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, start + 0.4);
    osc.start(start); osc.stop(start + 0.4);
  });
}
```

### 妯″紡閫熸煡琛?
| Sound | Core Technique | Key Parameters |
|-------|---------------|----------------|
| Click/Tap | Short sine + fast decay | freq 800-1500Hz, dur < 100ms |
| Pop/Bubble | Sine + freq ramp up | freq sweep up, short |
| Whoosh | Filtered noise + bandpass sweep | bandpass sweep 200鈫?k鈫?00 |
| Impact | Low sine + noise burst | freq 150鈫?0Hz, noise < 150ms |
| Typing | Highpass filtered noise | HPF 2kHz+, dur < 50ms |
| Rise/Tension | Sawtooth + filter sweep | LPF 100鈫?kHz over duration |
| Sparkle | Arpeggiated sine cluster | C-E-G-C-E, staggered 60ms |
| Boom/Rumble | Very low sine + slow decay | freq 40-80Hz, dur 0.5-2s |
| Slide/Move | Sine with pitch bend | freq ramp up or down |
| Error/Buzz | Square wave buzz | low freq square, short burst |

---

## 璺緞涓夛細HyperFrames / Remotion 闆嗘垚

### HyperFrames 闊抽闆嗘垚

鍦?HyperFrames 涓紝闊抽甯歌鏈変袱绉嶆柟寮忥細

**鏂瑰紡 A锛歐eb Audio API锛堝疄鏃跺悎鎴愶級**

```javascript
// In your HyperFrames component
const audioCtx = new AudioContext();

function MyAnimation() {
  const handleClick = () => playClick(audioCtx);

  return (
    <div onClick={handleClick}>
      <h1>Click Me</h1>
    </div>
  );
}
```

**鏂瑰紡 B锛氶鍔犺浇闊抽鏂囦欢**

```javascript
// 1. Import audio file
import whooshSfx from "./sfx/whoosh.mp3";

// 2. Play on animation event
const audio = new Audio(whooshSfx);
audio.play();
```

**鏂瑰紡 C锛歊emotion `<Audio>` 缁勪欢**锛堜娇鐢?Remotion 鏃讹級

```jsx
import { Audio, useCurrentFrame } from "remotion";

export const MyComp = () => {
  const frame = useCurrentFrame();
  return (
    <>
      <Audio src={staticFile("whoosh.mp3")} startFrom={30} volume={0.5} />
    </>
  );
};
```

### 瑙嗗惉鍚屾寤鸿

1. **Trigger sounds at animation keyframes**, not at random times
2. **Keep sounds short** (50-300ms for UI, 300-800ms for transitions)
3. **Layer sounds** 鈥?a whoosh + impact combo feels better than either alone
4. **Volume hierarchy**: BGM (0.1-0.2) < Transition SFX (0.2-0.3) < Key SFX (0.3-0.5) < Voiceover (1.0)
5. **Always test with audio on** 鈥?silent playback hides timing issues

---

## 閫夋嫨娴佺▼

```
Need a sound effect?
鈹溾攢鈹€ Is it a simple UI/click/pop? 鈫?Synthesize with Web Audio API (instant, no files)
鈹溾攢鈹€ Is it a complex/natural sound (footsteps, crowd, rain)? 鈫?Download from Freesound/Pixabay
鈹溾攢鈹€ Need precise control over timing? 鈫?Web Audio API synthesis
鈹溾攢鈹€ Need realism? 鈫?Download real recordings
鈹斺攢鈹€ Both? 鈫?Mix: download base layer + synthesize accents on top
```

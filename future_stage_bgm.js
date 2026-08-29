/* Lost Ruby - Future I stage BGM synthesizer (4-1 / 4-2 / 4-7 only) */
(() => {
  const KEY='lr_audio_settings_v1';
  let ctx=null, master=null, timer=null, currentStage=0, nextStart=0, cycleLen=0;

  const TRACKS={
    1:{name:'CHRONO PANIC',bpm:162,mode:'chrono',chords:[[45,52,57,60],[48,55,60,64],[43,50,55,59],[46,53,58,61]],lead:[69,72,73,76,75,72,71,69,72,75,76,80,78,76,75,72,71,74,77,78,81,78,77,74,72,73,76,79,78,76,73,71]},
    2:{name:'OVERDRIVE CITY',bpm:156,mode:'drive',chords:[[48,55,60,63],[46,53,58,62],[44,51,56,60],[43,50,55,58]],lead:[67,70,72,75,74,72,70,67,68,72,75,79,77,75,72,68,70,74,77,82,79,77,74,72,67,70,74,79,77,74,72,70]},
    7:{name:'NEON SIGNAL',bpm:168,mode:'moon',chords:[[50,57,62,65],[46,53,58,62],[48,55,60,63],[43,50,55,58]],lead:[74,77,79,82,81,79,77,74,72,75,79,84,82,79,77,75,77,81,84,86,84,82,81,77,74,77,81,84,82,81,79,77]}
  };

  function settings(){
    try{const s=JSON.parse(localStorage.getItem(KEY)||'{}');return{on:s.musicEnabled!==false,vol:Math.max(0,Math.min(100,Number(s.musicVolume??38)))/100};}
    catch(_){return{on:true,vol:.38};}
  }
  function hz(n){return 440*Math.pow(2,(n-69)/12);}
  function tone(note,t,dur,type='square',gain=.03,det=0){
    if(!ctx||!master)return; const o=ctx.createOscillator(),g=ctx.createGain();
    o.type=type;o.frequency.value=hz(note);o.detune.value=det;
    g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(gain,t+.008);g.gain.exponentialRampToValueAtTime(.0001,t+dur);
    o.connect(g).connect(master);o.start(t);o.stop(t+dur+.025);
  }
  function noise(t,dur,gain,hp){
    if(!ctx||!master)return; const len=Math.max(1,Math.floor(ctx.sampleRate*dur)),b=ctx.createBuffer(1,len,ctx.sampleRate),d=b.getChannelData(0);
    for(let i=0;i<len;i++)d[i]=(Math.random()*2-1)*(1-i/len);
    const s=ctx.createBufferSource(),f=ctx.createBiquadFilter(),g=ctx.createGain();s.buffer=b;f.type='highpass';f.frequency.value=hp;g.gain.value=gain;s.connect(f).connect(g).connect(master);s.start(t);
  }
  function kick(t,g=.1){
    if(!ctx||!master)return;const o=ctx.createOscillator(),gn=ctx.createGain();o.type='sine';o.frequency.setValueAtTime(145,t);o.frequency.exponentialRampToValueAtTime(44,t+.12);gn.gain.setValueAtTime(g,t);gn.gain.exponentialRampToValueAtTime(.0001,t+.15);o.connect(gn).connect(master);o.start(t);o.stop(t+.16);
  }
  function schedule(track,start){
    const beat=60/track.bpm,bars=16;
    for(let bar=0;bar<bars;bar++){
      const t0=start+bar*4*beat,ch=track.chords[bar%track.chords.length];
      const climax=bar>=12;
      const leadOn=track.mode==='moon'?bar>=6:bar>=8;
      if(bar<4){ch.forEach((n,i)=>tone(n,t0+i*beat,beat*.78,'triangle',track.mode==='moon'?.014:.017));}
      else{
        const div=climax?16:8;
        for(let s=0;s<div;s++){let n=ch[s%ch.length];if(climax&&s%4===3)n+=12;tone(n,t0+s*(4*beat/div),beat*(climax?.18:.32),'square',climax?.022:.016);}
      }
      if(bar>=2){const bass=ch[0]-12,steps=climax?8:4;for(let k=0;k<steps;k++)tone(bass,t0+k*(4*beat/steps),beat*(climax?.34:.68),'sawtooth',climax?.042:.026);}
      if(bar>=4){
        for(let k=0;k<4;k++){kick(t0+k*beat,climax?.13:.085);noise(t0+(k+.5)*beat,.026,climax?.016:.010,6200);}
        noise(t0+beat,.10,climax?.050:.032,1200);noise(t0+3*beat,.10,climax?.050:.032,1200);
        if(climax)for(let h=0;h<16;h++)noise(t0+h*(beat/4),.018,.010,7000);
      }
      if(leadOn){const steps=climax?16:8;for(let k=0;k<steps;k++){let n=track.lead[((bar-(track.mode==='moon'?6:8))*steps+k)%track.lead.length];if(climax&&k%4===3)n+=12;tone(n,t0+k*(4*beat/steps),beat*(climax?.17:.35),'square',climax?.045:.032,climax?5:0);}}
      if(climax){
        for(let k=0;k<8;k++){const n=track.lead[((bar-12)*8+k*2)%track.lead.length]-12;tone(n,t0+k*.5*beat,beat*.3,'triangle',.024,-7);}
        for(let r=0;r<8;r++)noise(t0+3*beat+r*(beat/8),.035,.012+r*.002,1400);
        kick(t0+3.5*beat,.09);kick(t0+3.75*beat,.1);
      }
    }
    return bars*4*beat;
  }

  async function start(stage){
    stop();
    const track=TRACKS[stage],s=settings();
    if(!track||!s.on)return;
    currentStage=stage;
    try{
      ctx=new (window.AudioContext||window.webkitAudioContext)();master=ctx.createGain();master.gain.value=s.vol*.72;
      const comp=ctx.createDynamicsCompressor();comp.threshold.value=-16;comp.ratio.value=4;master.connect(comp).connect(ctx.destination);
      if(ctx.state==='suspended')await ctx.resume();
      nextStart=ctx.currentTime+.04;cycleLen=schedule(track,nextStart);nextStart+=cycleLen;
      timer=setInterval(()=>{if(!ctx||!TRACKS[currentStage])return;while(nextStart<ctx.currentTime+cycleLen*.55){schedule(track,nextStart);nextStart+=cycleLen;}},450);
    }catch(e){console.warn('future stage BGM failed',e);stop();}
  }
  function stop(){
    currentStage=0;if(timer){clearInterval(timer);timer=null;}if(ctx){try{ctx.close();}catch(_){}ctx=null;}master=null;nextStart=0;cycleLen=0;
  }
  function apply(){
    const s=settings();if(!s.on){stop();return;}if(master)master.gain.value=s.vol*.72;
  }
  window.startFutureStageBgm=start;window.stopFutureStageBgm=stop;
  window.addEventListener('lr-audio-settings-changed',apply);
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&ctx)ctx.suspend().catch(()=>{});else if(!document.hidden&&ctx&&settings().on)ctx.resume().catch(()=>{});});
})();

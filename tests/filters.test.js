// Filter tests for index.html: a reference model built from data/workshops.json, random URL
// combos, and random click walks on desktop (1280px) and phone (390px). Run: node tests/filters.test.js
const {chromium}=require('playwright');
const fs=require('fs');
const ROOT=require('path').resolve(__dirname,'..');
const BASE='file://'+(process.env.PAGE||ROOT+'/index.html');
const QUICK=!!process.env.QUICK; const STATS={};
const D=JSON.parse(fs.readFileSync(ROOT+'/data/workshops.json','utf8'));
const WS=D.workshops, TOP=D.topics.map(t=>t.id), TLAB=Object.fromEntries(D.topics.map(t=>[t.id,t.label]));
const NAFS=D.naf.blocks.map(b=>b.id), NNAME=Object.fromEntries(D.naf.blocks.map(b=>[b.id,b.id==='practices'?'Practices':b.name]));
const SLOTS=['A','B','C','D'];
const DEF={block:'',topics:[],q:'',mat:true,oss:false,naf:''};

// ---------- reference model ----------
const search=w=>[w.code,w.title,w.org,w.tldr,w.proctors.join(' '),w.topics.map(t=>TLAB[t]).join(' '),(w.naf_core||[]).map(x=>NNAME[x]).join(' ')].join(' ').toLowerCase();
const rel=(w,id)=>(w.naf_core||[]).includes(id)||(w.naf_touch||[]).includes(id);
function failsM(w,s){const f=[];
  if(s.block&&w.code[0]!==s.block)f.push('block');
  if(s.topics.length&&!w.topics.some(t=>s.topics.includes(t)))f.push('topics');
  const words=s.q.toLowerCase().split(/\s+/).filter(Boolean); if(words.length&&!words.every(x=>search(w).includes(x)))f.push('q');
  if(s.mat&&!(w.links||[]).length)f.push('mat');
  if(s.oss&&w.openness==='product')f.push('oss');
  if(s.naf&&!rel(w,s.naf))f.push('naf');
  return f;}
const model=s=>WS.filter(w=>!failsM(w,s).length).map(w=>w.code.toLowerCase());
const drop=(s,k)=>({...s,...{block:{block:''},topics:{topics:[]},q:{q:''},mat:{mat:false},oss:{oss:false},naf:{naf:''}}[k]});
function canon(s){const p=new URLSearchParams();
  if(s.block)p.set('slot',s.block); if(s.topics.length)p.set('topic',s.topics.join(',')); if(s.q)p.set('q',s.q);
  if(!s.mat)p.set('material','0'); if(s.oss)p.set('oss','1'); if(s.naf)p.set('naf',s.naf);
  const x=p.toString().replace(/%2C/g,','); return x?'?'+x:'';}
function parse(search){const p=new URLSearchParams(search);
  return {block:p.get('slot')||'',topics:(p.get('topic')||'').split(',').filter(Boolean),q:p.get('q')||'',mat:p.get('material')!=='0',oss:p.get('oss')==='1',naf:p.get('naf')||''};}
const isDef=s=>!s.block&&!s.topics.length&&!s.q&&s.mat&&!s.oss&&!s.naf;
const same=(a,b)=>JSON.stringify({...a,topics:[...a.topics].sort()})===JSON.stringify({...b,topics:[...b.topics].sort()});

// ---------- read the page ----------
const snapshot=page=>page.evaluate(()=>{
  const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
  const pane=$$('.np').find(p=>!p.hidden);
  return {
    search:location.search, hash:location.hash,
    visible:$$('.ws').filter(c=>!c.hidden).map(c=>c.id),
    sections:Object.fromEntries($$('.blk').map(s=>[s.dataset.block,s.hidden])),
    count:$('#count').textContent,
    chips:Object.fromEntries($$('.chip').map(c=>[c.dataset.topic,[+c.querySelector('span').textContent,c.getAttribute('aria-pressed')==='true',c.classList.contains('zero')]])),
    tabs:Object.fromEntries($$('.tab').map(c=>[c.dataset.block,[+c.querySelector('.tn').textContent,c.getAttribute('aria-pressed')==='true',c.classList.contains('zero')]])),
    showall:[$('#showall').hidden,$('#showall').textContent],
    empty:$('#empty').classList.contains('show'),
    relax:$$('#relax [data-relax]').map(b=>[b.dataset.relax,b.textContent]), reset:!!$('#relax [data-reset]'),
    nafchip:[$('#nafchip').hidden,$('#nafchip span').textContent],
    clear:$('#clear').hidden, fcount:+$('#fcount').textContent,
    jumpOff:$$('#jump a.off').map(a=>a.dataset.for),
    pane:pane?pane.dataset.panel:null,
    nrOff:pane?$$('.np:not([hidden]) .nr.off').map(r=>r.dataset.ws):[],
    nrAll:pane?$$('.np:not([hidden]) .nr').map(r=>r.dataset.ws):[],
    go:pane&&pane.querySelector('[data-go]')?[pane.querySelector('[data-go]').textContent,pane.querySelector('[data-go]').disabled]:null,
    showrel:pane&&pane.querySelector('[data-showrel]')?[pane.querySelector('[data-showrel]').hidden,pane.querySelector('[data-showrel]').textContent]:null,
    rels:Object.fromEntries($$('.ws').map(c=>[c.id,c.querySelector('.ws-rel').textContent])),
    nbPressed:$$('.nb[aria-pressed="true"]').map(b=>b.dataset.naf),
    cardNafHit:$$('.ws-naf button.hit').map(b=>b.dataset.naf),
    tagHit:[...new Set($$('.ws .tag.hit').map(b=>b.dataset.topic))],
    qv:$('#q').value, mat:$('#mat').checked, oss:$('#oss').checked,
    overflow:document.documentElement.scrollWidth-innerWidth,
  };});

// check every invariant for state s against the DOM snapshot
function check(s,d,ctx){
  const errs=[]; const E=m=>errs.push(m);
  const vis=model(s), n=vis.length;
  if(JSON.stringify(d.visible)!==JSON.stringify(vis))E(`visible ${d.visible} != model ${vis}`);
  for(const b of SLOTS){const any=vis.some(c=>c[0]===b.toLowerCase());if(d.sections[b]===any)E(`section ${b} hidden=${d.sections[b]} but has cards=${any}`);}
  const ct=n===WS.length?`All ${WS.length} workshops`:`${n} of ${WS.length} workshops`; if(d.count!==ct)E(`count "${d.count}" != "${ct}"`);
  for(const t of TOP){const want=model({...s,topics:[t]}).length,[gn,gp,gz]=d.chips[t]||[];
    if(gn!==want)E(`chip ${t} shows ${gn}, picking it alone would give ${want}`);
    if(gp!==s.topics.includes(t))E(`chip ${t} pressed=${gp}`); if(gz!==(!want&&!gp))E(`chip ${t} zero=${gz}`);}
  for(const k of ['',...SLOTS]){const want=model({...s,block:k}).length,[gn,gp,gz]=d.tabs[k];
    if(gn!==want)E(`tab "${k}" shows ${gn}, want ${want}`); if(gp!==(s.block===k))E(`tab "${k}" pressed=${gp}`); if(gz!==(!want&&!gp))E(`tab ${k} zero=${gz}`);}
  const more=s.mat?model({...s,mat:false}).length-n:0;
  const saHidden=!n||!more; if(d.showall[0]!==saHidden)E(`showall hidden=${d.showall[0]} want ${saHidden} (more=${more})`);
  if(!saHidden&&d.showall[1]!==`+${more} without material`)E(`showall text "${d.showall[1]}"`);
  if(d.empty!==!n)E(`empty=${d.empty} with ${n} shown`);
  if(!n){const want=['mat','oss','block','topics','q','naf'].filter(k=>{const sd=drop(s,k);return !same(sd,s)&&model(sd).length;});
    const got=d.relax.map(r=>r[0]); if(JSON.stringify(got)!==JSON.stringify(want))E(`relax ${got} want ${want}`);
    for(const [k,txt] of d.relax){const m=+txt.match(/\d+/)[0],w=model(drop(s,k)).length;if(m!==w)E(`relax ${k} says ${m}, gives ${w}`);}
    if(!d.reset)E('no reset button in empty state');}
  else if(d.relax.length)E('relax buttons while results shown');
  if(d.nafchip[0]!==!s.naf)E(`nafchip hidden=${d.nafchip[0]}`); if(s.naf&&!d.nafchip[1])E('nafchip has no name');
  if(d.clear!==isDef(s))E(`reset hidden=${d.clear} but default=${isDef(s)}`);
  const fc=s.topics.length+(s.q?1:0)+(s.mat?1:0)+(s.oss?1:0); if(d.fcount!==fc)E(`fcount ${d.fcount} want ${fc}`);
  const off=WS.map(w=>w.code.toLowerCase()).filter(c=>!vis.includes(c)); if(JSON.stringify(d.jumpOff)!==JSON.stringify(off))E(`jump off ${d.jumpOff} want ${off}`);
  if((d.pane||'')!==s.naf)E(`pane ${d.pane} want ${s.naf}`);
  if(s.naf){const r=WS.filter(w=>rel(w,s.naf)).map(w=>w.code.toLowerCase()), rv=r.filter(c=>vis.includes(c));
    const wantOff=d.nrAll.filter(c=>!vis.includes(c)); if(JSON.stringify(d.nrOff)!==JSON.stringify(wantOff))E(`nr off ${d.nrOff} want ${wantOff}`);
    if(new Set(d.nrAll).size!==r.length)E(`panel lists ${new Set(d.nrAll).size}, related ${r.length}`);
    if(d.go[1]!==!rv.length)E(`go disabled=${d.go[1]}`); if(rv.length&&!d.go[0].includes(String(rv.length)))E(`go "${d.go[0]}" vs ${rv.length}`);
    if(d.showrel[0]!==(rv.length===r.length))E(`showrel hidden=${d.showrel[0]}`);
    for(const w of WS){const c=w.code.toLowerCase(),want=(w.naf_core||[]).includes(s.naf)?'Core: ':(w.naf_touch||[]).includes(s.naf)?'Touches ':'';
      if(!d.rels[c].startsWith(want)||(!want&&d.rels[c]))E(`ws-rel ${c} "${d.rels[c]}"`);}
    if(JSON.stringify(d.nbPressed)!==JSON.stringify([s.naf]))E(`diagram pressed ${d.nbPressed}`);
    if(d.cardNafHit.some(x=>x!==s.naf))E('card NAF hit mismatch');}
  else {if(d.nbPressed.length||d.cardNafHit.length)E('NAF pressed with no NAF filter'); if(Object.values(d.rels).some(Boolean))E('ws-rel shown with no NAF');}
  if(d.tagHit.some(t=>!s.topics.includes(t)))E(`tag hit ${d.tagHit}`);
  if(d.qv.trim()!==s.q)E(`search box "${d.qv}" vs q "${s.q}"`); if(d.mat!==s.mat)E('mat checkbox'); if(d.oss!==s.oss)E('oss checkbox');
  if(d.search!==canon(s))E(`url "${d.search}" != canonical "${canon(s)}"`);
  if(d.overflow>0)E(`horizontal overflow ${d.overflow}px`);
  if(errs.length)throw new Error(ctx+'\n  - '+errs.join('\n  - '));
}

// ---------- helpers ----------
let seed=7; const rnd=()=>(seed=(seed*1103515245+12345)%2147483648)/2147483648;
const pick=a=>a[Math.floor(rnd()*a.length)];
const QS=['','nokia','ai','lab','python ansible','zzz','intent','open','containerlab','git','arista','netbox','observ','  lab   ai  '];
function randState(){
  const t=[]; const k=rnd()<.45?0:rnd()<.7?1:2; while(t.length<k){const x=pick(TOP);if(!t.includes(x))t.push(x);}
  return {block:rnd()<.5?'':pick(SLOTS),topics:t,q:rnd()<.6?'':pick(QS).trim().replace(/\s+/g,' '),mat:rnd()<.6,oss:rnd()<.3,naf:rnd()<.5?'':pick(NAFS)};
}
const wait=ms=>new Promise(r=>setTimeout(r,ms));

async function openPanel0(page,P){if(P==='phone'&&!(await page.$eval('#panel',p=>p.classList.contains('open'))))await page.click('#fbtn');}
async function run(){
  const browser=await chromium.launch();
  let total=0, failures=[];
  const T=async(name,fn)=>{total++;try{await fn();}catch(e){failures.push(name+': '+e.message.split('\n').slice(0,8).join('\n'));}};
  for(const vp of [{name:'desktop',width:1280,height:860},{name:'phone',width:390,height:844,isMobile:true,hasTouch:true}]){
    const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height},isMobile:!!vp.isMobile,hasTouch:!!vp.hasTouch});
    // tests don't need the smooth-scroll animation; strip it so positions settle at once
    await ctx.addInitScript(()=>{const o=window.scrollTo.bind(window);window.scrollTo=(a,b)=>typeof a==='object'?o({...a,behavior:'auto'}):o(a,b);});
    const page=await ctx.newPage(); const errors=[];
    page.on('pageerror',e=>errors.push(e.message)); page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    const P=vp.name;

    // 1) URL combos
    const combos=[DEF,{...DEF,mat:false}];
    for(let i=0;i<(QUICK?40:P==='desktop'?300:120);i++)combos.push(randState());
    for(const s of combos){await T(`${P} url ${canon(s)}`,async()=>{
      await page.goto(BASE+canon(s)); check(s,await snapshot(page),`${P} load ${canon(s)||'(default)'}`);});}
    // invalid params get dropped
    await T(`${P} invalid params`,async()=>{await page.goto(BASE+'?slot=Z&topic=nope,ai&naf=bogus&material=0');
      check({...DEF,topics:['ai'],mat:false},await snapshot(page),'invalid params');});
    // deep link to a card hidden by default filters
    for(const w of WS){await T(`${P} deep link #${w.code}`,async()=>{
      await page.goto(BASE+'?oss=1#'+w.code.toLowerCase()); await wait(150);
      const s0={...DEF,oss:true}, f=failsM(w,s0); const s=f.reduce(drop,s0);
      const d=await snapshot(page); check(s,d,`deep link ${w.code}`);
      const box=await page.$eval('#'+w.code.toLowerCase(),c=>{const r=c.getBoundingClientRect();return [r.top,innerHeight,document.querySelector('#bar').getBoundingClientRect().bottom];});
      if(box[0]<box[2]-2||box[0]>box[1]-40)throw new Error(`card ${w.code} not in view after deep link: top ${box[0]} bar ${box[2]}`);
      const toast=await page.$eval('#note',n=>n.hidden?'':n.textContent); if(f.length&&!toast)throw new Error('no toast after relaxing');
      if(!f.length&&toast)throw new Error('toast without relaxing: '+toast);});}

    // typing with pauses must never eat spaces or letters
    await T(`${P} search typing with pauses`,async()=>{await page.goto(BASE+'?material=0');await openPanel0(page,P);
      await page.click('#q'); for(const part of ['open ','source ','lab']){await page.keyboard.type(part,{delay:30});await wait(400);}
      const v=await page.inputValue('#q'); if(v!=='open source lab')throw new Error(`search box reads "${v}" after typing with pauses`);
      check(parse(await page.evaluate(()=>location.search)),await snapshot(page),'typing');});
    // a filter change while scrolled deep must not leave you looking at the footer
    await T(`${P} chip while scrolled to bottom`,async()=>{await page.goto(BASE+'?material=0');await page.evaluate(()=>scrollTo(0,document.body.scrollHeight));
      await openPanel0(page,P); await page.evaluate(()=>document.querySelector('.chip[data-topic="iac"]').click()); await wait(100);
      const r=await page.$eval('#c4',c=>[c.getBoundingClientRect().top,innerHeight]); if(r[0]<0||r[0]>r[1])throw new Error(`only card C4 is off screen at ${r[0]}`);});
    // 2) random click walks
    const openPanel=async()=>{if(P==='phone'&&!(await page.$eval('#panel',p=>p.classList.contains('open'))))await page.click('#fbtn');};
    const ACTIONS=['tab','chip','tag','cardnaf','diagram','cov','nafchip','reset','showall','relax','mat','oss','search','jump','nr','showrel','undo','scroll'];
    for(let walk=0;walk<(QUICK?6:P==='desktop'?28:18);walk++){
      let s=walk<3?DEF:randState(); await page.goto(BASE+canon(s)); const log=[canon(s)||'(default)'];
      for(let step=0;step<14;step++){
        const a=pick(ACTIONS); let expect=null, desc=a, anchor=null, target=null, bar=false;
        await T(`${P} walk ${walk} step ${step} ${a}`,async()=>{
          if(a==='scroll'){await page.evaluate(y=>scrollTo(0,y*document.body.scrollHeight),rnd());return;}
          if(a==='tab'){const k=pick(['',...SLOTS]);desc+=' '+(k||'All');await page.click(`.tab[data-block="${k}"]`);expect={...s,block:k};bar=true;}
          else if(a==='chip'){await openPanel();const t=pick(TOP);desc+=' '+t;await page.click(`.chip[data-topic="${t}"]`);
            expect={...s,topics:s.topics.includes(t)?s.topics.filter(x=>x!==t):[...s.topics,t]};bar=true;}
          else if(a==='tag'||a==='cardnaf'){const sel=a==='tag'?'.ws:not([hidden]) .tag[data-topic]':'.ws:not([hidden]) .ws-naf button[data-naf]';
            const els=await page.$$(sel); if(!els.length){desc+=' (none visible)';return;}
            const el=pick(els); const v=await el.evaluate(e=>e.dataset.topic||e.dataset.naf); desc+=' '+v;
            await el.scrollIntoViewIfNeeded(); anchor=[el,await el.evaluate(e=>{const t=e.getBoundingClientRect().top;e.click();return t;})];
            expect=a==='tag'?{...s,topics:s.topics.includes(v)?s.topics.filter(x=>x!==v):[...s.topics,v]}:{...s,naf:s.naf===v?'':v};}
          else if(a==='diagram'||a==='cov'){if(a==='cov'&&s.naf){desc+=' (panel not idle)';return;}const id=pick(NAFS);desc+=' '+id;
            await page.click(a==='diagram'?`.nb[data-naf="${id}"]`:`.cov[data-naf="${id}"]`);expect={...s,naf:s.naf===id?'':id};}
          else if(a==='nafchip'){if(!s.naf){desc+=' (hidden)';return;}await page.click('#nafchip');expect={...s,naf:''};bar=true;}
          else if(a==='reset'){if(isDef(s)){desc+=' (hidden)';return;}await page.click('#clear');expect={...DEF};bar=true;}
          else if(a==='showall'){if(await page.$eval('#showall',b=>b.hidden)){desc+=' (hidden)';return;}await page.click('#showall');expect={...s,mat:false};bar=true;}
          else if(a==='relax'){const bs=await page.$$('#relax [data-relax]');if(!bs.length){desc+=' (none)';return;}const b=pick(bs);const k=await b.getAttribute('data-relax');desc+=' '+k;await b.click();expect=drop(s,k);bar=true;}
          else if(a==='mat'||a==='oss'){await openPanel();await page.click(`#${a}`);expect={...s,[a]:!s[a]};bar=true;}
          else if(a==='search'){await openPanel();const v=pick(QS);desc+=` "${v}"`;await page.fill('#q','');await page.type('#q',v,{delay:20});await wait(260);
            expect={...s,q:v.trim()};bar=true;}
          else if(a==='jump'||a==='nr'){
            const sel=a==='jump'?'#jump a':'.np:not([hidden]) .nr'; const els=await page.$$(sel); if(!els.length){desc+=' (none)';return;}
            const el=pick(els); const id=await el.evaluate(e=>e.dataset.for||e.dataset.ws); desc+=' '+id;
            await el.click(); const w=WS.find(x=>x.code.toLowerCase()===id); expect=failsM(w,s).reduce(drop,s); target=id;}
          else if(a==='showrel'){const b=await page.$('.np:not([hidden]) [data-showrel]:not([hidden])');if(!b){desc+=' (hidden)';return;}
            await b.click(); const r=WS.filter(w=>rel(w,s.naf)); expect=[...new Set(r.flatMap(w=>failsM(w,s)))].reduce(drop,s);}
          else if(a==='undo'){if(!(await page.$eval('#note',n=>!n.hidden))){desc+=' (no toast)';return;}await page.click('#undo');expect=s.__prev||s;}
          await wait(60);
          const d=await snapshot(page); const got=parse(d.search);
          if(!same(got,{...expect,__prev:undefined,topics:expect.topics})&&!same(got,{block:expect.block,topics:expect.topics,q:expect.q,mat:expect.mat,oss:expect.oss,naf:expect.naf}))
            throw new Error(`${desc}: state ${JSON.stringify(got)} expected ${JSON.stringify(expect)}`);
          check(got,d,`${P} walk ${walk} after [${log.join(' > ')} > ${desc}]`);
          if(anchor&&await anchor[0].evaluate(e=>!!e.offsetParent)){const y=await anchor[0].evaluate(e=>e.getBoundingClientRect().top);
            if(Math.abs(y-anchor[1])>2)throw new Error(`${desc}: clicked card moved ${anchor[1]}→${y}`);}
          if(target){const r=await page.$eval('#'+target,c=>[c.getBoundingClientRect().top,innerHeight,document.querySelector('#bar').getBoundingClientRect().bottom,location.hash]);
            if(r[0]<r[2]-2||r[0]>r[1]-40)throw new Error(`${desc}: card not in view (top ${r[0]}, bar ${r[2]})`); if(r[3]!=='#'+target)throw new Error('hash '+r[3]);}
          if(bar){const r=await page.evaluate(()=>{const b=document.querySelector('#bar').getBoundingClientRect();
              if(b.top>1)return 'ok';const els=[...document.querySelectorAll('.ws:not([hidden])')];const e=document.querySelector('#empty.show');if(e)els.push(e);
              return els.some(x=>{const r=x.getBoundingClientRect();return r.bottom>b.bottom+20&&r.top<innerHeight-20;})?'ok':'nothing in view';});
            if(r!=='ok')throw new Error(`${desc}: ${r} under the stuck bar`);}
          const prev={...s}; s={...got}; if(['jump','nr','showrel'].includes(a)&&!same(prev,s))s.__prev=prev; else if(a!=='undo'&&a!=='scroll')s.__prev=undefined;
          log.push(desc); if(!desc.includes('('))STATS[P+' '+a]=(STATS[P+' '+a]||0)+1;
        });
        if(failures.length>25)break;
      }
    }
    if(errors.length)failures.push(`${P} page errors: ${[...new Set(errors)].join(' | ')}`);
    await ctx.close();
  }
  await browser.close();
  if(!process.env.QUIET)console.log('actions exercised:',JSON.stringify(STATS));
  console.log(`${total} checks, ${failures.length} failed`);
  failures.slice(0,25).forEach(f=>console.log('\nFAIL '+f));
  process.exit(failures.length?1:0);
}
run();

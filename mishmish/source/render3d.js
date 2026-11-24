const {chromium}=require('playwright');const fs=require('fs'),path=require('path'),http=require('http');const {spawn}=require('child_process');
const root=__dirname;const types={'.html':'text/html','.js':'text/javascript','.woff2':'font/woff2','.json':'application/json'};
const srv=http.createServer((q,r)=>{const f=path.join(root,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);r.end();return}r.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});r.end(d)})}).listen(8765);
(async()=>{
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('console',m=>{if(m.type()==='error')console.log('ERR',m.text())});p.on('pageerror',e=>console.log('PAGEERR',e.message));
 await p.goto('http://localhost:8765/'+(process.env.SCENE||"scene3d.html")+'');await p.waitForFunction(()=>window.ready,null,{timeout:60000});
 await p.evaluate(async([tm,mo])=>{setData(tm,mo);await document.fonts.load('80px Lz','مشمش');await document.fonts.load('80px Lz','abc')},[JSON.parse(fs.readFileSync(root+'/'+(process.env.TIMING||'timing.json'),'utf8')),JSON.parse(fs.readFileSync(root+'/'+(process.env.MOUTH||'mouth.json'),'utf8'))]);
 const grab=async t=>Buffer.from((await p.evaluate(t=>{render(t);return document.getElementById('out').toDataURL('image/jpeg',.93)},t)).split(',')[1],'base64');
 if(process.argv[2]==='preview'){for(const t of process.argv.slice(3).map(Number)){const s=Date.now();fs.writeFileSync(`${root}/p3_${t}.jpg`,await grab(t));console.log(t,Date.now()-s,'ms')}}
 else{const [from,to,outp]=[+process.argv[3],+process.argv[4],process.argv[5]];
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',outp],{stdio:['pipe','inherit','inherit']});
  for(let f=from;f<to;f++){const buf=await grab(f/30);if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(f%150==0)console.log('frame',f,new Date().toISOString())}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));}
 await b.close();srv.close();
})();

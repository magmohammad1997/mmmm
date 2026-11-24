const {chromium}=require('playwright');const path=require('path'),http=require('http');const types={'.html':'text/html','.js':'text/javascript','.woff2':'font/woff2','.png':'image/png'};
const srv=http.createServer((q,r)=>{const f=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));require('fs').readFile(f,(e,d)=>{if(e){r.writeHead(404);r.end();return}r.writeHead(200,{'Content-Type':types[path.extname(f)]||'application/octet-stream'});r.end(d)})}).listen(+(process.env.PORT||8770));const fs=require('fs');const {spawn}=require('child_process');
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>console.log('PAGEERR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('ERR',m.text())});
 await p.goto('http://localhost:'+(process.env.PORT||8770)+'/scene2d.html');await p.waitForFunction(()=>window.ready);
 await p.evaluate(async([d,m])=>{await setData(d,m)},[JSON.parse(fs.readFileSync(__dirname+'/data.json','utf8')),JSON.parse(fs.readFileSync(__dirname+'/mouth.json','utf8'))]);
 const grab=async t=>Buffer.from((await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.92)},t)).split(',')[1],'base64');
 if(process.argv[2]==='preview'){for(const t of process.argv.slice(3).map(Number))fs.writeFileSync(`${__dirname}/pv_${t}.jpg`,await grab(t))}
 else{const out=process.argv[3];const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
  for(let f=0;f<1800;f++){const buf=await grab(f/30);if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(f%300==0)console.log('frame',f)}
  ff.stdin.end();await new Promise(r=>ff.on('close',r))}
 await b.close();srv.close();
})();

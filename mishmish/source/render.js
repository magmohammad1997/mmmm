const {chromium}=require('playwright');const fs=require('fs');const {spawn}=require('child_process');
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
 await p.goto('file://'+__dirname+'/scene.html');
 await p.evaluate(async j=>{setTiming(j);await document.fonts.load('80px Lz','مشمش');await document.fonts.load('80px Lz','abc');await document.fonts.ready},JSON.parse(fs.readFileSync(__dirname+'/timing.json','utf8')));
 const grab=async t=>Buffer.from((await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.93)},t)).split(',')[1],'base64');
 if(process.argv[2]==='preview'){for(const t of process.argv.slice(3).map(Number))fs.writeFileSync(`${__dirname}/prev_${t}.jpg`,await grab(t));}
 else{
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-i',__dirname+'/song.wav','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',process.argv[3]],{stdio:['pipe','inherit','inherit']});
  for(let f=0;f<1800;f++){const buf=await grab(f/30);if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(f%300==0)console.log('frame',f)}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));
 }
 await b.close();
})();

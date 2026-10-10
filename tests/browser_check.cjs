// Local artifact QA only; no user browser/session access.
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url'),{chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'.qa/browser');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const args=process.argv.slice(2),idx=args.indexOf('--browser');
 const browser=await chromium.launch({headless:true,...(idx>=0?{executablePath:args[idx+1]}:{})});
 const context=await browser.newContext({offline:true,viewport:{width:1440,height:1000}});
 const page=await context.newPage(),requests=[],errors=[];
 page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(root,'examples/sample-report.html')).href);
 const result={browser:browser.version()};
 result.chinese=(await page.locator('h1').innerText()).includes('理线夹');
 result.modules=await page.evaluate(()=>!!document.querySelector('header .decision')&&['overview','score','risks','profit','people','scenes','plays','topics','listing','plan','month','metrics','actions','evidence'].every(id=>document.getElementById(id)));
 result.desktop=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1);
 await page.screenshot({path:path.join(out,'desktop.png')});
 await page.locator('#topics').screenshot({path:path.join(out,'topics.png')});
 await page.locator('a[href="#e-P"]').first().click();result.evidence=await page.evaluate(()=>location.hash==='#e-P');
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));
 result.mobile=await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1);
 await page.screenshot({path:path.join(out,'mobile.png')});
 await page.setViewportSize({width:1440,height:1000});
 // Expand native details before printing, including browsers lacking ::details-content support.
 await page.locator('details').evaluateAll(nodes=>nodes.forEach(n=>n.open=true));
 await page.emulateMedia({media:'print'});await page.pdf({path:path.join(out,'print.pdf'),format:'A4',printBackground:true});
 result.print=fs.statSync(path.join(out,'print.pdf')).size>10000;
 await page.emulateMedia({media:'screen'});
 await page.goto(pathToFileURL(path.join(root,'examples/screenshot/xiaohongshu-product-strategy-report.html')).href);
 result.image=await page.evaluate(()=>document.images.length===1&&document.images[0].naturalWidth>0);
 await page.goto(pathToFileURL(path.join(root,'.qa/hostile.html')).href);
 result.security=await page.evaluate(()=>!globalThis.pwned&&document.querySelectorAll('script').length===0);
 result.offline=requests.length===0&&errors.length===0;
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 await browser.close();if(Object.values(result).some(x=>x===false))process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});

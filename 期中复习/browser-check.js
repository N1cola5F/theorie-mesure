async (page) => {
  const errors=[],failed=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('requestfailed',r=>failed.push(r.url()));
  page.on('request',r=>requests.push(r.url()));
  await page.setViewportSize({width:1280,height:900});
  await page.goto('http://127.0.0.1:8765/site/ds/');
  await page.locator('main h1').filter({hasText:'先过知识'}).waitFor();
  const initial=await page.evaluate(()=>({cards:document.querySelectorAll('.card').length,inlineSVG:document.querySelectorAll('svg').length,images:document.querySelectorAll('main img').length}));
  const initialPDFRequests=requests.filter(u=>u.includes('.pdf')).length;
  await page.locator('nav a[href="#ch1"]').click();
  await page.locator('#c1-13').waitFor();
  if(await page.locator('.card').count()!==13)throw Error('Chapter 1 card count');
  const modeTimes={};
  for(const mode of ['fr','compare','zh']){
    const start=Date.now();
    await page.locator('[data-mode="'+mode+'"]').click();
    await page.waitForFunction(m=>document.querySelector('[data-mode="'+m+'"]').getAttribute('aria-pressed')==='true'&&document.querySelector('#c1-01 .columns').children.length===(m==='compare'?2:1),mode);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    modeTimes[mode]=Date.now()-start;
  }
  await page.locator('#search').fill('Fubini');
  await page.locator('a.result[href="#c6-05"]').waitFor();
  await page.locator('a.result[href="#c6-05"]').click();
  await page.locator('#c6-05').waitFor();
  const searchJump=await page.evaluate(()=>({hash:location.hash,target:!!document.getElementById('c6-05')}));
  await page.locator('nav a[href="#proofs"]').click();
  await page.locator('main a[href="#p15"]').click();
  await page.locator('#p15').waitFor();
  const proof=await page.evaluate(()=>({cards:document.querySelectorAll('.card').length,dependencies:document.querySelectorAll('.panel .refs a').length,formulaImage:document.querySelector('#p15 img')?.getAttribute('src')}));
  await page.locator('.panel .refs a[href="#c5-10"]').click();
  await page.locator('#c5-10').waitFor();
  await page.setViewportSize({width:390,height:844});
  await page.locator('#menu').click();
  await page.locator('nav a[href="#ch8"]').click();
  await page.locator('#c8-13').waitFor();
  const mobile=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,cards:document.querySelectorAll('.card').length,menuClosed:!document.getElementById('sidebar').classList.contains('open'),hasExercises:document.querySelector('main').innerText.includes('学完后的练习建议')}));
  if(mobile.scrollWidth>mobile.width||mobile.hasExercises||mobile.cards!==13)throw Error('Mobile/chapter8 scope');
  await page.locator('#menu').click();
  await page.locator('nav a[href="#td"]').click();
  await page.locator('details').last().locator('summary').click();
  const td4=await page.locator('a').filter({hasText:'Ex. 1.1 · 用截面算单纯形体积'}).getAttribute('href');
  const head=await page.request.head('http://127.0.0.1:8765/site/'+td4.replace('../','').split('#')[0]);
  if(head.status()!==200)throw Error('TD4 PDF source missing');
  if(errors.length||failed.length)throw Error(JSON.stringify({errors,failed}));
  return {scope:'Representative chapter, language modes, search, proof/dependency, mobile and one new PDF; no screenshots',initial,initialPDFRequests,modeTimesMs:modeTimes,searchJump,proof,mobile,td4PDFStatus:head.status(),pageErrors:errors,failedRequests:failed};
}

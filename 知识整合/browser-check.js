async (page) => {
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.reload();
  await page.setViewportSize({width:1440,height:1000});
  await page.getByRole('link',{name:'§ 学期概览 Vue d’ensemble',exact:true}).click();
  await page.screenshot({path:'output/playwright/overview.png'});
  await page.getByRole('link',{name:'01 Lebesgue 外测度 Mesure extérieure de Lebesgue W1',exact:true}).click();
  await page.screenshot({path:'output/playwright/chapter1.png'});
  await page.locator('#set-limits .proof summary').click();
  const results = {proofOpens:await page.locator('#set-limits .proof').getAttribute('open')!==null};
  await page.screenshot({path:'output/playwright/proof.png'});
  await page.getByRole('searchbox').fill('continuité');
  await page.waitForFunction(()=>document.querySelector('#search-status').textContent.includes('continuité'));
  results.frenchSearch=await page.locator('#search-status').textContent();
  await page.getByRole('searchbox').fill('不存在的搜索词xyz');
  await page.waitForFunction(()=>!document.querySelector('#search-empty').hidden);
  results.emptySearch=await page.locator('#search-empty').isVisible();
  await page.getByRole('button',{name:'清除搜索',exact:true}).click();
  results.clearSearch=await page.locator('#ch1').isVisible();
  await page.locator('#caratheodory-theorem .dep-link[href="#sigma-algebra"]').click();
  await page.locator('#ch2').waitFor({state:'visible'});
  results.crossChapter=await page.locator('#ch2').isVisible();
  await page.screenshot({path:'output/playwright/chapter2.png'});
  results.layouts=[];
  for (const width of [1440,1024,768,390,320]) {
    await page.setViewportSize({width,height:900});
    for (const hash of ['ch1','ch2','ch3','ch4','resources']) {
      await page.evaluate(hash=>{location.hash=hash;},hash);
      await page.waitForFunction(hash=>!document.getElementById(hash).hidden,hash);
      results.layouts.push(await page.evaluate(()=>({width:innerWidth,chapter:location.hash,overflow:document.documentElement.scrollWidth>innerWidth+1})));
    }
  }
  await page.setViewportSize({width:390,height:844});
  await page.getByRole('button',{name:'切换章节目录',exact:true}).click();
  results.mobileMenu=await page.locator('#menu').getAttribute('aria-expanded');
  await page.getByRole('link',{name:'04 可测函数 Fonctions mesurables W2',exact:true}).click();
  results.mobileMenuClosed=await page.locator('#menu').getAttribute('aria-expanded');
  await page.screenshot({path:'output/playwright/mobile.png'});
  await page.setViewportSize({width:1440,height:1000});
  results.glyphs=await page.evaluate(()=>{
    const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
    return {duplicateIds:ids.length-new Set(ids).size,missingUses:[...document.querySelectorAll('use')].filter(x=>!document.getElementById((x.getAttribute('href')||x.getAttribute('xlink:href')).slice(1))).length,svgs:document.querySelectorAll('.tex-svg').length};
  });
  await page.emulateMedia({media:'print'});
  results.print = await page.evaluate(()=>({visibleCards:[...document.querySelectorAll('.card')].filter(x=>getComputedStyle(x).display!=='none').length,overviewHidden:getComputedStyle(document.querySelector('#overview')).display==='none',proofHidden:getComputedStyle(document.querySelector('.proof')).display==='none'}));
  await page.pdf({path:'output/playwright/知识提纲_打印核验.pdf',preferCSSPageSize:true,printBackground:true});
  await page.emulateMedia({media:'screen'});
  await page.getByRole('link',{name:'§ 学期概览 Vue d’ensemble',exact:true}).click();
  return results;
}

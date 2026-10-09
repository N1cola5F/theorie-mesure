async (page) => {
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.reload();
  await page.getByRole('searchbox').fill('可测');
  await page.waitForFunction(()=>document.querySelector('#search-status').textContent.includes('可测'));
  const results={chineseSearch:await page.locator('#search-status').textContent()};
  await page.getByRole('searchbox').fill('\\limsup');
  await page.waitForFunction(()=>document.querySelector('#search-status').textContent.includes('\\limsup'));
  results.latexSearch=await page.locator('#search-status').textContent();
  results.externalRequests=await page.evaluate(()=>performance.getEntriesByType('resource').filter(x=>/^https?:/.test(x.name)&&!x.name.startsWith(location.origin)).map(x=>x.name));
  await page.emulateMedia({media:'print'});
  await page.pdf({path:'output/playwright/知识提纲_打印核验.pdf',preferCSSPageSize:true,printBackground:true});
  await page.emulateMedia({media:'screen'});
  await page.getByRole('link',{name:'§ 学期概览 Vue d’ensemble',exact:true}).click();
  results.javascriptErrors=errors;
  return results;
}

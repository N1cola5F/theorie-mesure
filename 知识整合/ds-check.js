async (page) => {
  const errors = [], failed = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('requestfailed', r => failed.push({url: r.url(), error: r.failure()?.errorText}));
  await page.setViewportSize({width:1440,height:950});
  await page.goto('http://127.0.0.1:8765/site/reader/#intersection-sigma');
  await page.waitForSelector('#intersection-sigma .ds-scope');
  await page.locator('#intersection-sigma').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => [...document.querySelectorAll('#intersection-sigma .zh-reading img')].every(img => img.complete && img.naturalWidth));
  const added = await page.locator('#intersection-sigma').evaluate(card => ({
    ds: card.querySelector('.ds-badge').textContent,
    added: Boolean(card.querySelector('.ds-added')),
    official: card.querySelector('.ds-page').getAttribute('href'),
    statement: card.querySelector('.ds-statement').getAttribute('href'),
    proof: card.querySelector('.ds-proofs a').getAttribute('href'),
    chineseImage: card.querySelector('.zh-reading img').naturalWidth
  }));
  if (!added.added || added.statement !== '../ds/#c2-04' || added.proof !== '../ds/#p03') throw new Error('New-card annotation failed');
  const official = await page.request.head(await page.evaluate(href => new URL(href, document.baseURI).href, added.official));
  const counterpart = await page.request.get(await page.evaluate(href => new URL(href, document.baseURI).href, added.statement));
  if (official.status() !== 200 || counterpart.status() !== 200) throw new Error('DS source link failed');
  await page.locator('[data-reading-mode="compare"]').click();
  await page.waitForSelector('#intersection-sigma .fr-reading img');
  await page.locator('#intersection-sigma .fr-reading img').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => [...document.querySelectorAll('#intersection-sigma .fr-reading img')].every(img => img.complete && img.naturalWidth));
  const compare = await page.locator('#intersection-sigma').evaluate(card => ({
    mode: document.body.dataset.lang,
    marked: Boolean(card.querySelector('.ds-scope')),
    chinese: card.querySelectorAll('.zh-reading img').length,
    french: card.querySelectorAll('.fr-reading img').length,
    frenchWidth: card.querySelector('.fr-reading img').getBoundingClientRect().width
  }));
  await page.locator('[data-reading-mode="fr"]').click();
  await page.waitForFunction(() => document.body.dataset.lang === 'fr' && document.querySelector('#intersection-sigma .fr-reading img'));
  const french = await page.locator('#intersection-sigma .ds-scope').innerText();
  if (!french.includes('Au programme') || !french.includes('Intersection de tribus')) throw new Error('French annotation missing');
  await page.locator('[data-reading-mode="zh"]').click();
  await page.locator('#search').fill('DS');
  await page.waitForFunction(() => document.querySelectorAll('.search-result').length === 70);
  const searchDs = await page.evaluate(() => ({count: document.querySelectorAll('.search-result').length, allMarked: [...document.querySelectorAll('.search-result')].every(a => a.querySelector('.ds-search-label'))}));
  await page.locator('#search').fill('c3-04');
  await page.waitForFunction(() => document.querySelectorAll('.search-result').length === 1 && document.querySelector('.search-result')?.hash === '#lebesgue-rn');
  const searchId = await page.evaluate(() => ({ids: [...document.querySelectorAll('.search-result')].map(a => a.hash)}));
  await page.locator('.search-result').click();
  await page.waitForSelector('#lebesgue-rn .ds-added');
  await page.locator('#lebesgue-rn').scrollIntoViewIfNeeded();
  await page.waitForFunction(() => [...document.querySelectorAll('#lebesgue-rn .zh-reading img')].every(img => img.complete && img.naturalWidth));
  await page.evaluate(() => {location.hash = '#lp-spaces';});
  await page.waitForSelector('#lp-spaces .ds-qualifier');
  const statementOnly = await page.locator('#lp-spaces .ds-scope').innerText();
  if (!statementOnly.includes('只要求知识陈述')) throw new Error('Ch7 statement-only qualifier missing');
  await page.evaluate(() => {location.hash = '#measure-definition';});
  await page.waitForSelector('#measure-definition .ds-related a');
  await page.locator('#measure-definition .ds-related a').click();
  await page.waitForFunction(() => location.hash === '#finite-sigma-finite' && document.querySelector('#finite-sigma-finite .ds-scope'));
  const related = await page.evaluate(() => location.hash);
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(() => {location.hash = '#intersection-sigma';});
  await page.waitForSelector('#intersection-sigma .ds-scope');
  await page.locator('#intersection-sigma').scrollIntoViewIfNeeded();
  await page.locator('[data-reading-mode="compare"]').click();
  await page.waitForSelector('#intersection-sigma .fr-reading img');
  const mobile = await page.evaluate(() => ({
    width: innerWidth, documentWidth: document.documentElement.scrollWidth,
    overflow: document.documentElement.scrollWidth > innerWidth,
    badgeVisible: document.querySelector('#intersection-sigma .ds-badge').getBoundingClientRect().width > 0,
    dsPanelWidth: document.querySelector('#intersection-sigma .ds-scope').getBoundingClientRect().width
  }));
  const pdfRequests = await page.evaluate(() => performance.getEntriesByType('resource').filter(e => /\.pdf(?:#|$)/.test(e.name)).length);
  return {added, official_status:official.status(), counterpart_status:counterpart.status(), compare, french_annotation:true,
    search_ds:searchDs, search_id:searchId, statement_only:true, related_link:related, mobile,
    pdf_auto_requests:pdfRequests, errors, failed_requests:failed};
}

const { chromium } = require('/Users/wclin/.config/opencode/skills/playwright-skill/node_modules/playwright/lib/index.js');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    await page.goto('https://www.twse.com.tw/', { waitUntil: 'networkidle', timeout: 10000 });
    console.log('📄 Page title:', await page.title());
    console.log('📄 URL:', await page.url());
    console.log('📄 Text content length:', await page.textContent().then(t => t.length));
    console.log('✅ TWSE homepage loaded successfully');
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
})();

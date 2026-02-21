const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    // Massive initial viewport
    await page.setViewport({ width: 4000, height: 4000 });
    await page.goto('file:///Users/chenjianfeng/ReadBooks/BookQuoteApp/backend/static/mindmap_小王子_1771609185.html', { waitUntil: 'networkidle0' });
    
    await new Promise(r => setTimeout(r, 2000));
    
    // Evaluate the box
    const printBox = await page.evaluate(() => {
        const svg = document.querySelector('svg');
        const g = document.querySelector('svg > g');
        if (!g) return { width: 1920, height: 1080 };
        const bbox = g.getBBox();
        return { 
            width: Math.ceil(bbox.width) + 120, 
            height: Math.ceil(bbox.height) + 120 
        };
    });
    
    // Shrink the viewport explicitly to that box to force Markmap to fit perfectly!
    await page.setViewport(printBox);
    await new Promise(r => setTimeout(r, 1000)); // wait for markmap fit()
    
    // Now print it
    await page.pdf({
        path: 'test_viewport.pdf',
        width: printBox.width + 'px',
        height: printBox.height + 'px',
        printBackground: true,
        pageRanges: '1'
    });
    
    console.log("PDF Created with width:", printBox.width, "height:", printBox.height);
    await browser.close();
})();

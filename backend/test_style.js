const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setViewport({ width: 4000, height: 4000 });
    await page.goto('file:///Users/chenjianfeng/ReadBooks/BookQuoteApp/backend/static/mindmap_小王子_1771609185.html', { waitUntil: 'networkidle0' });
    
    await page.addStyleTag({ content: `
        body { background: #f5f5dc !important; margin: 0; padding: 0; } 
        svg { background: #f5f5dc !important; } 
    ` });
    
    await new Promise(r => setTimeout(r, 2000));
    const printBox = await page.evaluate(() => {
        const svg = document.querySelector('svg');
        const clone = svg.cloneNode(true);
        document.body.innerHTML = '';
        document.body.appendChild(clone);
        const bbox = clone.querySelector('svg > g').getBBox();
        const padding = 60;
        const newWidth = Math.ceil(bbox.width) + padding * 2;
        const newHeight = Math.ceil(bbox.height) + padding * 2;
        const newX = Math.floor(bbox.x) - padding;
        const newY = Math.floor(bbox.y) - padding;
        clone.style.width = newWidth + 'px';
        clone.style.height = newHeight + 'px';
        clone.setAttribute('viewBox', `${newX} ${newY} ${newWidth} ${newHeight}`);
        return { width: newWidth, height: newHeight };
    });
    
    await page.pdf({
        path: 'test_style.pdf',
        width: printBox.width + 'px',
        height: printBox.height + 'px',
        printBackground: true,
        pageRanges: '1'
    });
    console.log("PDF Created with width:", printBox.width, "height:", printBox.height);
    await browser.close();
})();

const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setViewport({ width: 4000, height: 4000 });
    // Load a recent html
    await page.goto('file:///Users/chenjianfeng/ReadBooks/BookQuoteApp/backend/static/mindmap_小王子_1771609185.html', { waitUntil: 'networkidle0' });
    
    await new Promise(r => setTimeout(r, 2000));
    const printBox = await page.evaluate(() => {
        const svg = document.querySelector('svg');
        const g = document.querySelector('svg > g');
        if (!g) return { width: 1920, height: 1080 };
        
        const bbox = g.getBBox();
        const padding = 60;
        const newWidth = Math.ceil(bbox.width) + padding * 2;
        const newHeight = Math.ceil(bbox.height) + padding * 2;
        
        // Reset transform so it starts at top-left padding
        g.setAttribute('transform', `translate(${-bbox.x + padding}, ${-bbox.y + padding}) scale(1)`);
        
        // Remove viewBox if exists
        svg.removeAttribute('viewBox');
        
        // Resize SVG to exactly fit the map
        svg.style.width = newWidth + 'px';
        svg.style.height = newHeight + 'px';
        
        return { width: newWidth, height: newHeight };
    });
    
    await page.pdf({
        path: 'test_output.pdf',
        width: printBox.width + 'px',
        height: printBox.height + 'px',
        printBackground: true,
        pageRanges: '1'
    });
    console.log("PDF Created with width:", printBox.width, "height:", printBox.height);
    await browser.close();
})();

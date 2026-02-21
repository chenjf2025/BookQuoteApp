const puppeteer = require('puppeteer');
(async () => {
    try {
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

            // Clone mapping to kill resize observers
            const clone = svg.cloneNode(true);
            document.body.innerHTML = '';
            document.body.appendChild(clone);
            document.body.style.margin = '0';
            document.body.style.padding = '0';

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
            path: 'test_output2.pdf',
            width: printBox.width + 'px',
            height: printBox.height + 'px',
            printBackground: true,
            pageRanges: '1'
        });
        console.log("PDF Created with width:", printBox.width, "height:", printBox.height);
        await browser.close();
    } catch (e) {
        console.error(e);
        process.exit(1);
    }
})();

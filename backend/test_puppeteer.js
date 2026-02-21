const puppeteer = require('puppeteer');
(async () => {
    try {
        console.log("Launching browser...");
        const browser = await puppeteer.launch();
        console.log("Browser launched.");
        await browser.close();
    } catch (e) {
        console.error("Puppeteer error:", e);
        process.exit(1);
    }
})();

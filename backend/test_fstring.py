import time
timestamp = 123
html_path = 'test.html'
pdf_path = 'test.pdf'
js_content = f"""
        const puppeteer = require('puppeteer');
        (async () => {{
            const browser = await puppeteer.launch();
            const page = await browser.newPage();
            // Start with a massive viewport so Markmap has space to unfold
            await page.setViewport({{ width: 4000, height: 4000 }});
            // Load the markmap HTML file
            await page.goto('file://{html_path}', {{ waitUntil: 'networkidle0' }});
            
            // Inject styles for print, strictly keeping beige background, letting Markmap handle original colors
            await page.addStyleTag({{ content: `
                body {{ background: #f5f5dc !important; margin: 0; padding: 0; }} 
                svg {{ background: #f5f5dc !important; }} 
            ` }});
            
            // Wait a moment for svg animations to finish unfolding
            await new Promise(r => setTimeout(r, 2000));
            
            // Crop the SVG to exactly fit the Mind Map drawing
            const printBox = await page.evaluate(() => {{
                const svg = document.querySelector('svg');
                const g = document.querySelector('svg > g');
                if (!g) return {{ width: 1920, height: 1080 }};
                
                // Clone the SVG to kill Markmap's ResizeObserver which fights our changes
                const clone = svg.cloneNode(true);
                document.body.innerHTML = '';
                document.body.appendChild(clone);
                document.body.style.margin = '0';
                document.body.style.padding = '0';
                
                const bbox = clone.querySelector('svg > g').getBBox();
                // Add margins around the edges
                const padding = 60;
                const newWidth = Math.ceil(bbox.width) + padding * 2;
                const newHeight = Math.ceil(bbox.height) + padding * 2;
                const newX = Math.floor(bbox.x) - padding;
                const newY = Math.floor(bbox.y) - padding;
                
                // Force the cloned SVG into these dimensions
                clone.style.width = newWidth + 'px';
                clone.style.height = newHeight + 'px';
                clone.setAttribute('viewBox', `${{newX}} ${{newY}} ${{newWidth}} ${{newHeight}}`);
                
                return {{ width: newWidth, height: newHeight }};
            }});
            
            // Print PDF strictly to the matched dimension
            await page.pdf({{
                path: '{pdf_path}',
                width: printBox.width + 'px',
                height: printBox.height + 'px',
                printBackground: true,
                pageRanges: '1'
            }});
            
            await browser.close();
        }})();
"""
print(js_content)

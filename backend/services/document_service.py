import os
import subprocess
import time

def generate_mindmap_document(book_title: str, markdown_content: str) -> str:
    """
    Saves the markdown to a file, uses markmap-cli to generate an interactive HTML,
    injects a floating export toolbar (PDF, XMind, MindManager) into the HTML,
    executes Puppeteer to create a bold, highly readable PDF, and saves all files.
    Returns the local path/URL to the interactive HTML.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    static_dir = os.path.join(base_dir, "static")
    os.makedirs(static_dir, exist_ok=True)
    
    timestamp = int(time.time())
    safe_title = book_title.replace(" ", "_").replace("/", "_")
    
    md_filename = f"mindmap_{safe_title}_{timestamp}.md"
    html_filename = f"mindmap_{safe_title}_{timestamp}.html"
    html_temp_filename = f"mindmap_{safe_title}_{timestamp}_temp.html"
    pdf_filename = f"mindmap_{safe_title}_{timestamp}.pdf"
    jpg_filename = f"mindmap_{safe_title}_{timestamp}.jpg"
    
    md_path = os.path.join(static_dir, md_filename)
    html_path = os.path.join(static_dir, html_filename)
    html_temp_path = os.path.join(static_dir, html_temp_filename)
    pdf_path = os.path.join(static_dir, pdf_filename)
    jpg_path = os.path.join(static_dir, jpg_filename)
    
    # 1. Save Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    try:
        # 2. Convert MD to HTML using markmap to a TEMP file
        subprocess.run(
            ["npx", "markmap-cli", md_path, "-o", html_temp_path],
            check=True,
            cwd=base_dir,
            capture_output=True
        )
        
        # 3. Create a quick Puppeteer script to convert HTML to PDF & JPG
        js_script_path = os.path.join(static_dir, f"render_{timestamp}.js")
        js_content = f"""
        const puppeteer = require('puppeteer');
        (async () => {{
            console.log("STEP 1: Launching Chrome");
            const browser = await puppeteer.launch({{ args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--single-process', '--no-zygote', '--disable-software-rasterizer'] }});
            console.log("STEP 2: Creating new page");
            const page = await browser.newPage();
            
            console.log("STEP 3: Setting viewport");
            await page.setViewport({{ width: 1587, height: 1122, deviceScaleFactor: 3 }});
            
            console.log("STEP 4: Loading HTML file from file://{html_temp_path}");
            await page.goto('file://{html_temp_path}', {{ waitUntil: 'networkidle0' }});
            
            console.log("STEP 5: Injecting SVG custom styles for JPG");
            await page.addStyleTag({{ content: `
                body {{ background: #0f172a !important; margin: 0; padding: 0; }} 
                svg {{ background: #0f172a !important; }} 
                svg text, foreignObject div, foreignObject span, foreignObject p {{ 
                    color: #f8fafc !important; 
                    fill: #f8fafc !important; 
                }} 
            ` }});
            
            console.log("STEP 6: Waiting 2s for anims");
            await new Promise(r => setTimeout(r, 2000));
            
            console.log("STEP 7: Generating screenshot path {jpg_path}");
            await page.screenshot({{
                path: '{jpg_path}',
                type: 'jpeg',
                quality: 100,
                fullPage: true
            }});
            
            console.log("STEP 8: Injecting custom styles for PDF");
            await page.addStyleTag({{ content: `
                body {{ background: #ffffff !important; }} 
                svg {{ background: #ffffff !important; }} 
                svg text, foreignObject div, foreignObject span, foreignObject p {{ 
                    color: #4b5563 !important; 
                    fill: #4b5563 !important; 
                }} 
            ` }});
            
            console.log("STEP 9: Waiting 500ms");
            await new Promise(r => setTimeout(r, 500));

            console.log("STEP 10: Printing PDF {pdf_path}");
            await page.pdf({{
                path: '{pdf_path}',
                format: 'A3',
                landscape: true,
                printBackground: true,
                margin: {{ top: '1cm', right: '1cm', bottom: '1cm', left: '1cm' }}
            }});
            
            console.log("STEP 11: Closing browser");
            await browser.close();
            console.log("STEP 12: SUCCESS");
        }})();
        """
        
        with open(js_script_path, "w", encoding="utf-8") as f:
            f.write(js_content)
            
        # Run node script for PDF & JPG
        result = subprocess.run(
            ["node", js_script_path],
            check=False,
            cwd=base_dir,
            capture_output=True
        )
        
        stdout_str = result.stdout.decode('utf-8', errors='replace') if result.stdout else ""
        if result.returncode != 0 and "STEP 12: SUCCESS" not in stdout_str:
            stderr_str = result.stderr.decode('utf-8', errors='replace') if result.stderr else ""
            raise Exception(f"Node execution failed: {result.returncode}\nSTDOUT: {stdout_str}\nSTDERR: {stderr_str}")
        
        # Cleanup temp JS
        os.remove(js_script_path)
        
        # 4. Inject Export Toolbar into the HTML for the browser
        with open(html_temp_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        toolbar_html = f"""
<div style="position: fixed; top: 20px; right: 20px; z-index: 9999; background: rgba(255,255,255,0.95); padding: 15px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; backdrop-filter: blur(10px); border: 1px solid rgba(0,0,0,0.05); min-width: 220px;">
    <h3 style="margin: 0 0 15px 0; font-size: 16px; color: #1e293b; text-align: center; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px;">💾 导出思维导图</h3>
    <a href="./{jpg_filename}" download style="display: block; margin-bottom: 10px; text-decoration: none; color: white; background: #eab308; padding: 10px 15px; border-radius: 8px; text-align: center; font-size: 14px; font-weight: 600; transition: background 0.2s; box-shadow: 0 2px 4px rgba(234, 179, 8, 0.3);">🖼️ 下载高清长图 (JPG)</a>
    <a href="./{pdf_filename}" download style="display: block; margin-bottom: 10px; text-decoration: none; color: white; background: #3b82f6; padding: 10px 15px; border-radius: 8px; text-align: center; font-size: 14px; font-weight: 600; transition: background 0.2s; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);">📄 下载打印版 (PDF)</a>
    <a href="./{md_filename}" download="mindmap_xmind.md" style="display: block; margin-bottom: 10px; text-decoration: none; color: white; background: #10b981; padding: 10px 15px; border-radius: 8px; text-align: center; font-size: 14px; font-weight: 600; transition: background 0.2s; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);">📊 导出 XMind 格式</a>
    <a href="./{md_filename}" download="mindmap_mindmanager.md" style="display: block; text-decoration: none; color: white; background: #f59e0b; padding: 10px 15px; border-radius: 8px; text-align: center; font-size: 14px; font-weight: 600; transition: background 0.2s; box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);">🧠 导出 MindManager</a>
    <p style="margin: 15px 0 0 0; font-size: 12px; color: #64748b; text-align: center; line-height: 1.4;">提示：XMind 和 MindManager<br>均原生支持直接导入 Markdown</p>
</div>
        """
        html_content = html_content.replace('</body>', toolbar_html + '</body>')
        
        # Also inject CSS to make the HTML view darker/clearer naturally
        css_inject = """
<style>
    body { background: #0f172a !important; }
    svg { background: #0f172a !important; }
    svg text, foreignObject div, foreignObject span, foreignObject p { 
        color: #f8fafc !important; 
        fill: #f8fafc !important; 
    } 
</style>
</head>
"""
        html_content = html_content.replace('</head>', css_inject)

        # Write finally to the real html_path
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Cleanup temp HTML
        if os.path.exists(html_temp_path):
            os.remove(html_temp_path)

        # Return the rich HTML page
        return f"/static/{html_filename}"
        
    except subprocess.CalledProcessError as e:
        stdout_str = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
        stderr_str = e.stderr.decode('utf-8', errors='replace') if e.stderr else ""
        print(f"Node execution failed with status {e.returncode}.\nSTDOUT: {stdout_str}\nSTDERR: {stderr_str}\nEXCEPTION: {e}")
        txt_path = os.path.join(static_dir, f"mindmap_{safe_title}_fallback.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return f"/static/mindmap_{safe_title}_fallback.txt"
        
    except Exception as e:
        print(f"Error generating Mind Map document: {e}")
        txt_path = os.path.join(static_dir, f"mindmap_{safe_title}_fallback.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return f"/static/mindmap_{safe_title}_fallback.txt"

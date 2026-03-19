import sys
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.on("console", lambda msg: print(f"Console: {msg.text}"))
    page.on("pageerror", lambda err: print(f"Page Error: {err}"))
    
    html = """
    <html>
    <head><script src="https://3Dmol.org/build/3Dmol-min.js"></script></head>
    <body>
    <div id="viewer" style="width: 400px; height: 400px;"></div>
    <script>
    setTimeout(() => {
        try {
            const viewer = window.$3Dmol.createViewer("viewer", { backgroundColor: "black" });
            const htmlError = "<!DOCTYPE html><html><head></head><body>Error</body></html>";
            const jsonError = '{"detail": "Not found"}';
            
            viewer.addModel(htmlError, "pdb");
            viewer.setStyle({}, { cartoon: {} });
            viewer.render();
            console.log("Success with html data");
        } catch (e) {
            console.error("Test Error HTML: " + e.message);
        }

        try {
            const viewer2 = window.$3Dmol.createViewer("viewer", { backgroundColor: "black" });
            const jsonError = '{"detail": "Not found"}';
            
            viewer2.addModel(jsonError, "pdbqt");
            viewer2.setStyle({}, { cartoon: {} });
            viewer2.render();
            console.log("Success with JSON data");
        } catch (e) {
            console.error("Test Error JSON: " + e.message);
        }
    }, 1000);
    </script>
    </body>
    </html>
    """
    page.set_content(html)
    page.wait_for_timeout(2000)
    browser.close()

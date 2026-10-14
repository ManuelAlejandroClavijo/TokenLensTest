"""Optional Playwright e2e against a running server. Does not call Claude or read settings."""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = os.getenv("TOKENLENS_TEST_URL", "http://127.0.0.1:4318")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1120})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(URL, wait_until="domcontentloaded")
        page.get_by_role("button", name="Demo", exact=True).click()
        page.get_by_text("Estás explorando el piloto.").wait_for()
        page.wait_for_function("document.querySelectorAll('tbody tr').length > 0")
        page.screenshot(
            path=str(Path(__file__).parents[1] / "docs" / "dashboard.png"),
            full_page=True,
        )
        page.locator("tbody tr").first.click()
        page.get_by_role("dialog", name="Detalle de solicitud").wait_for()
        page.get_by_role("button", name="Cerrar", exact=True).click()
        page.get_by_role("button", name="Sesiones", exact=False).first.click()
        page.get_by_role("button", name="Asignar HU / fase").first.click()
        page.get_by_label("Historia de usuario").fill("7777")
        page.get_by_label("Alcance").select_option("session")
        page.get_by_role("button", name="Guardar atribución").click()
        page.get_by_text("Atribución guardada y auditada.").wait_for()
        page.get_by_role("button", name="Diagnósticos", exact=True).click()
        page.get_by_text("7777", exact=True).first.wait_for()
        page.get_by_role("button", name="Nueva conciliación").click()
        for label in [
            "Entrada no cacheada",
            "Salida",
            "Lectura de caché",
            "Escritura de caché",
        ]:
            page.get_by_label(label, exact=True).fill("0")
        page.get_by_role("button", name="Comparar y guardar").click()
        page.get_by_text("Diferencias: observado − referencia").wait_for()
        page.get_by_role("button", name="Cerrar", exact=True).click()
        page.get_by_role("button", name="Vista general", exact=True).click()
        with page.expect_download() as downloaded:
            page.get_by_role("link", name="Exportar CSV").click()
        assert downloaded.value.suggested_filename == "tokenlens-demo.csv"
        page.get_by_role("button", name="Datos reales", exact=True).click()
        page.get_by_text("Captura local · solo metadatos").wait_for()
        page.get_by_role("button", name="Configuración", exact=True).click()
        page.get_by_role("dialog", name="Conecta tu máquina").wait_for()
        page.get_by_role("button", name="Cerrar", exact=True).click()
        page.get_by_role("button", name="Demo", exact=True).click()
        page.wait_for_function("document.querySelectorAll('tbody tr').length > 0")
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(
            path=str(Path(__file__).parents[1] / "docs" / "mobile.png"), full_page=True
        )
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth"
        )
        assert not errors, errors
        browser.close()
        print(
            "E2E OK: demo, detalle, atribución, auditoría, conciliación, CSV, datos reales, configuración y móvil."
        )


if __name__ == "__main__":
    main()

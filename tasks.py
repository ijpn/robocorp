from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.

    By Yasuke Software (Ivan José Peraza Navarro) 2024.03.12

    """

    browser.configure(
        slowmo=200
        )
    open_robot_order_website()
    download_orders_file()
    fill_form_with_csv_data()
    archive_receipts()
    clean_folders()


def open_robot_order_website():
    """Abrir la página de pedidos y hacer click en el primer modal"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click('text=OK')

def download_orders_file():
    """Descargar archivo CSV de pedidos desde la página de Robot Sparebin Industries
       y permitir sobre escribir el archivo cada vez que es descargado """
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)


def complete_and_send_robot_data(order):
    """ Completa y envía el formulario del robot """
    page = browser.page()
    head_names = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }
    head_number = order["Head"]
    page.select_option("#head", head_names.get(head_number))
    page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(order["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            order_new_bot()
            close_modal()
            break

def store_receipt_as_pdf(order_number):
    """ Almacenar cada pedido como un PDF """
    page = browser.page()
    order_receipt = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/robot{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt, pdf_path)
    return pdf_path

def fill_form_with_csv_data():
    """Read data from csv and fill in the robot order form"""
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("orders.csv")
    for order in robot_orders:
        complete_and_send_robot_data(order)
          
def screenshot_robot(order_number):
    """Captura de pantalla del robot"""
    page = browser.page()
    screenshot_path = "output/screenshots/imagen{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """Inserta la captura de pantalla y guarda la información en la ruta"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
                                   source_path=pdf_path, 
                                   output_path=pdf_path)

def close_modal():
    """ Cerrar modal cuando se van a crear un nuevo robot"""
    page = browser.page()
    page.click('text=OK')

def order_new_bot():
    """ Ordenar un nuevo robot """
    page = browser.page()
    page.click("#order-another")

def archive_receipts():
    """ Archivar todos los documentos PDF en un archivo .ZIP"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/orders.zip")

def clean_folders():
    """ Limpia las carpetas donde se guardan los recibos y las capturas de pantalla.."""
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")
 
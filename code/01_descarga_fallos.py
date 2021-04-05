"""
Software para descargar estados diarios de la corte suprema

    TODO:
        * Ingresar a https://oficinajudicialvirtual.pjud.cl/home/index.php#
        * Cerrar el dialogo
        * Al Apretar "Otros Servicios", escoger "Consulta de Causas"
        * En consulta de causas/ consulta unificada,
        * Seleccionar "Busqueda por Fecha"
        * Luego elegir:
            + Fecha desde: elegida por comando
            + Fecha hasta: elegida por comando
            + Competencia: Corte Suprema
            + Tipo Busqueda: Recurso Corte Suprema
        * Esperar que se cargue
        * Para cada resultado:
            + Seleccionar la "lupa", esperar a que modal se abra
            + Obtener direccion (url) para descargar todos los documentos guardando el rol
            + Cerrar modal

        Filtrar (no descargar) cualquier fallo que contenga la palabra "ISAPRE" en su caratula


Fecha:
    inicio  07-02-2021 16:00 -> 
            06-03-2021 11:40 -> 

"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import wget_custom as wget
from datetime import datetime, timedelta
import time 
import os
import utils
from fallo_data import Fallo
from enum import Enum
import urllib.parse
import sys

class MONTH(Enum):
    Enero = 1
    Febrero = 2
    Marzo = 3
    Abril = 4
    Mayo = 5
    Junio = 6
    Julio = 7
    Agosto = 8
    Septiembre = 9
    Octubre = 10
    Noviembre = 11
    Diciembre = 12

    @classmethod
    def findValueByName(cls, nameToFind):
        for name, member in cls.__members__.items():
            if name == nameToFind:
                return member.value

    @classmethod
    def findNameByValue(cls, valueToFind):
        for name, member in cls.__members__.items():
            if member.value == valueToFind:
                return name

url_web = "https://oficinajudicialvirtual.pjud.cl/home/index.php#"

ISAPRES_ARRAY = ["ISAPRE", "NUEVA MÁS VIDA", "CONSALUD", "CRUZ BLANCA", "COLMENA GOLDEN CROSS", "VIDA TRES", "BANMEDICA"]

# TODO: add debug print
SUBSTRACT_DAYS_FROM_TODAY = 1
downloadFolder = "downloads"
fileFolder = "files"

def load_page(driver):
    if not os.path.exists(downloadFolder):
        os.mkdir(downloadFolder)
        print("Directory " + downloadFolder + " Created ")
    else:
        print("Directory " + downloadFolder + " already exists")

    driver.get(url_web)
    print(driver.title)

    wait = WebDriverWait(driver, 10)

    if driver.title == "404 Not Found":
        print("Page not found")
        return None

    print("Page found")
    # time.sleep(4)
    # try:
    #     close_button_modal = driver.find_element_by_id("close_modal")
    #     if close_button_modal is not None:
    #         close_button_modal.click()
    # except exceptions.NoSuchElementException:
    #     print("close button modal not found")

    ############## Apretar "Otros Servicios", escoger "Consulta de Causas" #############
    dropdown_3 = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "myDropdown3"))
                )
    # dropdown_3 = driver.find_element_by_id("myDropdown3")
    dropdown_3_children = dropdown_3.find_elements_by_xpath(".//*")

    for element in dropdown_3_children:
        if element.get_attribute("tabindex") == '8':
            driver.execute_script(element.get_attribute("onclick"));
            break

    # time.sleep(3)

    ############## ESCOGER tab Busqueda por Fecha #############
    nuevo_colapsador = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "nuevocolapsador"))
                )
    # nuevo_colapsador = driver.find_element_by_id("nuevocolapsador");
    tab = nuevo_colapsador.find_element_by_xpath('//a[@href="#BusFecha"]')
    tab.click()
    time.sleep(1)
    return True

def get_date():
    ############## Pedir fecha a usuario ##############
    ##TODO: Revisar formato de hora ingresada
    currentDT = datetime.now()
    date2check = currentDT - timedelta(days=SUBSTRACT_DAYS_FROM_TODAY)
    date_name = date2check.strftime("%Y_%m_%d")

    input_text = "Date to check: " + date_name + "\n"
    input_text += "(1) OK\n"
    input_text += "(2) Enter other Date\n"
    input_index = input(input_text)

    isInputOk = True
    if input_index == "1":
        pass
    elif input_index == "2":
        input_text = "type date in format: %Y_%m_%d -> ex: 2019_05_19\n"
        input_date = input(input_text)
        try:
            date2check = datetime.strptime(input_date, "%Y_%m_%d")
            date_name = input_date
        except ValueError as ex:
            print(str(ex))
            isInputOk = False
    else:
        print("input " + input_index + " was not an option")
        print("Closing the program")
        isInputOk = False


    if isInputOk:
        print("Date to check: " + date_name)
        return date_name
    else:
        return ""

def navegate_to_date(driver, date_name):
    desde_date = date_name
    hasta_date = date_name

    ############## ESCOGER FECHA DESDE #############
    # desde_input = driver.find_element_by_id("fecDesde");
    desde_input = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "fecDesde"))
                )
    desde_input.click()

    ## split desde dates
    desde_date_array = desde_date.split("_")

    ## Seleccionar datepicker
    datepicker = driver.find_element_by_id("ui-datepicker-div")

    ## Seleccionar año
    year_selector = datepicker.find_element_by_xpath("//select[@class='ui-datepicker-year']")
    all_options = year_selector.find_elements_by_tag_name("option")
    for option in all_options:
        # print("Value is: %s" % option.get_attribute("value"))
        if option.get_attribute("value") == desde_date_array[0]:
            option.click()
            break

    ## Seleccionar mes: revisar que mes esta seleccionado, revisar que mes se necesita y calcular cuantos movimentos para adelante o atras se tienen que hacer
    month_selected_element = datepicker.find_element_by_xpath("//span[@class='ui-datepicker-month']")

    #print("Mes seleccionado: " + month_selected_element.text + " -> " + str(MONTH.findValueByName(month_selected_element.text)))
    #print("Mes elegido: " + MONTH.findNameByValue(int(desde_date_array[1])) + " -> " + desde_date_array[1])

    month_selected_value = MONTH.findValueByName(month_selected_element.text)
    month_chosen_value = int(desde_date_array[1])

    month_to_move = month_chosen_value - month_selected_value
    #print("month_to_move: " + str(month_to_move))

    if month_to_move > 0:
        for _ in range(month_to_move):
            more_month_element = datepicker.find_element_by_xpath("//span[@class='ui-icon ui-icon-circle-triangle-e']")
            more_month_element.click()
            time.sleep(0.2)

    elif month_to_move < 0:
        for _ in range(abs(month_to_move)):
            less_month_element = datepicker.find_element_by_xpath("//span[@class='ui-icon ui-icon-circle-triangle-w']")
            less_month_element.click()
            time.sleep(0.2)

    ## Seleccionar dia:
    day_calendar_picker_element = datepicker.find_element_by_xpath("//table[@class='ui-datepicker-calendar']")
    day_to_select = day_calendar_picker_element.find_element_by_xpath('//a[contains(text(), "' + str(int(desde_date_array[2])) + '")]')
    day_to_select.click()

    ############## ESCOGER FECHA hasta #############

    # hasta_input = driver.find_element_by_id("fecHasta");
    hasta_input = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "fecHasta"))
                )
    hasta_input.click()

    ## split desde dates
    hasta_date_array = hasta_date.split("_")

    ## Seleccionar datepicker
    datepicker = driver.find_element_by_id("ui-datepicker-div")

    ## Seleccionar año
    year_selector = datepicker.find_element_by_xpath("//select[@class='ui-datepicker-year']")
    all_options = year_selector.find_elements_by_tag_name("option")
    for option in all_options:
        # print("Value is: %s" % option.get_attribute("value"))
        if option.get_attribute("value") == hasta_date_array[0]:
            option.click()
            break;

    ## Seleccionar mes: revisar que mes esta seleccionado, revisar que mes se necesita y calcular cuantos movimentos para adelante o atras se tienen que hacer
    month_selected_element = datepicker.find_element_by_xpath("//span[@class='ui-datepicker-month']")

    #print("Mes seleccionado: " + month_selected_element.text + " -> " + str(MONTH.findValueByName(month_selected_element.text)))
    #print("Mes elegido: " + MONTH.findNameByValue(int(hasta_date_array[1])) + " -> " + hasta_date_array[1])

    month_selected_value = MONTH.findValueByName(month_selected_element.text)
    month_chosen_value = int(hasta_date_array[1])

    month_to_move = month_chosen_value - month_selected_value
    #print("month_to_move: " + str(month_to_move))

    if month_to_move > 0:
        for _ in range(month_to_move):
            more_month_element = datepicker.find_element_by_xpath("//span[@class='ui-icon ui-icon-circle-triangle-e']")
            more_month_element.click()
            time.sleep(0.2)

    elif month_to_move < 0:
        for _ in range(abs(month_to_move)):
            less_month_element = datepicker.find_element_by_xpath("//span[@class='ui-icon ui-icon-circle-triangle-w']")
            less_month_element.click()
            time.sleep(0.2)

    ## Seleccionar dia:
    day_calendar_picker_element = datepicker.find_element_by_xpath("//table[@class='ui-datepicker-calendar']")
    day_to_select = day_calendar_picker_element.find_element_by_xpath('//a[contains(text(), "' + str(int(hasta_date_array[2])) + '")]')
    day_to_select.click()


    ############## ESCOGER Competencia: Corte Suprema #############
    competencia_selector = driver.find_element_by_id("fecCompetencia")
    all_options = competencia_selector.find_elements_by_tag_name("option")
    for option in all_options:
        # print("Value is: %s" % option.get_attribute("value"))
        if option.get_attribute("value") == "Corte Suprema":
            option.click()
            break;


    ############## Apretar boton buscar #############
    # search_button = driver.find_element_by_id("btnConConsultaFec")
    search_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "btnConConsultaFec"))
                )
    search_button.click()
    time.sleep(2)

def get_fallos_list(driver):
    # TODO: 
    #       * Filtrar (no descargar) cualquier fallo que contenga la palabra "ISAPRE" en su caratula
    #       * Calcular numero de fallos en total

    hasMorePages = True
    n_fallos_total = 0
    fallo_list_total = []
    n_page = 1

    # TODO: Navegar por las siguientes paginas
    while hasMorePages:
        next_button = None
        fallo_list = []

        ############## Encontrar los fallos de la página #############
        result_table = driver.find_element_by_id("verDetalleFecha")
        table_rows_elements = result_table.find_elements_by_tag_name("tr")

        i = 0
        n_fallos = len(table_rows_elements) - 1
        n_fallos_total += n_fallos

        print("fallos en pagina " + str(n_page) + ": " + str(n_fallos))

        for row in table_rows_elements:
            if i < n_fallos:
                row_elements = row.find_elements_by_tag_name("td")
                lupa_element = row_elements[0].find_element_by_tag_name("a")
                rol_element = row_elements[1]
                caratulado_element = row_elements[3]
                # print("lupa : " + lupa_element.get_attribute("onclick"))
                # print("rol : " + str(rol_element.text))
                if caratulado_element.text != None and caratulado_element.text != "" and \
                    all(isapre not in caratulado_element.text for isapre in ISAPRES_ARRAY):
                    print("Caratulado agregado: " + caratulado_element.text)
                    fallo_list.append(Fallo(rol_element.text, caratulado_element.text, lupa_element.get_attribute("onclick")))
        
            i += 1

        for fallo in fallo_list:
        ########### Seleccionar la "lupa", esperar a que modal se abra
        ## TODO: modal no abrió, seguir con el siguiente
        ## TODO: Contabilizar urls encontradas vs fallos encontrados
            driver.execute_script(fallo.lupaScript)

            #### Seleccionar modal y tabla       
            try:
                modal_detalle_fallo = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "modalDetalleSuprema"))
                )

                table_modal = WebDriverWait(modal_detalle_fallo, 5).until(
                    EC.presence_of_element_located((By.ID, "movimientosSup"))
                ).find_element_by_tag_name("table")

                table_modal_rows = table_modal.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
            except exceptions.TimeoutException:
                print("Timed out waiting for modal_detalle_fallo or table_modal to load")
                error_modal_close_button = driver.find_element_by_xpath("//button[@class='confim']")
                error_modal_close_button.click()
                continue

            # print("table_modal_rows : " + str(len(table_modal_rows)))

            ##### obtener url de descarga

            n_doc = len(table_modal_rows)
            n_element = 0
            for row_element in table_modal_rows:
                try:
                    n_element += 1
                    doc_download_url = ""

                    download_doc_element_1 = row_element.find_element_by_tag_name("form")
                    doc_download_url = doc_download_url + download_doc_element_1.get_attribute("action")

                    download_doc_element_2 = row_element.find_element_by_tag_name("input")
                    doc_download_url = doc_download_url + "?valorFile=" + download_doc_element_2.get_attribute("value")
                    # print("doc_download_url: " + doc_download_url)
                    fallo.add_doc_download_url(doc_download_url)
                except exceptions.NoSuchElementException as e:
                    print("element n° " + str(n_element) + " no fue encontrado")
                    print(str(e))
            
            ### cerrar modal
            try:
                modal_close_button = WebDriverWait(modal_detalle_fallo, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-default']"))
                )
                modal_close_button.click()
            except exceptions.TimeoutException:
                print("Timed out waiting for modal_close_button to load")
                continue
        
        fallo_list_total.extend(fallo_list) 

        ## Encontrar next boton
        next_button = None

        try:
            next_button = result_table.find_element_by_id("sigId")
            next_button.click()
            n_page += 1
            time.sleep(2)
        except exceptions.NoSuchElementException:
            print("No more pages")
            hasMorePages = False

    for fallo in fallo_list_total:
        print(str(fallo))
    
    print("\nLos fallos encontrados son: " + str(n_fallos_total))
    print("\nLos fallos filtrados son: " + str(len(fallo_list_total)))
        
    return fallo_list_total

def download_fallos(date_name, fallo_list):
    print("Init to Download")
    print("Downloading " + str(len(fallo_list)) + " files")

    folderName = os.path.join(downloadFolder, date_name)
    fileFolderName = os.path.join(folderName, fileFolder)

    if not os.path.exists(folderName):
        os.mkdir(folderName)
        print("Directory " + folderName + " Created ")
    else:
        print("Directory " + folderName + " already exists")

    if not os.path.exists(fileFolderName):
        os.mkdir(fileFolderName)
        print("Directory " + fileFolderName + " Created ")
    else:
        print("Directory " + fileFolderName + " already exists")


    for fallo in fallo_list:
        for i in range(len(fallo.doc_download_url_list)):
            url_fallo = fallo.doc_download_url_list[i] 
            if url_fallo != None:
                file_path = os.path.join(
                    fileFolderName, date_name + "&" + fallo.rol + "&" + str(i+1))
                print("\n" + file_path)
                # file_extension = utils.get_extension(url_fallo)
                file_complete_path = file_path + ".pdf"

                if os.path.exists(file_complete_path):
                    os.remove(file_complete_path)
                
                file_name = wget.download(url_fallo, file_complete_path)
                # if(file_extension != "pdf"):
                #     utils.convert_to_pdf(file_name)    

def close(driver):
    driver.close()
    sys.exit()

if __name__ == "__main__":
    driver = webdriver.Chrome("./chromedriver")
    if load_page(driver) == None:
        print("No se pudo cargar la pagina. Revisar url e intentar nuevamente")
        close(driver)

    date_name = get_date()
    if date_name == "":
        print("Error al obterner fecha del usuario. Intente nuavemente")
        close(driver)

    navegate_to_date(driver, date_name)

    print("\nObteniendo Lista de fallos")
    fallos_list = get_fallos_list(driver)
    driver.close()

    if fallos_list != None and len(fallos_list) > 0:
        download_fallos(date_name, fallos_list)
        print("\nDescarga Terminada")
    else:
        print("Error al tratar de obtener la lista de fallos")

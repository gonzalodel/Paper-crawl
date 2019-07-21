from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy import Selector
#import scrapy
import time
import pandas as pd
import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
import PyPDF2 as pdf

##scihub project
from scihub import SciHub

def driver_open(url):
    # iniciando pagina science direct
    driver = webdriver.Chrome()
    driver.get(url)
    return driver
    pass

def page_click(driver,boton):
    #abriendo formulario
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, boton))
        )
        time.sleep(4)
        pass

    finally:
        driver.find_element_by_xpath(boton).click()
        pass
    return driver
    
    pass

def complementado_formulario(driver,formulario):
    #rellenando formulario
    
    element=driver.find_element_by_id("qs")
    element.send_keys(formulario['terminos_buqueda'])
    
    element=driver.find_element_by_id("date")
    element.send_keys(formulario['años'])
    #articles types
    articulo='//*[@id="adv-search-form"]/div/div/div[2]/div/fieldset/div[4]/div/div/fieldset/div/div[2]/div/ul[1]/li[1]/div/label/span[1]'
    element=driver.find_element_by_xpath(articulo).click()

    ##accediendo
    accediendo='//*[@id="adv-search-form"]/div/div/div[5]/div/div[2]/button/span'
    element=driver.find_element_by_xpath(accediendo).click()

    #cerrando ventana emergente
    element=driver.find_element_by_xpath("/html/body/div[3]/div/div/div/button").click()
    
    return driver
    pass

def procesar_pagina(resultados,datos):
    
        ##insertando datos al dataframe
    
    count=0
    for resultado in resultados:
        count=count+1
         #tipo articulo
        tipo_articulo=resultado.xpath('.//span[@class="article-type u-clr-grey8"]/text()').get()
        
        #nombre articulo
        nombre_articulo=resultado.xpath('string(.//h2/a[1])').get()    
        
        #revista_publicacion
        revista=resultado.css("a.subtype-srctitle-link>span::text").get()
        
        #link_revista
        url_base="https://www.sciencedirect.com"
        link_revista=url_base+resultado.css("a.subtype-srctitle-link::attr(href)").get()
        
        #AÑO-MES publicacion
        fecha_publicacion=resultado.css("div>ol.SubType>li>span::text").getall()[3]
        
        #AUTORES
        #autores=resultado.css("ol.Authors>li>span.author::text").getall()
        autor=resultado.xpath("string(.//ol[2])").get()
        autor=autor.strip()
        autor=autor[0:len(autor)-1]
        autores=autor
        
        #link_articulo
        url=resultado.xpath('.//h2/a/@href').get()
        
        ##copiando a dataframe
        datos=datos.append({'tipo_articulo':tipo_articulo,
                            'nombre_articulo':nombre_articulo,
                            'revista':revista,
                            'fecha_publicacion':fecha_publicacion,
                            'link_revista':link_revista,
                            'autores':autores,
                            'link_articulo':url_base+url},ignore_index=True)
        
        
        pass
        return datos
    pass

def valores_formulario():
    formulario={
    'terminos_buqueda':'',
    'años':'',
    'numero_paginas a scrapear':''
        
    }
    for key in formulario:
        valor=input("ingrese {} : ".format(key))
        formulario[key]=valor
        pass
    return formulario
    pass




def principal(terminos_busqueda='machine learning',year='2016',page='5'):
    ##datos de busqueda
    formulario={}
    formulario={'terminos_buqueda':terminos_busqueda,
                'años':year,
                'numero_paginas a scrapear':page
    }

    #Abriendo web y obteniendo web source
    url="https://www.sciencedirect.com/search/advanced"
    driver=driver_open(url)
    boton='//*[@id="adv-search-form"]/div/div/div[2]/div/fieldset/div[4]/div[1]/div[2]/button'
    driver=page_click(driver,boton)
    driver=complementado_formulario(driver,formulario)

    ##data formulario
    datos = pd.DataFrame(columns=['tipo_articulo','nombre_articulo', 'revista','fecha_publicacion','link_revista','autores','link_articulo'])

    contador_paginas=1
    url_base="https://www.sciencedirect.com"
    while contador_paginas<=int(formulario['numero_paginas a scrapear']):

        
        time.sleep(5)
        sel= Selector(text=driver.page_source)
        ##primera pagina
        
        resultados=sel.xpath('.//div[@class="result-item-content"]')

        if resultados:
            
            #next_page
            next_page=sel.css("div.stick-to-right li.pagination-link a::attr(href)").extract()[-1]
            url_base="https://www.sciencedirect.com"
            next_page=url_base+next_page 
            
            print("N° DE PAPERS EN PAGINA {} :{}".format(contador_paginas,len(resultados)))
            datos=procesar_pagina(resultados,datos)
            yield datos
            contador_paginas=contador_paginas+1
            driver=driver_open(next_page)
        else:
            print("NO SE ENCONTRARON RESULTADOS PARA LA BUSQUEDA")
            break
            pass
        pass
        
        pass

    datos.to_excel("datos_papers.xlsx",sheet_name='datos')
    
    return datos

    ##a excel
    




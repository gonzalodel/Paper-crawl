from tkinter import *
from tkinter import messagebox as MessageBox
from pandastable import Table, TableModel
import pandas as pd 
import os
from scihub import SciHub
from lib import crawl_scidirect,download_paper
 
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

datos = pd.DataFrame(columns=['tipo_articulo','nombre_articulo', 'revista','fecha_publicacion','link_revista','autores','link_articulo'])


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

def procesar_pagina(resultados):
    
        ##insertando datos al dataframe
    global datos
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
        #return datos
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



raiz=Tk()
terminos_busqueda=''


def pandas_interface():
    
    df=pd.read_excel("datos_papers.xlsx",sheet_name='datos')
    top=Toplevel()
    pt = Table(top, dataframe=df,
                                showtoolbar=True, showstatusbar=True)
    pt.show()  
    
    pass

def callback():
    print ("Buscando Papers!")
mystring = StringVar()

def entrada():
    terminos_busqueda=cuadroK.get()
    year=cuadroA.get()
    page=cuadroP.get()

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
    global datos
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
            procesar_pagina(resultados)
            
            contador_paginas=contador_paginas+1
            driver=driver_open(next_page)
        else:
            print("NO SE ENCONTRARON RESULTADOS PARA LA BUSQUEDA")
            break
            pass
        pass
        
        pass

    datos.to_excel("datos_papers.xlsx",sheet_name='datos',index=False)
    
    pass

def descargar_paper():
    ruta=os.getcwd()
    ruta=os.path.join(ruta,'paper')
    ruta_papers=download_paper.carpeta_paper(ruta,cuadroK.get())
    print(ruta_papers)
    df=pd.read_excel("datos_papers.xlsx",sheet_name='datos')

    for index, row in df.iterrows():
        sh = SciHub()
        print('Buscando paper #{} llamado: {}'.format(index+1,row['nombre_articulo']))
        paper_name=str(index+1)+'.'+row['nombre_articulo']+'.pdf'
        paper=os.path.join(ruta_papers,paper_name)
    try:
        result = sh.download(row['link_articulo'], path=paper)
        pass
    except:
        pass
    
    pass
    

#def dataframe():
 #   toplevel = Toplevel()
  #  toplevel.title('Datos de Estadística')
   # toplevel.focus_set()
def testVal(inStr,acttyp):
    if acttyp == '1': #insert
        if not inStr.isdigit():
            return False
    return True


raiz.title("Descargador de Papers")
raiz.iconbitmap(default=".\\lib\\img\\iconoP.ico")
raiz.resizable(0,1) #Largo y Ancho
#raiz.geometry("675x450")
#raiz.config(bg="brown")
miFrame=Frame(raiz,width="600",height="370")
miFrame.config(bg="brown")
#miFrame.config()
#miFrame.pack(side="bottom", anchor="n")
miFrame.pack(fill="y", expand="True")
miFrame.config(relief="groove")
miFrame.config(cursor="hand2")
miFrame.config(bd=5)
miImagen=PhotoImage(file=".\\lib\\img\\Titulo.png")
Label(miFrame, image=miImagen).place(x=220,y=5)
L0=Label(miFrame, text="Bot Descargador de Papers", fg="white",font=("Comic Sans MS",20))
L0.place(x=150,y=227)
L0.config(bg="brown")
tama=270
L1=Label(miFrame, text="Inserte sus Keywords", fg="black", font=("Comic Sans MS",12))
L1.place(x=100,y=tama)
L1.config(bg="brown")
L2=Label(miFrame, text="Inserte el año(s)", fg="black", font=("Comic Sans MS",12))
L2.place(x=100,y=tama+30)
L2.config(bg="brown")
cuadroK=Entry(miFrame)
cuadroK.place(x=350,y=tama)
cuadroA=Entry(miFrame)
cuadroA.place(x=350,y=tama+30)
L3=Label(miFrame, text="Número de páginas a buscar", fg="black", font=("Comic Sans MS",12))
L3.place(x=100,y=tama+60)
L3.config(bg="brown")
cuadroP=Entry(miFrame, validate="key")
cuadroP['validatecommand'] = (cuadroP.register(testVal),'%P','%d')
cuadroP.place(x=350,y=tama+60)

#botonE=Button(miFrame, text= "Buscar")
#botonE.pack(miFrame)
#botton.place(x=275,y=330)
mystring=StringVar()
b = Button(raiz, text="Buscar", command=entrada, font=("Comic Sans MS",16))
b.pack()

d = Button(raiz, text="Mostrar Data", command=pandas_interface, font=("Comic Sans MS",14))
d.pack(side="left")

h = Button(raiz, text="Descargar Papers", command=descargar_paper, font=("Comic Sans MS",14))
h.pack(side="right")

raiz.mainloop()
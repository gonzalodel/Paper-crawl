import pandas as pd 
##scihub project
from scihub import SciHub
import os


def carpeta_paper(ruta_base,palabra_clave):
    #creando carpeta para almacenar papers
    ruta_papers=os.path.join(ruta_base,palabra_clave)

    if os.path.isdir(ruta_papers)==False:
        os.mkdir(os.path.join(ruta_base,palabra_clave))
        print("ruta creada")
        return ruta_papers
    else:
        print("ruta ya existe")
        return ruta_papers
        pass

    pass

def descarga_sichub(ruta_papers,df):
    #decargando los papers
    for index, row in df.iterrows():
        sh=SciHub()
        print('Buscando paper #{} llamado: {}'.format(index+1,row['nombre_articulo']))
        paper_name=str(index+1)+'.'+row['nombre_articulo']+'.pdf'
        paper=os.path.join(ruta_papers,paper_name)
        try:
            #sh.download()
            sh.download(row['link_articulo'], path=paper)
            sh.f
            pass
        except Exception as e:
            print(e)
            pass
        
        pass
    pass



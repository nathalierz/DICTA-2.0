class Ponente:
    def __init__(self, nombre='', participaciones=0, puesto='', content='', fecha='' ):
        self.nombre =  nombre
        self.participaciones = participaciones
        self.puesto = puesto
        self.content = content
        self.fecha = fecha
    def get_nombre(self,):
        return self.nombre
    
    def get_participaciones(self,):
        return self.participaciones
    
    def get_puesto(self,):
        return self.puesto
    
    def get_content(self,):
        return self.content
    
    def get_fecha():
        return self.fecha
    
    def __str__(self,):
        cadena = "{0}".format(self.nombre)
        return cadena
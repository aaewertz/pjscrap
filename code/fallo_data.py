
class Fallo():

    def __init__(self, rol, caratulado, lupaScript):
        self.rol = rol
        self.caratulado = caratulado
        self.lupaScript = lupaScript
        self.doc_download_url_list = []

    def add_doc_download_url(self, new_url):
        self.doc_download_url_list.append(new_url)

    def __str__(self):
        text = "Fallo data is:\n"
        text += "\trol: " + self.rol + "\n"
        text += "\tcaratulado: " + self.caratulado + "\n"
        text += "\tlupaScript: " + self.lupaScript + "\n"
        text += "\doc_download_url_list: \n"
        for url in self.doc_download_url_list:
            text += "\t\t" + url + "\n"

        return text
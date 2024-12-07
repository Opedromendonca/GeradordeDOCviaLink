import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from ebooklib import epub

class Main:
    def __init__(self, link, caminho, tipo, titulo):
        self.link = link
        self.caminho = caminho
        self.tipo = tipo
        self.titulo = titulo

class Formatador:
    def __init__(self, tipo):
        self.tipo = tipo

    def formatar(self, content):
        if self.tipo == "PDF":
            return self.formatar_pdf(content)
        elif self.tipo == "TXT":
            return self.formatar_txt(content)
        elif self.tipo == "EPUB":
            return self.formatar_epub(content)
        else:
            raise ValueError("Tipo de formato não suportado")

    def formatar_pdf(self, content):
        return '\n'.join(line.strip() for line in content.splitlines() if line.strip())

    def formatar_txt(self, content):
        return '\n'.join(line.strip() for line in content.splitlines() if line.strip())

    def formatar_epub(self, content):
        return '\n'.join(f"<p>{line.strip()}</p>" for line in content.splitlines() if line.strip())

class Documento:
    def __init__(self, main, formatador=None):
        self.main = main
        self.formatador = formatador if formatador else Formatador(main.tipo)
        self.content = self.carregar()
        self.content = self.formatador.formatar(self.content)

    def carregar(self):
        response = requests.get(self.main.link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text(separator='\n', strip=True)

    def salvar(self):
        pass

class Txt(Documento):
    def __init__(self, main, formatador=None):
        super().__init__(main, formatador)

    def salvar(self):
        with open(self.main.caminho, 'w', encoding='utf-8') as file:
            file.write(self.content)
        print(f"Arquivo TXT salvo em: {self.main.caminho}")

class Pdf(Documento):
    def __init__(self, main, formatador=None):
        super().__init__(main, formatador)

    def salvar(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, self.main.titulo, ln=True, align="C")
        for line in self.content.splitlines():
            pdf.multi_cell(0, 10, line)
        pdf.output(self.main.caminho)
        print(f"Arquivo PDF salvo em: {self.main.caminho}")

class Epub(Documento):
    def __init__(self, main, formatador=None):
        super().__init__(main, formatador)

    def salvar(self):
        book = epub.EpubBook()
        book.set_title(self.main.titulo)
        book.set_language('pt')
        chapter = epub.EpubHtml(title='Capítulo 1', file_name='chapter_01.xhtml', lang='pt')
        chapter.set_content(f"<h1>{self.main.titulo}</h1>{self.content}")
        book.add_item(chapter)
        book.spine = ['nav', chapter]
        epub.write_epub(self.main.caminho, book)
        print(f"Arquivo EPUB salvo em: {self.main.caminho}")

# Menu
while True:
    print("\nMenu:")
    print("1. Salvar conteúdo de um link em um arquivo.")
    print("2. Sair")

    escolha = input("Escolha uma opção: ")

    if escolha == "1":
        link = input("Digite o link: ")
        caminho = input("Digite o caminho (inclua o nome do arquivo e seu tipo{PDF, TXT, EPUB}): ")
        tipo = caminho.split(".")[-1].upper()
        titulo = caminho.split("/")[-1].split(".")[0]
        main = Main(link, caminho, tipo, titulo)

        if tipo == "PDF":
            documento = Pdf(main)
        elif tipo == "TXT":
            documento = Txt(main)
        elif tipo == "EPUB":
            documento = Epub(main)
        else:
            print("Tipo de arquivo não suportado.")
            continue

        documento.salvar()

    elif escolha == "2":
        print("Saindo do programa.")
        break

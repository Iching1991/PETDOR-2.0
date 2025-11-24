from fpdf import FPDF
from datetime import datetime
import os

class PDFRelatorio(FPDF):
    def header(self):
        # Logo no topo
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 25)  # imagem, x, y, tamanho
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'PETDor - Relatório de Avaliação', ln=True, align='C')
        self.ln(5)

    def footer(self):
        # Número da página
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, 'C')


def gerar_pdf_relatorio(
    nome_tutor,
    nome_pet,
    especie,
    veterinario,
    avaliacao,
    observacoes,
    output_path="relatorio.pdf"
):
    pdf = PDFRelatorio()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # ---------------------------
    # Dados do Tutor e Pet
    # ---------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Informações do Tutor", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, f"Tutor: {nome_tutor}")
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Informações do Pet", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, f"Nome: {nome_pet}")
    pdf.multi_cell(0, 8, f"Espécie: {especie}")
    pdf.ln(3)

    # ---------------------------
    # Dados do Veterinário
    # ---------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Responsável", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, f"Veterinário(a): {veterinario}")
    pdf.ln(3)

    # ---------------------------
    # Avaliação
    # ---------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Avaliação de Dor", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, f"Resultado: {avaliacao}")
    pdf.ln(3)

    # ---------------------------
    # Observações
    # ---------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Observações", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, observacoes if observacoes else "Sem observações.")
    pdf.ln(3)

    # ---------------------------
    # Data e hora
    # ---------------------------
    pdf.set_font("Arial", size=10)
    pdf.ln(5)
    pdf.cell(0, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "R")

    # ---------------------------
    # Salva arquivo
    # ---------------------------
    pdf.output(output_path)

    return output_path

import tempfile
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")

    def title_page(self):
        self.add_page()
        self.set_font("DejaVu", size=24)
        self.cell(0, 60, "Bedrijfsconfigurator Rapport", 0, 1, "C")
        self.set_font("DejaVu", size=18)
        self.cell(0, 10, "Overzicht van financiële prestaties", 0, 1, "C")
        self.ln(10)
        self.set_font("DejaVu", size=14)
        self.cell(0, 10, f"Datum: {datetime.now().strftime('%d-%m-%Y')}", 0, 1, "C")
        self.ln(20)

    def chapter_title(self, num, title):
        self.set_font("DejaVu", size=16)
        self.cell(0, 10, f"Hoofdstuk {num}: {title}", 0, 1, 'L')
        self.ln(5)

    def chapter_subtitle(self, subtitle):
        self.set_font("DejaVu", size=12)
        self.cell(0, 10, subtitle, 0, 1, 'L')
        self.ln(3)

    def add_table(self, data, col_widths=None):
        self.set_font("DejaVu", size=10)
        if not col_widths:
            col_widths = [self.w / (len(data.columns) + 1)] * len(data.columns)
        row_height = self.font_size + 3

        for column in data.columns:
            self.cell(col_widths[data.columns.get_loc(column)], row_height, column, border=1, align='C')
        self.ln(row_height)
        for i in range(len(data)):
            for column in data.columns:
                text = f"€{data[column].iloc[i]:,.2f}" if isinstance(data[column].iloc[i], (int, float)) else str(data[column].iloc[i])
                self.cell(col_widths[data.columns.get_loc(column)], row_height, text, border=1, align='C')
            self.ln(row_height)

    def add_content_table(self, chapters):
        self.set_font("DejaVu", size=14)
        self.cell(0, 10, "Inhoudsopgave", 0, 1, 'L')
        self.ln(5)
        self.set_font("DejaVu", size=12)
        for chapter_num, chapter_title in chapters.items():
            self.cell(0, 10, f"Hoofdstuk {chapter_num}: {chapter_title}", 0, 1, 'L')
        self.ln(10)

    def add_specifications(self, specifications):
        self.set_font("DejaVu", size=12)
        for month, spec in specifications.items():
            self.chapter_subtitle(f"Specificaties voor {month}")
            for key, value in spec.items():
                self.cell(0, 10, f"{key}: €{value:,.2f}", 0, 1, 'L')
            self.ln(5)

def genereer_rapport(aantal_installeurs, aantal_verkopers, fulltime_verkopers):
    pdf = PDF()
    pdf.add_font("DejaVu", "", "DejaVSanus.ttf", uni=True)  # Adjust path to font file
    pdf.set_font("DejaVu", size=12)

    # Titelpagina
    pdf.title_page()

    # Inhoudsopgave op pagina 2
    pdf.add_page()
    chapters = {
        1: "Inleiding",
        2: "Financiële Overzichten",
        3: "Detailgegevens",
        4: "Specificaties"
    }
    pdf.add_content_table(chapters)
    
    # Inleiding
    pdf.add_page()
    pdf.chapter_title(1, "Inleiding")
    pdf.set_font("DejaVu", size=10)
    inleiding_tekst = (
        "Dit rapport geeft een uitgebreid overzicht van de financiële prestaties van het bedrijf "
        "over de afgelopen maanden. Het doel van dit rapport is om inzicht te geven in de omzet, "
        "marges, kosten en resultaten per maand, evenals de vaste maandelijkse kosten. "
        "De informatie in dit rapport is bedoeld om beslissingsondersteuning te bieden en om een "
        "duidelijk beeld te geven van de financiële gezondheid van het bedrijf.\n\n"
        "In het hoofdstuk 'Financiële Overzichten' worden de maandelijkse financiële gegevens "
        "gepresenteerd, inclusief omzet, marges en kosten. Daarnaast worden er grafieken getoond "
        "om trends en verhoudingen te visualiseren. Het hoofdstuk 'Detailgegevens' bevat een gedetailleerde "
        "tabel met alle financiële gegevens van de afgelopen maanden.\n\n"
        "We hopen dat dit rapport u helpt bij het nemen van geïnformeerde beslissingen en het verbeteren "
        "van de financiële prestaties van het bedrijf."
    )
    pdf.multi_cell(0, 10, inleiding_tekst)
    pdf.ln(10)

    # Financiële Overzichten
    pdf.chapter_title(2, "Financiële Overzichten")
    for maand in df['maand'].unique():
        maand_data = df[df['maand'] == maand]

        pdf.chapter_subtitle(f"Maand: {maand}")
        
        pdf.set_font("DejaVu", size=12)
        pdf.cell(0, 10, "Financiële Overzicht", 0, 1)
        pdf.ln(5)
        financial_overview = pd.DataFrame({
            "Categorie": ["Totale Omzet", "Totale Marge", "Totale Kosten", "Resultaat", "Omzet per Persoon", "Marge per Persoon"],
            "Bedrag": [
                f"€{maand_data['omzet'].values[0]:,.2f}",
                f"€{maand_data['brutomarge'].values[0]:,.2f}",
                f"€{maand_data['kostprijs'].values[0] * -1:,.2f}",
                f"€{maand_data['resultaat'].values[0]:,.2f}",
                f"€{maand_data['omzet'].values[0] / (aantal_installeurs + aantal_verkopers + fulltime_verkopers + 1):,.2f}",
                f"€{maand_data['brutomarge'].values[0] / (aantal_installeurs + aantal_verkopers + fulltime_verkopers + 1):,.2f}"
            ]
        })
        pdf.add_table(financial_overview)
        pdf.ln(10)

        pdf.cell(0, 10, "Omzet en Marges", 0, 1)
        pdf.ln(5)
        omzet_marges = pd.DataFrame({
            "Categorie": ["Omzet Laadpalen", "Marge Laadpalen", "Omzet Zonnepanelen", "Marge Zonnepanelen"],
            "Bedrag": [
                f"€{maand_data['omzet_laadpalen'].values[0]:,.2f}",
                f"€{maand_data['brutomarge_laadpalen'].values[0]:,.2f}",
                f"€{maand_data['omzet_zonnepanelen'].values[0]:,.2f}",
                f"€{maand_data['brutomarge_zonnepanelen'].values[0]:,.2f}"
            ]
        })
        pdf.add_table(omzet_marges)
        pdf.ln(10)

        pdf.cell(0, 10, "Kostenoverzicht", 0, 1)
        pdf.ln(5)
        kostenoverzicht = pd.DataFrame({
            "Categorie": ["Totale Personeelskosten", "IT Kosten", "Solar Kosten", "Contributie Installatiebedrijf", "Autokosten", "Afschrijving Vervoersmiddelen"],
            "Bedrag": [
                f"€{maand_data['personeelskosten'].values[0]:,.2f}",
                f"€{-maand_data['it_kosten'].values[0]:,.2f}",
                f"€{-maand_data['solar_kosten'].values[0]:,.2f}",
                f"€{-maand_data['contributie_kosten'].values[0]:,.2f}",
                f"€{-maand_data['autokosten'].values[0]:,.2f}",
                f"€{-maand_data['afschrijving_kosten'].values[0]:,.2f}"
            ]
        })
        pdf.add_table(kostenoverzicht)
        pdf.ln(10)

        # Voeg grafieken toe met mooiere layout
        fig, ax = plt.subplots(figsize=(6, 3))
        sns.barplot(x=["Omzet", "Marge", "Resultaat"], y=[maand_data['omzet'].values[0], maand_data['brutomarge'].values[0], maand_data['resultaat'].values[0]], palette="viridis", ax=ax)
        ax.set_ylim(0, 250000)
        ax.set_ylabel("Bedrag in €")
        ax.set_title("Financiële Overzicht")
        fig.tight_layout()
        
        # Save figure to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, bbox_inches='tight')
            pdf.image(tmpfile.name, x=10, y=None, w=180)
        
        plt.close(fig)
        pdf.ln(10)

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(df["maand"], df["omzet"], marker='o', label="Omzet", color='blue')
        ax.plot(df["maand"], -df["kostprijs"], marker='o', label="Kosten", color='red')
        ax.plot(df["maand"], df["resultaat"], marker='o', label="Winst", color='green')
        ax.set_ylabel("Bedrag in €")
        ax.set_title("Trends en Verhoudingen")
        ax.legend()
        fig.tight_layout()
        sns.despine()
        
        # Save figure to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, bbox_inches='tight')
            pdf.image(tmpfile.name, x=10, y=None, w=180)
        
        plt.close(fig)
        pdf.add_page()

    # Detailgegevens
    pdf.chapter_title(3, "Detailgegevens")
    pdf.ln(5)

    pdf.set_font("DejaVu", size=10)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size + 3

    for column in df.columns:
        pdf.cell(col_width, row_height, column, border=1, align='C')
    pdf.ln(row_height)
    for i in range(len(df)):
        for column in df.columns:
            text = f"€{df[column].iloc[i]:,.2f}" if isinstance(df[column].iloc[i], (int, float)) else str(df[column].iloc[i])
            pdf.cell(col_width, row_height, text, border=1, align='C')
        pdf.ln(row_height)

    # Add specifications
    pdf.chapter_title(4, "Specificaties")
    pdf.add_specifications(st.session_state.specificaties)

    return pdf.output(dest='S').encode('latin1')

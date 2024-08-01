import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="Bedrijfsconfigurator", layout="wide")

# Gegevens
historische_data = {
    "maand": ["apr-24", "mei-24", "jun-24"],
    "laadpalen": [17, 32, 22],
    "zonnepanelen": [1, 1, 2],
    "omzet": [47815.08, 77623.70, 70814.06],
    "kostprijs": [-31635.08, -53237.07, -48733.60],
    "brutomarge": [16180.00, 24386.63, 22080.46],
    "omzet_laadpalen": [39006.93, 72205.14, 53114.71],
    "kostprijs_laadpalen": [-27304.85, -51170.81, -42461.63],
    "brutomarge_laadpalen": [11702.08, 21034.33, 10653.08],
    "omzet_zonnepanelen": [8808.15, 5418.56, 17699.35],
    "kostprijs_zonnepanelen": [-4330.23, -2066.26, -6271.97],
    "brutomarge_zonnepanelen": [4477.92, 3352.30, 11427.38],
    "personeelskosten": [-16315.00, -16315.00, -16315.00],
    "it_kosten": [-311.29, -284.03, -391.83],
    "solar_kosten": [-704.50, -704.50, -704.50],
    "contributie_kosten": [-154.74, -154.74, -154.74],
    "afschrijving_kosten": [-3631.45, -3449.16, -3348.98],
    "autokosten": [-500, -500, -500],
    "resultaat": [-4936.98, 3479.20, 1165.41]
}

specificaties = {
    "apr-24": {
        "Personeelskosten": -16315.00,
        "Loonjournaalpost": -16315.00,
        "IT Kosten": -311.29,
        "Acknowledge cloud dienst": -56.25,
        "ACK CSP 14-02-24": -51.3,
        "ACK SLA 37,60 PER WERKPLEK": -112.8,
        "Ack Back Up storage": -44.79,
        "BUBBLE": -13.52,
        "SLA Licenties 2024-03": -23.44,
        "kpn": -9.19,
        "Contributies/ Lidmaatschappen": -859.24,
        "2Solar software licentie": -704.5,
        "Contributie installatiebedrijf": -154.74,
        "Afschrijvingen": -3631.45,
        "5231 afschrijving service auto": -2000.00,
        "Afschrijving combo": -881.45,
        "1 demo voor Bink & Ian": -750,
    },
    "mei-24": {
        "Personeelskosten": -16315.00,
        "Loonjournaalpost": -16315.00,
        "IT Kosten": -284.03,
        "ACK CSP 14-02-24": -51.3,
        "ACK SLA 37,60 PER WERKPLEK": -112.8,
        "Ack Back Up storage": -44.79,
        "BUBBLE": -13.52,
        "SLA licenties 2024": -46.88,
        "Yomani SDLE pin Worldline": -14.74,
        "Contributies/ Lidmaatschappen": -859.24,
        "2Solar software licentie": -704.5,
        "Contributie installatiebedrijf": -154.74,
        "Afschrijvingen": -3449.16,
        "5231 afschrijving service auto": -2000.00,
        "Afschrijving combo": -699.16,
        "1 demo voor Bink & Ian": -750,
    },
    "jun-24": {
        "Personeelskosten": -16315.00,
        "Loonjournaalpost": -16315.00,
        "IT Kosten": -391.83,
        "ACK CSP 14-02-24": -51.3,
        "ACK SLA 37,60 PER WERKPLEK": -112.8,
        "Ack Back Up storage": -44.79,
        "BUBBLE": -13.52,
        "SLA licenties 2024": -46.88,
        "Coolblue Samsung ViewFinity": -47.92,
        "Acknowledge adobe lightroom": -74.63,
        "Contributies/ Lidmaatschappen": -859.24,
        "2Solar software licentie": -704.5,
        "Contributie installatiebedrijf": -154.74,
        "Afschrijvingen": -3348.98,
        "5231 afschrijving service auto": -2000.00,
        "Afschrijving combo": -598.98,
        "1 demo voor Bink & Ian": -750,
    }
}

# Zet de oorspronkelijke data in een DataFrame
df = pd.DataFrame(historische_data)

# Laad opgeslagen gegevens als die er zijn
if "data" not in st.session_state:
    st.session_state.data = df
else:
    df = st.session_state.data

if "specificaties" not in st.session_state:
    st.session_state.specificaties = specificaties
else:
    specificaties = st.session_state.specificaties

def bereken_afschrijving(kosten, percentage):
    return kosten * (1 - percentage / 100)

# Functie om de gegevens te berekenen op basis van de invoer
def bereken_gegevens(aantal_laadpalen, aantal_zonnepanelen, marge_laadpalen, marge_zonnepanelen, aantal_installeurs, aantal_verkopers, fulltime_verkopers, marketing_budget, maand):
    # Omzet en marge berekeningen
    omzet_laadpalen = aantal_laadpalen * (sum(df["omzet_laadpalen"] / df["laadpalen"]) / len(df))
    marge_laadpalen = aantal_laadpalen * (sum(df["brutomarge_laadpalen"] / df["laadpalen"]) / len(df)) * (marge_laadpalen / 100)
    omzet_zonnepanelen = aantal_zonnepanelen * (sum(df["omzet_zonnepanelen"] / df["zonnepanelen"]) / len(df))
    marge_zonnepanelen = aantal_zonnepanelen * (sum(df["brutomarge_zonnepanelen"] / df["zonnepanelen"]) / len(df)) * (marge_zonnepanelen / 100)

    totale_omzet = omzet_laadpalen + omzet_zonnepanelen
    totale_marge = marge_laadpalen + marge_zonnepanelen

    # Personeelskosten
    fulltime_installeurs_kosten = aantal_installeurs * 4000  # Fulltime installateurs à €4000 p.m.
    parttime_verkopers_kosten = aantal_verkopers * 20 / 40 * 3000  # Parttime verkopers (20 uur p.p) à €3000 p.m.
    fulltime_verkoper_kosten = fulltime_verkopers * 3000  # Fulltime verkopers à €3000 p.m.
    parttime_registratie_kosten = 8 / 40 * 2500  # 1x parttime registratie (8 uur p.w.) à €2500 p.m.
    personeelskosten = fulltime_installeurs_kosten + parttime_verkopers_kosten + fulltime_verkoper_kosten + parttime_registratie_kosten

    # Vaste kosten
    it_kosten = -sum(df["it_kosten"]) / len(df)
    solar_kosten = -sum(df["solar_kosten"]) / len(df)
    contributie_kosten = -sum(df["contributie_kosten"]) / len(df)
    autokosten = -200  # Verander hier naar de juiste autokosten
    afschrijving_service_auto = bereken_afschrijving(-2000, 5)  # Afschrijving van 5% per maand
    afschrijving_combo = bereken_afschrijving(-600, 5)  # Afschrijving van 5% per maand

    afschrijving_kosten = afschrijving_service_auto + afschrijving_combo

    vaste_kosten = it_kosten + solar_kosten + contributie_kosten + autokosten + afschrijving_kosten
    totale_kosten = personeelskosten + vaste_kosten + marketing_budget

    resultaat = totale_marge - totale_kosten

    totale_personen = aantal_installeurs + aantal_verkopers + fulltime_verkopers + 1  # Totaal personeel incl. registratie medewerker
    omzet_per_persoon = totale_omzet / totale_personen
    marge_per_persoon = totale_marge / totale_personen

    nieuwe_data = {
        "maand": maand,
        "laadpalen": aantal_laadpalen,
        "zonnepanelen": aantal_zonnepanelen,
        "omzet": totale_omzet,
        "kostprijs": -(omzet_laadpalen + omzet_zonnepanelen - totale_marge),
        "brutomarge": totale_marge,
        "omzet_laadpalen": omzet_laadpalen,
        "kostprijs_laadpalen": -((omzet_laadpalen * 100 / marge_laadpalen) - omzet_laadpalen),
        "brutomarge_laadpalen": marge_laadpalen,
        "omzet_zonnepanelen": omzet_zonnepanelen,
        "kostprijs_zonnepanelen": -((omzet_zonnepanelen * 100 / marge_zonnepanelen) - omzet_zonnepanelen),
        "brutomarge_zonnepanelen": marge_zonnepanelen,
        "personeelskosten": personeelskosten,
        "it_kosten": it_kosten,
        "solar_kosten": solar_kosten,
        "contributie_kosten": contributie_kosten,
        "autokosten": autokosten,
        "afschrijving_kosten": afschrijving_kosten,
        "resultaat": resultaat
    }

    specificatie_nieuwe_maand = {
        "Personeelskosten": personeelskosten,
        "IT Kosten": it_kosten,
        "Solar kosten": solar_kosten,
        "Contributie installatiebedrijf": contributie_kosten,
        "Autokosten": autokosten,
        "Afschrijvingen": afschrijving_kosten,
    }

    return nieuwe_data, specificatie_nieuwe_maand

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

def genereer_rapport():
    pdf = PDF()
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)  # Adjust path to font file
    pdf.set_font("DejaVu", size=12)

    # Titelpagina
    pdf.title_page()

    # Inhoudsopgave op pagina 2
    pdf.add_page()
    chapters = {
        1: "Inleiding",
        2: "Financiële Overzichten",
        3: "Detailgegevens"
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
                f"€{maand_data['omzet'].values[0] / (aantal_installeurs + aantal_verkopers + 1):,.2f}",
                f"€{maand_data['brutomarge'].values[0] / (aantal_installeurs + aantal_verkopers + 1):,.2f}"
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
        img = plot_to_image(fig)
        pdf.image(img, x=10, y=None, w=180)
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
        img = plot_to_image(fig)
        pdf.image(img, x=10, y=None, w=180)
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

    return pdf.output(dest='S').encode('latin1')

# Rapport genereren en download button
if st.button("Genereer Rapport"):
    pdf_content = genereer_rapport()
    st.download_button(label="Download PDF", data=pdf_content, file_name="financiele_configurator.pdf", mime="application/pdf")

# Streamlit interface
st.set_page_config(page_title="Bedrijfsconfigurator", layout="wide")

st.title("Bedrijfsconfigurator")

with st.sidebar:
    st.header("Invoerparameters")
    aantal_laadpalen = st.slider("Aantal verkochte laadpalen", 0, 100, 22)
    aantal_zonnepanelen = st.slider("Aantal verkochte zonnepanelen", 0, 50, 2)
    marge_laadpalen = st.slider("Marge Laadpalen (%)", 0, 100, 32)
    marge_zonnepanelen = st.slider("Marge Zonnepanelen (%)", 0, 100, 32)
    aantal_installeurs = st.slider("Aantal fulltime installateurs", 1, 10, 2)
    aantal_verkopers = st.slider("Aantal parttime verkopers", 0, 10, 2)
    fulltime_verkopers = st.slider("Aantal fulltime verkopers", 0, 10, 0)
    marketing_budget = st.slider("Marketing Budget (€)", 0, 50000, 5000)
    maand = st.text_input("Maand (bijv. jul-24)", "jul-24")

    if st.button("Invoeren"):
        # Bereken de gegevens voor nieuwe maand
        nieuwe_data, specificatie_nieuwe_maand = bereken_gegevens(aantal_laadpalen, aantal_zonnepanelen, marge_laadpalen, marge_zonnepanelen, aantal_installeurs, aantal_verkopers, fulltime_verkopers, marketing_budget, maand)
        df_nieuwe_data = pd.DataFrame([nieuwe_data])
        df = pd.concat([df, df_nieuwe_data], ignore_index=True)
        
        # Sla de bijgewerkte gegevens op in de sessie
        st.session_state.data = df

        # Voeg nieuwe maand toe aan specificaties
        if maand not in st.session_state.specificaties:
            st.session_state.specificaties[maand] = specificatie_nieuwe_maand
            specificaties = st.session_state.specificaties

st.markdown("### Resultaten")

# Dropdown menu voor maand specificaties
selected_month = st.selectbox("Selecteer een maand voor specificaties", ["Selecteer een maand"] + list(st.session_state.specificaties.keys()))

if selected_month and selected_month != "Selecteer een maand":
    with st.expander(f"Specificaties voor {selected_month}"):
        specificatie_data = st.session_state.specificaties[selected_month]
        for key, value in specificatie_data.items():
            st.write(f"{key}: €{value:,.2f}")

# Organiseer de resultaten in een kolomstructuur
with st.container():
    col1, col2, col3, col4 = st.columns((2, 1, 1, 1))

    with col1:
        st.metric("Totale Omzet", f"€{df['omzet'].iloc[-1]:,.2f}")
        st.metric("Omzet per Persoon", f"€{df['omzet'].iloc[-1] / (aantal_installeurs + aantal_verkopers + fulltime_verkopers + 1):,.2f}")

    with col2:
        st.metric("Totale Marge", f"€{df['brutomarge'].iloc[-1]:,.2f}")
        st.metric("Marge per Persoon", f"€{df['brutomarge'].iloc[-1] / (aantal_installeurs + aantal_verkopers + fulltime_verkopers + 1):,.2f}")

    with col3:
        st.metric("Resultaat", f"€{df['resultaat'].iloc[-1]:,.2f}")
        st.metric("Totale Personeelskosten", f"€{df['personeelskosten'].iloc[-1]:,.2f}")

    with col4:
        st.metric("IT kosten", f"€{-df['it_kosten'].iloc[-1]:,.2f}")
        st.metric("Solar kosten", f"€{-df['solar_kosten'].iloc[-1]:,.2f}")
        st.metric("Contributie installatiebedrijf", f"€{-df['contributie_kosten'].iloc[-1]:,.2f}")
        st.metric("Autokosten", f"€{-df['autokosten'].iloc[-1]:,.2f}")
        st.metric("Afschrijving vervoersmiddelen", f"€{-df['afschrijving_kosten'].iloc[-1]:,.2f}")

# Visualisaties
st.markdown("### Visualisaties")

def plot_to_image(figure):
    img = BytesIO()
    figure.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    return img

with st.container():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        fig1 = px.bar(x=["Omzet", "Marge", "Resultaat"], y=[df['omzet'].iloc[-1], df['brutomarge'].iloc[-1], df['resultaat'].iloc[-1]],
                      labels={'x': 'Categorie', 'y': 'Bedrag in €'}, title="Financiële Overzicht")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(x=["Omzet per Persoon", "Marge per Persoon"], y=[df['omzet'].iloc[-1] / (aantal_installeurs + aantal_verkopers + fulltime_verkopers + 1), df['brutomarge'].iloc[-1] / (aantal_installeurs + aantal_verkopers + fulltime_verkopers + 1)],
                      labels={'x': 'Categorie', 'y': 'Bedrag in €'}, title="Omzet en Marge per Persoon")
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        fig3 = px.bar(x=["Omzet Laadpalen", "Marge Laadpalen"], y=[df['omzet_laadpalen'].iloc[-1], df['brutomarge_laadpalen'].iloc[-1]],
                      labels={'x': 'Categorie', 'y': 'Bedrag in €'}, title="Laadpalen Omzet en Marge")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = px.bar(x=["Omzet Zonnepanelen", "Marge Zonnepanelen"], y=[df['omzet_zonnepanelen'].iloc[-1], df['brutomarge_zonnepanelen'].iloc[-1]],
                      labels={'x': 'Categorie', 'y': 'Bedrag in €'}, title="Zonnepanelen Omzet en Marge")
        st.plotly_chart(fig4, use_container_width=True)

st.markdown("### Trends en Verhoudingen")

with st.container():
    fig5 = px.line(df, x="maand", y=["omzet", "kostprijs", "resultaat"], labels={'value': 'Bedrag in €', 'variable': 'Categorie'},
                   title="Omzet, Kosten en Winst")
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("### Detailgegevens")
st.dataframe(df)

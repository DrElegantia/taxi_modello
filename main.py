import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Intestazione dell'applicazione
st.title("Modello Sbagliato di Simulazione Reddito Taxi, basato su dati 2022")
st.write("Per conoscere i dettagli del modello vai qui: [https://stupendous-florentine-aa1d05.netlify.app/article/modello-taxi](#)")

# Parametri fissi
np.random.seed(2)
tariffe_iniziali = {'feriale': 3.50, 'festivo': 5.00, 'notturna': 7.50}
tariffe_km = [1.31, 1.42, 1.70]
soglie_tariffe = [7.00, 25.00]
supplementi = {'bagagli': 1.00, 'passeggero': 5.00, 'radiotaxi': 5.00}

# Input da barra laterale
st.sidebar.header("Impostazioni simulazione")
st.sidebar.subheader("Caratteristiche delle Corse")
ore_giornaliere = st.sidebar.slider("Ore al giorno di lavoro effettivamente fatturabili, escludi i tempi morti (media)", 1, 12, 6)
giorni_settimanali = st.sidebar.slider("Giorni alla settimana di lavoro", 1, 7, 5)
settimane_annuali = st.sidebar.slider("Settimane lavorative nell'anno", 1, 52, 42)
velocita_min = st.sidebar.slider("Velocità minima (km/h)", 0, 30, 15)
velocita_max = st.sidebar.slider("Velocità massima (km/h)", 0, 200, 70)
costo_massimo=st.sidebar.slider("Costo massimo corsa", 50, 200, 80)
st.sidebar.subheader("Scenari delle corse")




st.sidebar.subheader("Distribuzione tipologia di corse")
distribuzione_corse = st.sidebar.radio(
    "Seleziona la distribuzione delle corse",
    options=["Random", "Prevalentemente notturno", "Prevalentemente festivo",  "Festivo e notturno"],
    index=0
)

scenario_distanze = st.sidebar.radio(
    "Seleziona lo scenario della corsa",
    options=["Distanze corte", "Distanze lunghe", "Random", "Mediamente corte", "Mediamente lunghe"],
    index=2
)
d_min= st.sidebar.slider("Distanza minima della corsa", 1, 100, 4)
d_max= st.sidebar.slider("Distanza minima della corsa", 1, 100, 30)

st.sidebar.subheader("Consumi veicolo")
consumo_benzina =st.sidebar.slider("Consumo KM/Litro Medio", 1, 30, 15)
costo_benzina_per_litro =st.sidebar.slider("Costo Litro carburante", 1.00, 3.00, 1.80)

st.sidebar.subheader("Costi veicolo")
Auto =st.sidebar.slider("Costo auto", 10000, 50000, 30000)
Manutenzione =st.sidebar.slider("Costo manutenzione annua (pneumatici, cambio olio, incidenti)", 1000, 30000, 4000)
Assicurazione =st.sidebar.slider("Costo assicurazione annua", 500, 10000, 2000)


q1 = d_min + (d_max - d_min) * 0.25
q2 = d_min + (d_max - d_min) * 0.5
q3 = d_min + (d_max - d_min) * 0.75

# Funzione per generare una corsa
def genera_corsa_modificata():
    if distribuzione_corse == "Random":
        tipo_corsa = np.random.choice(['feriale', 'festivo', 'notturna'])
    elif distribuzione_corse == "Prevalentemente notturno":
        tipo_corsa = np.random.choice(['feriale', 'festivo', 'notturna'], p=[0.05, 0.35, 0.6])
    elif distribuzione_corse == "Prevalentemente festivo":
        tipo_corsa = np.random.choice(['feriale', 'festivo', 'notturna'], p=[0.05, 0.6, 0.35])
    elif distribuzione_corse == "Festivo e notturno":
        tipo_corsa = np.random.choice(['feriale', 'festivo', 'notturna'], p=[0, 0.5, 0.5])

    if scenario_distanze == "Random":
        # Distanze uniformemente distribuite tra minimo e massimo
        distanza = np.random.uniform(d_min, d_max)
    elif scenario_distanze == "Distanze corte":
        # Maggioranza di corse con distanze vicine al minimo (più brevi)
        distanza = np.random.choice(
            [d_min,q1, q2, q3, d_max],  # Range da minimo a metà circa
            p=[0.5, 0.2, 0.1, 0.1, 0.1]  # Alta probabilità per distanze molto brevi
        )
    elif scenario_distanze == "Distanze lunghe":
        # Maggioranza di corse con distanze vicine al massimo (più lunghe)
        distanza = np.random.choice(
            [d_min,q1, q2, q3, d_max],  # Range dalla metà superiore al massimo
            p=[0.1, 0.1, 0.1, 0.2, 0.5]  # Alta probabilità per distanze molto lunghe
        )
    elif scenario_distanze == "Mediamente corte":
        # Corse distribuite verso la parte corta, ma con bilanciamento
        distanza = np.random.choice(
            [d_min,q1, q2, q3, d_max],  # Range fino a metà circa
            p=[0.3, 0.3, 0.2, 0.1, 0.1]  # Maggior peso per distanze corte e medie
        )
    elif scenario_distanze == "Mediamente lunghe":
        # Corse distribuite verso la parte lunga, ma con bilanciamento
        distanza = np.random.choice(
            [d_min,q1, q2, q3, d_max],  # Range dalla metà superiore al massimo
            p=[0.1, 0.1, 0.2, 0.3, 0.3]   # Maggior peso per distanze medie-lunghe
        )

    bagagli = np.random.randint(0, 2)
    passeggeri = np.random.randint(1, 2)


    return tipo_corsa, distanza, bagagli, passeggeri



# Funzione per calcolare il costo della benzina
def calcola_costo_benzina(distanza):
    return (distanza / consumo_benzina) * costo_benzina_per_litro

# Funzione per calcolare i costi e il fatturato
def calcola_fatturato_e_costo(corsa):
    tipo_corsa, distanza, bagagli, passeggeri = corsa
    costo = tariffe_iniziali[tipo_corsa]
    accumulato = 0
    tempo_totale = 0

    for km in range(int(distanza)):
        velocita = np.random.uniform(velocita_min, velocita_max)
        tempo_totale += 60 / velocita
        tariffa_km = tariffe_km[0] if accumulato < soglie_tariffe[0] else (
            tariffe_km[1] if accumulato < sum(soglie_tariffe) else tariffe_km[2])
        costo += tariffa_km
        accumulato += tariffa_km

    costo += max(0, bagagli - 1) * supplementi['bagagli']
    costo += max(0, passeggeri - 2) * supplementi['passeggero']

    costo = min(costo, costo_massimo)
    return costo, calcola_costo_benzina(distanza), tempo_totale

# Simulazione della giornata
dati_corse = []
dati_giornate = []

def simula_giornata():
    fatturato_giornaliero = 0
    tempo_totale = 0
    numero_corse = 0
    while tempo_totale < ore_giornaliere * 60:
        corsa = genera_corsa_modificata()
        fatturato, costo_benzina, tempo = calcola_fatturato_e_costo(corsa)
        if tempo_totale + tempo > ore_giornaliere * 60:
            break

        dati_corse.append({
            'Tipo Corsa': corsa[0],
            'Distanza (km)': corsa[1],
            'Bagagli': corsa[2],
            'Passeggeri': corsa[3],
            'Fatturato': fatturato,
            'Costo Benzina': costo_benzina,
            'Tempo Totale (min)': tempo
        })

        fatturato_giornaliero += fatturato
        tempo_totale += tempo
        numero_corse += 1

    dati_giornate.append({'Numero Corse': numero_corse, 'Fatturato Giornaliero': fatturato_giornaliero})

# Simulazione
giorni_totali = giorni_settimanali * settimane_annuali
for _ in range(giorni_totali):
    simula_giornata()

# Creazione dei DataFrame
df_corse = pd.DataFrame(dati_corse)
df_giornate = pd.DataFrame(dati_giornate)

# Statistiche
fatturato_totale = df_corse['Fatturato'].sum()
costo_benzina_totale = df_corse['Costo Benzina'].sum()
numero_totale_corse = len(df_corse)
km_totali = df_corse['Distanza (km)'].sum()


ricavo_marginale=fatturato_totale-costo_benzina_totale
ammortamento=Auto/4
costi_extra=Manutenzione+Assicurazione
RAI=ricavo_marginale-ammortamento-costi_extra
contributi = 3828.72 + ((RAI - 15953) * 0.24 if RAI > 15953 else 0)

imponibile_irpef=RAI-contributi

if imponibile_irpef <= 15000:
    imposte = 0.23 * imponibile_irpef
elif imponibile_irpef <= 28000:
    imposte = 3450 + 0.25 * (imponibile_irpef - 15000)
elif imponibile_irpef <= 50000:
    imposte = 6700 + 0.35 * (imponibile_irpef - 28000)
else:  # imponibile_irpef > 50000
    imposte = 14400 + 0.43 * (imponibile_irpef - 50000)

netto=imponibile_irpef-imposte

st.header("Risultati della simulazione")
st.metric("Fatturato Totale (€)", f"{fatturato_totale:.2f}")
st.metric("Costo Totale Benzina (€)", f"{costo_benzina_totale:.2f}")
st.metric("Numero Totale di Corse", numero_totale_corse)
st.metric("Chilometri Totali Percorsi", f"{km_totali:.2f} km")
st.metric("Ricavo marginale (Fatturato - carburante)", f"{ricavo_marginale:.2f}")
st.metric("Ammortamento veicolo (25%)", f"{ammortamento:.2f}")
st.metric("Manutenzione+assicurazione", f"{costi_extra:.2f}")

st.metric("Reddito anteimposte", f"{RAI:.2f}")

st.metric("contirbuti dovuti", f"{contributi:.2f}")
st.metric("Imponibile IRPEF", f"{imponibile_irpef:.2f}")

st.metric("IRPEF dovuta", f"{imposte:.2f}")
st.metric("Reddito netto", f"{netto:.2f}")

# Grafici
st.header("Analisi dei risultati")

# Grafico: Distribuzione dei tipi di corsa
fig1 = go.Figure(data=[go.Bar(
    x=df_corse['Tipo Corsa'].value_counts().index,
    y=df_corse['Tipo Corsa'].value_counts()
)])
fig1.update_layout(title="Distribuzione delle Corse per Tipo di Servizio", xaxis_title="Tipo Corsa", yaxis_title="Numero di Corse")
st.plotly_chart(fig1)

# Grafico: Distribuzione delle distanze
fig2 = go.Figure(data=[go.Histogram(x=df_corse['Distanza (km)'], nbinsx=20)])
fig2.update_layout(title="Distribuzione delle Distanze delle Corse", xaxis_title="Distanza (km)", yaxis_title="Numero di Corse")
st.plotly_chart(fig2)

# 5. Tempo Totale in funzione della Distanza delle Corse
fig3 = go.Figure(
    data=[go.Scatter(x=df_corse['Distanza (km)'], y=df_corse['Tempo Totale (min)'], mode='markers', opacity=0.5)])
fig3.update_layout(title="Tempo VS Distanza delle Corse", xaxis_title="Distanza (km)", yaxis_title="Tempo Totale (min)")
st.plotly_chart(fig3)

fig4 = go.Figure(data=[go.Histogram(x=df_giornate['Numero Corse'], nbinsx=20)])
fig4.update_layout(title="Distribuzione Corse al Giorno", xaxis_title="Numero di Corse al Giorno", yaxis_title="Frequenza")
st.plotly_chart(fig4)


# Esplorazione dati
st.header("Esplorazione Dati")
st.dataframe(df_corse)

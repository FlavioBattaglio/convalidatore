import os
import csv
import glob
import re 
#print(os.listdir())
import pandas as pd
import streamlit as st
import pyperclip
 
files = [f for f in glob.glob("*.xxx") if os.path.isfile(f) and f not in ["elencatore.py", "filefinale.csv"]]
 
if not files:
    st.error("Nessun file con estensione .xxx trovato.")
    st.stop()

nomefile = st.selectbox("Scegli file con estensione .xxx", files)
#modifica spazio 
st.markdown("""
    <style>
    header {visibility: hidden;}
    h1 {
            font-size: 18px !important;     /* Dimensione del font */
            margin-top: 0.2rem !important;  
            margin-bottom: 0.2rem !important; 
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
    html, body, [class*="css"]  {
        margin: 0;
        padding: 5px;
        height: 30%;
        overflow: hidden;
    }
    .block-container {
        padding-top: 5px;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

 
    </style>
""", unsafe_allow_html=True)
############ fine modifica spazio
 
try:
    df = pd.read_csv(nomefile)
    ### aggiungere se non esistente la colonna "elaborato" nell'header
    df['elaborato']=df.get('elaborato')
     

    df = df.astype({"CAP": "string", "Comune": "string", "Provincia": "string", "Email": "string" })
except Exception as e:
    st.error(f"Errore nel caricamento del file: {e}")
    st.stop()

 
st.title("Programma Convalidazione")
# Filtro: solo righe con sito web
filtro = (df["Sito Web"].notna()) & (df["Sito Web"] != "")
df_filtrato = df[filtro].copy().reset_index()  # Mantiene l'indice originale

# Controllo righe
if "riga_corrente" not in st.session_state:
    st.session_state.riga_corrente = 0

max_righe = len(df_filtrato)

# Navigazione
col1, col2, col3 = st.columns(3, gap="large",vertical_alignment="center")
col4, col5, col6  = st.columns(3, gap="medium")

# aggiungi variabile di status di Conferma eliminazione cosi da lavorare col bottone eliminazione
if "conferma_eliminazione" not in st.session_state:
    st.session_state.conferma_eliminazione = False


with col1:
    if st.button("◀️ Indietro" , use_container_width=True) and st.session_state.riga_corrente > 0:
        st.session_state.conferma_eliminazione = False #chiude pulsante elimina
        st.session_state.mostra_email = False  # Chiude la checkbox
        st.session_state.riga_corrente -= 1
        st.rerun()
with col2:
        
        #riga_target = st.number_input(
        #    "Vai alla riga:",
        #    min_value=1,
        #    max_value=max_righe,
        #    value=st.session_state.riga_corrente + 1,
        #    step=1
        #)
        #if st.button("Vai ▶️", use_container_width=True):
        #    st.session_state.conferma_eliminazione = False
        #    st.session_state.riga_corrente = int(riga_target) - 1
        #  st.session_state.mostra_email = False
        #    st.rerun()

        if st.button("vai all'ultimo Dato modificato"):
            ## ultima riga con elaborato  == 2
            ## se è presente 
            
            ultima_riga_elaborata_df = df[df['elaborato'] == 2].tail(1)

            if not ultima_riga_elaborata_df.empty:
                indice_reale = ultima_riga_elaborata_df.index[0]

                #  è presnete l'indice nella query?
                mask = df_filtrato["index"] == indice_reale
                if mask.any():
                    posizione_filtrato = df_filtrato[mask].index[0]

                    st.session_state.conferma_eliminazione = False
                    st.session_state.riga_corrente = posizione_filtrato
                    st.rerun()
                else:
                    st.warning("L'ultima riga modificata  no è presente")
with col3:
    
    if st.button("Avanti ▶️" , use_container_width=True) and st.session_state.riga_corrente < max_righe - 1:
        st.session_state.conferma_eliminazione = False #chiude pulsante elimina
        st.session_state.mostra_email = False  # Chiude la checkbox
        st.session_state.riga_corrente += 1
        st.rerun()
        
  


# Riga corrente
riga = df_filtrato.iloc[st.session_state.riga_corrente]
nomeragionesociale= df_filtrato.iloc[st.session_state.riga_corrente]
indice_df = df_filtrato.loc[st.session_state.riga_corrente, 'index']


numerotel=df_filtrato.loc[st.session_state.riga_corrente,'index']

riga_originale = df.loc[indice_df]

st.write(f"Riga {st.session_state.riga_corrente + 1} di {max_righe}")
st.text(f"Sito Web:  {riga['Sito Web']}")

col1_bis, col2_bis = st.columns(2, gap="large",vertical_alignment="center")

with col1_bis:
    st.text((f"Ragione sociale:  {riga['Nomi']}"))
with col2_bis:
    #da passare come parametro da salvare!
    nuova_telefono = st.text_input("Telefono", value=riga["Telefono"] if pd.notna(riga["Telefono"]) else "")

sito_corrente = riga["Sito Web"]

occorrenze = df[df["Sito Web"] == sito_corrente]
if len(occorrenze) > 1:
    st.warning(f"Il sito '{sito_corrente}' è presente in {len(occorrenze)} righe  .")



def copia_sito_web():
    pyperclip.copy(riga["Sito Web"])
    #st.success("Sito Web copiato negli appunti!")
    

st.markdown(
    f"""
    <style>
    .button-like {{
       border: 2px solid rgba(49, 51, 63, 0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-decoration: none;
        display: inline-block;
        font-weight: 600;
        transition: background-color 0.2s;
    }}
    .button-like:hover {{
        background-color: #d42b5b;
    }}
    </style>

    <a href="{riga["Sito Web"]}" target="_blank" class="button-like">🌐 Apri Sito Web</a>
    """,
    unsafe_allow_html=True
)
# Pulsante per copiare il sito web
#if st.button("Copia Sito Web"):
#    copia_sito_web()
#
nuova_email = st.text_input("Email", value=riga["Email"] if pd.notna(riga["Email"]) else "")
###warning email doppia
mailsingola = riga["Email"]
occorrenze_email = df[df["Email"] == mailsingola]
if len(occorrenze_email) > 1:
    st.warning(f"⚠️ L'email '{mailsingola}' è presente in {len(occorrenze_email)} righe.⚠️")



with col4:

    cap_raw = riga["CAP"]
    cap_clean = ""

    if pd.notna(cap_raw):
        try:
            cap_raw = cap_raw.decode('utf-8')  # se è bytes
        except AttributeError:
            cap_raw = str(cap_raw)  # se è già stringa o altro

        cap_clean = re.sub(r"\.", "", cap_raw)

    nuova_cap = st.text_input("CAP", value=cap_clean)


with col5:
    nuova_comune = st.text_input("Comune", value=riga["Comune"] if pd.notna(riga["Comune"]) else "")
with col6:
    nuova_provincia = st.text_input("Provincia", value=riga["Provincia"] if pd.notna(riga["Provincia"]) else "")




 

st.checkbox("➕ Aggiungi altre email", key="mostra_email")

if st.session_state.get("mostra_email", False):
    st.markdown("Inserisci Le altre email ritrovate")
    email_inputs = [st.text_input(f"Email #{i+1}", key=f"email_{i}") for i in range(6)]

if st.session_state.get("salvataggio_completo", False):
    st.success("Dati salvati direttamente nel file.")
    st.session_state.salvataggio_completo = False 

col7, col8 ,col9 = st.columns(3, gap="medium")

with col7:
    righe_da_aggiungere = []
    if st.button("Aggiorna file💾"):
               
        try:
            if email_inputs:
                for email in email_inputs:
                    if email.strip():
                        nuova_riga = riga_originale.copy()
                        nuova_riga["Email"] = email.strip()
                        nuova_riga["Telefono"] = nuova_telefono
                        nuova_riga["CAP"] = nuova_cap
                        nuova_riga["Comune"] = nuova_comune
                        nuova_riga["Provincia"] = nuova_provincia
                        nuova_riga["elaborato"] =2
                        righe_da_aggiungere.append(nuova_riga)

                
                if righe_da_aggiungere:
                    # Aggiorna la riga corrente
                    df.loc[indice_df, "Telefono"] = nuova_telefono
                    df.loc[indice_df, "Email"] = nuova_email
                    df.loc[indice_df, "CAP"] = nuova_cap
                    df.loc[indice_df, "Comune"] = nuova_comune
                    df.loc[indice_df, "Provincia"] = nuova_provincia
                    df.loc[indice_df, "elaborato"] =2
                    # Inserisci nuove righe dopo la riga corrente
                    parte1 = df.iloc[:indice_df + 1]
                    parte2 = df.iloc[indice_df + 1:]

                    #  CONVERTIRE in DataFrame le righe da aggiungere!!!!
                    righe_df = pd.DataFrame(righe_da_aggiungere)
                    df = pd.concat([parte1, righe_df, parte2], ignore_index=True)

                    df.to_csv(nomefile, index=False)
                    st.session_state.mostra_email = False
                    st.session_state.salvataggio_completo = True  # <-- flag per mostrare messaggio

                    st.rerun()
                else:
                    st.warning("Nessuna email inserita.")

        except Exception as e:
            ## email_inputs non è definita  salvare email 
            try:
                df.loc[indice_df, "Email"] = nuova_email
                df.loc[indice_df, "elaborato"] = 2

                df.to_csv(nomefile, index=False)
                st.session_state.salvataggio_completo = True
                st.rerun()
              

            except Exception as e:
                st.error(f"Errore durante il salvataggio: {e}")
                    
 

with col8:
    if st.button("🗑️ Elimina questo contatto"):
   
        if(st.session_state.conferma_eliminazione== True):
            st.session_state.conferma_eliminazione = False
        else:
            st.session_state.conferma_eliminazione = True

    if st.session_state.conferma_eliminazione:
         
        st.markdown("""
        <script>
            setTimeout(function() {
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }, 300);
        </script>
        """, unsafe_allow_html=True)
        with col9:
            if st.button("Clicca qui per confermare eliminazione ⚠️"):
    
                df = df.drop(indice_df).reset_index(drop=True)
                df.to_csv(nomefile, index=False)
                st.success("Riga eliminata dal file.")
                st.session_state.conferma_eliminazione = False
                st.rerun()



col10,col11,col12= st.columns(3, gap="medium")
if st.session_state.riga_corrente + 1 == max_righe:
    with col11:
        if st.button("💾Clicca qui per Terminare e Salvare il lavoro💾")   :

                estensione= ".xxx"
                fileRinominato = nomefile.replace(estensione,".csv")
                
                df.to_csv(fileRinominato, index=False)
                st.success(f"Tutte le modifiche sono state salvate in {fileRinominato}")
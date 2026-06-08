import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="Predictive Inventory Dashboard", layout="wide")

st.title("📊 Système Intelligent de Prévision des Ventes & Optimisation de Stock")
st.markdown("---")

# 2. Load Historical Data
@st.cache_data
def load_historical_data():
    return pd.read_csv('cleaned_monthly_sales.csv')

df_hist = load_historical_data()

# 3. Sidebar Form
st.sidebar.header("🔮 Paramètres de Prédiction (IA)")

produits_dispo = ['Laptop Gamer', 'Laptop Bureautique', 'Clavier Mecanique', 'Serveur Enterprise']

produit_choisi = st.sidebar.selectbox("Sélectionnez le produit :", produits_dispo)
annee_choisie = st.sidebar.number_input("Année :", min_value=2023, max_value=2027, value=2026)
mois_choisi = st.sidebar.slider("Mois :", min_value=1, max_value=12, value=6)
promo_choisie = st.sidebar.selectbox("Activer une Promotion ?", ["Non", "Oui"])
promo_value = 1 if promo_choisie == "Oui" else 0

btn_predict = st.sidebar.button("📊 Lancer la Prédiction")

qte_predite_graph = None
date_predite_graph = None

# 4. Main Dashboard Display
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("💡 Résultat de l'IA")
    
    if btn_predict:
        payload = {
            "annee": annee_choisie,
            "mois": mois_choisi,
            "promo": promo_value,
            "produit": produit_choisi
        }
        
        try:
            response = requests.post("http://127.0.0.1:5000/predict", json=payload)
            result = response.json()
            
            if response.status_code == 200 and result['status'] == 'success':
                qte_predite = result['quantite_predite']
                
                qte_predite_graph = qte_predite
                date_predite_graph = f"{annee_choisie}-{str(mois_choisi).zfill(2)}"
                
                # ---- Business Logic (Stock Management) ----
                stock_securite = int(round(qte_predite * 0.15))
                point_commande = qte_predite + stock_securite
                
                st.markdown("### 📈 Recommandations Stock")
                
                kpi1, kpi2, kpi3 = st.columns(3)
                with kpi1:
                    st.metric(label="Prévision de Vente", value=f"{qte_predite} u")
                with kpi2:
                    st.metric(label="Stock de Sécurité (+15%)", value=f"{stock_securite} u")
                with kpi3:
                    st.metric(label="Point de Commande", value=f"{point_commande} u")
                
                st.markdown("---")
                
                # ---- LOGIQUE DE SEUILS INTELLIGENTE ET ADAPTATIVE ----
                if qte_predite == 0:
                    st.info("ℹ️ **Période de creux :** Aucune demande prévue pour ce produit ce mois-ci.")
                
                # Gestion des seuils pour la gamme d'ordinateurs (Laptops)
                elif "Laptop" in produit_choisi:
                    if point_commande > 700:
                        st.warning(f"⚠️ **Alerte Stock Fort :** Le point de commande atteint {point_commande} u. Anticipez de l'espace dans le dépôt.")
                    elif point_commande < 150:
                        st.error(f"🚨 **Risque de Rupture :** Niveau très bas ({point_commande} u). Commandez immédiatement !")
                    else:
                        st.success("✅ **Niveau de Stock Optimal :** Les quantités de PC sont parfaitement équilibrées avec la demande.")
                
                # Gestion des seuils pour les accessoires (Claviers) qui se vendent en gros volumes
                elif "Clavier" in produit_choisi:
                    if point_commande > 1200:
                        st.warning(f"⚠️ **Alerte Stock Fort :** Très gros volume de claviers ({point_commande} u).")
                    elif point_commande < 300:
                        st.error(f"🚨 **Risque de Rupture :** Moins de 300 unités disponibles !")
                    else:
                        st.success("✅ **Niveau de Stock Optimal :** Stock des accessoires parfaitement optimisé.")
                
                # Gestion des seuils pour les produits rares et chers (Serveurs)
                else:
                    if point_commande > 100:
                        st.warning(f"⚠️ **Alerte Stock Fort pour Serveurs :** Quantité élevée ({point_commande} u).")
                    elif point_commande < 10:
                        st.error(f"🚨 **Risque de Rupture :** Moins de 10 serveurs en dépôt !")
                    else:
                        st.success("✅ **Niveau de Stock Optimal :** Parfait pour la gamme Enterprise.")
                
            else:
                st.error(f"Erreur API : {result.get('message', 'Inconnue')}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Impossible de se connecter au Backend Flask. Vérifiez que `app.py` est bien démarré dans le terminal 1 !")
    else:
        st.info("Sélectionnez les paramètres dans la barre latérale et cliquez sur **Lancer la Prédiction**.")

with col2:
    st.subheader("📈 Historique & Prévisions Futures")
    
    df_filtered = df_hist[df_hist['Produit'] == produit_choisi].copy()
    df_filtered['Date_Display'] = df_filtered['Annee'].astype(str) + "-" + df_filtered['Mois'].astype(str).str.zfill(2)
    df_filtered = df_filtered.sort_values(by=['Annee', 'Mois'])
    
    fig = go.Figure()
    
    # Historical Line (Blue)
    fig.add_trace(go.Scatter(
        x=df_filtered['Date_Display'], 
        y=df_filtered['Target_Quantite'],
        mode='lines+markers',
        name='Ventes Réelles (Historique)',
        line=dict(color='#2E86C1', width=2)
    ))
    
    # Future Prediction Line (Orange Dash)
    if qte_predite_graph is not None and date_predite_graph is not None:
        derniere_date_reelle = df_filtered['Date_Display'].iloc[-1]
        derniere_qte_reelle = df_filtered['Target_Quantite'].iloc[-1]
        
        fig.add_trace(go.Scatter(
            x=[derniere_date_reelle, date_predite_graph],
            y=[derniere_qte_reelle, qte_predite_graph],
            mode='lines+markers',
            name='Prédiction IA (Futur)',
            line=dict(color='#E67E22', width=3, dash='dash'),
            marker=dict(size=10, symbol='star')
        ))
    
    fig.update_layout(
        title=f"Évolution et Projection des Ventes - {produit_choisi}",
        xaxis_title="Période (Année-Mois)",
        yaxis_title="Quantité Vendue",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    fig.update_xaxes(type='category')
    
    st.plotly_chart(fig, use_container_width=True)
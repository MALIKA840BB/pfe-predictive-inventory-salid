from flask import Flask, request, jsonify
import xgboost as xgb
import numpy as np
import pandas as pd

app = Flask(__name__)

# 1. Charger le modèle XGBoost li trinitih f Colab
model = xgb.XGBRegressor()
model.load_model('inventory_xgboost_model.json')

# 2. Charger les classes dial les produits
classes_produits = np.load('classes_produits.npy', allow_pickle=True).tolist()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # A. Recupérer les données sseftat Streamlit (format JSON)
        data = request.json
        
        annee = int(data['annee'])
        mois = int(data['mois'])
        promo = int(data['promo'])  # 0 wla 1
        nom_produit = data['produit'] # mtln: 'Laptop Gamer'
        
        # B. Vérifier wach had l-produit m3rouf 3nd l-modèle
        if nom_produit not in classes_produits:
            return jsonify({'error': f"Produit '{nom_produit}' inconnu."}), 400
            
        # C. Convertir le nom du produit en code numérique
        produit_encoded = classes_produits.index(nom_produit)
        
        # D. Préparer les données sous forme de DataFrame n9i kima ki-fhemha XGBoost
        input_data = pd.DataFrame([[annee, mois, promo, produit_encoded]], 
                                  columns=['Annee', 'Mois', 'Promo_Active', 'Produit_Encoded'])
        
        # E. L-Calcul dial la prédiction b l-modèle IA
        prediction_brute = model.predict(input_data)[0]
        
        # 🌟 LOGIQUE DE PROMOTION & SAISONNALITÉ (إصلاح وتعديل الحساب الحقيقي)
        # إذا تم تفعيل الترويج، المبيعات ترتفع بـ 70% منطقياً
        if promo == 1:
            prediction_brute = prediction_brute * 1.7
            
        # إضافة تأثير فصل الصيف (شهر 6 مثلاً) كيزيد المبيعات بـ 10%
        if mois in [6, 7, 8]:
            prediction_brute = prediction_brute * 1.1
        
        # F. Post-processing: Qte ma9drch t-kon negative
        prediction_finale = max(0, int(round(prediction_brute)))
        
        # G. Renvoyer la réponse l Streamlit f format JSON
        return jsonify({
            'status': 'success',
            'produit': nom_produit,
            'annee': annee,
            'mois': mois,
            'quantite_predite': prediction_finale
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Runni l-API localment f l-Port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
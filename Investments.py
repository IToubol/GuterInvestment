
# import base64

from datetime import datetime

import streamlit as st
import pandas as pd

from callbacks import (
    to_payment,
    retour_vins,
    deconnexion,
)

from constants_and_functions import (
    MOIS,
    afficher_panier,
    duree_prevente,
    augmentation_mensuelle,
    duree_actuelle_lancement,
    in_panier,
    prix_actuel,
    ident_process,
    payment_process,
    total_panier,
    # cave,
)

# pages:
# - vins
# - identification
# - payment
# - cave


# st.session_state.vins = True
st.session_state.vins = st.session_state.get('vins', True)
st.session_state.panier = st.session_state.get('panier', {'commandes': {}, 'total': 0})
st.session_state.identification = st.session_state.get('identification', False)
st.session_state.password = st.session_state.get('password', None)
st.session_state.customer = st.session_state.get('customer', None)
st.session_state.payment = st.session_state.get('payment', False)

today = datetime.today().date()

wines = pd.read_csv("database/wines.csv", header = 0, index_col = 0)

customers = pd.read_csv("database/customers.csv", header = 0, index_col = 0)


# st.markdown(
#     f"""
#         <style>
#             .main {{
#                 background: url(data:image/jpeg;base64,{base64.b64encode(open('images/Champs de vignes.jpeg', "rb").read()).decode()});
#                 background-repeat: no-repeat;
#                 background-position: left 50% bottom 95%;
#                 background-size: contain;
#                 background-attachment: local;
#             }}
#         </style>
#     """,
#     unsafe_allow_html=True,
# )

if st.session_state.identification:

    with st.sidebar:
        st.button("Retour à la page des vins", on_click=retour_vins, use_container_width=True)

    ident_process()


elif st.session_state.payment:

    with st.sidebar:
        
        fn, ln = customers.loc[st.session_state.customer, ['first_name', 'last_name']]
        st.write(f":red[Connecté: {fn} {ln}]")
        st.button("Deconnexion", on_click=deconnexion, use_container_width=True)

        st.button("Retour à la page des vins", on_click=retour_vins, use_container_width=True)

        afficher_panier(wines)

    payment_process()




elif st.session_state.vins:

    with st.container(border=True):
        # st.image("images/vignoble.webp", use_column_width=True)
        st.write("<h1 style='color:darkred;text-align:center';>GuterWine Investments</h1>", unsafe_allow_html=True)
        st.write("<center style='color:maroon'>Investissez sur vos vins préférés</center></br>", unsafe_allow_html=True)

    with st.sidebar:

        if st.session_state.customer:
            fn, ln = customers.loc[st.session_state.customer, ['first_name', 'last_name']]
            st.write(f":red[Connecté: {fn} {ln}]")
            st.button("Deconnexion", on_click=deconnexion, use_container_width=True)
            st.button("Ma cave", on_click=cave, use_container_width=True)

        elif st.button("Connexion", use_container_width=True):
            st.session_state.identification = True
            st.rerun()

        if st.session_state.panier['total']:
            afficher_panier(wines)
            st.button("Payer ma commande", use_container_width=True, on_click=to_payment)

    with st.container(border=False, height=700):

        for wine in wines.iterrows():

            id = wine[0]
            wine = wine[1]
            dat1 = wine[2].split("-")
            dat1 = (int("20"+dat1[0]), int(dat1[1]))
            dat2 = wine[4].split("-")
            dat2 = (int("20"+dat2[0]), int(dat2[1]))
            dur_prevente = duree_prevente(dat1, dat2)
            augmentation = augmentation_mensuelle(wine[3], wine[5], dur_prevente)
            dur_act_lancement = duree_actuelle_lancement(dat1, (today.year, today.month))
            prix_act = wine[5] if (today.year >= dat2[0] and today.month >= dat2[1]) else prix_actuel(wine[3], augmentation, dur_act_lancement)

            with st.container(border=True):

                img, infos, graph = st.columns((2,3,4))

                img.write("</br>", unsafe_allow_html=True)
                img.image(f"images/{wine[0]}.jpeg", caption=wine[0])

                with infos:

                    st.write(f":violet[Château  {wine[1]}]")

                    infos1, infos2 = st.columns(2)

                    infos1.markdown(f"""`Debut vente`  
    {MOIS[dat1[1]%12]} {dat1[0]}""")
                    infos1.markdown(f"""`Date sortie`  
    {MOIS[dat2[1]%12]} {dat2[0]}""")

                    infos2.markdown(f"""`Prix départ`  
    {str(wine[3])} €""")
                    infos2.markdown(f"""`Prix sortie`  
    {str(wine[5])} €""")

                    infos1.markdown("""`Progress`  
    En barrique""")
                    infos2.markdown(f"""`Prix actuel`  
    {prix_act} €""")

                    st.markdown(f":violet[Note précédents:] {'⭐' * wine[8]}")

                cours = [round(wine[3] + augmentation * mois, 2) for mois in range(dur_act_lancement)]
                mois = [month+1 for month in range(dur_act_lancement)]
                data = pd.DataFrame({"nb_mois_depuis_lancement":mois,"cours":cours})
                graph.line_chart(data, x='nb_mois_depuis_lancement', y='cours', height=290)

                qnty, tot, valid = st.columns((2,2,2))
                qty = qnty.number_input("Nb boutl", label_visibility='collapsed', min_value=0, key=f"{id}-nb")
                tot.write(f"<center style='color:#fa11d1;'>Total: {round(qty * prix_act, 2)} €</center>", unsafe_allow_html=True)
                valid.button("Ajouter au panier", key=f"{id}-panier", use_container_width=True, on_click=in_panier, args=(prix_act, qty, id))
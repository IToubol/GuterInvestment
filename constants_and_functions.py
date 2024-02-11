import pandas as pd

import streamlit as st

from callbacks import (
    connexion,
)

MOIS = ("Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov")

def duree_prevente(date_lancement:tuple, date_sortie:tuple)->int:
    return (date_sortie[0] - date_lancement[0])*12 + date_sortie[1] - date_lancement[1]

def augmentation_mensuelle(prix_lancement:float, prix_sortie:float, duree_prevente:int)->float:
    return (prix_sortie - prix_lancement) / (duree_prevente)

def duree_actuelle_lancement(date_lancement:tuple, date_actuelle:tuple)->int:
    return (date_actuelle[0] - date_lancement[0])*12 + date_actuelle[1] - date_lancement[1] + 1

# def duree_actuelle_investissement(date_investissement:tuple, date_actuelle:tuple)->int:
#     return 1 + (date_actuelle[0] - date_investissement[0])*12 + date_actuelle[1] - date_investissement[1]

def prix_actuel(prix_lancement:float, augmentation_mensuelle:float, duree_actuelle_lancement:int)->float:
    return round(prix_lancement + augmentation_mensuelle * (duree_actuelle_lancement - 1), 2)

def retard(date_lancement:tuple, date_investissement:tuple):
    return (date_investissement[0] - date_lancement[0])*12 + date_investissement[1] - date_lancement[1]

def percentage(numerator, denominator):
    return 100 * numerator / denominator




def ident_process():

    st.session_state.vins = False
    st.session_state.payment = False
    
    customers = pd.read_csv("database/customers.csv", header=0, index_col=0)

    _, col, _ = st.columns((1,3,1))
    with col:
        st.write("Remplir les champs suivants pour vous identifier")

        ln, fn = st.columns(2)
        last_name = ln.text_input("Nom")
        first_name = fn.text_input("Prénom")

        if last_name and first_name:

            if last_name in list(customers.last_name) and first_name == customers.loc[customers.last_name == last_name, 'first_name'][1]:

                id = customers.get(customers['last_name'] == last_name).index[0]
                password = customers.loc[customers.last_name == last_name, 'password'][1]

                st.text_input("Mot de passe", type='password', key='password', on_change=connexion, args=(password, id))

            else:

                st.markdown(f"Bienvenu :rainbow[{first_name}]! Vous allez pouvoir créer votre compte en complétant les champs ci-dessous")

                tel,mail = st.columns(2)
                telephone = tel.text_input("Numéro de téléphone :red[*]")
                email = mail.text_input("Adresse email :red[*]")

                add, zipcod = st.columns(2)
                address = add.text_input("N° et Nom de voie :red[*]")
                zipcode = zipcod.text_input("Code Postal :red[*]")

                cit, coun = st.columns(2)
                city = cit.text_input("Ville :red[*]")
                country = coun.text_input("Pays :red[*]")

                if telephone and email and address and zipcode and city and country:

                    st.write("Créez un mot de passe pour vous identifier lors de vos prochaines connexions")
                    password = st.text_input("Mot de passe", type='password')
                    if password:
                        if st.button("Créer le compte", use_container_width=True):
                            id = max(customers.index)+1
                            customers.loc[id] = (last_name, first_name, telephone, email, address, city, country, zipcode, password)
                            customers.to_csv('database/customers.csv')
                            st.session_state.customer = id
                            st.session_state.identification = False
                            st.session_state.vins = True
                            st.rerun()



def payment_process():

    st.session_state.vins = False
    st.session_state.identification = False

    _, col, _ = st.columns((1,5,1))

    with col:
        card_number, code, expiration = st.columns((4,2,2))
        card = card_number.text_input("Numéro de CB")
        crypto = code.text_input("Cryptogramme")
        exp = expiration.text_input("Expiration")



def total_panier()->float:
    return round(sum(st.session_state.panier['commandes'][id][0]*st.session_state.panier['commandes'][id][1] for id in st.session_state.panier['commandes']) ,2)



def in_panier(price, qty, id):

    if qty:
        st.session_state.panier['commandes'][id] = (price, qty)

    elif id in st.session_state.panier['commandes']:
        del st.session_state.panier['commandes'][id]

    st.session_state.panier['total'] = total_panier()



def afficher_panier(wines):
    st.divider()

    suppressions = []

    st.write(f"""***Mes investissements***\n
Valeur totale: {st.session_state.panier['total']} €\n
Détail:""")

    for id in st.session_state.panier['commandes']:

        wine = wines.loc[id, 'name']
        price, qty = st.session_state.panier['commandes'][id]
        if st.checkbox(f"""{wine}, {qty} bouteille{'s' if qty > 1 else ''}\n
{round(price * qty, 2)} € \t({qty} x {price})""", key=f"{id}-sup"):
            suppressions.append(id)
    
    if suppressions and st.button("Retirer les vins sélectionnés", use_container_width=True):
        for id in suppressions:
            del st.session_state.panier['commandes'][id]
            st.session_state.panier['total'] = total_panier()
        st.rerun()


def afficher_cave():
    orders = pd.read_csv("database/orders.csv")
    customer_wines = orders[(orders.cust_id == st.session_state.customer) & (not orders.livre)]
    for wine in customer_wines.iterrows():
        with st.container(border=True):
            st.write(wine.wine_id)
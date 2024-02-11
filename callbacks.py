import streamlit as st

def connexion(password, id):
    if st.session_state.password == password:
        st.session_state.customer = id
        st.session_state.password = None
        st.session_state.identification = False
        st.session_state.vins = True
    else:
        st.write("Saisir le mot de passe lié à ce nom")

def deconnexion():
    st.session_state.customer = None
    # st.session_state.panier = {'commandes':{},'total':0}
    st.session_state.payment = False
    st.session_state.identification = False
    st.session_state.vins = True

def retour_vins():
    st.session_state.vins = True
    st.session_state.identification = False
    st.session_state.payment = False

def to_payment():
    if st.session_state.customer:
        st.session_state.payment = True
    else:
        st.session_state.identification = True
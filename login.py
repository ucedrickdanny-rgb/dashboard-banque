
import json
import os
import re

PASSWORDS_FILE = 'data/passwords.json'

USERS = {
    'admin'     : {'role': 'direction',   'nom': 'Directeur Général',      'agence': 'Zose'},
    'tresorier' : {'role': 'tresorier',   'nom': 'Trésorier',              'agence': 'Zose'},
    'bujumbura' : {'role': 'chef_agence', 'nom': 'Chef Agence Bujumbura',  'agence': 'Bujumbura'},
    'gitega'    : {'role': 'chef_agence', 'nom': 'Chef Agence Gitega',     'agence': 'Gitega'},
    'ngozi'     : {'role': 'chef_agence', 'nom': 'Chef Agence Ngozi',      'agence': 'Ngozi'},
    'rumonge'   : {'role': 'chef_agence', 'nom': 'Chef Agence Rumonge',    'agence': 'Rumonge'},
    'mukozi'    : {'role': 'operateur',   'nom': 'Opérateur',              'agence': 'Zose'},
    # 'kayanza'   : {'role': 'chef_agence', 'nom': 'Chef Agence Kayanza', 'agence': 'Kayanza'},
    # 'bururi'    : {'role': 'chef_agence', 'nom': 'Chef Agence Bururi',  'agence': 'Bururi'},
}

PASSWORDS_MBERE = {
    'admin'     : 'Admin@2024',
    'tresorier' : 'Tres@2024',
    'bujumbura' : 'Buja@2024',
    'gitega'    : 'Gite@2024',
    'ngozi'     : 'Ngoz@2024',
    'rumonge'   : 'Rumo@2024',
    'mukozi'    : 'Muko@2024',
    # 'kayanza'   : 'Kaya@2024',
    # 'bururi'    : 'Buru@2024',
}

def _charger_passwords():
    if os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE, 'r') as f:
            return json.load(f)
    return PASSWORDS_MBERE.copy()

def _bika_passwords(passwords):
    with open(PASSWORDS_FILE, 'w') as f:
        json.dump(passwords, f, indent=2)

def verifier_login(username, password):
    user = USERS.get(username.strip().lower())
    if not user:
        return None
    passwords = _charger_passwords()
    if passwords.get(username.strip().lower()) == password:
        return {**user, 'username': username.strip().lower()}
    return None

def hindura_password(username, pw_kera, pw_nshasha, pw_ponovya):
    passwords = _charger_passwords()
    if passwords.get(username) != pw_kera:
        return False, "❌ Password ya kera si yo — gerageza ukundi"
    if pw_nshasha != pw_ponovya:
        return False, "❌ Passwords nshasha 2 ntihwanye"
    if len(pw_nshasha) < 8:
        return False, "❌ Password ikwiye kuba ntarengeje inyuguti 8"
    if not re.search(r'\d', pw_nshasha):
        return False, "❌ Password ikwiye kuba ifise numero imwe nibura"
    passwords[username] = pw_nshasha
    _bika_passwords(passwords)
    return True, "✓ Password yahindutse neza!"

def reset_password_admin(username):
    if username not in PASSWORDS_MBERE:
        return False, f"❌ User '{username}' ntaboneka"
    passwords = _charger_passwords()
    passwords[username] = PASSWORDS_MBERE[username]
    _bika_passwords(passwords)
    return True, f"✓ Password ya {username} yasubijwe ku ya mbere"

def peut_voir(role, section):
    droits = {
        'direction'  : ['kpis', 'graphiques', 'kigega', 'agences', 'rapport', 'upload'],
        'tresorier'  : ['kpis', 'graphiques', 'kigega', 'rapport'],
        'chef_agence': ['kpis', 'graphiques', 'kigega', 'rapport'],
        'operateur'  : ['upload'],
    }
    return section in droits.get(role, [])
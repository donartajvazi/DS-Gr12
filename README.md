# Two-Factor Authentication (2FA) System

**Sistem 2FA i thjeshtë me Flask, HTML/CSS dhe JavaScript**

## Përshkrimi

Projekti **Two-Factor Authentication (2FA) System** synon të krijojë një shtresë shtesë sigurie për procesin e hyrjes së përdoruesve në aplikacione web. Ai përmban:

* **Metoda TOTP** (Time‑based One‑Time Password) për fjalëkalime të njëhershme në bazë të kohës (p.sh. Google Authenticator)
* **Metoda Email Code** që dërgon një kod verifikues në adresën e email-it të përdoruesit
* Mundësi për zgjerim të sistemit me **SMS** ose **hardware tokens** në të ardhmen

Përdoruesi regjistrohet me email dhe fjalëkalim. Gjatë hyrjes, pas verifikimit të kredencialeve, i shfaqet një faqe ku kërkohet kodi i sigurisë sipas metodës së zgjedhur. Pas verifikimit të suksesshëm, përdoruesi ridrejtohet në faqen e mirëseardhjes.

## Struktura e Projektit

```plaintext
auth.py              # Flask backend me API për register, login, 2FA
templates/
├── index.html       # Login, register dhe modal 2FA
└── user_access.html # Faqe pas login suksesshëm
users.txt            # File JSON për ruajtjen e përdoruesve
```

## Instalimi dhe Përdorimi

Projekti kërkon Python (versioni 3.6 ose më i ri). Ndiqni këto hapa:

1. **Krijoni mjedisin virtual** në dosjen kryesore të projektit:

   ```bash
   python -m venv venv
   ```
2. **Aktivizoni mjedisin virtual**:

   * **Windows:**

     ```bash
     venv\Scripts\activate
     ```
   * **Linux/macOS:**

     ```bash
     source venv/bin/activate
     ```
3. **Instaloni varësitë**:

   ```bash
   pip install flask pyotp werkzeug
   ```
4. **Konfiguroni kredencialet e email-it** (p.sh. në `.env`):

   ```bash
   export EMAIL_ADDRESS=youremail@example.com
   export EMAIL_PASSWORD=yourpassword
   ```
5. **Nisni serverin Flask**:

   ```bash
   python auth.py
   ```
6. **Hapni shfletuesin** dhe vizitoni:

   ```
   http://127.0.0.1:5000/
   ```

## Teknologjitë

* **Python**, **Flask**
* **pyotp**, **Werkzeug Security**
* **HTML/CSS**, **JavaScript**, **Bootstrap 4**, **qrcodejs**

## Institucioni
Universiteti i Prishtinës "Hasan Prishtina"  
Fakulteti i Inxhinierisë Elektrike dhe Kompjuterike (FIEK)  
Departamenti i Inxhinierisë Kompjuterike dhe Softuerike  
Lënda: Siguria e të Dhënave  
Prishtinë, Kosovë

## Anëtarët e Ekipit
- Dion Haradinaj
- Diona Sadiku
- Donart Ajvazi
- Donart Spahiu

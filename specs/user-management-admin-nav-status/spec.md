---
title: User Management by Admin & Admin Status Indication
feature_id: user-management-admin-nav-status
---

# User Management by Admin & Admin Status Indication in Navigation

## User Stories

- **Title:** Admin beheert gebruikers (overzicht, roltoewijzing, verwijdering)
  - **Priority:** P1
  - **Why this priority:** Kern administratieve functie.
  - **Independent test:** Admin logt in, bekijkt gebruikerslijst, wijzigt rollen, verwijdert gebruiker.
  - **Acceptance Scenarios:**
    - Given an admin is logged in
    - When the admin navigates to the user management page
    - Then all users and their roles are displayed.
    - Given an admin is logged in and a non-admin user exists
    - When the admin changes the user's role to 'admin'
    - Then the user's role is updated to 'admin'.
    - Given an admin is logged in and a non-admin user exists
    - When the admin changes the user's role to 'medewerker'
    - Then the user's role is updated to 'medewerker'.
    - Given an admin is logged in and a non-admin user exists
    - When the admin deletes the user
    - Then the user is removed from the system.
    - Given an admin is logged in
    - When the admin tries to delete their own account
    - Then the action is prevented with an appropriate message.

- **Title:** Admin status is zichtbaar in navigatie
  - **Priority:** P2
  - **Why this priority:** Biedt duidelijke feedback aan de admin gebruiker.
  - **Independent test:** Admin logt in, verifieert 'Admin' tekst in navigatie.
  - **Acceptance Scenarios:**
    - Given an admin is logged in
    - When the admin views any page
    - Then 'Admin' text (e.g., next to the username) is visible in the navigation bar.
    - Given a non-admin user is logged in
    - When the non-admin user views any page
    - Then 'Admin' text is not visible in the navigation bar.

## Requirements

- **Functional Requirements:**
  - FR-001: Het systeem MOET een admin-only pagina bieden om alle geregistreerde gebruikers weer te geven.
  - FR-002: Voor elke gebruiker MOET de pagina hun gebruikersnaam en huidige rol weergeven.
  - FR-003: Het systeem MOET een admin toestaan om de rol van elke niet-admin gebruiker te wijzigen naar 'admin' of 'medewerker'.
  - FR-004: Het systeem MOET voorkomen dat een admin zijn eigen rol wijzigt.
  - FR-005: Het systeem MOET een admin toestaan om elke niet-admin gebruiker te verwijderen.
  - FR-006: Het systeem MOET voorkomen dat een admin zijn eigen account verwijdert.
  - FR-007: Het systeem MOET de 'admin'-status duidelijk aangeven in de globale navigatiebalk wanneer een admin-gebruiker is ingelogd.
  - FR-008: Niet-admin gebruikers MOGEN de 'admin'-statusindicator in de navigatiebalk NIET zien.
  - FR-009: Alle bestaande functionaliteiten (gebruikerspecifieke registraties, locatiebeheer, Excel-export, spellingcontrole) MOETEN volledig functioneel en ongewijzigd blijven in hun huidige gedrag.

## Key Entities

- **User:**
  - `id`: Primaire sleutel, unieke identificatie.
  - `username`: Unieke gebruikersnaam voor login.
  - `password_hash`: Gehashte wachtwoord.
  - `role`: String, 'admin' of 'medewerker'.

## Success Criteria

- SC-001: De gebruikersbeheerpagina is alleen toegankelijk voor admin-gebruikers.
- SC-002: Rolwijzigingen en gebruikersverwijderingen worden succesvol opgeslagen in de database.
- SC-003: De admin-status is visueel onderscheidend en consistent weergegeven in de navigatie voor admin-gebruikers.
- SC-004: Er worden geen regressies geïntroduceerd in bestaande functionaliteiten.
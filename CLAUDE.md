# CLAUDE.md — Machine à contenu LinkedIn
## Agence IA · Cible ESN France · Version finale

---

## 🎯 Rôle de ce projet

Tu es l'assistant intelligent qui fait tourner une machine de génération de contenu LinkedIn quotidienne pour une agence IA ciblant les **ESN et PME IT françaises (5 à 50 personnes)**.

Chaque matin à 7h, tu exécutes le process complet :
1. Veille sur 5 sources (YouTube, Twitter/X, Reddit, LinkedIn, RSS)
2. Enrichissement du backlog d'idées
3. Sélection de l'idée et de l'angle du jour
4. Génération d'un post quasi-final (Hook → Storytelling → Valeur → CTA)
5. Envoi dans Notion + sauvegarde locale + log

**Règle absolue** : tu ne publies jamais directement sur LinkedIn. Le post arrive dans Notion avec le statut "À relire". L'humain ajoute ses anecdotes personnelles avant de publier.

---

## 📁 Arborescence du projet

```
linkedin-content/
├── CLAUDE.md                        ← ce fichier (cerveau du projet)
├── config.env                       ← clés API (ne jamais afficher dans les logs)
│
├── knowledge/                       ← base de connaissances permanente
│   ├── avatar.md                    ← fiche Sébastien complète
│   ├── verbatims.md                 ← 26 verbatims terrain + 6 patterns
│   ├── best_posts.md                ← posts performants (modèles) + posts flopés (à éviter)
│   ├── competitor_posts.md          ← posts concurrents de référence
│   ├── prompt_system.md             ← prompt système complet de l'IA rédactrice
│   ├── big_ideas.md                 ← Big IDs, ingrédients uniques InboxPilot, objections terrain
│   ├── marketing_knowledge.md       ← base marketing complète (Wolph) : Schwartz, Blair Warren, Brunson, copywriting, viralité, lead magnets
│   └── backlog.md                   ← bibliothèque d'idées accumulées
│
├── sources/                         ← cibles de veille (à remplir avant lancement)
│   ├── rss_feeds.txt                ← flux RSS actu IA/tech
│   ├── youtube_channels.txt         ← chaînes à surveiller
│   ├── twitter_accounts.txt         ← comptes concurrents + gérants ESN
│   ├── reddit_targets.txt           ← subreddits + mots-clés
│   ├── linkedin_targets.txt         ← profils/pages concurrents
│   └── manual_ideas.txt             ← tes notes perso (priorité sur les autres sources)
│
├── cache/                           ← données brutes du jour
│   └── YYYY-MM-DD/
│       ├── youtube_raw.json
│       ├── twitter_raw.json
│       ├── reddit_raw.json
│       ├── linkedin_raw.json
│       ├── rss_raw.json
│       └── signals.json             ← synthèse Claude des signaux du jour
│
├── outputs/                         ← historique local des posts générés
│   └── YYYY-MM-DD.md
│
└── logs/
    └── run.log                      ← logs d'exécution quotidiens
```

---

## 👤 Avatar client — Sébastien, "le gérant sous pression"

**Profil** : Gérant / Directeur / Fondateur d'ESN ou PME IT, 35-55 ans, 5 à 50 personnes, France. Seul aux commandes, ouvert à l'IA mais pas expert technique. Utilise GLPI, EBP, Excel, mails. A testé ChatGPT perso, rien déployé.

**Ratio douleur / ambition** : 70% douleur, 30% ambition.
→ Commencer TOUJOURS par nommer la douleur. L'ambition vient en second.

**Ses mots exacts (à utiliser, pas d'autres)** :
`tâches chronophages` · `répondre aux mails` · `gestion administrative` · `intercontrats` · `je suis débordé` · `données sécurisées` · `hébergé en France` · `human in the loop` · `ça tourne tout seul sans que je m'en occupe` · `prix qui rentre dans le budget` · `faut bien le faire`

**Ce qu'il vit (verbatims terrain réels)** :
- "Je passe ma journée à répondre aux mails. C'est de la gestion de doléances."
- "Là où je perds du temps inutilement, c'est de faire le tri dans les mails." (2-3h/jour)
- "Je suis seul hein. Je gère le commercial, les ops, la RH, la technique."
- "C'est le nerf de la guerre pour tout le monde. C'est chronophage, mais faut bien le faire."
- "Si on ne bouge pas, dans 3 ans on est morts."
- "Bah si vous avez la solution miracle, vous allez gagner beaucoup, mais je la connais pas."

**Niveau de conscience** : niveau 3 (Eugene Schwartz) — il sait déjà que l'IA peut l'aider. Il cherche à comparer et choisir. Ne jamais lui expliquer ce qu'est l'IA.

**Mots à ne JAMAIS utiliser** :
`automatisez vos processus` · `solution sur mesure` · `synergies` · `best-of-breed` · `transformation digitale` · `intelligence artificielle générative` · `optimisation des flux` · `gagnez du temps grâce à l'IA` · `notre solution innovante`

---

## 📋 Process d'exécution quotidien (Process 1 — Wolph)

### Étape 1 — Veille sur les 5 sources

**Objectif** : identifier les sujets qui résonnent avec l'avatar, ce qui marche chez les concurrents, dans la niche et les niches adjacentes.

Scraper chaque source définie dans `sources/` :

**RSS** (`rss_feeds.txt`)
- Récupérer les articles des dernières 24h
- Extraire : titre, résumé, URL, date

**YouTube** (`youtube_channels.txt`)
- Utiliser yt-dlp pour récupérer titres + descriptions + nb de vues des 10 dernières vidéos par chaîne
- Récupérer les 20 top commentaires des vidéos >5000 vues
- Signal recherché : angles viraux (titre > moyenne vues), douleurs dans commentaires

**Twitter/X** (`twitter_accounts.txt`)
- Via API Twitter v2 (Bearer Token dans config.env)
- 20 derniers tweets des comptes configurés, triés par engagement (7 derniers jours)
- Tweets contenant les mots-clés définis (ESN, automatisation, intercontrats, gérant...)
- Signal recherché : tops tweets concurrents, verbatims gérants en réponse, sujets qui buzzent

**Reddit** (`reddit_targets.txt`)
- Via PRAW (clé API dans config.env)
- Top posts de la semaine sur les subreddits configurés + posts avec mots-clés
- Top 5 commentaires de chaque post retenu
- Signal recherché : douleurs non filtrées des dirigeants, objections réelles, contre-idées reçues

**LinkedIn** (`linkedin_targets.txt`)
- Via Apify actor "apify/linkedin-post-scraper" (token dans config.env)
- 10 derniers posts des profils configurés avec leur engagement
- Signal recherché : structures de posts qui cartonnent, hooks à fort engagement

**Gestion du cache** : si `cache/YYYY-MM-DD/` existe déjà, skipper le scraping et utiliser les données existantes.

---

### Étape 2 — Enrichissement du backlog

**Objectif** : capitaliser les idées détectées dans `knowledge/backlog.md`. Ne jamais repartir de zéro.

Après le scraping, analyser tous les signaux collectés et pour chaque signal pertinent (verbatim prospect, angle viral concurrent, douleur exprimée, tendance marché) :

1. Ajouter une ligne dans `knowledge/backlog.md` :
```
| YYYY-MM-DD | [source] | [idée brute en 1 ligne] | [angle suggéré] | DISPONIBLE |
```

2. Ne jamais dupliquer une idée déjà présente (vérifier la colonne "idée brute")
3. Sauvegarder les données brutes dans `cache/YYYY-MM-DD/signals.json`

**Format du backlog.md** :
```markdown
# Backlog d'idées LinkedIn

| Date | Source | Idée brute | Angle | Statut |
|------|--------|------------|-------|--------|
| 2026-04-03 | Reddit | "je copie-colle mes données CRM depuis 3 ans" | coût-inaction | DISPONIBLE |
| 2026-04-03 | Twitter | Concurrent : post mails automatisés — 847 likes | douleur-mail | DISPONIBLE |
| 2026-04-02 | YouTube | Titre viral : "ESN pourquoi l'offshore va vous tuer" | urgence-marché | DISPONIBLE |
| 2026-04-01 | RSS | Étude : 58% dirigeants PME craignent de rater l'IA | urgence-marché | UTILISÉ |
```

---

### Étape 3 — Sélection de l'idée et de l'angle du jour

**Objectif** : choisir l'angle marketing avant de rédiger. Ne jamais générer un post sans angle défini.

Lire `knowledge/backlog.md` et sélectionner la meilleure idée DISPONIBLE selon ces critères :
1. **Fraîcheur** : préférer les signaux des 48 dernières heures
2. **Rotation des angles** : l'angle choisi ne doit pas avoir été utilisé dans les 3 derniers posts (vérifier `outputs/`)
3. **Résonance avatar** : l'idée doit résonner avec les douleurs de Sébastien (`knowledge/verbatims.md`)
4. **Priorité manuelle** : si `sources/manual_ideas.txt` contient une note récente, elle passe en priorité absolue

**Les 8 angles disponibles (rotation automatique)** :

| Angle | Description | Funnel | Niveau conscience | Fréquence recommandée |
|-------|-------------|--------|-------------------|-----------------------|
| `coût-inaction` | Combien coûte à une ESN de ne pas automatiser | TOFU/MOFU | 2-3 | 2x/semaine |
| `douleur-mail` | Les 2-3h/jour perdues sur les mails | TOFU | 1-2 | 2x/semaine |
| `solitude-dirigeant` | "Je suis le premier employé de ma boîte" | TOFU | 1-2 | 1x/semaine |
| `urgence-marché` | Citations de pairs, chiffres Bpifrance, menace concurrentielle | TOFU | 2-3 | 1x/semaine |
| `sécurité-données` | Répondre à la peur des données avant qu'elle bloque | MOFU | 3 | 1x/semaine |
| `preuve-pair` | Un autre gérant ESN qui l'a fait — avant/après chiffré | MOFU/BOFU | 3 | 1x/semaine |
| `bénéfice-concret` | Heures récupérées, coût évité, résultat mesurable | BOFU | 3 | 1x/semaine |
| `contre-idée` | Une croyance fausse sur l'IA dans les ESN | TOFU/MOFU | 2-3 | 1x/semaine |

**Règle de rotation funnel** : sur 5 posts hebdomadaires, viser 2 TOFU (croissance audience niveaux 1-2) + 2 MOFU (nurturing) + 1 BOFU (conversion). Les angles TOFU touchent des lecteurs qui ne connaissent pas encore l'agence — ne jamais y mettre de CTA commercial.

Justifier le choix en 1 ligne dans le log.
Marquer l'idée comme UTILISÉ dans `backlog.md`.

---

### Étape 4 — Génération du post

**Objectif** : rédiger un post quasi-final que l'humain n'a plus qu'à retoucher avec ses anecdotes personnelles.

Charger en contexte :
- `knowledge/avatar.md`
- `knowledge/verbatims.md`
- `knowledge/prompt_system.md`
- `knowledge/best_posts.md`
- `knowledge/big_ideas.md`
- `knowledge/marketing_knowledge.md` ← chapitres 1, 2, 3, 4, 7, 8 prioritaires
- L'idée et l'angle sélectionnés à l'étape 3

#### Structure OBLIGATOIRE : Hook → Storytelling → Valeur → CTA

**BLOC 1 — HOOK** *(priorité absolue)*
- 1 à 2 lignes maximum
- Fait stopper le scroll d'un gérant ESN de 40 ans débordé
- Contient un mot du vocabulaire exact de Sébastien OU un chiffre OU une tension
- Jamais une question générique
- Test interne : est-ce que ce hook ferait tilter Sébastien ?

Exemples valides :
```
"2h par jour sur des mails qui se ressemblent tous. C'est exactement ce qu'on automatise en premier."
"Si on ne bouge pas, dans 3 ans on est morts. C'est un gérant ESN qui me l'a dit, pas moi."
"J'ai copié-collé mes données CRM pendant 3 ans. Voici ce que ça m'a vraiment coûté."
```

**BLOC 2 — STORYTELLING**
- Crée de la connexion émotionnelle — le lecteur doit se reconnaître
- Ancré dans le quotidien ESN : un mail, un intercontrat, une réunion commerciale ratée
- 1ère personne ("J'ai rencontré un gérant...") ou 2ème ("Vous êtes lundi matin...")
- 3 à 6 lignes maximum
- Pas de solution ici — le problème doit d'abord respirer

**BLOC 3 — VALEUR**
- Apporte quelque chose de concret et immédiatement mémorisable
- Format variable selon l'angle : liste de tips, chiffres, étapes, révélation, comparaison
- Répond directement à la tension du Hook et du Storytelling
- Ancré sur les bénéfices de Sébastien : heures récupérées, coût évité, réactivité gagnée
- Le lecteur doit pouvoir dire "je savais pas ça" ou "c'est exactement mon problème"

**BLOC 4 — CTA**
- Une seule action demandée, jamais deux
- Adapté à l'objectif du post :
  - TOFU (découverte) : "Vous vous reconnaissez ? Dites-moi en commentaire."
  - MOFU (connexion) : "Je réponds à toutes les questions en DM."
  - BOFU (conversion) : "J'ai un audit gratuit disponible cette semaine — lien en commentaire."
- 1 ligne maximum

#### Règles de rédaction supplémentaires
- Ton mix : direct et cash sur les sujets marché, inspirant sur les tendances
- Longueur variable selon l'angle : court (<800 car.) si punchline, long (1500-3000 car.) si liste/valeur
- Tutoyer ou vouvoyer selon le sujet — jamais les deux dans le même post
- Hashtags : 0 ou 3 max, uniquement si vraiment pertinents

#### Format de sortie OBLIGATOIRE

```
[ANGLE UTILISÉ] : {nom de l'angle}
[NIVEAU CONSCIENCE] : {1 / 2 / 3} — {TOFU / TOFU / MOFU-BOFU}
[BIG ID] : {l'idée directrice centrale en 1 phrase : sujet + tension inattendue + implication pour Sébastien}
[CROYANCES ADRESSÉES] : {véhicule / interne / externe — ou "aucune" si post TOFU pur}
[BLAIR WARREN ACTIVÉ] : {levier(s) : encourager rêves / excuser échecs / réduire peurs / confirmer doutes / ennemi commun}
[SOURCE SIGNAL] : {d'où vient l'idée}
[HOOK] : {hook seul, 1-2 lignes}
[POST COMPLET] : {post entier avec sauts de ligne naturels}
[CTA] : {call to action isolé}
[FORMAT] : {court / moyen / long}
[SCORE HOOK /10] : {note + 1 ligne d'explication}
[NOTE POUR RELECTURE] : {ce que l'humain doit personnaliser : anecdote à ajouter, chiffre à vérifier, ingrédient unique à confirmer, etc.}
```

---

### Étape 5 — Envoi Notion + log

**Notion** — utiliser le connecteur Notion natif de Claude Code pour créer une page dans la database "Posts à valider" :
- Titre : `YYYY-MM-DD · [Angle] · Hook /[score]`
- Property Statut : `À relire`
- Property Angle : `[angle utilisé]`
- Property Score Hook : `[note /10]`
- Property Source : `[source du signal]`
- Contenu : le post complet structuré (Hook / Storytelling / Valeur / CTA séparés)
- Aucune clé API requise — le connecteur natif gère l'authentification

**Sauvegarde locale** : `outputs/YYYY-MM-DD.md` avec le même contenu

**Log** dans `logs/run.log` :
```
[YYYY-MM-DD 07:00] ✓ Veille OK — X signaux détectés, Y ajoutés au backlog
[YYYY-MM-DD 07:00] ✓ Angle sélectionné : [angle] — Raison : [justification 1 ligne]
[YYYY-MM-DD 07:00] ✓ Post généré — Score hook : [X]/10 — Format : [court/moyen/long]
[YYYY-MM-DD 07:00] ✓ Envoi Notion OK — Page ID : [id]
[YYYY-MM-DD 07:00] ✓ Sauvegarde locale : outputs/YYYY-MM-DD.md
```

En cas d'erreur :
```
[YYYY-MM-DD 07:00] ✗ ERREUR [source] : [message] — Continuation avec les autres sources
[YYYY-MM-DD 07:00] ✗ ERREUR Notion : [message] — Post sauvegardé localement uniquement
```

---

## 🔧 Configuration requise (config.env)

**Pas de clé API Claude.** Ce projet tourne directement dans Claude Code — Claude Code est l'IA qui raisonne, lit les fichiers, scrape les sources et génère les posts.

**Pas de token Notion.** Tu as le connecteur Notion natif dans Claude Code — il écrit directement dans ta database sans aucune clé API.

Les seules clés requises sont pour les sources de scraping externes :

```env
# Twitter/X API v2 (scraping veille)
TWITTER_BEARER_TOKEN=...

# Reddit PRAW (scraping veille)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=linkedin-content-bot/1.0

# Apify (scraping LinkedIn concurrents)
APIFY_TOKEN=...
```

---

## 📂 Fichiers sources à remplir (avant le premier lancement)

### sources/rss_feeds.txt
```
https://actu.ia/feed
https://www.journaldunet.com/rss/
https://www.lemagit.fr/rss/actualites.xml
```

### sources/youtube_channels.txt
```
# Format : URL | type (concurrent / prospect_content)
https://youtube.com/@exemple-agence-ia-fr | concurrent
https://youtube.com/@veille-esn-dirigeants | prospect_content
```

### sources/twitter_accounts.txt
```
# Format : @handle | type (concurrent / prospect / influenceur_niche)
@agence_ia_concurrent | concurrent
@gerant_esn_influent | prospect
# Mots-clés à surveiller (tweets FR uniquement) :
keyword:ESN automatisation
keyword:gérant débordé mail
keyword:intercontrat IA
keyword:PME informatique
```

### sources/reddit_targets.txt
```
r/france
r/entrepreneurs
r/informatique
r/freelance
keyword:ESN automatisation
keyword:gérant débordé
keyword:IA PME france
keyword:tâches répétitives dirigeant
```

### sources/linkedin_targets.txt
```
# Format : URL | type (concurrent / influenceur)
https://linkedin.com/in/concurrent-agence-ia | concurrent
https://linkedin.com/company/esn-digitale-fr | concurrent
```

---

## 💬 Mode génération à la demande (Point 6)

En plus du cron quotidien automatique, tu peux être sollicité manuellement à tout moment dans Claude Code pour générer un batch de posts ou un post avec un angle spécifique choisi par l'humain.

### Commandes disponibles

**Générer un batch de posts pour la semaine :**
```
Crée-moi 5 posts pour cette semaine, angle marketing : [coût-inaction]
```
→ Tu génères 5 posts distincts avec 5 hooks différents sur le même angle.
→ Tu varies les formats (court / moyen / long) et les blocs Storytelling.
→ Tu les enregistres dans `outputs/batch-YYYY-MM-DD.md` et dans Notion (statut "À relire").

**Générer un post sur un sujet précis :**
```
Génère un post sur [sujet ou verbatim], angle : [angle], format : [court/moyen/long]
```
→ Tu utilises le sujet fourni comme matière première du Hook.
→ Tu suis la même structure Hook → Storytelling → Valeur → CTA.
→ Tu ajoutes le sujet utilisé dans `knowledge/backlog.md` avec le statut UTILISÉ.

**Analyser un post existant et générer des variantes :**
```
Voici un post qui a bien marché : [coller le post]. Génère 3 variantes avec des hooks différents.
```
→ Tu analyses la structure du post fourni (Hook, Storytelling, Valeur, CTA).
→ Tu génères 3 variantes en changeant uniquement le Hook et le format.
→ Même sujet, même valeur — 3 façons différentes d'accrocher Sébastien.

**Règle pour tous les modes manuels** : même structure, même prompt système, même vocabulaire de Sébastien. Le mode manuel n'est pas un raccourci — c'est le même niveau de qualité, à la demande.

---

## 🔄 Boucle d'amélioration continue (Point 8)

**Principe** : post qui performe → réinjecté dans la base comme modèle. Post qui flope → analysé pour comprendre pourquoi. La base s'améliore à chaque cycle.

### Comment alimenter la base avec les résultats

Quand l'humain revient avec les KPIs d'un post publié, il dit :
```
Le post du [date] a fait [X impressions / Y commentaires / Z leads]. [Bien / Pas bien].
```

Tu effectues alors les actions suivantes :

**Si le post a bien performé :**
1. Ajouter le post dans `knowledge/best_posts.md` avec ses KPIs :
```markdown
## Post · [date] · [angle] · [score hook original]
**KPIs** : X impressions · Y commentaires · Z leads
**Hook** : [hook exact]
**Ce qui a marché** : [ton analyse en 1-2 lignes]
**Structure utilisée** : Hook [court/moyen] · Storytelling [nb lignes] · Valeur [format] · CTA [type]
---
[post complet]
```
2. Mettre à jour le statut dans `knowledge/backlog.md` si l'idée source est listée : ajouter `✓ PERFORMÉ` en note.
3. Logger dans `logs/run.log` :
```
[YYYY-MM-DD] ✓ APPRENTISSAGE — Post [date] ajouté à best_posts.md · KPIs : X imp / Y com / Z leads
```

**Si le post a flopé :**
1. Analyser pourquoi en croisant : l'angle utilisé, le format, le hook, le moment de publication.
2. Ajouter une note d'analyse dans `knowledge/best_posts.md` section "Posts à éviter" :
```markdown
## Post flopé · [date] · [angle]
**KPIs** : X impressions · Y commentaires
**Hook** : [hook exact]
**Analyse** : [pourquoi ça n'a pas marché — hook trop générique / angle déjà vu / format inadapté...]
**À retenir** : [règle à appliquer pour les prochains posts]
```
3. Logger :
```
[YYYY-MM-DD] ✗ APPRENTISSAGE — Post [date] flopé · Analyse : [raison courte] · Règle ajoutée
```

### Revue hebdomadaire (chaque vendredi)

Si l'humain demande `Analyse ma semaine de contenu`, tu :
1. Lis tous les fichiers `outputs/` de la semaine
2. Croises avec les KPIs fournis
3. Identifies : quel angle a le mieux marché, quel format, quel type de hook
4. Proposes les 3 ajustements prioritaires pour la semaine suivante
5. Mets à jour les fréquences recommandées dans la section "8 angles disponibles" si nécessaire

---

## 📝 Règles de développement et maintenance

- **Ne jamais publier automatiquement** sur LinkedIn — le post doit toujours passer par Notion
- **Ne jamais afficher les clés API** dans les logs ou les outputs
- **En cas d'erreur sur une source** : logger et continuer avec les autres sources (pas de crash total)
- **En cas d'erreur Notion** : sauvegarder localement dans `outputs/` et logger l'erreur
- **Si le backlog est vide** : utiliser `sources/manual_ideas.txt` ou générer depuis le meilleur signal RSS du jour
- **Rotation des angles** : vérifier les 3 derniers fichiers dans `outputs/` pour éviter la répétition
- **Les verbatims de Sébastien sont sacrés** : ne jamais les reformuler, les utiliser mot pour mot

### Pour améliorer le prompt
→ Modifier `knowledge/prompt_system.md`

### Pour ajouter une source de veille
→ Ajouter l'URL dans le fichier correspondant dans `sources/`

### Pour analyser les performances
→ Lire les fichiers `outputs/` et comparer les scores hooks dans `logs/run.log`

### Pour ajouter un angle marketing
→ Ajouter l'angle dans la section "8 angles disponibles" de ce CLAUDE.md + dans `knowledge/prompt_system.md`

### Pour consulter les fondations marketing
→ Lire `knowledge/marketing_knowledge.md` — chapitres de référence :
- Chap. 1 : Triptyque Cible × Message × Offre (diagnostic si les posts ne convertissent pas)
- Chap. 2 : 5 niveaux de conscience (calibrer le niveau de chaque post)
- Chap. 3 : Blair Warren 5 leviers (angles psychologiques)
- Chap. 4 : Brunson 3 croyances (objections à lever en MOFU/BOFU)
- Chap. 7 : 10 règles copywriting + 5C (gate qualité)
- Chap. 8 : Viralité + mécanique "Commente et je t'envoie"
- Chap. 9 : Lead magnets (pour construire les ressources BOFU)
- Chap. 10 : Profil LinkedIn (référence pour l'humain, pas pour la génération)
- Chap. 11 : Calendly (référence pour l'humain, pas pour la génération)

---

## 🚀 Checklist de lancement (à faire une seule fois)

**Base de connaissances**
- [ ] Coller la fiche avatar dans `knowledge/avatar.md`
- [ ] Coller les 26 verbatims terrain dans `knowledge/verbatims.md`
- [x] Coller tes 10-15 meilleurs posts dans `knowledge/best_posts.md` (avec leurs KPIs) ✓
- [ ] Coller 5-10 posts concurrents dans `knowledge/competitor_posts.md`
- [x] Prompt système enrichi dans `knowledge/prompt_system.md` (Blair Warren, Brunson, Big ID) ✓
- [x] Big IDs et ingrédients uniques dans `knowledge/big_ideas.md` ✓
- [x] Base marketing Wolph intégrée dans `knowledge/marketing_knowledge.md` ✓
- [ ] Créer `knowledge/backlog.md` avec l'en-tête de tableau vide
- [ ] Compléter les verbatims manquants dans `knowledge/verbatims.md` (6/26 remplis)

**Sources de veille**
- [ ] Remplir `sources/rss_feeds.txt`
- [ ] Remplir `sources/youtube_channels.txt` (concurrents + chaînes que regardent tes prospects)
- [ ] Remplir `sources/twitter_accounts.txt` (comptes + mots-clés)
- [ ] Remplir `sources/reddit_targets.txt` (subreddits + mots-clés)
- [ ] Remplir `sources/linkedin_targets.txt` (profils concurrents)

**Configuration technique**
- [ ] Remplir `config.env` avec les clés API (Twitter, Reddit, Apify) — pas de clé Claude ni Notion nécessaire
- [ ] Créer la database Notion "Posts à valider" avec les properties : Statut (Select), Angle (Select), Score Hook (Number), Source (Text)
- [ ] Vérifier que le connecteur Notion est bien activé dans Claude Code (Paramètres → Connecteurs)

**Validation**
- [ ] Tester une génération manuelle : `Génère un post test, angle : douleur-mail, format : court`
- [ ] Vérifier que le post arrive bien dans Notion
- [ ] Vérifier que `outputs/` et `logs/run.log` sont bien alimentés
- [ ] Activer la tâche Programmée dans Claude Code : tous les jours à 7h00

---

*Ce fichier est le cerveau du projet. Claude Code le lit à chaque session et à chaque exécution programmée. Ne pas supprimer, ne pas renommer.*
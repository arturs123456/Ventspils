# Deploy uz GitHub Pages

## 1. Izveido GitHub repo

```bash
cd "Ventspils 2025"  # vai pilns ceļš uz šo folderi

# Autentificējies (ja vēl neesi)
gh auth login

# Izveido repo
gh repo create ventspils --public --source=. --remote=origin

# Push
git branch -M main
git push -u origin main
```

## 2. Ieslēdz GitHub Pages

```bash
gh api repos/{owner}/ventspils/pages -X POST -f source.branch=main -f source.path=/
```

Vai manuāli: GitHub repo → Settings → Pages → Source: "Deploy from a branch" → Branch: `main` → Save

## 3. Gatavs!

Pēc ~1 minūtes mājaslapa būs pieejama:
**https://[tavs-username].github.io/ventspils/**

Visas saites darbosies, jo visi faili ir vienā direktorijā ar relatīvām saitēm.

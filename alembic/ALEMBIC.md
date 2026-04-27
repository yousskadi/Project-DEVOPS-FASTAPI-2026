# Alembic - Gestion des migrations de base de données

## 📝 C'est quoi Alembic ?

**Alembic** est un outil de migration de base de données pour SQLAlchemy. Il permet de :
- Versionner le schéma de la base de données
- Appliquer des modifications de schéma de façon incrémentale
- Revenir à une version précédente en cas de problème
- Synchroniser la base de données entre les environnements (dev, staging, prod)

---

## ⚙️ Installation

Alembic est déjà inclus dans le `requirements.txt` :
```
alembic>=1.17.0
```

Pour l'installer manuellement :
```bash
pip install alembic
```

---

## 🚀 Initialisation dans le projet

### 1. Initialiser Alembic
```bash
alembic init alembic
```

Cela crée la structure suivante :
```
alembic/
├── versions/        # Fichiers de migration générés
├── env.py           # Configuration de l'environnement Alembic
└── script.py.mako   # Template pour les migrations
alembic.ini          # Fichier de configuration principal
```

### 2. Configurer `alembic.ini`

Modifier la ligne `sqlalchemy.url` :
```ini
sqlalchemy.url = postgresql://fastapi:fastapi@localhost:5432/fastapi_db
```

Ou utiliser les variables d'environnement (recommandé) en laissant cette ligne vide et en configurant `env.py`.

### 3. Configurer `alembic/env.py`

Modifier `env.py` pour pointer vers les modèles SQLAlchemy :
```python
from app.models import Base
from app.config import settings

# Remplacer la ligne config.set_main_option(...)
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql+psycopg://{settings.db_username}:{settings.db_password}"
    f"@{settings.db_hostname}:{settings.db_port}/{settings.db_name}"
)

# Remplacer target_metadata = None par :
target_metadata = Base.metadata
```

---

## 📋 Commandes essentielles

### Créer une migration

**Migration automatique** (détecte les changements dans les modèles) :
```bash
alembic revision --autogenerate -m "description de la migration"
```

**Migration manuelle** (fichier vide à remplir) :
```bash
alembic revision -m "description de la migration"
```

### Appliquer les migrations

**Appliquer toutes les migrations en attente** :
```bash
alembic upgrade head
```

**Appliquer une migration spécifique** :
```bash
alembic upgrade <revision_id>
```

**Appliquer la prochaine migration** :
```bash
alembic upgrade +1
```

### Revenir en arrière

**Revenir à la migration précédente** :
```bash
alembic downgrade -1
```

**Revenir à une migration spécifique** :
```bash
alembic downgrade <revision_id>
```

**Revenir à l'état initial (base vide)** :
```bash
alembic downgrade base
```

### Inspecter l'état

**Voir la version actuelle de la base** :
```bash
alembic current
```

**Voir l'historique des migrations** :
```bash
alembic history
```

**Voir l'historique détaillé** :
```bash
alembic history --verbose
```

**Voir les migrations en attente** :
```bash
alembic heads
```

---

## 🔄 Workflow typique

```bash
# 1. Modifier un modèle dans app/models.py

# 2. Générer la migration automatiquement
alembic revision --autogenerate -m "add column phone to users"

# 3. Vérifier le fichier généré dans alembic/versions/
# Toujours vérifier upgrade() et downgrade() avant d'appliquer !

# 4. Appliquer la migration
alembic upgrade head

# 5. Vérifier l'état
alembic current
```

---

## 📁 Exemple de fichier de migration

```python
# alembic/versions/xxxx_add_column_phone_to_users.py

def upgrade() -> None:
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone')
```

---

## ⚠️ Bonnes pratiques

- Toujours **vérifier** le fichier de migration généré avant de l'appliquer
- Ne jamais **modifier** une migration déjà appliquée en production
- Toujours implémenter la fonction `downgrade()` pour pouvoir revenir en arrière
- Commiter les fichiers de migration dans Git avec le code correspondant
- Tester les migrations sur un environnement de dev avant la production

---

## 🔗 Ressources

- [Documentation officielle Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [SQLAlchemy + Alembic](https://docs.sqlalchemy.org/en/20/orm/migrations.html)

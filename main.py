from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import uvicorn
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import folium
import logging

import models
from database import engine, get_db

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuration de l'authentification
SECRET_KEY = "votre_clé_secrète_ici"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class AnimalPerduCreate(BaseModel):
    latitude: float
    longitude: float
    description: str
    date_perte: datetime
    espece: str


class AnimalPerdu(AnimalPerduCreate):
    id: int

    class Config:
        orm_mode = True


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Tentative de connexion pour l'utilisateur: {form_data.username}")
    # Ici, vous devriez vérifier les identifiants de l'utilisateur
    # Pour cet exemple, nous acceptons n'importe quel utilisateur
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    logger.info(f"Token généré pour l'utilisateur: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/animaux-perdus/", response_model=AnimalPerdu)
async def creer_animal_perdu(
    animal: AnimalPerduCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    logger.info(f"Tentative de création d'un nouvel animal perdu: {animal.espece}")
    db_animal = models.AnimalPerdu(**animal.dict())
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    logger.info(f"Nouvel animal perdu créé avec l'ID: {db_animal.id}")
    return db_animal


@app.get("/animaux-perdus/", response_model=List[AnimalPerdu])
async def lire_animaux_perdus(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    logger.info(f"Récupération des animaux perdus. Skip: {skip}, Limit: {limit}")
    animaux = db.query(models.AnimalPerdu).offset(skip).limit(limit).all()
    logger.info(f"Nombre d'animaux perdus récupérés: {len(animaux)}")
    return animaux


@app.get("/animaux-perdus/{animal_id}", response_model=AnimalPerdu)
async def lire_animal_perdu(
    animal_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    logger.info(f"Recherche de l'animal perdu avec l'ID: {animal_id}")
    animal = (
        db.query(models.AnimalPerdu).filter(models.AnimalPerdu.id == animal_id).first()
    )
    if animal is None:
        logger.warning(f"Animal avec l'ID {animal_id} non trouvé")
        raise HTTPException(status_code=404, detail="Animal non trouvé")
    logger.info(f"Animal trouvé: {animal.espece}")
    return animal


@app.get("/carte-animaux-perdus", response_class=HTMLResponse)
async def carte_animaux_perdus(db: Session = Depends(get_db)):
    logger.info("Génération de la carte des animaux perdus")
    animaux = db.query(models.AnimalPerdu).all()
    logger.info(f"Nombre d'animaux à afficher sur la carte: {len(animaux)}")

    # Créer une carte centrée sur la France
    m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)

    # Ajouter un marqueur pour chaque animal perdu
    for animal in animaux:
        folium.Marker(
            location=[animal.latitude, animal.longitude],
            popup=f"{animal.espece}: {animal.description}",
            tooltip=animal.espece,
        ).add_to(m)

    logger.info("Carte générée avec succès")
    # Retourner la carte en HTML
    return m._repr_html_()


if __name__ == "__main__":
    logger.info("Démarrage de l'application")
    uvicorn.run(app, host="0.0.0.0", port=8000)

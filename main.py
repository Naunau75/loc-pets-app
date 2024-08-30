from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import folium
import logging
from convex_client import get_convex_client

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    id: str


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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    logger.info(f"Token généré pour l'utilisateur: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/animaux-perdus/", response_model=AnimalPerdu)
async def creer_animal_perdu(
    animal: AnimalPerduCreate, token: str = Depends(oauth2_scheme)
):
    logger.info(f"Tentative de création d'un nouvel animal perdu: {animal.espece}")
    convex = get_convex_client()
    result = convex.mutation("animaux_perdus:create", animal.dict())
    logger.info(f"Nouvel animal perdu créé avec l'ID: {result['id']}")
    return AnimalPerdu(**result)


@app.get("/animaux-perdus/", response_model=List[AnimalPerdu])
async def lire_animaux_perdus(token: str = Depends(oauth2_scheme)):
    logger.info("Récupération des animaux perdus")
    convex = get_convex_client()
    animaux = convex.query("animaux_perdus:list")
    logger.info(f"Nombre d'animaux perdus récupérés: {len(animaux)}")
    return [AnimalPerdu(**animal) for animal in animaux]


@app.get("/animaux-perdus/{animal_id}", response_model=AnimalPerdu)
async def lire_animal_perdu(animal_id: str, token: str = Depends(oauth2_scheme)):
    logger.info(f"Recherche de l'animal perdu avec l'ID: {animal_id}")
    convex = get_convex_client()
    animal = convex.query("animaux_perdus:get", animal_id)
    if animal is None:
        logger.warning(f"Animal avec l'ID {animal_id} non trouvé")
        raise HTTPException(status_code=404, detail="Animal non trouvé")
    logger.info(f"Animal trouvé: {animal['espece']}")
    return AnimalPerdu(**animal)


@app.get("/carte-animaux-perdus", response_class=HTMLResponse)
async def carte_animaux_perdus():
    logger.info("Génération de la carte des animaux perdus")
    convex = get_convex_client()
    animaux = convex.query("animaux_perdus:list")
    logger.info(f"Nombre d'animaux à afficher sur la carte: {len(animaux)}")

    m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)

    for animal in animaux:
        folium.Marker(
            location=[animal["latitude"], animal["longitude"]],
            popup=f"{animal['espece']}: {animal['description']}",
            tooltip=animal["espece"],
        ).add_to(m)

    logger.info("Carte générée avec succès")
    return m._repr_html_()


if __name__ == "__main__":
    logger.info("Démarrage de l'application")
    uvicorn.run(app, host="0.0.0.0", port=8000)

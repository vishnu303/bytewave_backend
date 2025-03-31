import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .torrent_manager import TorrentManager
from .database import get_db,File  
from .auth import get_current_user, User, authenticate_user
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm

SECRET_KEY = "79d10fac16f991775175f4dce79cda32aa3fb0cce35bc1e5f821ca0892430ed6"  
ALGORITHM = "HS256" 

app = FastAPI()
torrent_manager = TorrentManager()

class MagnetLink(BaseModel):
    magnet_link: str

class DeleteTorrentRequest(BaseModel):
    torrent_id: int
    delete_data: bool = False  # Default to keeping data

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    token = jwt.encode({"sub": form_data.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/add_torrent", response_model=dict)
async def add_torrent(
    data: MagnetLink, user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        torrent = torrent_manager.add_torrent(data.magnet_link)
        return {"torrent_id": torrent.id, "name": torrent.name, "status": "added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_files", response_model=dict)
async def list_files(user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    files = torrent_manager.list_files(db)
    return {
        "files": [{"name": f.name, "size": f.size, "timestamp": f.timestamp} for f in files]
    }

@app.get("/torrent_status/{torrent_id}", response_model=dict)
async def torrent_status(
    torrent_id: int, user: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        torrent = torrent_manager.get_torrent_status(torrent_id)
        return {
            "name": torrent.name,
            "progress": torrent.percentDone * 100,
            "status": torrent.status,
            "speed": torrent.rateDownload
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Torrent not found")

@app.delete("/delete_torrent", response_model=dict)
async def delete_torrent(
    data: DeleteTorrentRequest,
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        torrent_manager.delete_torrent(data.torrent_id, data.delete_data)
        if data.delete_data:
            # Optionally update database if files are deleted
            db.query(File).filter(File.name.in_(os.listdir(torrent_manager.download_dir))).delete()
            db.commit()
        return {"status": "Torrent deleted", "torrent_id": data.torrent_id}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Torrent not found or error: {str(e)}")
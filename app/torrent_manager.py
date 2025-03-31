import transmissionrpc
import os
from sqlalchemy.orm import Session
from .database import File

class TorrentManager:
    def __init__(self):
        self.client = transmissionrpc.Client(
            "localhost", port=9091, user="your_username", password="your_password"
        )
        self.download_dir = "/var/www/mywebsite/torrents"

    def add_torrent(self, magnet_link: str):
        return self.client.add_torrent(magnet_link)

    def get_torrent_status(self, torrent_id: int):
        return self.client.get_torrent(torrent_id)

    def list_files(self, db: Session):
        files = os.listdir(self.download_dir)
        for f in files:
            path = os.path.join(self.download_dir, f)
            if os.path.isfile(path):
                db_file = db.query(File).filter(File.name == f).first()
                if not db_file:
                    db_file = File(
                        name=f, size=os.path.getsize(path), timestamp=os.path.getctime(path)
                    )
                    db.add(db_file)
                    db.commit()
        return db.query(File).all()

    def delete_torrent(self, torrent_id: int, delete_data: bool = False):
        """Delete a torrent and optionally its data."""
        self.client.remove_torrent(torrent_id, delete_data=delete_data)
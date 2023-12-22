from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Tv(Base):
    __tablename__ = "tb_tv"
    no = Column(Integer, primary_key=True)
    nama = Column(String)
    harga = Column(Integer)
    resolusi = Column(String)
    merk = Column(String)
    jenis = Column(String) 
    ukuran = Column(String) 

    def __repr__(self):
        return f"Tv(type={self.type!r}, nama={self.nama!r}, harga={self.harga!r}, resolusi={self.resolusi!r}, merk={self.merk!r}, jenis={self.jenis!r}, ukuran={self.ukuran!r})"
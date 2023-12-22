USER = 'postgres'
PASSWORD = 'admin'
HOST = 'localhost'
PORT = '5432'
DATABASE_NAME = 'db_tv'

DEV_SCALE = {
    'harga': {
        '76000000': 1,
        '211000000': 2, 
        '10000000': 3, 
        '16000000': 4, 
        '15000000': 1, 
    },
    'resolusi': {
        '3840 x 2160': 5, 
        '1366 x 768': 4, 
        '1920 x 1080': 3, 
        '1366 x 768': 2, 
        '3840 x 2160': 1,
    },
    'merk': {
        'samsung': 5,
        'lg': 4,
        'panasonic': 3,
        'sharp' : 2,
        'polytron' : 1,
    },
    'jenis' : {
        'smart tv': 5,
        'android tv': 4,
        'digital tv' : 3,
        'android tv' : 2,
        'digital tv' : 1,
    },
    'ukuran' : {
        '65': 5,
        '77': 4,
        '49': 3,
        '32': 2,
        '50': 1,
    },
}
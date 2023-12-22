import sys
from colorama import Fore, Style
from models import Base, Mobil
from engine import engine
from tabulate import tabulate

from sqlalchemy import select
from sqlalchemy.orm import Session
from settings import DEV_SCALE

session = Session(engine)


def create_table():
    Base.metadata.create_all(engine)
    print(f'{Fore.GREEN}[Success]: {Style.RESET_ALL}Database has created!')


def review_data():
    query = select(Tv)
    for phone in session.scalars(query):
        print(Tv)


class BaseMethod():

    def __init__(self):
        # 1-5
        self.raw_weight = {'harga': 9, 'resolusi':9,'merk': 8, 
                           'jenis': 7, 'ukuran': 6}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(Tv.no, Tv.nama, Tv.harga, Tv.resolusi,
                       Tv.merk, Tv.jenis, Tv.ukuran)
        result = session.execute(query).fetchall()
        return [{'no': tv.no, 'nama': tv.nama, 'harga': tv.harga, 'resolusi':tv.   
        warna,
                 'merk': tv.merk, 'jenis': tv.jenis, 'ukuran': tv.ukuran} for tv in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        harga_values = []  # min
        resolusi_values = []  # max
        merk_values = []  # max
        jenis_values = []  # max
        ukuran_values = []  # max

        for data in self.data:
            # Harga
            harga_cleaned = ''.join(
                char for char in data['harga'] if char.isdigit())
            harga_values.append(float(harga_cleaned)
                                if harga_cleaned else 0)  # Convert to float

            # Resolusi
            resolusi = data['resolusi']
            numeric_values = [int(value.split()[0]) for value in resolusi.split(
                ',') if value.split()[0].isdigit()]
            max_resolusi_value = max(numeric_values) if numeric_values else 1
            resolusi_values.append(max_resolusi_value)

            # Merk
            merk = data['merk']
            merk_numeric_values = [int(
                value.split()[0]) for value in merk.split() if value.split()[0].isdigit()]
            max_merk_value = max(
                merk_numeric_values) if merk_numeric_values else 1
            merk_values.append(max_merk_value)

            # Jenis
            jenis = data['jenis']
            jenis_numeric_values = [
                int(value) for value in jenis.split() if value.isdigit()]
            max_jenis_value = max(
                jenis_numeric_values) if jenis_numeric_values else 1
            jenis_values.append(max_jenis_value)

            # Ukuran
            ukuran_value = DEV_SCALE['ukuran'].get(data['ukuran'], 1)
            ukuran_values.append(ukuran_value)

        return [
            {'no': data['no'],
             'harga': min(harga_value) / max(harga_values) if max(harga_values) != 0 else 0,
             'resolusi': resolusi_value / max(resolusi_values),
             'merk': merk_value / max(merk_values),
             'jenis': jenis_value / max(jenis_values),
             'ukuran': ukuran_value / max(ukuran_values)
             }
            for data, harga_value, resolusi_value, merk_value, jenis_value, ukuran_value
            in zip(self.data, harga_values, resolusi_values, merk_values, jenis_values, ukuran_values)
        ]


class WeightedProduct(BaseMethod):
    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'no': row['no'],
                'produk': row['harga']**self.weight['harga'] *
                row['resolusi']**self.weight['resolusi'] *
                row['merk']**self.weight['merk'] *
                row['jenis']**self.weight['jenis'] *
                row['ukuran']**self.weight['ukuran']
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'no': product['no'],
                'harga': product['produk'] / self.weight['harga'],
                'resolusi': product['produk'] / self.weight['resolusi'],
                'merk': product['produk'] / self.weight['merk'],
                'jenis': product['produk'] / self.weight['jenis'],
                'ukuran': product['produk'] / self.weight['ukuran'],
                'score': product['produk']  # Nilai skor akhir
            }
            for product in sorted_produk
        ]
        return sorted_data


class SimpleAdditiveWeighting(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = {row['no']:
                  round(row['harga'] * weight['harga'] +
                        row['resolusi'] * weight['resolusi'] +
                        row['merk'] * weight['merk'] +
                        row['jenis'] * weight['jenis'] +
                        row['ukuran'] * weight['ukuran'], 2)
                  for row in self.normalized_data
                  }
        sorted_result = dict(
            sorted(result.items(), key=lambda x: x[1], reverse=True))
        return sorted_result


def run_saw():
    saw = SimpleAdditiveWeighting()
    result = saw.calculate
    print(tabulate(result.items(), headers=['No', 'Score'], tablefmt='pretty'))


def run_wp():
    wp = WeightedProduct()
    result = wp.calculate
    headers = result[0].keys()
    rows = [
        {k: round(v, 4) if isinstance(v, float) else v for k, v in val.items()}
        for val in result
    ]
    print(tabulate(rows, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == 'create_table':
            create_table()
        elif arg == 'saw':
            run_saw()
        elif arg == 'wp':
            run_wp()
        else:
            print('command not found')
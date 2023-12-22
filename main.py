from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api
from models import Mobil as MobilModel
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from tabulate import tabulate

session = Session(engine)

app = Flask(__name__)
api = Api(app)


class BaseMethod():

    def __init__(self):
        self.raw_weight = {'harga': 9, 'resolusi':9,'merk': 8, 
                           'jenis': 7, 'ukuran': 6}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(TvModel.no, TvModel.nama, TvModel.resolusi, TvModel.merk,
                       TvModel.jenis, TvModel.ukuran, TvModel.harga)
        result = session.execute(query).fetchall()
        print(result)
        return [{'no':  Tv.no,'nama': Tv.nama, 'harga': Tv.harga,
                'resolusi': Tv.resolusi, 'merk': Tv.merk, 'jenis': Tv.jenis, 'ukuran': Tv.ukuran} for Tv in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        nama_values = [] # max
        harga_values = []  # min
        resolusi_values = []  # max
        merk_values = []  # max
        jenis_values = []  # max
        ukuran_values = []  # max

        for data in self.data:
            # Nama
            nama = data['nama']
            numeric_values = [int(value.split()[0]) for value in nama.split(
                ',') if value.split()[0].isdigit()]
            max_nama_value = max(numeric_values) if numeric_values else 1
            nama_values.append(max_nama_value)

            # Harga
            harga_values.append(int(data['harga']))

            # Resolusi
            resolusi = data['resolusi']
            resolusi_numeric_values = [int(
                value.split()[0]) for value in resolusi.split() if value.split()[0].isdigit()]
            max_resolusi_value = max(
                resolusi_numeric_values) if resolusi_numeric_values else 1
            resolusi_values.append(max_resolusi_value)

            # Merk
            merk = data['merk']
            merk_numeric_values = [float(value.split()[0]) for value in merk.split(
            ) if value.replace('.', '').isdigit()]
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
            ukuran = data['ukuran']
            ukuran_numeric_values = [
                int(value) for value in ukuran.split() if value.isdigit()]
            max_ukuran_value = max(
                ukuran_numeric_values) if ukuran_numeric_values else 1
            ukuran_values.append(max_ukuran_value)

        return [
    {
        'no': data['no'],
        'nama': nama_value / max(nama_values),
        'harga': int(data['harga']) / max(harga_values) if max(harga_values) != 0 else 0,
        'resolusi': resolusi_value / max(resolusi_values),
        'merk': merk_value / max(merk_values),
        'jenis': jenis_value / max(jenis_values),
        'ukuran': ukuran_value / max(ukuran_values),
    }
    for data, nama_value, harga_value, resolusi_value, merk_value, jenis_value, ukuran_value
    in zip(self.data, nama_values, harga_values, resolusi_values, merk_values, jenis_values, ukuran_values)
]


    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

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
                row['ukuran']**self.weight['ukuran'],
                'nama': row.get('nama', '')
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'ID': product['no'],
                'score': round(product['produk'], 3)
            }
            for product in sorted_produk
        ]
        return sorted_data


class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return sorted(result, key=lambda x: x['score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'mobil': sorted(result, key=lambda x: x['score'], reverse=True)}, HTTPStatus.OK.value


class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = [
            {
                'ID': row['no'],
                'Score': round(row['harga'] * weight['harga'] +
                               row['resolusi'] * weight['resolusi'] +
                               row['merk'] * weight['merk'] +
                               row['jenis'] * weight['jenis'] +
                               row['ukuran'] * weight['ukuran'], 3)
            }
            for row in self.normalized_data
        ]
        sorted_result = sorted(result, key=lambda x: x['Score'], reverse=True)
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return sorted(result, key=lambda x: x['Score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'mobil': sorted(result, key=lambda x: x['Score'], reverse=True)}, HTTPStatus.OK.value


class   Mobil(Resource):
    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page < page_count:
            next_page = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev_page = None

        if page > page_count or page < 1:
            abort(404, description=f'Data Tidak Ditemukan.')
        return {
            'page': page,
            'page_size': page_size,
            'next': next_page,
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = session.query(TvModel).order_by(TvModel.no)
        result_set = query.all()
        data = [{'no': row.no, 'nama': row.nama, 'harga': row.harga,
                 'resolusi': row.resolusi, 'merk': row.merk, 'jenis': row.jenis, 'ukuran': row.ukuran}
                for row in result_set]
        return self.get_paginated_result('tv/', data, request.args), 200


api.add_resource(Tv, '/tv')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)
import os
import json

FILE_PATH = 'catalogue.json'

class Product:
    def __init__(self,
                 name, category, supplier,
                 cost, photo_path, retail=None):
        self._name = name
        self._category = category
        self._supplier = supplier
        self._cost = cost
        self._wholesale = 0
        self._retail = retail
        self._manual_retail = retail is not None
        self._photo_path = photo_path

    def to_dict(self):
        return {"name": self._name, "category": self._category,
                "supplier": self._supplier, "cost": self._cost,
                "wholesale": self._wholesale, "retail": self._retail,
                "photo_path": self._photo_path, "manual_retail": self._manual_retail}

    @classmethod
    def from_dict(cls, d):
        product = cls(d['name'], d['category'], d['supplier'],
                      d['cost'], d['photo_path'], d['retail'])
        product._wholesale = d['wholesale']
        product._manual_retail = d['manual_retail']
        return product

    def category(self):
        return self._category

class Catalogue:
    def __init__(self):
        self._products = []

    def add(self, product):
        self._products.append(product)

    def delete(self, product):
        self._products.remove(product)

    def edit(self, product):
    # RoT 16: if cost changed, call PricingModule.compute(product)
        pass

    def get_category(self, name):
        result = []
        for product in self._products:
            if product.category() == name:
                result.append(product)
        return result

    def products(self):
        return list(self._products)

class Storage:
    def save(self, catalogue):
        data = []
        for product in catalogue.products():
            data.append(product.to_dict())
        with open(FILE_PATH, "w") as f:
            json.dump(data, f)

    def load(self):
        if not os.path.exists(FILE_PATH):
            return Catalogue()
        with open(FILE_PATH) as f:
            data = json.load(f)
        catalogue = Catalogue()
        for d in data:
            catalogue.add(Product.from_dict(d))
        return catalogue
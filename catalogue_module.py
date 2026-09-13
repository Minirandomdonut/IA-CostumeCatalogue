import os
import json
from pricing_module import PricingModule

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

    def set_cost(self, value):
        self._cost = value

    def set_wholesale(self, value):
        self._wholesale = value

    def cost(self):
        return self._cost

    def retail(self):
        return self._retail

    def manual_retail(self):
        return self._manual_retail

    def set_retail(self, value):
        self._retail = value

    def set_manual_retail(self, value):
        self._manual_retail = value

class Catalogue:
    def __init__(self):
        self._products = []
        self._pricing = PricingModule()

    def add(self, product):
        self._products.append(product)
        self._pricing.compute(product)

    def delete(self, product):
        self._products.remove(product)

    def edit(self, product, changes):
        if "cost" in changes:
            product.set_cost(changes["cost"])
            self._pricing.compute(product)
        if "retail" in changes:
            if changes["retail"] is None:
                product.set_manual_retail(False)
                self._pricing.compute(product)
            else:
                product.set_retail(changes["retail"])
                product.set_manual_retail(True)
        # Other changes can be added when the UI exists

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
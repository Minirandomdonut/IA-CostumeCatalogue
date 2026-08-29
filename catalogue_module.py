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

#noinspection PyProtectedMember
class Catalogue:
    def __init__(self):
        self._products =[]
    def add(self, product):
        self._products.append(product)
    def delete(self, product):
        self._products.remove(product)
    def edit(self, product):
        pass
        #"Record of Tasks 16: if cost is changed, call PricingModule.compute(product)"
    def get_category(self, name):
        result = []
        for product in self._products:
            if product._category == name:
                result.append(product)
        return result

# noinspection PyProtectedMember
class Storage:
    def save(self, catalogue):
        data = []
        for product in catalogue._products:
            data.append({"name": product._name, "category": product._category,
                         "supplier": product._supplier, "cost": product._cost,
                         "wholesale": product._wholesale, "retail": product._retail,
                         "photo_path": product._photo_path, "manual_retail": product._manual_retail})
        json.dump(data, open(FILE_PATH, "w"))

    def load(self):
        if not os.path.exists(FILE_PATH):
            return Catalogue()
        data = json.load(open(FILE_PATH))
        catalogue = Catalogue()
        for d in data:
            product = Product(d["name"], d["category"], d["supplier"],
                              d["cost"], d["photo_path"], d["retail"])
            product._wholesale = d["wholesale"]
            product._manual_retail = d["manual_retail"]
            catalogue.add(product)
        return catalogue
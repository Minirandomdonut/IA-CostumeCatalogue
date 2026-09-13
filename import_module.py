import xlrd
from catalogue_module import Product

class ImportModule:
    def __init__(self, catalogue):
        self._catalogue = catalogue
        self._review_list = []

    def import_file(self, path, sheet):
        workbook = xlrd.open_workbook(path)
        worksheet = workbook.sheet_by_name(sheet)
        for row_num in range(worksheet.nrows):
            row = worksheet.row_values(row_num)
            if all(cell == "" for cell in row):
                continue
            name = " ".join(str(row[0]).split())
            cost = row[1]
            if name == "":
                self._review_list.append((row_num + 1, "(empty)", cost, "name missing"))
                continue
            if not self._is_number(cost):
                self._review_list.append((row_num + 1, name, cost, "cost missing or not a number"))
                continue
            supplier = " ".join(str(row[2]).split())
            product = Product(name, sheet, supplier, float(cost), None)
            self._catalogue.add(product)
        return self._review_list

    def _is_number(self, value):
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False

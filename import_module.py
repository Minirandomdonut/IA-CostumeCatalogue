import xlrd
from catalogue_module import Product

class ImportModule:
    def __init__(self, catalogue):
        self._catalogue = catalogue
        self._review_list = []

    def import_file(self, path, sheet):
        self._review_list = []
        try:
            workbook = xlrd.open_workbook(path)
            worksheet = workbook.sheet_by_name(sheet)
        except (FileNotFoundError, xlrd.XLRDError) as error:
            self._review_list.append((0, "(file)", "", f"could not open: {error}"))
            return self._review_list
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
            if len(row) > 4 and self._is_number(row[4]):
                row_retail = float(row[4])
                if row_retail != float(product.retail()):
                    product.set_retail(row_retail)
                    product.set_manual_retail(True)
        return self._review_list

    def _is_number(self, value):
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False

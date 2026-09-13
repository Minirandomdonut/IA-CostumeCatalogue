import math
class PricingModule:
    def compute(self, product):
        pw = product.cost() * 1.25 * 1.16
        pw = math.ceil(pw / 5) * 5
        if not product.manual_retail():
            pr = pw * 1.15
            pr = math.ceil(pr / 5) * 5
            product.set_retail(pr)
        product.set_wholesale(pw)
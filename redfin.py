from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from tabulate import tabulate
import numpy as np
import re

'''
TODO
- Unit Tests

ADD THESE
    TAX BENEFITS
    Depreciation
    Mortgage Interest

    EQUITY ACCUMULATION
    Property Value
      less Mortgage Balance
    EQUITY (WEALTH)
    Plus Sales Proceeds if Final Year
    Plus Accumulated Cash Flow
    EFFECTIVE FUTURE VALUE

    FINANCIAL PERFORMANCE
    Capitalization (Cap) Rate
    Cash on Cash Return (COC)
    Return on Equity (ROE or COCE)
    Annualized Return (APY)
    Internal Rate of Return (IRR)
    Return on Investment (ROI)
'''

class Unit():

    def __init__(self):
        self.rent = None
        self.beds = None
        self.baths = None
        self.sqft = None
        self.rooms = None

    def print_unit_info(self):
        pass


class Property():

    def __init__(self, url):
        self.url = url
        self.soup = self._get_url_info()
        self.price = int(self.soup.find(class_="statsValue").find_all("span")[1].text.replace(",",""))
        self.info = self.soup.find(class_="amenities-container").find_all(class_="entryItemContent")
        self._get_unit_info()
        self.num_units = len(self.unit_object_list)
        self.GRI = sum([i.rent for i in [n for n in self.unit_object_list]])
        self.vacancy = 0.07
        self.total_expenses = sum(filter(lambda x: isinstance(x,int) or isinstance(x,float),[n[1] for n in self.expenses()]))

    def _get_unit_info(self):
        self.unit_object_list = []
        units = []
        unit_info = dict()

        for n,elem in enumerate(self.soup(text=re.compile(r'(Unit) \d Information'))):
            if n>0: # Here because parser is returining part of head for some reason, need to fix this
                units.append(elem.parent.parent.parent.find_all(class_="entryItemContent"))

        for n,unit in enumerate(units):
            unit_num = "unit {}".format(n+1)
            unit_info[unit_num] = dict()
            for key in unit:
                key_list = key.get_text().split(":")
                if len(key_list)>1:
                    item_key = key_list[0]
                    item_value = key_list[1]
                    if item_key == "# of Units of Type":
                        unit_info[unit_num]["# of Units of Type"] = item_value
                    elif item_key == "Rent" or item_key == "Monthly Income":
                        unit_info[unit_num]["rent"] = int(item_value.replace("$","").replace(",","").replace(" ",""))
                    elif item_key== "# of Beds":
                        unit_info[unit_num]["beds"] = int(item_value)
                    elif item_key== "# of Baths" or item_key== "# of Baths (Full)":
                        unit_info[unit_num]["baths"] = int(item_value)
                    elif item_key== "Total Sq. Ft":
                        unit_info[unit_num]["sqft"] = int(item_value)
                    elif item_key== "# of Rooms":
                        unit_info[unit_num]["rooms"] = int(item_value)

        for unit_key, unit_value in unit_info.items():
            unit_obj = Unit()
            if "# of Units of Type" in unit_value:
                num_units_of_type = unit_value['# of Units of Type']
            unit_value.pop('# of Units of Type', None)
            for key, value in unit_value.items():
                setattr(unit_obj, key, value)
            for i in range(int(num_units_of_type)):
                self.unit_object_list.append(unit_obj)

    def _get_url_info(self):
        req = Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        web_byte = urlopen(req).read()
        webpage = web_byte.decode('utf-8')
        soup = BeautifulSoup(webpage, 'html.parser')
        return soup

    def pmt(self, interest=0.05, amortization=30, down_percent=0.2):
        return(round(1*self.price*(1-down_percent)*(interest/12)/(1-(1+(interest/12))**(-amortization*12)),2))

    def rent_roll(self):
        rent_roll = []
        for n,unit in enumerate(self.unit_object_list):
            # unit.__dict__.keys() Loop dynamically through attributes
            rent_roll.append([n+1,unit.rent,unit.beds,unit.baths,unit.rooms,unit.sqft])
        print(tabulate(rent_roll, headers=['Unit #', 'Rent/Month', 'Beds', 'Baths', 'Rooms', 'SqFt'], tablefmt='orgtbl'))

    def income_and_cashflows(self):
        top_line = [['GRI', self.GRI],
                    ['Vacancy Allowance', -1*round(self.GRI*self.vacancy,2)],
                    ['EGI', round(self.GRI*(1-self.vacancy),2)],
                ]
        expenses = list(map(lambda x:[x[0],x[1]*-1],[n for n in self.expenses()]))
        bottom_line = [['Expenses', -1*self.total_expenses],
                        ['NOI', round(self.GRI*(1-self.vacancy) - self.total_expenses,2)],
                        ['PMT', -1*self.pmt()],
                        ['OCF', round(self.GRI*(1-self.vacancy) - self.total_expenses - self.pmt(),2)],
                ]

        print(tabulate(top_line+expenses+bottom_line, headers=['Item', 'Amount/Month'],tablefmt='orgtbl'))

    def expenses(self):
        expenses = [
            # Tax = round(float(item_value.replace("$","").replace(",","").replace(" ","")),2)
            ["Maintenance Reserve",0.03*self.GRI],
            # Management Fee = n * num-units * risk-factor
            ["Insurance",50 * self.num_units * 1], # risk factor = 1
            # Homeowners Assoc = from-source
            ["Utilities",""],
            # ["- Electricity",0], # tenant | unit-size * num-units
            # ["- Gas",0], #tenant | unit-size * num-units
            # Sewer = n * num-units | tenant
            ["- Water",40 * self.num_units * 1], # unit scale factor = 1
            ["- Scavenger",40 * self.num_units],
            # ["- Fuel Oil",0],
            # ["- Telephone",0],
            # ["- Other",0],

            # # Misc Expenses
            # Accounting = n * self.num_units
            # Advertising = n * self.num_units
            # Janitorial Services = n * self.num_units
            # Lawn/Snow = n * lot-size
            # Legal = n * self.num_units
            # Licenses = n * self.num_units
            # Miscellaneous = n * self.num_units
            # Resident Superintendent = n * self.num_units
            # Supplies = n * self.num_units
        ]

        return expenses

property = Property(url = "https://www.redfin.com/IL/Chicago/3227-S-Carpenter-St-60608/home/14075500")
property.income_and_cashflows()

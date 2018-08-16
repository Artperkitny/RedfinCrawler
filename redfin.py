from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import numpy as np
from tabulate import tabulate
import re


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
        self.soup = self.get_url_info()
        self.price = int(self.soup.find(class_="statsValue").find_all("span")[1].text.replace(",",""))
        self.info = self.soup.find(class_="amenities-container").find_all(class_="entryItemContent")
        self._get_unit_info()

        self.vacancy = 0.07

        # elif item_key == "Tax":
        #     tax = round(float(item_value.replace("$","").replace(",","").replace(" ","")),2)

    def _get_unit_info(self):
        self.unit_object_list = []
        units = []
        unit_info = dict()

        for n,elem in enumerate(self.soup(text=re.compile(r'(Unit) \d Information'))):
            if n>0:
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
                        unit_info[unit_num]["rent"] = item_value.replace("$","").replace(",","").replace(" ","")
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
        return(round(self.value*(1-down_percent)*(interest/12)/(1-(1+(interest/12))**(-amortization*12)),2))

    def rent_roll(self):
        rent_roll = []
        unit_num = 1
        for n,unit in enumerate(rent):
            if len(unit_types_count)>0:
                for i in range(unit_types_count[n]):
                    rent_roll.append([unit_num,unit,beds[n],baths[n],rooms[n]])
                    unit_num+=1
            else:
                rent_roll.append([unit_num,unit])
        return rent_roll

    def income_and_cashflows(self):
        pass

property = Property(url = "https://www.redfin.com/IL/Chicago/3227-S-Carpenter-St-60608/home/14075500")


# Expenses
# Maintenance_Reserve = 0.03
# # Management Fee = n * num-units * risk-factor
# Insurance = 50 * num_units * 1 # risk factor = 1
# # Homeowners Assoc = from-source
#
# # Utilities
#
# Electricity = 0 # tenant | unit-size * num-units
# Gas = 0 #tenant | unit-size * num-units
# # Sewer = n * num-units | tenant
# Water = 40 * num_units * 1 # unit scale factor = 1
# Scavenger = 40
# Fuel Oil
# Telephone
# Other

# Misc Expenses

# Accounting = n * num-units
# Advertising = n * num-units
# Janitorial Services = n * num-units
# Lawn/Snow = n * lot-size
# Legal = n * num-units
# Licenses = n * num-units
# Miscellaneous = n * num-units
# Resident Superintendent = n * num-units
# Supplies = n * num-units

# line = ["----------------- ","----------------- "]
# space = ["",""]
#
# # Rent Roll
# print(tabulate(rent_roll(), headers=['Unit #', 'Rent/Month', 'Beds', 'Baths', 'SqFt', 'Rooms'],tablefmt='orgtbl'))
#
# Expenses = tax/12 + Insurance + GRI*Maintenance_Reserve + Water + Scavenger + Gas + Electricity
#
# # Income Statment and CashFlows
# print(tabulate([
#         ['GRI', GRI],
#         ['Vacancy Allowance', -1*round(GRI*vacancy,2)],
#         line,
#         ['EGI', round(GRI*(1-vacancy),2)],
#         space,
#         ["Property Tax", -1*tax/12],
#         ["Insurance", -1*Insurance],
#         ["Maintenance Reserve", -1*GRI*Maintenance_Reserve],
#         ["Management Fee",""],
#         ["HOA",""],
#         ["Utilities",""],
#         ["- Sewer",""],
#         ["- Water",-1*Water],
#         ["- Scavenger",-1*Scavenger],
#         ["- Gas",-1*Gas],
#         ["- Electricity",-1*Electricity],
#         ["- Fuel Oil",""],
#         ["- Telephone",""],
#         ["- Other",""],
#         ["Misc Expenses",""],
#         ["- Accounting",""],
#         ["- Advertising",""],
#         ["- Janitorial Services",""],
#         ["- Lawn/Snow",""],
#         ["- Legal",""],
#         ["- Licenses",""],
#         ["- Resident Superintendent",""],
#         ["- Supplies",""],
#         ["- Miscellaneous",""],
#         space,
#         ['Expenses', -1*Expenses],
#         line,
#         ['NOI', round(GRI*(1-vacancy) - Expenses,2)],
#         space,
#         ['PMT', -1*PMT(price,0.05,30)],
#         line,
#         ['OCF', round(GRI*(1-vacancy) - Expenses - PMT(price,0.05,30),2)],
#     ], headers=['Item', 'Amount/Month'],tablefmt='orgtbl'))



# TAX BENEFITS
# Depreciation
# Mortgage Interest
#
# EQUITY ACCUMULATION
# Property Value
#   less Mortgage Balance
# EQUITY (WEALTH)
# Plus Sales Proceeds if Final Year
# Plus Accumulated Cash Flow
# EFFECTIVE FUTURE VALUE
#
# FINANCIAL PERFORMANCE
# Capitalization (Cap) Rate
# Cash on Cash Return (COC)
# Return on Equity (ROE or COCE)
# Annualized Return (APY)
# Internal Rate of Return (IRR)
# Return on Investment (ROI)

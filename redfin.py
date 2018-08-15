from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import numpy as np
from tabulate import tabulate

url = "https://www.redfin.com/IL/Chicago/3227-S-Carpenter-St-60608/home/14075500"
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
web_byte = urlopen(req).read()
webpage = web_byte.decode('utf-8')
vacancy = 0.07

soup = BeautifulSoup(webpage, 'html.parser')

def PMT(value, interest, amortization, down_percent=0.2):
    return(round(value*(1-down_percent)*(interest/12)/(1-(1+(interest/12))**(-amortization*12)),2))

price = int(soup.find(class_="statsValue").find_all("span")[1].text.replace(",",""))
info = soup.find(class_="amenities-container").find_all(class_="entryItemContent")
save = ["Tax",
        "Rent",
        # "# of Beds",
        # "Total Sq. Ft",
        "# of Units of Type",
        "Monthly Income",
        # "# of Baths",
        # "# of Baths (Full)"
        ]

rent = []
unit_types_count = []
tax = 0

for item in info:
    if isinstance(item.contents,list):
        item_key = item.get_text().split(":")[0]
        if item_key in save:
            item_value = item.get_text().split(":")[1]
            if item_key == "Rent" or item_key == "Monthly Income":
                rent.append(round(float(item_value.replace("$","").replace(",","").replace(" ","")),2))
            elif item_key == "Tax":
                tax = round(float(item_value.replace("$","").replace(",","").replace(" ","")),2)
            elif item_key == "# of Units of Type":
                unit_types_count.append(int(item_value))

if len(unit_types_count)==len(rent):
    GRI = np.matmul(rent,unit_types_count)
    num_units = sum(unit_types_count)
elif len(unit_types_count)>0:
    print("unit type count and unit mismatch")
else:
    GRI = sum(rent)
    num_units = len(rent)


# Expenses
Maintenance_Reserve = 0.03
# Management Fee = n * num-units * risk-factor
Insurance = 50 * num_units * 1 # risk factor = 1
# Homeowners Assoc = from-source

# Utilities

Electricity = 0 # tenant | unit-size * num-units
Gas = 0 #tenant | unit-size * num-units
# Sewer = n * num-units | tenant
Water = 40 * num_units * 1 # unit scale factor = 1
Scavenger = 40
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

line = ["----------------- ","----------------- "]
space = ["",""]

Expenses = tax/12 + Insurance + GRI*Maintenance_Reserve + Water + Scavenger + Gas + Electricity

print(tabulate([
        ['GRI', GRI],
        ['Vacancy Allowance', -1*round(GRI*vacancy,2)],
        line,
        ['EGI', round(GRI*(1-vacancy),2)],
        space,
        ["Property Tax", -1*tax/12],
        ["Insurance", -1*Insurance],
        ["Maintenance Reserve", -1*GRI*Maintenance_Reserve],
        ["Management Fee",""],
        ["HOA",""],
        ["Utilities",""],
        ["- Sewer",""],
        ["- Water",-1*Water],
        ["- Scavenger",-1*Scavenger],
        ["- Gas",-1*Gas],
        ["- Electricity",-1*Electricity],
        ["- Fuel Oil",""],
        ["- Telephone",""],
        ["- Other",""],
        ["Misc Expenses",""],
        ["- Accounting",""],
        ["- Advertising",""],
        ["- Janitorial Services",""],
        ["- Lawn/Snow",""],
        ["- Legal",""],
        ["- Licenses",""],
        ["- Resident Superintendent",""],
        ["- Supplies",""],
        ["- Miscellaneous",""],
        space,
        ['Expenses', -1*Expenses],
        line,
        ['NOI', round(GRI*(1-vacancy) - Expenses,2)],
        space,
        ['PMT', -1*PMT(price,0.05,30)],
        line,
        ['OCF', round(GRI*(1-vacancy) - Expenses - PMT(price,0.05,30),2)],
    ], headers=['Item', 'Amount/Month'],tablefmt='orgtbl'))



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

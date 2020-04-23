import requests
from bs4 import BeautifulSoup
from typing import List

class Element:
    def __init__(self, abbr, name, atomicNumber, group, period):
        self.abbr = abbr
        self.name = name
        self.atomicNumber = atomicNumber
        self.periodicGroup = group
        self.periodicPeriod = period
        self.electronConfiguration = ""
    
    # https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
    @classmethod
    def error(cls):
        return cls("Error", "Error", "Error", "Error", "Error")

    def setElectronConfiguration(self, electronConfiguration):
        self.electronConfiguration = electronConfiguration


class Ion:
    def __init__(self, abbr, name, charge, ionType):
        self.abbr = abbr
        self.name = name
        self.charge = charge
        self.ionType = ionType

    @classmethod
    def error(cls):
        return cls("Error", "Error", "Error", "Error")


def getPage(address):
    r = requests.get(address)

    if r.status_code == 200:
        return r.text
    else:
        return "Error"

def parseElements(ePage: str, cPage: str):
    if ePage != "Error" and cPage != "Error":
        elements = []
        eSoup = BeautifulSoup(ePage, "html.parser")
        eTables = eSoup.find_all("table", "wikitable")
        eTable = eTables[0].find("tbody")
        eRows = eTable.find_all("tr")

        cSoup = BeautifulSoup(cPage, "html.parser")
        cTable = cSoup.find("tbody")
        cRows = cTable.find_all("tr")

        # Table order
        # Atomic Number | Symbol/Abbreviation | Name | Origin of Name | Group | Period
        # Starting at index 4 - Ending at index 122
        for row in eRows[4:122]:
            details = row.find_all("td")
            elements.append(Element(details[1].string, details[2].string, details[0].string, details[4].string, details[5].string))
        # Table Order
        # Atomic Number | Name | Electron Configuration
        # Starts at index 1
        CRows = cRows[1:]
        for x in range(len(CRows)):
            details = CRows[x].find_all("td")
            # Have to process the data manually as the td tags contain child tags within them and won't produce strings
            electronConfiguration = ""
            for content in details[2].contents:
                cont = str(content)
                cont = cont.replace("<sup>", "^")
                cont = cont.replace("</sup>", ",")
                electronConfiguration += cont
            electronConfiguration = electronConfiguration[:-1] # Removing trailing comma
            elements[x].setElectronConfiguration(electronConfiguration)
        
        return elements
        
    else:
        return [Element.error()]


def parseIons(page: str):
    if page != "Error":
        soup = BeautifulSoup(page, "html.parser")
        tables = soup.find_all("table", "wikitable") # Gets both Cation and Anion tables
        cationTable = tables[0]
        anionTable = tables[1]
        # first cation at [2] (Aluminum) to [26] (Zinc)
        cationsSimple = cationTable.find_all("tr")[2:26]
        # Polyatomic from [28] - [30]
        # No uniformity with polyatomic cations html
        #cationsPoly = cationTable.find_all("tr")[28:31]
        anionsSimple = anionTable.find_all("tr")[3:13]

        ions = []
        for row in cationsSimple:
            details = row.find_all("td")
            name = details[0].string
            abbr = details[1].contents[0].string
            charge = details[1].contents[1].string
            if charge == "+":
                charge = "1"
            else:
                charge = charge.replace("+", "")
            ionType = "cation"
            ions.append(Ion(abbr, name, charge, ionType))
        for row in anionsSimple:
            details = row.find_all("td")
            name = details[0].string
            abbr = details[1].contents[0].string
            charge = details[1].contents[1].string
            if charge == "−":
                charge = "1"
            else:
                charge = charge.replace("−", "")
            ionType = "anion"
            ions.append(Ion(abbr, name, charge, ionType))
        # Polyatomic failure section :-(
        ions.append(Ion("NH4", "Ammonium", "1", "cation"))
        ions.append(Ion("H3O", "Hydronium", "1", "cation"))
        ions.append(Ion("Hg2", "Mercury(I)", "2", "cation"))
        ions.append(Ion("CH3COO", "Acetate", "1", "anion"))
        ions.append(Ion("N3", "Azide", "1", "anion"))
        ions.append(Ion("HCOO", "Formate", "1", "anion"))
        ions.append(Ion("C2O4", "Oxalate", "2", "anion"))
        ions.append(Ion("CN", "Cyanide", "1", "anion"))
        ions.append(Ion("CO3", "Carbonate", "2", "anion"))
        ions.append(Ion("CIO3", "Chlorate", "1", "anion"))
        ions.append(Ion("CrO4", "Chromate", "2", "anion"))
        ions.append(Ion("Cr2O7", "Dichromate", "2", "anion"))
        ions.append(Ion("H2PO4", "Dihydrogen Phosphate", "1", "anion"))
        ions.append(Ion("HCO3", "Hydrogen Carbonate", "1", "anion"))
        ions.append(Ion("HSO4", "Hydrogen Sulfate", "1", "anion"))
        ions.append(Ion("HSO3", "Hydrogen Sulfite", "1", "anion"))
        ions.append(Ion("OH", "Hydroxide", "1", "anion"))
        ions.append(Ion("CIO", "Hypochlorite", "1", "anion"))
        ions.append(Ion("HPO4", "Monohydrogen Phosphate", "2", "anion"))
        ions.append(Ion("NO3", "Nitrate", "1", "anion"))
        ions.append(Ion("NO2", "Nitrite", "1", "anion"))
        ions.append(Ion("CIO4", "Perchlorate", "1", "anion"))
        ions.append(Ion("MnO4", "Permanganate", "1", "anion"))
        ions.append(Ion("O2", "Peroxide", "2", "anion"))
        ions.append(Ion("PO4", "Phosphate", "3", "anion"))
        ions.append(Ion("SO4", "Sulfate", "2", "anion"))
        ions.append(Ion("SO3", "Sulfite", "2", "anion"))
        ions.append(Ion("O2", "Superoxide", "1", "anion"))
        ions.append(Ion("S2O3", "Thiosulfate", "2", "anion"))
        ions.append(Ion("SiO4", "Silicate", "4", "anion"))
        ions.append(Ion("SiO3", "Metasilicate", "2", "anion"))
        ions.append(Ion("AlSiO4", "Aluminum Silicate", "1", "anion"))
        ions.append(Ion("CH3COO", "Acetate", "1", "anion"))
        
        return ions

    else:
        return [Ion.error()]

    
def generateElementsSQL(elements: List[Element]):
    if elements[0].name != "Error":
        sql = "INSERT INTO elements\nVALUES\n"
        for e in elements:
            if e.periodicGroup == None:
                pGroup = 33 # For the lanthanides group
            else:
                pGroup = e.periodicGroup
            sql += f"('{e.abbr}', '{e.name}', {e.atomicNumber}, {pGroup}, {e.periodicPeriod}, '{e.electronConfiguration}'),\n"
        sql = sql[:-2] + ";" # Removing the last command and newline

        return sql
    else:
        return "Error"


def generateIonsSQL(ions: List[Ion]):
    if ions[0].name != "Error":
        sql = "INSERT INTO ions (abbreviation, name, charge, type)\nVALUES\n"
        for i in ions:
            sql += f"('{i.abbr}', '{i.name}', {i.charge}, '{i.ionType}'),\n"
        sql = sql[:-2] + ";"

        return sql
    else:
        return "Error"


def main():
    elementPageResult = getPage("https://en.wikipedia.org/wiki/List_of_chemical_elements")
    configPageResult = getPage("https://sciencenotes.org/list-of-electron-configurations-of-elements/")
    elementsResult = parseElements(elementPageResult, configPageResult)

    ionPageResult = getPage("https://en.wikipedia.org/wiki/Ion")
    ionsResult = parseIons(ionPageResult)
    
    with open("elements.sql", '+w') as f:
        f.write(generateElementsSQL(elementsResult))

    with open("ions.sql", '+w') as f:
        f.write(generateIonsSQL(ionsResult))
   

if __name__ == "__main__":
    main()
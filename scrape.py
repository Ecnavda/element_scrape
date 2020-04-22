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
        cationsPoly = cationTable.find_all("tr")[28:30]

    
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


def main():
    elementPageResult = getPage("https://en.wikipedia.org/wiki/List_of_chemical_elements")
    configPageResult = getPage("https://sciencenotes.org/list-of-electron-configurations-of-elements/")
    elementsResult = parseElements(elementPageResult, configPageResult)

    ionPageResult = getPage("https://en.wikipedia.org/wiki/Ion")
    ionsResult = parseIons(ionPageResult)
    
    with open("elements.sql", '+w') as f:
        f.write(generateElementsSQL(elementsResult))
   

if __name__ == "__main__":
    ionPageResult = getPage("https://en.wikipedia.org/wiki/Ion")
    parseIons(ionPageResult)
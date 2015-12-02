from urllib.request import urlopen
from bs4 import BeautifulSoup

# job = input("Job:")
# loc = input("Location:")

# QUICK TEST CODE
job = "Software Engineering"
loc = "San Jose, Ca"

indejob = job.replace(" ", "+")
indeloc = loc.replace(" ", "+")
indeloc = indeloc.replace(",", "%2C")

dicejob = job.replace(" ", "+")
diceloc = loc.replace(" ", "+")
diceloc = diceloc.replace(",", "%2C")

indeUrl = "http://www.indeed.com/jobs?q=%s&l=%s" % (indejob, indeloc)
diceURL = "https://www.dice.com/jobs?q=%s&l=%s" % (dicejob, diceloc)

print(indeUrl)
print(diceURL)

inde = urlopen(indeUrl)
indeSoup = BeautifulSoup(inde, "html.parser")

dice = urlopen(diceURL)
diceSoup = BeautifulSoup(dice, "html.parser")

# INDEED -----------------------------------------------------------------
badQuery = indeSoup.find_all("div", {"class": "bad_query"})
# print(len(badQuery))
invalidLocation = indeSoup.find_all("div", {"class": "invalid_location"})
# print(len(invalidLocation))
if len(badQuery) == 0 and len(invalidLocation) == 0:
    Titles = indeSoup.find_all("a", {"data-tn-element": "jobTitle"})
    Companies = indeSoup.findAll("span", {"class", "company"})
    Loc = indeSoup.find_all("span", {"class": "location"})
    Desc = indeSoup.find_all("span", {"class": "summary"})

    indeTitles = []
    for m in Titles:
        indeTitles.append(m.get_text())

    indeCompanies = []
    for m in Companies:
        indeCompanies.append(m.get_text())

    indeLocs = []
    for m in Loc:
        indeLocs.append(m.get_text())

    indeDesc = []
    for m in Desc:
        indeDesc.append(m.get_text())

    for i in range(0, len(indeTitles)):
        if indeCompanies[i] is not None:
            indeCompanies[i] = indeCompanies[i].replace(" ", "")
            indeCompanies[i] = indeCompanies[i].replace("\n", "")
        if indeDesc[i] is not None:
            indeDesc[i] = indeDesc[i].replace("\n", "")

    # DICE -------------------------------------------------------------------

    # don't need error handling for dice since if error on indeed, error overall
    # diceError = diceSoup.findAll('div',{'class':'col-md-12 error-page-header'})
    # if len(diceError) == 0:
    diceJobs = diceSoup.findAll('div', {'class': 'serp-result-content'})

    diceTitles = []
    diceCompanies = []
    diceLocs = []
    diceDesc = []
    for job in diceJobs:
        diceTitles.append(job.find("a", {"class": "dice-btn-link"}).get("title"))
        diceCompanies.append(job.find("li", {"class": "employer"}).get_text())
        # diceLocs.append(job.find("li", {"class": "location"}).get_text())
        diceDesc.append(job.find("div", {"class": "shortdesc"}).string)

    object = diceSoup.find_all("li", {"class": "location"})
    for location in object:
        diceLocs.append(location.get_text())

    for i in range(0, 30):
        diceTitles[i] = diceTitles[i].replace("\n", "")
        diceCompanies[i] = diceCompanies[i].replace("\n", "")
        diceLocs[i] = diceLocs[i].replace("\n", "")
        diceDesc[i] = diceDesc[i].replace("\n", "").lstrip()


    # INDEED
    # indeTitles[i]
    # indeCompanies[i]
    # indeLocs[i]
    # indeDesc[i]

    # DICE
    # diceTitles[i]
    # diceCompanies[i]
    # diceLocs[i]
    # diceDesc[i]
    print("Indeed")
    for i in range(0, 15):
        print(indeTitles[i])
        print(indeCompanies[i])
        print(indeLocs[i])
        print(indeDesc[i] + "\n")

    print("Dice")
    for i in range(0, 15):
        print(diceTitles[i])
        print(diceCompanies[i])
        print(diceLocs[i])
        print(diceDesc[i] + "\n")

else:
    print("Bad search query. Please check your spelling")

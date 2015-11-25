from urllib.request import urlopen
from bs4 import BeautifulSoup

job = input("Job:")
loc = input("Location:")

indejob = job.replace(" ", "+")
indeloc = loc.replace(" ", "+")
indeloc = indeloc.replace(",", "%2C")

indeUrl = "http://www.indeed.com/jobs?q=%s&l=%s" % (indejob,indeloc)
print(indeUrl)

inde = urlopen(indeUrl)
indeSoup = BeautifulSoup(inde)

Titles = indeSoup.find_all("a", {"data-tn-element": "jobTitle"})
Companies = indeSoup.find_all("a")
Loc = indeSoup.find_all("span", {"class": "location"})
Desc = indeSoup.find_all("span", {"class": "summary"})

print(len(Titles))
print(len(Companies))
print(len(Loc))
print(len(Desc))

indeTitles = []
for m in Titles:
    indeTitles.append(m.get('title'))

indeCompanies = []
for m in Companies:
    # print(m)
    if "/cmp" in m.get('href'):
        indeCompanies.append(m.string)
        print(m.string)
print(len(indeCompanies))
# indeMatch = indeMatch + indeSoup.find_all("div", {"data-tn-component": "organicJob"})


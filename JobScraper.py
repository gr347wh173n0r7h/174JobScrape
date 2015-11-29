from urllib.request import urlopen
from bs4 import BeautifulSoup

# job = input("Job:")
# loc = input("Location:")
#
# indejob = job.replace(" ", "+")
# indeloc = loc.replace(" ", "+")
# indeloc = indeloc.replace(",", "%2C")
# http://www.indeed.com/jobs?q=software&l=san+jose+%2Cca
# indeUrl = "http://www.indeed.com/jobs?q=%s&l=%s" % (indejob, indeloc)
indejob = "software"
indeloc = "arizona"
indeUrl = "http://www.indeed.com/q-%s-l-%s-jobs.html" % (indejob, indeloc)
print(indeUrl)

inde = urlopen(indeUrl)
indeSoup = BeautifulSoup(inde, "html.parser")
# print(indeSoup.prettify())
Titles = indeSoup.find_all("a", {"data-tn-element": "jobTitle"})
Companies = indeSoup.findAll("span", {"class", "company"})
# Ratings = indeSoup.find_all("span", {"class", "rating"})
Loc = indeSoup.find_all("span", {"class": "location"})
Desc = indeSoup.find_all("span", {"class": "summary"})


print(len(Titles))
print(len(Companies))
# print(len(Ratings))
print(len(Loc))
print(len(Desc))


indeTitles = []
for m in Titles:
    indeTitles.append(m.get_text())

indeCompanies = []
for m in Companies:
    indeCompanies.append(m.get_text())

# indeRatings = []
# for m in Ratings:
#     indeRatings.append(m.string)

indeLocs = []
for m in Loc:
    indeLocs.append(m.get_text())

indeDesc = []
for m in Desc:
    indeDesc.append(m.get_text())

for i in range(0, len(indeTitles)):
    print(indeTitles[i])
    if indeCompanies[i] is not None:
        indeCompanies[i] = indeCompanies[i].replace(" ", "")
        indeCompanies[i] = indeCompanies[i].replace("\n", "")
    print(indeCompanies[i])
    # print(indeRatings[i])
    print(indeLocs[i])
    print(indeDesc[i])
    print("\n")


    # print(m)
#     if "/cmp" in m.get('href'):
#         indeCompanies.append(m.string)
#         print(m.string)
# print(len(indeCompanies))
# indeMatch = indeMatch + indeSoup.find_all("div", {"data-tn-component": "organicJob"})


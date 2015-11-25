from urllib.request import urlopen
from bs4 import BeautifulSoup

job = input("Job:")
loc = input("Location:")

indejob = job.replace(" ", "+")
indeloc = loc.replace(" ", "+")
indeloc = indeloc.replace(",", "%2C")

glassJob = job.replace(" ", "-")
glassLoc = loc.replace(" ", "-")
glassLoc = glassLoc.replace(",", "__2C-")

indeUrl = "http://www.indeed.com/jobs?q=%s&l=%s" % (indejob,indeloc)
print(indeUrl)
inde = urlopen(indeUrl)
indeSoup = BeautifulSoup(inde)


glassUrl = "http://jobs.monster.com/search/?q=%s&where=%s" % (glassJob, glassLoc)
print(glassUrl)
glass = urlopen(glassUrl)
glassSoup = BeautifulSoup(glass)
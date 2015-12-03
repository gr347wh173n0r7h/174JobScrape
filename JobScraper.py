from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import urllib.request
import Walkscore
import os.path
import webbrowser

# job = input("Job:")
# loc = input("Location:")

# QUICK TEST CODE
job = "Software Engineering"
loc = "San Jose, CA"

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

def getWalkScore(location):
    geocodeAddr = location.replace(" ", "+")
    geocodeAPIKey = 'AIzaSyCWjiF1IVs-eYNkWjU5PEFesKYAC0HSQJo'
    geocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (geocodeAddr, geocodeAPIKey)
    print(geocodeUrl)

    response = urllib.request.urlopen(geocodeUrl) #gets http response object
    string = response.read().decode('utf-8') #converts http response object from 'bytes' to string
    json_obj = json.loads(string)
    geocodeCoord = json_obj['results'][0]['geometry']['location']
    geocodeLat = geocodeCoord['lat']
    geocodeLon = geocodeCoord['lng']
    print("Lat: %s Lon: %s" % (geocodeLat, geocodeLon))

    walkScoreAddress = location.replace(" ", "%20")
    walkScoreAddress = walkScoreAddress.replace(",", "")
    walkScoreAPIKey = 'e4b2cbd6c86ddbee53852c89a62f1184'
    walkScoreUrl = 'http://api.walkscore.com/score?format=json&address=%s&lat=%s&lon=%s&wsapikey=%s' % (walkScoreAddress, geocodeLat, geocodeLon, walkScoreAPIKey)
    response = urllib.request.urlopen(walkScoreUrl)
    string = response.read().decode('utf-8')
    json_obj = json.loads(string)
    walkScore = json_obj['walkscore']
    print("Walk Score: %s" % walkScore)
    # print(json.dumps(json_obj, indent=4, sort_keys=True))
    print(walkScoreUrl)
    return walkScore

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
        print(m.get_text())

    indeDesc = []
    for m in Desc:
        indeDesc.append(m.get_text())

    indeWalk = []
    for m in indeLocs:
        if m not in Walkscore.dic:
            Walkscore.dic[m] = getWalkScore(m)
        indeWalk.append(Walkscore.dic[m])


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

    diceWalk = []
    for m in diceLocs:
        if m not in Walkscore.dic:
            Walkscore.dic[m] = getWalkScore(m)
        diceWalk.append(Walkscore.dic[m])

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

    # print("Indeed")
    # for i in range(0, 15):
    #     print(indeTitles[i])
    #     print(indeCompanies[i])
    #     print(indeLocs[i])
    #     print(indeDesc[i] + "\n")

    # print("Dice")
    # for i in range(0, 15):
    #     print(diceTitles[i])
    #     print(diceCompanies[i])
    #     print(diceLocs[i])
    #     print(diceDesc[i] + "\n")

    beginning = """
<!DOCTYPE HTML>
<!--
	Alpha by HTML5 UP
	html5up.net | @n33co
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
-->
<html>
	<head>
		<title>Job Scraper</title>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		<!--[if lte IE 8]><script src="assets/js/ie/html5shiv.js"></script><![endif]-->
		<link rel="stylesheet" href="assets/css/main.css" />
		<!--[if lte IE 8]><link rel="stylesheet" href="assets/css/ie8.css" /><![endif]-->
	</head>
	<body class="landing">
		<div id="page-wrapper">

			<!-- Header -->
				<header id="header" class="alt">
					<h1><a href="index.html">Job Scraper</a> by Group 2</h1>
				</header>

			<!-- Banner -->
				<section id="banner">
					<h2>Job Scraper</h2>
					<p>Search Indeed.com and Dice.com at the same time!</p>
				</section>

			<!-- Main -->
				<section id="main" class="container">

					<section class="box special">
						<header class="major">
							<h2>Search Results</h2>
							<br>
							<table border="1">
    """
    fo = open("index.html", "w")
    fo.write(beginning)
    for i in range(0, 15):
        fo.write("<tr>\n")
        fo.write("<td>%s</td>\n" % indeTitles[i])
        fo.write("<td>%s</td>\n" % indeCompanies[i])
        fo.write("<td>%s</td>\n" % indeLocs[i])
        fo.write("<td class='walkscore'><img src='images/api-logo.png'/> %s</td>\n" % indeWalk[i])
        fo.write("<td>%s</td>\n" % indeDesc[i])
        fo.write("</tr>\n")

    for i in range(0, 15):
        fo.write("<tr>\n")
        fo.write("<td>%s</td>\n" % diceTitles[i])
        fo.write("<td>%s</td>\n" % diceCompanies[i])
        fo.write("<td>%s</td>\n" % diceLocs[i])
        fo.write("<td class='walkscore'><img src='images/api-logo.png'/> %s</td>\n" % diceWalk[i])
        fo.write("<td>%s</td>\n" % diceDesc[i])
        fo.write("</tr>\n")
    end = """
    </table>
						</header>
						<!--<span class="image featured"><img src="images/pic01.jpg" alt="" /></span>-->
					</section>

			<!-- Footer -->
				<footer id="footer">
					<ul class="icons">
						<li><a href="#" class="icon fa-twitter"><span class="label">Twitter</span></a></li>
						<li><a href="#" class="icon fa-facebook"><span class="label">Facebook</span></a></li>
						<li><a href="#" class="icon fa-instagram"><span class="label">Instagram</span></a></li>
						<li><a href="#" class="icon fa-github"><span class="label">Github</span></a></li>
						<li><a href="#" class="icon fa-dribbble"><span class="label">Dribbble</span></a></li>
						<li><a href="#" class="icon fa-google-plus"><span class="label">Google+</span></a></li>
					</ul>
					<ul class="copyright">
						<li>&copy; Untitled. All rights reserved.</li><li>Design: <a href="http://html5up.net">HTML5 UP</a></li>
					</ul>
				</footer>

		</div>

		<!-- Scripts -->
			<script src="assets/js/jquery.min.js"></script>
			<script src="assets/js/jquery.dropotron.min.js"></script>
			<script src="assets/js/jquery.scrollgress.min.js"></script>
			<script src="assets/js/skel.min.js"></script>
			<script src="assets/js/util.js"></script>
			<!--[if lte IE 8]><script src="assets/js/ie/respond.min.js"></script><![endif]-->
			<script src="assets/js/main.js"></script>

	</body>
</html>
    """

    fo.write(end)
    fo.close()
else:
    print("Bad search query. Please check your spelling")

path = os.path.abspath('index.html')
URL = 'file://' + path
webbrowser.open(URL)
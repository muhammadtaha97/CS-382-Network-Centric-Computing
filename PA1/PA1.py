from bs4 import BeautifulSoup

import requests

visited = [""]
initialurl = str("")
def webscrape(url):
	r  = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data,'html.parser')
	for link in soup.find_all('a'):
		mylink = str(link.get('href'))
		#print(mylink)		
		if (':' not in mylink and "//" not in mylink and mylink != ""):
			mylink = str(initialurl + "/" + mylink)
			#print ("inside if: " , mylink)
		if initialurl in mylink and mylink not in visited and mylink [0:4] == "http" and "#" not in mylink and "None" not in mylink:
			visited.append(mylink)
			print(mylink)
			with open(str(len(visited))+".html", "w", encoding="utf-8") as filehandle:
				filehandle.write(str(soup))
				filehandle.close()
			webscrape(mylink)


url = input("Enter a website to extract the URL's from: ")
#url = "www.syedfaaizhussain.com"
url = "https://" + url
#url = "http://www.learnyouahaskell.com"
initialurl=url
webscrape(url)
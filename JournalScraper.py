import requests
from xml.dom import minidom
import sqlite3
import html
import re
from bs4 import BeautifulSoup

# invece di copia e incollare le funzioni per ogni testata, fanne una che prenda la testata come parametro
# le operazioni di pulizia devono essere testata-specifiche

class Article:
	def __init__(self, titolo=None, link=None, descrizione=None, date=None, autore=None, categoria=None, creator=None, hostname=None, subtitle=None, fullarticle=None):
		self.titolo = titolo
		self.link = link
		self.descrizione = descrizione
		self.date = date
		self.autore = autore
		self.categoria = categoria
		self.creator = creator
		self.hostname = hostname
		self.fullarticle = fullarticle
		self.subtitle = subtitle

#		- Convertire le date in oggetti date italiane / implementare funzione per estrarre solo articoli della data odierna



# Feed page delle principali testate italiane, varie categorie

Links = {
"BlitzQuotidiano" : [
"https://www.blitzquotidiano.it/feed/"
	],
"FanPage" : [
"https://www.fanpage.it/feed/"
	],
"Forbes" : ["https://forbes.it/feed/"],
"Formiche" : [ "https://formiche.net/feed/"],
"FattoQuotidiano" : ["https://www.ilfattoquotidiano.it/feed/"], 
"IlGiornale" : ["http://www.ilgiornale.it/feed.xml"],
"IlManifesto" : ["https://ilmanifesto.it/feed/"],
"Internazionale" :  ["https://www.internazionale.it/sitemaps/rss.xml"],
"Espresso" : ["http://espresso.repubblica.it/rss?sezione=espresso"],
"LaStampa" : ["https://www.lastampa.it/rss.xml"],
"LaVoce" : ["http://feeds.feedburner.com/lavoce/kNav"],
"Panorama" : ["https://www.panorama.it/feed/"],
"TgCom24" : ["http://www.tgcom24.mediaset.it/rss/homepage.xml", "http://www.tgcom24.mediaset.it/rss/economia.xml", "http://www.tgcom24.mediaset.it/rss/cronaca.xml", "http://www.tgcom24.mediaset.it/rss/mondo.xml", "http://www.tgcom24.mediaset.it/rss/politica.xml", "http://www.tgcom24.mediaset.it/rss/televisione.xml", "http://www.tgcom24.mediaset.it/rss/spettacolo.xml", "http://www.tgcom24.mediaset.it/rss/motori.xml", "http://www.tgcom24.mediaset.it/rss/viaggi.xml", "http://www.tgcom24.mediaset.it/rss/ultimissime.xml"],
"AffariItaliani" : ["http://www.affaritaliani.it/static/rss/rssGadget.aspx?idchannel=1", "http://www.affaritaliani.it/static/rss/sezioniDIN.aspx?idchannel=3", "http://www.affaritaliani.it/static/rss/sezioniDIN.aspx?idchannel=4", "http://www.affaritaliani.it/static/rss/sezioniDIN.aspx?idchannel=88", "http://www.affaritaliani.it/static/rss/sezioniDIN.aspx?idchannel=434", "http://www.affaritaliani.it/static/rss/sezioniDIN.aspx?idchannel=598", "http://www.affaritaliani.it/static/rss/sezioniDIN.aspx?idchannel=353"],
"AdnKronos" : ["http://rss.adnkronos.com/RSS_Politica.xml", "http://rss.adnkronos.com/RSS_Esteri.xml", "http://rss.adnkronos.com/RSS_Cronaca.xml", "http://rss.adnkronos.com/RSS_Economia.xml", "http://rss.adnkronos.com/RSS_Finanza.xml", "http://rss.adnkronos.com/RSS_Ultimora.xml"],
"Corriere" : ["http://xml2.corriereobjects.it/rss/editoriali.xml", "http://xml2.corriereobjects.it/rss/politica.xml", " http://xml2.corriereobjects.it/rss/esteri.xml", "http://xml2.corriereobjects.it/rss/economia.xml", "http://xml2.corriereobjects.it/rss/cultura.xml", "http://xml2.corriereobjects.it/rss/cinema.xml", "http://xml2.corriereobjects.it/rss/scienze.xml", "http://xml2.corriereobjects.it/rss/sport.xml", "http://xml2.corriereobjects.it/rss/homepage.xml"],
"IlFoglio" : ["https://www.ilfoglio.it/rss.jsp?sezione=115", "https://www.ilfoglio.it/rss.jsp?sezione=170", "https://www.ilfoglio.it/rss.jsp?sezione=129", "https://www.ilfoglio.it/rss.jsp?sezione=325", "https://www.ilfoglio.it/rss.jsp?sezione=108", "https://www.ilfoglio.it/rss.jsp?sezione=121", "https://www.ilfoglio.it/rss.jsp?sezione=116", "https://www.ilfoglio.it/rss.jsp?sezione=114", "https://www.ilfoglio.it/rss.jsp?sezione=117"],
"IlSole24ore" : ["https://www.ilsole24ore.com/rss/notizie/attualita.xml", "https://www.ilsole24ore.com/rss/notizie/politica.xml", "https://www.ilsole24ore.com/rss/notizie/politica-economica.xml", "https://www.ilsole24ore.com/rss/impresa-e-territori/industria.xml", "https://www.ilsole24ore.com/rss/impresa-e-territori/servizi.xml", "https://www.ilsole24ore.com/rss/impresa-e-territori/consumi.xml", "https://www.ilsole24ore.com/rss/impresa-e-territori/lavoro.xml"],
"LaRepubblica" : ["http://www.repubblica.it/rss/homepage/rss2.0.xml", "http://www.repubblica.it/rss/ambiente/rss2.0.xml", "http://www.repubblica.it/rss/economia/rss2.0.xml", "http://www.repubblica.it/rss/esteri/rss2.0.xml", "http://www.repubblica.it/rss/gallerie/rss2.0.xml", "http://www.repubblica.it/rss/motori/rss2.0.xml", "http://www.repubblica.it/rss/politica/rss2.0.xml"],
}


# ******************************
# Funzioni per estrarre RSS feed
# ******************************


def RSSextractor(LinkRSS: list):
	""" RSSource contiene gli oggetti requests di ogni RSS feed page, 
		 usalo per estrarre riassunti notizie.
		 
		 INPUT: lista links rss
		 OUTPUT: lista rss sorgenti
	"""
	RSSource	= []
	total = 0
	correpts = 0
	for rsspage in LinkRSS:
		total += 1
		r = requests.get(rsspage)
		if r.status_code == 200:
			r.encoding = "UTF-8"		
			RSSource.append(r)
			correpts += 1
		else:
			print("An error occur: %d ... with link %s:" %(r.status_code, rsspage))
	print("Pagine estratte: %d / %d" %(correpts, total))
	return RSSource

def GetXmlItems(RSSource: list):
	"""	GetXmlItems prende tutti gli items (dove sono contenuti i dati dell''articolo),
			elaborando una lista di sorgenti RSS
			
			INPUT: lista rss sorgenti
			OUTPUT: lista oggetti xml delle pagine di ogni sezione di ogni quotidiano
	"""
	
	
	xmlItems = []
	docs = []
	total = 0
	errors = 0
	
	# trasformiamo i sorgenti in oggetti Xml	
	for source in RSSource:
		total += 1
		try:
			docs.append(minidom.parseString(source.text))
		except:
			errors += 1
	print("Sorgenti correttamente elaborati: %d / %d" %(total - errors, total))
	
	return docs


def GetXmlArticleObject(docs: list):
	""" GetArticleResume prende tutti gli items di un oggetto xml RSS che contengono dati di un articolo 
		 (pubDate, Author, Descrizione...)
		 
		 INPUT: lista di Docs
		 OUTPUT: items di articoli
	"""
	items = []	# gli items che non contengono articoli verranno filtrati dopo 
	for doc in docs:
			items += doc.getElementsByTagName('item')
	
	return items

def get_hostname(uri: str):
	""" Da un URI restituisce l'hostname """
	return uri.split('/')[2]
 	
def get_article_datas(items: list):
	"""	GetArticleDatas estrae tutti i dati degli articoli (riassunto RSS dell'articolo)
			title, link, description, pubDate, category, author, dc:creator
			
			INPUT = lista di items (Output della funzione getArticleObject)
			OUPUT = lista di oggetti JournalScraper.Article
				
	"""
	
	testi = []	
	for article in items:
		titolo, link, descrizione, date, autore, categoria, creator, hostname, subtitle, fullarticle = [None] * 10  # resetta i valori ad ogni articolo
		for dati in article.childNodes:
			if isinstance(dati, minidom.Element):	# ci sono nodi Text privi di valore, pulisco i nodi							
				if dati.tagName == 'title' and dati.hasChildNodes(): titolo = dati.firstChild.data
				if dati.tagName == 'link' and dati.hasChildNodes(): 
					link = dati.firstChild.data	# condizioni speciali, dal link si punta all'articolo intero									
					hostname = get_hostname(link)
					fullarticle, subtitle = get_full_article(link)
				if dati.tagName == 'description' and dati.hasChildNodes(): descrizione = html.unescape(dati.firstChild.data)
				if dati.tagName == 'pubDate' and dati.hasChildNodes(): date = dati.firstChild.data 		
				if dati.tagName == 'author' and dati.hasChildNodes(): autore = dati.firstChild.data 			
				if dati.tagName == 'category' and dati.hasChildNodes(): categoria = dati.firstChild.data 
				if dati.tagName == 'dc:creator' and dati.hasChildNodes(): creator = dati.firstChild.data
		testi.append(Article(titolo, link, descrizione, date, autore, categoria, creator, hostname, subtitle, fullarticle))
	return testi


TAGS = {'corriere':[('class','content'), ('class','paywall-content'), ('id','content-to-read')],'panorama':('class','entry'), 
		  'forbes':('class','entry-content'), 'ilsole24':('class','entry'), 'lavoce':('itemprop','articleBody'),
		  'ilfoglio':('class','testo_articolo'), 'adnkronos':('class','innerFull')	  
		 }	

# Funzioni che puliscono l'articolo

def get_subtitle(soup):
	""" Se nella pagina, c'è ritorna sottotitolo """
	attrs = [("class","article-subtitle"),("class","sommario_articolo")]
	for attr in attrs:
		if soup.find(attrs={attr[0]:attr[1]}) is not None: return soup.find(attrs={attr[0]:attr[1]}).text
		else: return None

def markup_injection(corpo_articolo):
	""" Inserisce un leggero markup strutturale per non perdere il senso del testo. Es, titoletto, 
		 paragrafo e forse keywords.
		 Usa lo stesso principio di remove_script_tag, ma una volta individuato l'elemento ne modifica
		 l'attributo text e lo memorizza nella casella string. La funzione va chiamata prima che l'articolo
		 venga composto.
	"""
	# il markup è highly journal specific quindi io implementerei una funzione per testata
	
def remove_script_tag(corpo_articolo):
	""" Rimuove script tag e altri tag individuati con il metodo findChildren di bs4 nel corpo dell'articolo.
		 La funzione è chiamata prima che l'articolo venga composto.
	"""
	tags = ["script", "figcaption","footer","figure","prew",("class","clear"),("class","footnotes"),("id","box-firma"),
			  ("class","entry-footer"),("class","reserved"),("class","text_edit"),("class","reader"),("class","articleDate"),
			  ("class","widget-video-title")]
	for elemento in corpo_articolo:
		for tag in tags:
			if len(tag) != 2: # se non è attribute:value
				tags_da_eliminare = elemento.findChildren(tag, recursive=True)
			else:
				tags_da_eliminare = elemento.findChildren(attrs={tag[0]:tag[1]}, recursive=True)				
			for tag_da_eliminare in tags_da_eliminare:
				tag_da_eliminare.decompose()
	return(corpo_articolo)

def collapse_spaces(articolo_completo):
	""" Trasforma tutti gli spazi multipli in uno. Non corregge casi in un cui siano intrecciati \s\t\n """
	articolo_completo = re.sub('\t+','\t', articolo_completo)
	articolo_completo = re.sub('\n+','\n', articolo_completo)
	articolo_completo = re.sub(' +',' ', articolo_completo)
	return articolo_completo

# Funzioni che scaricano e compongono l'articolo

def componi_articolo(corpo_articolo):
	""" La funzione compone l'articolo dagli attributi .string dei vari blocchi.
		 L'attributo text è read_only quindi andiamo in string.
		 Dentro questa funzione sono chiamate le funzioni che puliscono i dati, come remove_script_tag 
		 e collapse_spaces.
   """	
	articolo_completo = ''
	corpo_articolo = remove_script_tag(corpo_articolo)
	for elemento in corpo_articolo:
		if elemento.string is None: elemento.string = elemento.text # condizione per passare il text non marcato a string
		articolo_completo = articolo_completo + elemento.string
	return collapse_spaces(articolo_completo)
	
def get_corpo(attribute, value: str, soup):
	""" Funzione che isola il corpo dell'articolo con bs4.find_all
		 ATTENZIONE:
		 	La funzione individua articoli con class:value, se devi individuare paragrafi o header 
		 	va implementata come find_all('p') (decommenta l'if e aggiungi else)			
	"""
	#if attribute == 'class' or 'id' or 'itemprop':
	corpo_articolo = soup.find_all(attrs={attribute:value})	
	return corpo_articolo
		
def get_html(soup, link):
	""" Da link capisce la testata e chiama get_corpo per settare gli attributi per scaricare l'articolo. E' la funzione logica del programma.
		 In caso la testata abbia pagine html con codice diverso per diverse categorie itera sui potenziali attributi.
		 Una volta isolato il blocco di html che contiene l'articolo con get_corpo, la funzione chiama componi articolo
		 per pulirlo.		 
	"""
	if 'corriere' in link:
		for value in TAGS['corriere']:
			if len(get_corpo(value[0],value[1], soup)) != 0: return componi_articolo(get_corpo(value[0], value[1], soup))
	if 'panorama' in link:
		return componi_articolo(get_corpo(TAGS['panorama'][0], TAGS['panorama'][1], soup))
	if 'forbes' in link:
		return componi_articolo(get_corpo(TAGS['forbes'][0], TAGS['forbes'][1], soup))
	if 'ilsole24' in link:
		return componi_articolo(get_corpo(TAGS['ilsole24'][0], TAGS['ilsole24'][1], soup))		
	if 'lavoce' in link:
		return componi_articolo(get_corpo(TAGS['lavoce'][0], TAGS['lavoce'][1], soup))
	if 'ilfoglio' in link:
		return componi_articolo(get_corpo(TAGS['ilfoglio'][0], TAGS['ilfoglio'][1], soup))
	if 'adnkronos' in link:
		return componi_articolo(get_corpo(TAGS['adnkronos'][0], TAGS['adnkronos'][1], soup))

def get_full_article(link):
	""" E' la funzione che lancia la richiesta HTTP. Chiama get_html per maneggiare la risposta.
		 Restituisce articolo completo e se c'è sottotitolo.
	"""
	
	
	with requests.get(link, verify=False) as r:
		soup = BeautifulSoup(r.text, "html.parser")
		if r.status_code == 200: return get_html(soup, link), get_subtitle(soup)
		else: 
			print("An error occured with request at link: %s" %(link))			
			return (None, None)

#######################################################################################################
# -------------------------------------------------------------
# TEST SECTION
# -------------------------------------------------------------

def FULL_ARTICLE_TEST(testata, check=False):
	""" Passa come argomento la stringa che identifica una testata. La funzione si connette al database, estrae i link degli articoli
		 che puntano all'articolo completo e prova a scaricarlo. Se ci sono errori riporta stampa a video.
		 Set check = True per avere la stampa dell'articolo (very verbose).
	""" 	
	
	conn = sqlite3.connect('articoli.db')
	cur = conn.cursor()
	query = "SELECT link FROM Articoli WHERE link LIKE '%" + testata + "%'"
	data = cur.execute(query)
	rows = data.fetchall()
	for uri in rows:
		if get_full_article(uri[0]) is None:
			print("An error occured with uri request: ", uri[0])
		else: 
			print("OK! ", uri[0])
			if check:
				print(get_full_article(uri[0]))

def UN_PEZZO_TEST():
	""" La funzione restituisce un pezzo per testata, testata e link """
	testate = ['panorama','corriere','forbes','ilsole24','ilfoglio','lavoce']	
	conn = sqlite3.connect('articoli.db')
	cur = conn.cursor()
	pezzi = []
	for testata in testate:
		query = "SELECT link FROM Articoli WHERE link LIKE '%" + testata + "%'"
		data = cur.execute(query)
		rows = data.fetchall()
		pezzi.append((testata, get_full_article(rows[0][0]), rows[0][0]))
	return pezzi

	
if __name__ == "__main__":
	
	# tutti gli urls in una lista
	urls = []
	for k in Links.keys():
		urls += Links[k]
	
	# i sorgenti del feed RSS
	sources = RSSextractor(urls)
	
	# gli articoli in formato xml
	xmlarticles = GetXmlArticleObject(GetXmlItems(sources))
	
	# pulizia e estrazione dati rilevanti dall'xml ----> lista oggetti Articolo
	articoli = get_article_datas(xmlarticles)
	
	
	# inseriamo i dati in un database sqlite3 di articoli (db = articoli.db)

	# TABELLA articoli schema:
	# IDarticolo | link | titolo | descrizione | date | autore | categoria | creator | subtitle | fullarticle
 	
 	# APRI O CHIUDI QUESTE RIGHE PER SALVARE IN DATABASE
	conn = sqlite3.connect('articoli.db')
	cur = conn.cursor()
	
	for articolo in articoli:
		cur.execute("INSERT INTO Articoli (link, titolo, descrizione, date, autore, categoria, creator, hostname, subtitle, fullarticle) VALUES (?,?,?,?,?,?,?,?,?,?);", (articolo.link, articolo.titolo, articolo.descrizione, articolo.date, articolo.autore, articolo.categoria, articolo.creator, articolo.hostname, articolo.subtitle, articolo.fullarticle))
	
	conn.commit()
	conn.close()





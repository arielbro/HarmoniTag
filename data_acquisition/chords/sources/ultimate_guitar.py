from bs4 import BeautifulSoup
from urllib2 import urlopen

BASE_URL = "http://www.ultimate-guitar.com/"
 
def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html, "lxml")

def get_rating(chords):
    try:
        rating_ = chords.find("span", {"class": "rating"})
        return int(rating_.span["class"][0][2])
    except:
        return 0

def get_raters(chords):
    try:
        raters_ = chords.find("b", {"class": "ratdig"}).text
        return int(raters_)
    except:
        return 0
    
def get_url(chords):
    try:
        all_ = chords.findAll("a",{"class": "song"})
        if len(all_)>1: return all_[1]["href"]
        else: return all_[0]["href"]
    except:
        return None
    
def is_chord_type(chords):
    try:
        if chords.find("strong").text == 'chords': return True
        else: return False
    except:
        return None

def choose_best_chords(by_rate, by_raters):
    last = len(by_rate)-1
    if (by_rate[last]["raters"]) >= ((by_raters[last]["raters"])/2):
        return (by_rate[last])["url"]
    if (by_raters[last]["rating"]) >= ((by_rate[last]["rating"])-1):
        return by_raters[last]["url"]
    else: 
        return (by_rate[last])["url"]
        
"""
get the result page in ultimate-guitar with all the results for the given (artist, title), 
parse the results page. each result has a url, type, rating and raters. 
filter by type and get only chords (remove tabs, bass, ukulele etc.). 
then sort by rating and raters and choose best chords based on those parameters. 
finally, return the url of best chords to parse
"""         
def get_best_chords(all_url):
    soup = make_soup(all_url)
    all_results = soup.find("table", "tresults")
    if not all_results: return None
    all_chords = []
    #filter all non-chords out
    for stripe in all_results.findAll("tr"):
        if is_chord_type(stripe):
            chord_params = {"rating": get_rating(stripe),
                            "raters": get_raters(stripe), 
                            "url": get_url(stripe) }
            all_chords.append(chord_params)
    if len(all_chords)==0: return None
    #find highest rated chords  
    by_rate = sorted(all_chords, key=lambda chord: chord["rating"])
    by_raters = sorted(all_chords, key=lambda chord: chord["raters"])
    return choose_best_chords(by_rate, by_raters)

"""
given a url of best chords, parses the page and returns a chord vector which contains
the ordered sequence of the songs' chords. 
(currently includes noise: if the chords are prsented before the song, they are added to the vector, 
if they are repeated by a special sign, they are not added, and so on)
"""
def get_chord_vector(chords_url):
    soup = make_soup(chords_url)
    song_text = soup.findAll("pre")[2]
    chord_vector = [str(chord.text) for chord in song_text.findAll('span')]
    return chord_vector


"""
given (artist, title), finds best chords, scrapes chord vector
"""
def get_chords(title,artist):
    name = (artist+"+"+title).replace(' ','+')
    all_chords_url = (BASE_URL + "search.php?search_type=title&value="+name)
    best_chords_url = get_best_chords(all_chords_url)
    if best_chords_url==None: return None
    chord_vector = get_chord_vector(best_chords_url)
    #print chord_vector
    return chord_vector
    
    
    
def test():
    get_chords("blues for alice", "charlie parker") 
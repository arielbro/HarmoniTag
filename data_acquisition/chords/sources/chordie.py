from bs4 import BeautifulSoup
from urllib2 import urlopen

BASE_URL = "http://www.chordie.com"
 
def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html, "lxml")

def get_url(option):
    try:
        line = option.findAll("tr")[1].findAll("td")[1].i.a
        if line.span.text=="CHORDS": 
            return BASE_URL+ line["href"]
        else: return None
    except:
        return None
    
"""
Chordie is a based on a chord search engine - hence it contains several results for each song.
We filter out the non-Chord type of results, and parse each of the remaining into a chord vector.
Returns an array containing all available chord vectors.
"""
def get_chord_options(chords_url):
    soup = make_soup(chords_url)
    all_text = soup.find("div", {"id": "resultc"})
    if not all_text: return None
    all_song_chords = all_text.findAll("table")
    chord_options = []
    for option in all_song_chords:
        url = get_url(option)
        if not url==None: 
            chord_vector = get_chord_vector(url)
            if not chord_vector==None and len(chord_vector)>0: 
                #print url+": "+str(chord_vector)
                chord_options.append(chord_vector)
    return chord_options

"""
Given a relevant url, parses it into a chord vector
"""
def get_chord_vector(chords_url):
    soup = make_soup(chords_url)
    song_chords = soup.findAll("td", "c")
    chord_vector = [str(chord.text) for chord in song_chords]
    return chord_vector


"""
Given (artist, title), scrapes *all* suiteble chord vectors
"""
def get_chords(title,artist):
    name = "songtitle/"+title.replace(' ','+')+"/songartist/"+artist.replace(' ','+')+"/index.html"
    all_chords_url = (BASE_URL +"/allsongs.php/"+ name)
    chord_options = get_chord_options(all_chords_url)
    return chord_options
    
    
    
def test():
    get_chords("Suzanne", "leonard cohen") 
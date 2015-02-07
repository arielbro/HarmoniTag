from bs4 import BeautifulSoup
from urllib2 import urlopen

BASE_URL = "http://www.e-chords.com/chords/"
 
def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html, "lxml")


"""
given a url of best chords, parses the page and returns a chord vector which contains
the ordered sequence of the songs' chords
"""
def get_chord_vector(chords_url):
    soup = make_soup(chords_url)
    all_text = soup.find("pre", "core")
    if not all_text: return None
    song_chords = all_text.findAll("u")
    chord_vector = [str(chord.text) for chord in song_chords]
    return chord_vector


"""
given (artist, title), finds best chords, scrapes chord vector
"""
def get_chords(title,artist):
    name = artist.replace(' ','-')+"/"+title.replace('\'','').replace(' ','-')
    all_chords_url = (BASE_URL + name)
    chord_vector = get_chord_vector(all_chords_url)
    #print chord_vector
    return chord_vector
    
    
    
def test():
    get_chords("boogie Down", "al jarreau") 
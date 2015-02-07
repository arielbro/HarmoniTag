import json
import os
import time
import conf
import datetime


def standardize_tag(tag):
    """convert a tag to standard format, so that tags with multiple names (e.g. rock, Rock) will not be treated
    as multiple tags"""
    return ' '.join(sorted(tag.lower().replace('_', ' ').replace('-', ' ').split()))


def read_last_fm_tags(last_home):
    """
    read the last.fm s ong tags dataset, and return a dictionary, where the keys
    are (song_title,artist) tuples, and the values are tag sets.
    The dataset is formatted in nested subdirectories, where each file contains
    one json line, formatted as a dictionary, with "title","artist" and "tags"
    among them. the "tags" value contains a list of lists, each list contains
    the tag name, and certainty value (? last.fm didn't specify that), ranging
    from 0 to 100. We filter out the tags with a certainty threshold.
    """
    last_songs = dict()
    average_tags_per_song = 0
    number_of_songs_with_tags = 0
    number_of_songs = 0
    # iterate over dataset files
    for root, dirs, files in os.walk(last_home):
        for song_file_path in files:
            number_of_songs += 1
            with open(os.path.join(root, song_file_path)) as song_file:
                song_data = json.loads(song_file.readline())
                # if song_data['tags']:
                certain_tags = {standardize_tag(tag) for tag, certainty in song_data['tags'] if
                                int(certainty) >= conf.certainty_threshold}
                if certain_tags:
                    number_of_songs_with_tags += 1
                average_tags_per_song += len(certain_tags)
                last_songs[(song_data['title'], song_data['artist'])]= certain_tags
            if not number_of_songs % 20000:
                print "songs_read={}".format(number_of_songs)
    average_tags_per_song /= float(number_of_songs)
    print ("number of songs = {0}\nnumber of songs with tags = {1}\naverage number "
        + " of tags per song = {2}").format(number_of_songs, number_of_songs_with_tags, average_tags_per_song)
    return last_songs    


def last_fm_tags_iterator():
    """
    iterate over the last.fm song tags dataset, each time returning a
    ((song_title,artist),tag_set) pair. This will allow the user to filter
    only songs they need during fly time,
    instead of keeping whole of the dataset in memory.
    """
    
    average_tags_per_song = 0
    number_of_songs_with_tags = 0
    number_of_songs = 0
    # iterate over dataset files
    batch_start_time = time.time()
    for root, dirs, files in os.walk(conf.last_home):
        for song_file_path in files:
            number_of_songs += 1
            with open(os.path.join(root,song_file_path)) as song_file:
                song_data = json.loads(song_file.readline())
                # if song_data['tags']:
                certain_tags = {standardize_tag(tag) for tag,certainty in song_data['tags'] if \
                    int(certainty) >= conf.tag_certainty_threshold}
                if certain_tags: number_of_songs_with_tags+=1
                average_tags_per_song += len(certain_tags)
                yield (song_data['title'],song_data['artist']),certain_tags
            if not number_of_songs % 5000:
                print "songs_read=", number_of_songs, "time taken=", datetime.timedelta(
                    seconds=(time.time() - batch_start_time))
                batch_start_time = time.time()
            #delete files already read (helps with re-runs because of errors, but be aware of it!)
            os.remove(os.path.join(root,song_file_path))
    average_tags_per_song /= float(number_of_songs)
    print ("number of songs = {0}\nnumber of songs with tags = {1}\naverage number "\
        + " of tags per song = {2}").format(number_of_songs,number_of_songs_with_tags,\
                                       average_tags_per_song)    


def update_database_with_last_fm_tags():
    for (title, artist), tags in last_fm_tags_iterator():
        #chords go through Chord_index
        song, created = Song.objects.get_or_create(title=title, artist=artist)
        #if tag already exists for song (including song appearing twice on last.fm), addition does nothing.
        tags=[Tag.objects.get_or_create(name=tag)[0] for tag in tags]
        for tag in tags: song.tags.add(tag)
        #when fails, there's some rollback problem
        song.save()
    print 'done updating database'
    
#management.call_command('syncdb', verbosity=0, interactive=False)
#management.call_command('flush', verbosity=0, interactive=False)
print "tag number: " + str(Tag.objects.all().distinct().count())
print 'song number: ' + str(Song.objects.all().distinct().count())
print "number of songXtag couples: " + str(Song.objects.filter(tags__isnull=False).count())

#for tag in Tag.objects.all(): tag.delete()
update_database_with_last_fm_tags()

#for song in Song.objects.filter(title="Amor De Cabaret",artist="La Sonora Santanera"):
#    print song
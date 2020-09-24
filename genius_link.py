import spotipy
import re
import requests
from requests.exceptions import HTTPError
import unidecode
import os


def get_user(username):
    """
    Authenticates user to spotify developer app by creating spotify authentication object from username
    :return: spotify user object
    """

    # grabs the client_id and client_id_secret from the spotify developer app (keys stored on computer)
    client_id = os.environ.get('spotify_client_id')
    client_id_secret = os.environ.get('spotify_client_id_secret')

    # implements the o_auth_2 model which connects used to spotify developer app (generates access/refresh keys)
    o_auth_object = spotipy.oauth2.SpotifyOAuth(client_id=client_id, client_secret=client_id_secret, state='code',
                                                scope='user-read-private user-read-email user-read-currently-playing',
                                                username=username, redirect_uri='http://localhost:8888/callback')

    # implements the client model and allows access to user information (depends on scope provided)
    user = spotipy.Spotify(auth_manager=o_auth_object)

    # returns the user object
    return user


def remove_unnecessary_punctuation(list_check):
    """
    Removes any unnecessary punctuation in the list such as '', '-', ' ' as these disrupt link pattern
    :param list_check: list that is going to be checked
    :return: list_check after removing any redundancies
    """

    # list to store any values which should be removed from list_check
    remove = []

    # iterates through list_check and removes all unnecessary punctuation
    for num, i in enumerate(list_check):
        if i == '' or i == '-' or i == ' ':
            remove.append(num)
    for i in sorted(remove, reverse=True):
        del list_check[i]

    # returns edited list
    return list_check


def remove_elements(list_iter, list_check):
    """
    Removes any elements which can disrupt link from working
    :param list_iter: original list to be checked and where elements will be removed from
    :param list_check: list containing elements to remove
    :return: cleaned version of list_iter
    """

    # list to store any values which should be removed from list_check
    remove = []

    # iterates through list_iter and removes any elements in list_check from list_iter
    for num, i in enumerate(list_iter):
        for j in list_check:
            if i in j:
                remove.append(num)
    for i in sorted(remove, reverse=True):
        del list_iter[i]

    # returns cleaned version of list_iter
    return list_iter


def remove_accents(input_str):
    """
    Removes the accents from a string
    :param input_str: name of artist or song which might contain accents
    :return: cleaned version of artist name or track name
    """

    # cleans up input string (removes the accents)
    unaccented_string = unidecode.unidecode(input_str)

    # returns the cleaned string
    return unaccented_string


def regex_remove_artists(regex_string, track_name, find_group, exclude_artists):
    """
    This method is used as a dependency to remove_artists_featured to extract artist names who are featured in a track
    :param regex_string: string pattern being search for
    :param track_name: the actual name of the track to look at the featured artists on it
    :param find_group: boolean variable to denote if featured artists are contained in some kind of brackets
    :param exclude_artists: the actual list object being passed in as a reference
    :return: pass back the updated version of the referenced exclude_artists list
    """

    # if else statement searches through the track name to extract artist names contained in the feat section
    # the if statement checks for the regex expressions where there is extra information after the feat artists
    # the else statement only runs if there is no extra information after the feat artists
    if re.search(regex_string, track_name):
        # finds the match in the track name and returns to the user
        match = re.search(regex_string, track_name)
        substring_track_name = track_name[track_name.find('feat.') + 6:track_name.find('feat.') + 6 + len(match.group(0)
                                                                                                          ) - 2]
    else:
        # first statement is run if the feat. artists names are contained in some sort of container
        if find_group:
            # finds the artist names in the track removing the brackets
            substring_track_name = re.match(r'[^)\]]+', track_name[track_name.find('feat.') + 6:])
            substring_track_name = substring_track_name.group(0)
        # this statement is run if the feat. artists are not contained in some sort of container
        else:
            # finds the artist names in the track
            substring_track_name = track_name[track_name.find('feat.') + 6:]
            substring_track_name = substring_track_name.strip()

    # removes any mention of the word 'and' with ',' in the substring
    substring_track_name = re.sub(' and ', ',', substring_track_name)

    # if else statement splits artists along the commas and the ampersands and adds it to exclude_artist list
    if re.search('[,&]+', substring_track_name):
        multiple_artists_exclude = re.split('[,&]', substring_track_name)
        multiple_artists_exclude = [artist.strip() for artist in multiple_artists_exclude]
        exclude_artists.extend(multiple_artists_exclude)
    else:
        exclude_artists.append(substring_track_name)

    # returns an updated version of exclude_artists list
    return exclude_artists


def remove_artists_featured(artists_json, track_name):
    """
    Determines the relevant artists who were responsible for song
    :param artists_json: an list containing the names of all artists responsible in anyway for the making of the song
    :param track_name: the name of the song
    :return: list of all relevant artists who were responsible for the song
    """

    # list of artists to exclude from genius link
    exclude_artists = []

    # if elif statements to check the different kinds of way artists might be featured in the song title
    # if statement checks for '(feat. ---)'
    if re.search(r'[(\[](?=(feat))', track_name):
        exclude_artists = \
            regex_remove_artists(
                r'((?<=feat)[\w\s.,@_!#$%^&*<>?\/|\}{~:\)\]-]+(?=([\[\(])))', track_name, True, exclude_artists)
    # elif statement checks for '-feat. --- ('
    elif re.search(r'-[\s]?(?=(feat.))', track_name):
        regex_remove_artists(r'(?=(feat.))[\w\s.,@_!#$%^&*<>?/|\}{~:-]+(?=([()\[\]]))', track_name, False,
                             exclude_artists)
    # elif statement checks for 'feat. --- ('
    elif re.search('feat.', track_name, re.IGNORECASE):
        regex_remove_artists(r'(?=(feat.))[\w\s.,@_!#$%^&*<>?/|\}{~:-]+(?=([()\[\]]))', track_name, False,
                             exclude_artists)

    # saves all artists who are responsible in making of song in list
    all_artists = [artists_json[i]['name'].lower() for i in range(len(artists_json))]
    print(all_artists, exclude_artists)

    # removes feat artists in exclude_artists list
    all_artists = remove_elements(all_artists, exclude_artists)

    # removes the accents from the artist names
    for num, i in enumerate(all_artists):
        all_artists[num] = remove_accents(i)

    # returns all_artists list containing all relevant artists in making of song
    return all_artists


def split_artists(all_artists):
    """
    Determines the portion of the genius link which contains the artists
    :param all_artists: list of all relevant artists responsible for song
    :return: list of individual elements of the artist portion of the genius link
    """

    # if statement adds 'and' word in if more than 1 artist present
    if len(all_artists) > 1:
        all_artists.insert(len(all_artists) - 1, 'and')

    # for loop goes through each artist in the track and subs out any abnormal characters
    for num, i in enumerate(all_artists):
        all_artists[num] = re.sub(r'[\'’.,?\\/]+', '', all_artists[num])
        all_artists[num] = re.sub(r'[$]+', ' ', all_artists[num])

    # list holds all individual artists after their names are split on spaces
    all_artists_split = []
    [all_artists_split.extend(i.split(' ')) for i in all_artists]

    # removes any unnecessary characters which might disrupt the genius link by adding unnecessary elements
    all_artists_split = remove_unnecessary_punctuation(all_artists_split)

    # list of individual elements of the artist portion of the genius link (includes every artist name split on space)
    all_artists_split = [i + '-' for i in all_artists_split]
    [all_artists_split.remove(i) for i in all_artists_split if i == '-']

    # returns the final list used in genius link formation
    return all_artists_split


def remove_end_track(track_name, all_artists_split):
    """
    Removes unnecessary information anywhere in a song title
    :param track_name: name of the song
    :param all_artists_split: list of individual elements of the artist portion of the genius link
    :return:
        track_name - cleaned version of track name
        extra_information - contains information in parenthesis or brackets inside song title
        inside_parenthesis - boolean stating if there is any information inside of parenthesis or brackets
        slash - boolean stating if there is a slash in the song title
        track_name_slashed - contains information after the slash in song titles
    """

    print(track_name)

    # remove accents from track name
    track_name = remove_accents(track_name)

    # statement goes through each artist in the track and subs out any abnormal characters
    track_name = re.sub(r'[\'’.,?]', '', track_name)
    track_name = re.sub(r'[$!]+', ' ', track_name)

    # boolean variable which assesses if information (the artist names) is in the parenthesis
    important_in_par = False

    # boolean variable which assesses if there are words inside of the parenthesis in track name
    inside_parenthesis = False
    # list to hold information inside of parenthesis in track name
    extra_information = []

    # boolean variable which assesses if there is a slash present in the track name
    slash = False
    # list to hold information after the slash in track name
    track_name_slashed = []

    # if statements check for information inside of the track name
    # if statement searches for the feat. or with within some kind of container
    if re.search(r'[(\[-]+[\s]?(?=(feat.|with))', track_name):
        # if statement looks for feat. or with contained in brackets
        if re.search(r'[(\[]+(?=(feat.|with))', track_name):
            # cleans up the track name by cleaning up the feat. or with statement completely
            track_name = re.sub(r'[(\[]+(?=(feat.|with))[\w\s.,@_!#$%^&*<>?/|\}{~:-]+(?=([)\]]))[)\]]', '', track_name)
        # elif statement looks for feat. or with after hyphen
        elif re.search(r'[-]?[\s]+(?=(feat.|with))', track_name):
            # cleans up the track name by cleaning up the feat. or with statement completely
            track_name = re.sub(r'[-]?[\s]+(?=(feat.|with))[\w\s.,@_!#$%^&*<>?/|\}{~:-]+', '', track_name)
    # if statement searches for feat. or with when it is not enclosed within some kind of container
    if re.search(r'(?<!\()(?<!\[)(?<!-)(feat.|with)', track_name):
        # if there is a container afterwards, subs in everything before it
        if re.search(r'(?<!\()(?<!\[)(?<!-)(feat|with)[\w\s.,@_!#$%^&*<>?/|\}{~:-]+(?=([()\[\]]))', track_name):
            # cleans up track name by substituting the feat. or with part before the container
            track_name = re.sub(r'(?<!\()(?<!\[)(?<!-)(feat|with)[\w\s.,@_!#$%^&*<>?/|\}{~:-]+(?=([()\[\]]))', '',
                                track_name)
        # if there is no container afterwards, subs in everything after feat. or with
        else:
            # cleans up track name by substituting the feat. or with part
            track_name = re.sub(r'(?<!\()(?<!\[)(?<!-)(feat|with)[\w\s.,@_!#$%^&*<>?/|\}{~:-]+', '', track_name)
    # if statement looks for remastered, bonus, acoustic, or medley within the track name
    if 'remastered' in track_name or 'bonus' in track_name or 'acoustic' in track_name or 'medley' in track_name:
        # cleans up track name by cleaning up the remastered, bonus, acoustic, medley statement completely
        track_name = re.sub(r'[\-][\s]?(?=(remastered|bonus|acoustic|medley))[\w\s.,@_!#$%^&*()<>?/|\}{~:-]+', '',
                            track_name)
    # if statement looks for prelude, intro, outro, or interlude within the track name
    if 'prelude' in track_name or 'intro' in track_name or 'outro' in track_name or 'interlude' in track_name:
        # cleans up track name by removing any sort of brackets or hyphens (genius link uses those words)
        track_name = re.sub('[()[]-]+', '', track_name)
    # if statement searches for any information in containers
    if re.search(r'[\[(]+[\w\s.,@_!#$%^&*<>?/|\}{~:-]+[\])]+', track_name):
        # surfs through relevant artists and if a relevant artist appears inside, sets important_in_par to True
        for i in all_artists_split:
            if i in track_name:
                important_in_par = True
                break

        # if a relevant artist exists within the container, then this statement runs
        if important_in_par:
            # if feat. exists in the container, it is replaced with '' along with the rest of the statement
            if re.search('feat.', track_name):
                # cleans up track name by removing all information in the parenthesis along with the 'feat.' word
                track_name = re.sub(r'(?<=(feat.))[\w\s.,@_!#$%^&*<>?/|\}{~:-]+', '', track_name).replace('feat.', '')
            # if feat. does not exist in the container, then this code is run
            else:
                # cleans up track name by removing the information in the container
                track_name = re.sub(r'[\[(]+[\w\s.,@_!#$%^&*()<>?/|\}{~:-]+[\])]+', '', track_name)
        # if no artist name lies within the container, then this statement runs
        else:
            print("DSFDSFDFDF")
            # this block stores the information inside of container in the extra_information variable
            # if the genius link does not work normally, this information can be removed from the end
            extra_information = re.search(r'[\[(]+[\w\s.,@_!#$%^&*()<>?/|\}{~:-]+[\])]+', track_name)
            extra_information = re.sub('[(\)\[\]]+', '', extra_information.group(0))
            # stores the words inside the container in an list, so it can be easily plugged into genius link
            extra_information = extra_information.split(' ')
            # removes any containers left from the cleanup
            track_name = re.sub('[(\)\[\]]+', '', track_name)
            # variable changed to true to signify that there is information contained within parenthesis
            inside_parenthesis = True

    # if statement searches for any slashes in of track name
    if re.search(r'(?:[\s]?[/\\]+[\s]?)', track_name):
        # this block stores the information after the slash (sometimes only information behind slash is needed for link)
        track_name_slashed = re.split(r'(?:[\s]?[/\\]+[\s]?)', track_name)[1:]
        track_name = re.sub(r'(?:[\s]?[/\\]+[\s]?)', ' ', track_name)
        # variable changed to true to signify that there is a slash in the track name
        slash = True

    print(track_name)

    # returns the cleaned track name
    # returns the extra information inside of the parenthesis if there was any
    # returns the boolean variable stating if there was extra information within the parenthesis
    # returns the boolean variable stating if there was a slash in the track name
    # returns information to the right of the slash in the track name
    return track_name, extra_information, inside_parenthesis, slash, track_name_slashed


def split_track_name(track_name):
    """
    Determines the portion of the genius link which contains the track name
    :param track_name: cleaned version of the name of the song
    :return: list of individual elements of the track name of the genius link
    """

    # splits track name along spaces into list
    track_name = track_name.split(' ')

    print(track_name)

    # block removes any inconsistencies in track name (empty spaces or hyphens)
    track_name = remove_unnecessary_punctuation(track_name)

    # splits track name along hyphens and removes any elements which just consist of only hyphens
    track_name = [i + '-' for i in track_name]
    [track_name.remove(i) for i in track_name if i == '-']

    # returns cleaned version of track name in the form of an list with a hyphen after each element
    return track_name


def genius_link(all_artists_split, track_name):
    """
    Determine the actual genius link
    :param all_artists_split: list of individual elements of the artist portion of the genius link
    :param track_name: list of individual elements of the song title of the genius link
    :return: string containing genius link
    """

    # list containing the list containing the artist names and list containing the track name
    return_add = []
    return_add.extend(all_artists_split)
    return_add.extend(track_name)

    # using the combined list containing everything, a string is creating for the genius link
    return_add_string = ''
    for i in return_add:
        return_add_string = return_add_string + i

    print(return_add_string)

    # the string is compiled into a link
    html_address = 'https://genius.com/' + return_add_string + 'lyrics'

    # the genius link is returned to the user
    return html_address


def main():
    """
    Runs the entire program
    :return: genius link of song user is currently listening to
    """

    # creates a user object which links to the user's spotify
    user = get_user('raghu2001')

    # gets all artists responsible in making the song (stores in an list)
    artists_json = user.current_user_playing_track()['item']['artists']

    # gets the track name and makes it lowercase
    track_name = user.current_user_playing_track()['item']['name']
    track_name = track_name.lower()

    print(track_name)

    # removes any irrelevant artists and stores it in a new list
    all_artists = remove_artists_featured(artists_json, track_name)

    # splits artists and stores the result in an list (adds hyphen after each word)
    all_artists_split = split_artists(all_artists)

    # cleans up track name and the information inside of it
    track_name, extra_information, inside_parenthesis, slash, track_name_slashed = remove_end_track(track_name,
                                                                                                    all_artists_split)

    print(track_name_slashed)

    # splits track name and stores it in a list (adds hyphen after each word)
    track_name = split_track_name(track_name)

    # compiles the artist list and the track name list together to make a link for the genius lyrics
    html_address = genius_link(all_artists_split, track_name)

    # this block of code tests if the genius link
    # try statement first tests the genius link from the first run
    try:
        # tests the response to check if the link is available
        response = requests.get(html_address)
        print(response.raise_for_status())
        print(response.status_code)
    # if there is an HTTP exception, this block is run with changes to the link
    except HTTPError:
        # this block checks if there are multiple artists responsible for the song, tries with only the main artist
        if len(all_artists) > 1:
            # gets the first artist responsible for the song
            all_artists = [artists_json[0]['name']]
            # for loop goes through the artist and removes the accents from the artist name
            for num, i in enumerate(all_artists):
                all_artists[num] = remove_accents(i)
            # splits the artist name by each word and adds a hyphen at the end
            all_artists_split = split_artists(all_artists)
            # returns the genius link
            html_address = genius_link(all_artists_split, track_name)

        # block of code retires the genius link
        if requests.get(html_address).status_code == 200:
            pass

        # this block checks if the track name contained a container with misc. information
        if inside_parenthesis:
            # block of code to remove unnecessary information (information in parenthesis)
            track_name = remove_elements(track_name, extra_information)
            # returns the genius link
            html_address = genius_link(all_artists_split, track_name)

        # block of code retires the genius link
        if requests.get(html_address).status_code == 200:
            pass

        # this block checks if the track name contains a slash
        if slash:
            # block of code to remove unnecessary information (information after the slash)
            track_name = remove_elements(track_name, track_name_slashed)
            # returns the genius link
            html_address = genius_link(all_artists_split, track_name)

        # block of code retires the genius link
        # if the link does not work, returns that the link is not available
        if requests.get(html_address).status_code == 200:
            pass
        else:
            print('Cannot find link!')
            html_address = ''

    return html_address


# calls the entire function and returns the link
link = main()
print(link)

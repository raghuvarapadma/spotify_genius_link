# Spotify Genius Link

## Introduction
Welcome! This program is designed to scan a user's currently playing song using the Spotify API, and then using the Regex library, the program returns the Genius link back to the user. Otherwise, if a Genius link cannot be found, no link is returned back to the user.
## How it Works
All Genius links take the form of **https://<span></span>www<span>.</span>genius.com/(name of artists)-(name of track)-lyrics**. However, since many different artist names and track names might have unconventional characters, Regex is used to surf through these names to identify the important parts. Below are some rules on how the Genius links are formatted to work and some of the edge cases which are checked for.
* Rules for Artist Formatting in Links:
  * For the first of the link where the (name of artists) is, each artist is broken by spaces in their name
    * An example would be **Travis Scott** whose name would be formatted as **travis-scott** in the link
  * If a track consists more than one artist, it will usually include an **and** in the link
    * An example would be **The Ways (with Swae Lee) by Khalid** which would be formatted as **khalid-and-swae-lee** in the link
  * Any featured artists on the track are not included inside of the Genius link
    * An example would be **Weekend (feat. Miguel) by Mac Miller** which would be formatted as **mac-miller** in the link
  * Anytime a track says with *artist*, the artist is usually included within the Genius link
    * An example would be **Big Shot (with Travis Scott) by Kendrick Lamar**, which would be formatted as **kendrick-lamar-and-travis-scott** in the link
  * However, sometimes a song might list multiple artists responsible; however, it might not always work
    * An example would be **The Question by Mac Miller and Lil Wayne** which would be formatted as **mac-miller** in the link
* Rules for Track Name Formatting in Links:
  * For the second part of the link where (name of track) is, the track is split on spaces
    * An example would be **Strawberry Fields Forever** which would be formatted as **strawberry-field-forever** in the link
  * When a track name contains *feat* or *with*, any of those corresponding words along with the artists listed afterward or containers (such as (), [], -)
    * An example would be **Pray 4 Love (feat. The Weeknd)** which would be formatted as **pray-4-love** in the link
  * Some tracks contain more information in containers (such as (), [], -) which can be important sometimes, but not important sometimes (the program tries    both versions of the link)
    * An example would be **I Am Who Am (Killin' Time) [feat. Niki Randa]** which would be formatted as **i-am-who-am-killin-time** in the link
    * An opposite example would be **Never Recover (Lil Baby & Gunna, Drake)** which would be formatted as **never-recover** in the link
  * Some tracks contain **/** in the song name, and sometimes only the part before the slash is important or all words in the track name might be important
    * An example would be **Cameras / Good Ones Go Interlude - Medley** which would be formatted as **cameras** in the link
    * An opposite example would be **Perfect Circle / God Speed** which would be formatted as **perfect-circle-god-speed** in the link
  * Anytime a track contains the words **remastered**, **bonus**, **acoustic**, **medley**, these words along with any other words or containers (such as (), [], -) are removed from the title
  * Anytime a track contains the words **prelude**, **intro**, **outro**, **interlude**, **remix**, these words are left in, but any containers (such as (), [], -) are removed
## Important Links
If you want to do your own research, here are some helpful links:
* Regex (Python Library): https://docs.python.org/3/library/re.html
* Regex Tester: https://regex101.com/
* Spotify API: https://developer.spotify.com/documentation/web-api/
* Spoify API (Python Library): https://spotipy.readthedocs.io/en/2.16.0/
## Future Improvements
* Adding in further edge cases
* Some accented characters disrupt link, update remove_accents method
* Create Chrome Extension to host program

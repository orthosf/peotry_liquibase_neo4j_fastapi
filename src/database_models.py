"""
The module provides classes for representing music data in a Neo4j database using neomodel.

Classes:
- Album: Represents an album in the music database.
- Song: Represents a song in the music database.
- Artist: Represents an artist in the music database.
- Playlist: Represents a playlist in the music database.

Dependencies:
- neomodel: The module relies on the neomodel library for interacting with the Neo4j database.
"""

from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    FloatProperty,
    BooleanProperty,
    RelationshipTo,
    ZeroOrMore,
    OneOrMore,
    UniqueIdProperty,
    RelationshipTo, 
    StructuredRel,
    DateTimeProperty,
    RelationshipFrom
    
)
class FollowRel(StructuredRel):
    since = DateTimeProperty(default_now=True)
    #status = StringProperty(choices={'requested', 'accepted', 'blocked'})
    #interaction_count = IntegerProperty(default=0)
    #last_interaction = DateTimeProperty()
    #message_count = IntegerProperty(default=0)


class User(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(index=True)
    email = StringProperty(index=True)
    first_name = StringProperty(index=True)
    last_name = StringProperty(index=True)
    
    # Use the relationship model to add more details to the relationship
    following = RelationshipTo('User', 'FOLLOWING', model=FollowRel)
    followers = RelationshipFrom('User', 'FOLLOWING', model=FollowRel)
     
class Person(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    
class Actor(Person):
    pass

class Director(Person):
    pass

class Album(StructuredNode):
    """
    An album is represented only by its unique identifier.

    Properties:
    - uid: str

    Relationships: None
    """

    uid = UniqueIdProperty()


class Song(StructuredNode):
    """
    A song has a title and musical characteristics defined by Spotify.

    It is released in at least one album.

    Properties:
    - uid: str
    - title: str
    - ... see class

    Relationships:
    - albums: One or more
    """

    uid = UniqueIdProperty()
    title = StringProperty(index=True)
    loudness = FloatProperty()
    liveness = FloatProperty()
    tempo = FloatProperty()
    valence = FloatProperty()
    instrumentalness = FloatProperty()
    danceability = FloatProperty()
    speechiness = FloatProperty()
    duration = IntegerProperty()
    mode = BooleanProperty()
    popularity = IntegerProperty()
    acousticness = FloatProperty()
    key = IntegerProperty()
    energy = FloatProperty()

    albums = RelationshipTo(Album, "RELEASED_IN", cardinality=OneOrMore)


class Artist(StructuredNode):
    """
    An artist has a name, and can have recorded songs.

    Properties:
    - uid: str
    - name: str

    Relationships:
    - songs: Zero or more
    """

    uid = UniqueIdProperty()
    name = StringProperty(index=True)

    songs = RelationshipTo(Song, "RECORDED", cardinality=ZeroOrMore)


class Playlist(StructuredNode):
    """
    A playlist has a title, and at least one song.

    Properties:
    - uid: str
    - title: str

    Relationships:
    - songs: One or more
    """

    uid = UniqueIdProperty()
    title = StringProperty(index=True)

    songs = RelationshipTo(Song, "CONTAINS", cardinality=OneOrMore)

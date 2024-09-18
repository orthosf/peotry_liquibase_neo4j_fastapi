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
    RelationshipFrom,
    DateTimeProperty,
    DateProperty,
)

from src.common.models import FollowRel

class Person(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(index=True)
    email = StringProperty(index=True)
    first_name = StringProperty(index=True)
    last_name = StringProperty(index=True)

class Actor(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(index=True)
    email = StringProperty(index=True)
    first_name = StringProperty(index=True)
    last_name = StringProperty(index=True)    

    acted = RelationshipTo('Movie', 'ACTEDIN') # take care of it at the end
    #TODO identify the directions of the relationship from and to and delete the necessary

class Director(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(index=True)
    email = StringProperty(index=True)
    first_name = StringProperty(index=True)
    last_name = StringProperty(index=True)   

class Movie(StructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty(index=True)
    releasedate = DateProperty(index=True)      
    

    
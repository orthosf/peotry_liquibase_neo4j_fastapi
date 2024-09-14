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
)

from src.common.models import FollowRel

class User(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(index=True)
    email = StringProperty(index=True)
    first_name = StringProperty(index=True)
    last_name = StringProperty(index=True)
    
    # Use the relationship model to add more details to the relationship
    following = RelationshipTo('User', 'FOLLOWING', model=FollowRel)
    followers = RelationshipFrom('User', 'FOLLOWING', model=FollowRel)


    
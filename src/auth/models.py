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
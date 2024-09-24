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


class UserProfile(StructuredNode):
    # Unique identifier for each user profile
    uid = UniqueIdProperty()

    # String properties with various constraints
    username = StringProperty(unique=True, max_length=30, index=True)  # unique username with an index and max length
    email = StringProperty(unique_index=True, required=True)  # unique index on email, also required
    first_name = StringProperty(max_length=50, required=True)  # required with max length constraint
    last_name = StringProperty(max_length=50, required=True)  # required with max length constraint
    
    # Property with a default value
    robot = BooleanProperty(default=False)  # default set to False
    
    # String with choices
    role = StringProperty(choices={"admin": "Admin", "user": "User", "guest": "Guest"}, default="user")  # must be one of these values
    
    # String that must be lowercase
    country = StringProperty(lowercase=True)  # forces lowercase
    
    # String that must be uppercase
    currency = StringProperty(uppercase=True, max_length=3, default="USD")  # forces uppercase, max length of 3
    
    # String that must match a regex pattern
    phone_number = StringProperty(regex=r'^\+?[1-9]\d{1,14}$')  # enforces E.164 phone number format
    
    # Integer with min and max values
    age = IntegerProperty(min_value=18, max_value=100)  # must be between 18 and 100
    
    # Float property with a minimum value
    height = FloatProperty(min_value=0.5)  # minimum height is 0.5 meters
    
    # Optional property (not required) but indexed for faster lookup
    bio = StringProperty(max_length=250, index=True)  # optional with an index for faster searches    
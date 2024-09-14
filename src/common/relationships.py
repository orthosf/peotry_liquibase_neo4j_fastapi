from neomodel import StructuredRel, DateTimeProperty

class FollowRel(StructuredRel):
    since = DateTimeProperty(default_now=True)
    #status = StringProperty(choices={'requested', 'accepted', 'blocked'})
    #interaction_count = IntegerProperty(default=0)
    #last_interaction = DateTimeProperty()
    #message_count = IntegerProperty(default=0)
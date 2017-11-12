from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_db_user import Catalog, Items, User, Base

engine = create_engine('sqlite:///catalogappwithuserslogin.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
user1 = User(username="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()

# New catalog
catalog1 = Catalog(id=1, name="Cricket")

session.add(catalog1)
session.commit()

catalog2 = Catalog(id=2, name="Soccer")

session.add(catalog2)
session.commit()

catalog3 = Catalog(id=3, name="Baseball")

session.add(catalog3)
session.commit()

catalog4 = Catalog(id=4, name="Frisbee")

session.add(catalog4)
session.commit()

catalog5 = Catalog(id=5, name="Hockey")

session.add(catalog5)
session.commit()

catalog6 = Catalog(id=6, name="Snowboarding")

session.add(catalog6)
session.commit()


item1 = Items(id=1, name="Cricket Bat", description="Cricket bat", catalog=catalog1, user=user1)
session.add(item1)
session.commit()

item2 = Items(id=2, name="Cricket Ball", description="Cricket ball", catalog=catalog1, user=user1)
session.add(item2)
session.commit()

item3 = Items(id=3, name="Stumps", description="Used betweeen the wickets", catalog=catalog1, user=user1)
session.add(item3)
session.commit()

item4 = Items(id=4, name="SoccerBall", description="Cricket bat", catalog=catalog2, user=user1)
session.add(item4)
session.commit()

item5 = Items(id=5, name="Baseball Bat", description="Baseball bat", catalog=catalog3, user=user1)
session.add(item5)
session.commit()

item6 = Items(id=6, name="Frisbee", description="Frisbee", catalog=catalog4, user=user1)
session.add(item6)
session.commit()

item7 = Items(id=7, name="Hockey Stick", description="Hockey stick", catalog=catalog5, user=user1)
session.add(item7)
session.commit()

item8 = Items(id=8, name="Snowboard", description="Snowboard", catalog=catalog6, user=user1)
session.add(item8)
session.commit()

print("added menu items!")



































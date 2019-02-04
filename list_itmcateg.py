from database_setup import Base, User, HCategory, Item
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///homecatalog.db',
                       connect_args={'check_same_thread': False})

# Bind the above engine to a session.
# Make declaratives accessible through a DBSession instance.
Session = sessionmaker(bind=engine)

# Create a Session object.
session = Session()

# Create a User.
user1 = User(
    name='admin',
    email='chettaoui.neila@gmail.com',
    picture='https://goo.gl/i7dmgH'
)
session.add(user1)
session.commit()

# Category 1: Tissue Covers.
category1 = HCategory(name='Tissue Covers', user=user1)

session.add(category1)
session.commit()

item1 = Item(
    name='Wooden Tissue Box Cover',
    description='Wooden Tissue Box Cover.'
    'Color: Brown. Type: Tissue Covers. Material: Wood',
    category=category1,
    user=user1
)

session.add(item1)
session.commit()

item2 = Item(
    name='Large Tissue Holder',
    description='Large Tissue Holder.'
                ' Color: Black. Type: Tissue Covers. Material: Plastic',
    category=category1,
    user=user1
)

session.add(item2)
session.commit()

# Category 2: Vases.
category2 = HCategory(name='Vases', user=user1)

session.add(category2)
session.commit()

item1 = Item(
    name='Glass Vase',
    description='Glass Vase. Color: Clear. Type: Vases. Material: Glass',
    category=category2,
    user=user1
)

session.add(item1)
session.commit()

item2 = Item(
    name='Bohimia Vase',
    description='Bohimia Vase. Color: Clear. Type: Vases. Material: Glass',
    category=category2,
    user=user1
)

session.add(item2)
session.commit()

# Category 3: Candle Holders.
category3 = HCategory(name='Candle Holders', user=user1)

session.add(category3)
session.commit()

item1 = Item(
    name='Silver Candle Stick',
    description='Silver Candle Stick.'
    ' Color: Silver. Type: Candle Holders. Material: Silver Plated',
    category=category3,
    user=user1
)

session.add(item1)
session.commit()

item2 = Item(
    name='Cooper Candle Stick',
    description='A Cooper Candle Stick.'
    'Color: Copper. Type: Candle Holders. Material: Metal',
    category=category3,
    user=user1
)

session.add(item2)
session.commit()

item3 = Item(
    name='Crystal Candle Stick',
    description='A Crystal Candle Stick.'
    ' Color: Clear. Type: Candle Holders. Material: Glass',
    category=category3,
    user=user1
)

session.add(item3)
session.commit()

# Category 4: Door Hangers.
category4 = HCategory(name='Door Hangers', user=user1)

session.add(category4)
session.commit()


item1 = Item(
    name='Wooden Door Accessory',
    description='A Wooden Door Accessory.'
    ' Color: Beige. Type: Door Hanger. Material: Wood',
    category=category4,
    user=user1
)

session.add(item1)
session.commit()

item2 = Item(
    name='Heart Hanger',
    description='Heart Hanger.'
    ' Color: Silver. Type: Door Hanger. Material: Linen',
    category=category4,
    user=user1
)

session.add(item2)
session.commit()

print('Categories and Items are successfully added')

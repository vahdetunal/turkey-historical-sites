from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import City, Base, Site, User


engine = create_engine('sqlite:///historicalsites.db')
Session = sessionmaker(bind=engine)
session = Session()


# Create a dummy user
User1 = User(name="Vahdet Unal", email="vahdetunal58gmail.com",
             picture=("https://pbs.twimg.com/profile_images/2671170543" +
                      "/18debd694829ed78203a5a36dd364160_400x400.png"))
session.add(User1)
session.commit()


# Sites for Sivas
city1 = City(name='Sivas', user_id=1,
             image=("https://pbs.twimg.com/profile_images/2671170543" +
                    "/18debd694829ed78203a5a36dd364160_400x400.png"))
session.add(city1)
session.commit()

site1 = Site(name='Ulu Mosque', civilization='Seljuk', city_id=1, user_id=1,
             description="A mosque built by Anatolian Seljuks in 1196.",
             image=("https://pbs.twimg.com/profile_images/2671170543" +
                    "/18debd694829ed78203a5a36dd364160_400x400.png"))
session.add(site1)
session.commit()

site2 = Site(name='Buruciye Madrasah', civilization='Seljuk',
             city_id=1, user_id=1,
             description=("Built by Anatolian Seljuks in 1271, it is " +
                          "located in the city center. Currently, " +
                          "several tea houses reside inside the building"),
             image=("https://pbs.twimg.com/profile_images/2671170543" +
                    "/18debd694829ed78203a5a36dd364160_400x400.png"))
session.add(site2)
session.commit()


# Sites for Istanbul
city2 = City(name='Istanbul', user_id=1,
             image=("https://pbs.twimg.com/profile_images/2671170543" +
                    "/18debd694829ed78203a5a36dd364160_400x400.png"))
session.add(city2)
session.commit()

site1 = Site(name='Hagia Sophia', civilization='Byzantine',
             city_id=2, user_id=1,
             description=("Built by Bizantines in 537 AD. It was built as a " +
                          "cathedral, converted to a mosque by Ottomans and " +
                          "is now a museum."),
             image=("https://pbs.twimg.com/profile_images/2671170543" +
                    "/18debd694829ed78203a5a36dd364160_400x400.png"))
session.add(site1)
session.commit()

site2 = Site(name='Sultan Ahmed Mosque', civilization='Ottoman',
             city_id=2, user_id=1,
             description=("Popularly known as the Blue Mosque, it was built" +
                          "by the Ottoman Sultan Ahmed I."),
             image=("https://pbs.twimg.com/profile_images/2671170543" +
                    "/18debd694829ed78203a5a36dd364160_400x400.png"))
session.add(site2)
session.commit()

print("Sites added to the database")

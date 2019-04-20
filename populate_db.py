from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import City, Base, Site, User


engine = create_engine("postgres://postgres:postgres@localhost:5432/historicalsights2")
Session = sessionmaker(bind=engine)
session = Session()


# Create a dummy user
User1 = User(name="Vahdet Unal", email="vahdet2unal@hotmail.com",
             picture=("https://pbs.twimg.com/profile_images/2671170543" +
                      "/18debd694829ed78203a5a36dd364160_400x400.png"))
session.add(User1)
session.commit()


# Sites for Sivas
city1 = City(name='Sivas', user_id=1,
             image=("http://www.sivas.bel.tr/Files" +
                    "/panosivas/d_meydan-pengu2.jpg"))
session.add(city1)
session.commit()

site1 = Site(name='Ulu Mosque', civilization='Seljuk', city_id=1, user_id=1,
             description=("An ornately inscribed mosque built in 1228." +
                          "One of the UNESCO World Heritage."),
             image=("http://www.kulturvarliklari.gov.tr" +
                    "/Resim/33393,unescodivrigijpg.png?0"))
session.add(site1)
session.commit()

site2 = Site(name='Buruciye Madrasah', civilization='Mengujekids',
             city_id=1, user_id=1,
             description=("Built by Anatolian Seljuks in 1271, it is " +
                          "located in the city center. Currently, " +
                          "several tea houses reside inside the building"),
             image=("https://media-cdn.tripadvisor.com" +
                    "/media/photo-s/0b/54/e2/a3/buruciye-medresesi.jpg"))
session.add(site2)
session.commit()


# Sites for Istanbul
city2 = City(name='Istanbul', user_id=1,
             image=("https://ist01.mncdn.com/Files/a-2017-nisan-ve-sonrasi" +
                    "/istanbul-bogazi-bilgileri-min.jpg"))
session.add(city2)
session.commit()

site1 = Site(name='Hagia Sophia', civilization='Byzantine',
             city_id=2, user_id=1,
             description=("Built by Bizantines in 537 AD. It was built as a " +
                          "cathedral, converted to a mosque by Ottomans and " +
                          "is now a museum."),
             image=("https://ayasofyamuzesi.gov.tr" +
                    "/sites/default/files/hagia-sophia-interior_1.jpg"))
session.add(site1)
session.commit()

site2 = Site(name='Sultan Ahmed Mosque', civilization='Ottoman',
             city_id=2, user_id=1,
             description=("Popularly known as the Blue Mosque, it was built" +
                          "by the Ottoman Sultan Ahmed I."),
             image=("http://www.istanbulkultur.gov.tr" +
                    "/Resim/180114,sultanahmet-camiijpg.png?0"))
session.add(site2)
session.commit()


# Sites for Çorum
city3 = City(name='Çorum', user_id=1,
             image=("http://www.corumtime.com/wp-content" +
                    "/uploads/2016/12/%C3%87ORUM-648x330.jpg"))
session.add(city3)
session.commit()

site1 = Site(name='Hattusa', civilization='Hittite',
             city_id=3, user_id=1,
             description=("Ruins of the capital of the Hittite Empire. " +
                          "Included in the UNESCO World Heritage list "),
             image=("https://66.media.tumblr.com" +
                    "/27e48a78f7d10f1ce7b1bc86594c8fe4" +
                    "/tumblr_pcfzrdO2GM1thchlco1_1280.jpg"))
session.add(site1)
session.commit()

print("Sites added to the database")

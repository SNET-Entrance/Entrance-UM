from bootstrap import db
from um import models

# Contact 1
u1 = models.Contact('Contact 1', 'user1@example.com')
db.session.add(u1)
db.session.commit()

# Contact 1 properties
p = models.Property('first_name', 'Peter', u1.id)
p1 = models.Property('last_name', 'Wanowan', u1.id)
p2 = models.Property('email', 'peter.wanowan@example.com', u1.id)
p3 = models.Property('fon', '+1 555 101', u1.id)

db.session.add(p)
db.session.add(p1)
db.session.add(p2)
db.session.add(p3)
db.session.commit()

# Contact 2
u2 = models.Contact('Contact 2', 'user2@example.com')
db.session.add(u2)
db.session.commit()

# Contact 2 properties
p = models.Property('first_name', 'John', u2.id)
p1 = models.Property('last_name', 'Twootwo', u2.id)
p2 = models.Property('email', 'j.twootwo@example.com', u2.id)
p3 = models.Property('fon', '+1 555 202', u2.id)

db.session.add(p)
db.session.add(p1)
db.session.add(p2)
db.session.add(p3)
db.session.commit()

# Contact 3
u3 = models.Contact('Contact 3', 'user3@example.com')
db.session.add(u3)
db.session.commit()

# Contact 3 properties
p = models.Property('first_name', 'Steve', u3.id)
p1 = models.Property('last_name', 'Thriotree', u3.id)
p2 = models.Property('email', 'steven.thriotree@example.com', u3.id)
p3 = models.Property('fon', '+1 555 303', u3.id)

db.session.add(p)
db.session.add(p1)
db.session.add(p2)
db.session.add(p3)
db.session.commit()

# Contacts attributes
a = models.Attribute('age')
a1 = models.Attribute('group')
a2 = models.Attribute('department')

u1.attributes.append(a)
u1.attributes.append(a1)
u1.attributes.append(a2)

u2.attributes.append(a)
u2.attributes.append(a2)

u3.attributes.append(a1)

db.session.add(u1)
db.session.add(u2)
db.session.add(u3)
db.session.commit()
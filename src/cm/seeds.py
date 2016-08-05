from bootstrap import db
from cm import models

c1 = models.Container('Gallery', '/home/user/pictures/gallery')
c2 = models.Container('Music', '/home/user/music')
c3 = models.Container('Summer 96', '/home/user/pictures/vacation')
c4 = models.Container('Work', '/home/user/work')
c5 = models.Container('Notes', '/home/user/notes')

db.session.add(c1)
db.session.add(c2)
db.session.add(c3)
db.session.add(c4)
db.session.add(c5)
db.session.commit()

f1 = models.File('/home/user/pictures/gallery/picture1.png', 'PABE14', 'all', c1.id)
f2 = models.File('/home/user/pictures/gallery/picture2.png', 'PABE14', 'all', c1.id)
f3 = models.File('/home/user/pictures/gallery/picture3.png', 'PABE14', 'all', c1.id)

f4 = models.File('/home/user/music/song1.mp3', 'PABE14', 'all', c2.id)
f5 = models.File('/home/user/music/song2.mp3', 'PABE14', 'all', c2.id)
f6 = models.File('/home/user/music/song3.mp3', 'PABE14', 'all', c2.id)

f7 = models.File('/home/user/pictures/vacation/summer96_1.jpg', 'PABE14', 'all', c3.id)
f8 = models.File('/home/user/pictures/vacation/summer96_2.jpg', 'PABE14', 'all', c3.id)
f9 = models.File('/home/user/pictures/vacation/summer96_3.jpg', 'PABE14', 'all', c3.id)

f10 = models.File('/home/user/work/work1.pdf', 'PABE14', 'all', c4.id)
f11 = models.File('/home/user/work/work2.pdf', 'PABE14', 'all', c4.id)
f12 = models.File('/home/user/work/work3.pdf', 'PABE14', 'all', c4.id)

f13 = models.File('/home/user/notes/note1.txt', 'PABE14', 'all', c5.id)
f14 = models.File('/home/user/notes/note2.txt', 'PABE14', 'all', c5.id)
f15 = models.File('/home/user/notes/note3.txt', 'PABE14', 'all', c5.id)

db.session.add(f1)
db.session.add(f2)
db.session.add(f3)
db.session.add(f4)
db.session.add(f5)
db.session.add(f6)
db.session.add(f7)
db.session.add(f8)
db.session.add(f9)
db.session.add(f10)
db.session.add(f11)
db.session.add(f12)
db.session.add(f13)
db.session.add(f14)
db.session.add(f15)

db.session.commit()
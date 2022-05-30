from app import db

class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String))
  facebook_link = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  website_link = db.Column(db.String(200))
  seeking_talent = db.Column(db.Boolean,default = False)
  seeking_description = db.Column(db.String(1000))
  shows = db.relationship('Show',backref = 'venue')

  def __repr__(self):
    return f'<Venue {self.id} {self.name} {self.city}>'


class Artist(db.Model):

  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String))
  facebook_link = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  website_link = db.Column(db.String(200))
  seeking_venue = db.Column(db.Boolean, default = False)
  seeking_description = db.Column(db.String(1000))
  shows = db.relationship('Show',backref = 'artist')

  def __repr__(self):
    return f'<Artist {self.id} {self.name} {self.city}>'


class Show(db.Model):
  __tablename__  = 'show'

  id = db.Column(db.Integer,primary_key = True)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable = False)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable = False)
  start_time = db.Column(db.DateTime,nullable = False)

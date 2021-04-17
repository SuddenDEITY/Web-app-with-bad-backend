import json
import sys
from flask import Flask, request, render_template,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super secret key'
db = SQLAlchemy(app)

class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    def __repr__(self):
        return '{}'.format(self.name)

db.create_all()
@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = Weather.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')

def day_or_night(currenttime, sunrisetime, sunsettime):
    if int(currenttime) < int(sunrisetime):
        return "night"
    elif int(currenttime) < int(sunsettime):
        return "day"
    else:
        return "evening-morning"

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        city_name = request.form['city_name']
        check = requests.get(
            'http://api.openweathermap.org/data/2.5/weather?q={}&appid=34f118c924d172de600a728aacb501b6&units=metric'.format(
                city_name))
        if city_name == '':
            return redirect('/')
        elif json.loads(check.content)['cod'] == '404':
            flash("The city doesn't exist!")
            return redirect('/')
        elif city_name.lower() in [str(el) for el in Weather.query.all()]:
            flash("The city has already been added to the list!")
            return redirect('/')
        else:
            city = Weather(name=city_name.lower())
            db.session.add(city)
            db.session.commit()
            return redirect('/')
    else:
      if Weather.query.all():
        sp=[]
        for el in Weather.query.all():
            res = requests.get(
                'http://api.openweathermap.org/data/2.5/weather?q={}&appid=34f118c924d172de600a728aacb501b6&units=metric'.format(
                    el))
            dict_with_weather_info = {'name': json.loads(res.content)['name'].upper(),
                                      'temp': int(json.loads(res.content)['main']['temp']),
                                      'weather': json.loads(res.content)['weather'][0]['main'],
                                      'id': el.id,
                                      'pic':day_or_night(json.loads(res.content)['dt'],
                                                         json.loads(res.content)['sys'].get('sunrise'),
                                                         json.loads(res.content)['sys'].get('sunset')
                                                         )}
            sp.append(dict_with_weather_info)
        return render_template('index.html',weather=reversed(sp))
      else:
          return render_template('index.html')

# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
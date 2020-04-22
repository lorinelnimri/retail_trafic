import json
from flask import request, render_template, make_response
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy(app)


@app.template_filter('formatdatetime')
def format_datetime(value, format="%Y-%m-%d %H:%M:%S.%f"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""

    if value is None:
        return ""
    dt = datetime.strptime(value, format)
    return dt.strftime('%B %d %Y - %I:%M %p')


@app.route('/', methods=['GET'])
def index():
    mac_log = db.engine.execute('SELECT * FROM mac_log')
    mac_log_no = db.engine.execute('SELECT COUNT(*) FROM mac_log')
    no = mac_log_no.fetchone()
    return render_template('index.html', mac_log=mac_log, device=no[0])


@app.route('/macs', methods=['GET'])
def macs():
    mac_log = db.engine.execute('SELECT * FROM mac_log')
    return render_template('macs.html', mac_log=mac_log)


@app.route('/mac/<mac>/', methods=['GET'])
def details(mac):
    mac_log = db.engine.execute(f'SELECT * FROM probes WHERE mac="{mac}" ')
    return render_template('frequency.html', mac_log=mac_log)

@app.route('/analytics/<mac>', methods=['GET'])
@app.route('/analytics', methods=['GET'])
def analytics(mac=None):
    if mac:
        probes = db.engine.execute(f'SELECT * FROM probes WHERE mac="{mac}" ')
        label = []
        data = []
        for mac in probes:

            enter_datetime = datetime.strptime(mac[2], '%Y-%m-%d %H:%M:%S.%f')
            last_seen = datetime.strptime(mac[3], '%Y-%m-%d %H:%M:%S.%f')
            time_diff = divmod((last_seen - enter_datetime).total_seconds(), 60)
            
            dt = datetime.strptime(mac[2], "%Y-%m-%d %H:%M:%S.%f")
            dt = dt.strftime('%B %d %Y - %I:%M %p')
            label.append(dt)
            data.append(time_diff[0])


        return make_response({
            'label': label,
            'data': data
            }), 200
        
    else:
        mac_log = db.engine.execute(f'SELECT * FROM mac_log  ORDER BY id DESC LIMIT 15')
        mac_data = []
        label = []
        data = []
        time_diff = []
        for mac in mac_log:
            mac_data.append({
                'id': mac[0],
                'mac': mac[1],
                'start_data': mac[2],
                'end_date': mac[3],
                'hz': mac[4],
            })
            enter_datetime = datetime.strptime(
                mac[2], '%Y-%m-%d %H:%M:%S.%f')
            last_seen = datetime.strptime(mac[3], '%Y-%m-%d %H:%M:%S.%f')

            label.append(mac[1].upper())
            data.append(mac[4])
            time_diff.append(divmod((last_seen - enter_datetime).total_seconds(), 3600)[0])

        return make_response({
            # 'message': mac_data,
            'pie': {
                'label': label, 
                'data': data
            },
            'bar': {
                'label': label,
                'data': time_diff
            },
        }), 200

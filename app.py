from flask import Flask, render_template, request, redirect, url_for, session
import paramiko

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management


def ssh_connect(hostname, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        return client, None
    except Exception as e:
        return None, str(e)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        hostname = request.form['hostname']
        username = request.form['username']
        password = request.form['password']

        ssh_client, error = ssh_connect(hostname, username, password)

        if ssh_client:
            session['ssh_client'] = True  # Store login state
            session['hostname'] = hostname
            session['username'] = username
            session['ssh_connection'] = ssh_client.get_transport().is_active()
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error=error)

    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if 'ssh_client' in session:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('dashboard.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


@app.route('/logout', methods=['POST'])
def logout():
    # Close SSH connection if exists
    session.pop('ssh_client', None)
    session.pop('hostname', None)
    session.pop('username', None)
    return redirect(url_for('login'))


#  code for the dashboard uris
@app.route('/backup_zone')
def backup_zone():
    # Logic for backing up the zone file
    if 'ssh_client' in session:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('backup_zone.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


@app.route('/generate_keys')
def generate_keys():
    # Logic for generating keys
    if 'ssh_client' in session:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('generate_keys.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


@app.route('/sign_zone')
def sign_zone():
    # Logic for signing the zone
    if 'ssh_client' in session:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('sign_zone.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


@app.route('/apply_changes')
def apply_changes():
    # Logic for signing the zone
    if 'ssh_client' in session:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('apply_changes.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))

@app.route('/statistics')
def statistics():
    # Logic for displaying statistics
    if 'ssh_client' in session:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('statistics.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

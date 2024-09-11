from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import paramiko

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ssh_client = None


def ssh_connect(hostname, username, password, port=22):
    global ssh_client
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, username=username, password=password, port=port)
        return None
    except Exception as e:
        ssh_client = None
        return str(e)


def execute_ssh_command(command):
    global ssh_client
    if ssh_client:
        try:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            stdout_data = stdout.read().decode('utf-8').strip()
            stderr_data = stderr.read().decode('utf-8').strip()

            if stderr_data:
                return None, stderr_data
            return stdout_data, None
        except Exception as e:
            return None, str(e)
    else:
        return None, "SSH session not active."


@app.route('/', methods=['GET', 'POST'])
def login():
    global ssh_client
    if request.method == 'POST':
        hostname = request.form['hostname']
        username = request.form['username']
        password = request.form['password']

        port = 2222 if hostname == 'localhost' else 22

        error = ssh_connect(hostname, username, password, port)

        if ssh_client:
            session['hostname'] = hostname
            session['username'] = username
            session['password'] = password
            session['port'] = port
            session['ssh_connection'] = ssh_client.get_transport().is_active()
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error=error)
    else:
        if ssh_client:
            ssh_client.close()
            ssh_client = None
        session.clear()
        return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    global ssh_client
    if ssh_client:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('dashboard.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


@app.route('/logout', methods=['POST'])
def logout():
    global ssh_client
    if ssh_client:
        ssh_client.close()
        ssh_client = None
    session.clear()
    return redirect(url_for('login'))


@app.route('/backup_zone')
def backup_zone():
    global ssh_client
    if ssh_client:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('backup_zone.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


# To be developed
@app.route('/check_zone_file_availability', methods=['POST'])
def check_zone_file_availability():
    data = request.get_json()
    zone_path = data['zone_path']
    file_name = data['file_name']

    if not zone_path or not file_name:
        return jsonify({'error': 'Zone path and file name are required.'}), 400

    command = f'ls {zone_path}/{file_name}'

    output, error = execute_ssh_command(command)

    if error:
        return jsonify({'available': False, 'error': error, 'zone_path': zone_path, 'file_name': file_name})
    else:
        return jsonify(
            {'available': True, 'message': f'{output}: File is available.', 'zone_path': zone_path,
             'file_name': file_name})


@app.route('/confirm_backup_zone_file', methods=['POST'])
def confirm_backup_zone_file():
    data = request.get_json()
    zone_path = data['zone_path']
    file_name = data['file_name']
    backup_zone_path = '/etc/bind/backup'

    if not zone_path or not file_name:
        return jsonify({'error': 'Zone path and file name are required.'}), 400

    check_backup_dir_command = f'mkdir -p {backup_zone_path}'
    output, error = execute_ssh_command(check_backup_dir_command)

    backup_file_command = f'cp {zone_path}/{file_name} {backup_zone_path}/{file_name}.backup'
    output, error = execute_ssh_command(backup_file_command)

    if error:
        return jsonify({
            'success': False,
            'error': f"Error occurred while creating the backup folder: {error}",
            'zone_path': zone_path,
            'file_name': file_name
        }),
    else:
        if error:
            return jsonify({
                'success': False,
                'error': f"Error occurred while backing up the file: {error}",
                'zone_path': zone_path,
                'file_name': file_name
            }),
        else:
            backup_file_location = f"{backup_zone_path}/{file_name}.backup"
            return jsonify({
                'success': True,
                'message': f"File has been successfully backed up to {backup_file_location}",
                'backup_location': backup_file_location
            })


# end of to be developed

@app.route('/generate_keys')
def generate_keys():
    global ssh_client
    if ssh_client:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('generate_keys.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


@app.route('/sign_zone')
def sign_zone():
    global ssh_client
    if ssh_client:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('sign_zone.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


@app.route('/apply_changes')
def apply_changes():
    global ssh_client
    if ssh_client:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('apply_changes.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


@app.route('/statistics')
def statistics():
    global ssh_client
    if ssh_client:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('statistics.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

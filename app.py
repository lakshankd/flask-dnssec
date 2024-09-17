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
    zone_path = data.get('zone_path')
    file_name = data.get('file_name')
    backup_zone_path = '/etc/bind/backup'

    if not zone_path or not file_name:
        return jsonify({'error': 'Zone path and file name are required.'}), 400

    mkdir_command = f'mkdir -p {backup_zone_path}'
    output, error = execute_ssh_command(mkdir_command)

    if error:
        return jsonify({'error': f"Error creating backup folder: {error}"}), 500

    command = f'cp {zone_path}/{file_name} {backup_zone_path}/{file_name}.backup'
    output, error = execute_ssh_command(command)

    if error:
        return jsonify({'error': f"Error occurred while backing up the file: {error}"}), 500
    else:
        backup_location = f"{backup_zone_path}/{file_name}.backup"
        return jsonify({
            'success': True,
            'message': f"File successfully backed up to {backup_location}",
            'backup_location': backup_location
        }), 200


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


@app.route('/generate_zsk_key', methods=['POST'])
def generate_zsk_key():
    data = request.get_json()
    algorithm = data.get('algorithm')
    key_size = data.get('key_size')
    domain_name = data.get('domain_name')

    if not algorithm or not key_size or not domain_name:
        return jsonify({'error': 'Algorithm, key size, and domain name are required.'}), 400

    mkdir_command = 'mkdir -p /etc/bind/keys'
    output, error = execute_ssh_command(mkdir_command)
    if error:
        return jsonify({'error': f"Error creating directory: {error}"}), 500

    zsk_command = f'cd /etc/bind/keys && dnssec-keygen -a {algorithm} -b {key_size} -n ZONE {domain_name}'
    zsk_output, zsk_error = execute_ssh_command(zsk_command)
    if zsk_error:
        return jsonify({'error': f"Error occurred while generating the ZSK key: {zsk_error}"}), 500

    return jsonify({
        'success': True,
        'message': 'ZSK key successfully generated',
        'output': zsk_output
    }), 200


@app.route('/generate_ksk_key', methods=['POST'])
def generate_ksk_key():
    data = request.get_json()
    algorithm = data.get('algorithm')
    key_size = data.get('key_size')
    domain_name = data.get('domain_name')

    if not algorithm or not key_size or not domain_name:
        return jsonify({'error': 'Algorithm, key size, and domain name are required.'}), 400

    mkdir_command = 'mkdir -p /etc/bind/keys'
    output, error = execute_ssh_command(mkdir_command)
    if error:
        return jsonify({'error': f"Error creating directory: {error}"}), 500

    ksk_command = f'cd /etc/bind/keys && dnssec-keygen -f KSK -a {algorithm} -b {key_size} -n ZONE {domain_name}'
    ksk_output, ksk_error = execute_ssh_command(ksk_command)
    if ksk_error:
        return jsonify({'error': f"Error occurred while generating the KSK key: {ksk_error}"}), 500

    return jsonify({
        'success': True,
        'message': 'KSK key successfully generated',
        'output': ksk_output
    }), 200


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

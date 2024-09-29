from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import paramiko
import re

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


def execute_ssh_command_with_sudo_password(command, password):
    global ssh_client
    if ssh_client:
        try:
            stdin, stdout, stderr = ssh_client.exec_command(f'echo {password} | sudo -S {command}')
            stdin.write(password + '\n')
            stdin.flush()

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


@app.route('/sign_zone_request', methods=['POST'])
def sign_zone_request():
    data = request.get_json()
    origin = data.get('origin')
    keys_directory = data.get('keys_directory')
    zone_file_path = data.get('zone_file_path')

    if not origin or not keys_directory or not zone_file_path:
        return jsonify({'error': 'Origin, keys directory, and zone file path are required.'}), 400

    check_zone_file_command = f'test -f {zone_file_path}'
    _, error = execute_ssh_command(check_zone_file_command)
    if error:
        return jsonify({'error': f'Zone file not found at {zone_file_path}.'}), 404

    check_keys_dir_command = f'test -d {keys_directory}'
    _, error = execute_ssh_command(check_keys_dir_command)
    if error:
        return jsonify({'error': f'Keys directory not found at {keys_directory}.'}), 404

    chown_keys_command = f'chown -R bind:bind {keys_directory}'
    _, chown_keys_error = execute_ssh_command(chown_keys_command)
    if chown_keys_error:
        return jsonify({'error': f"Error changing ownership of keys directory: {chown_keys_error}"}), 500

    chown_zones_command = f'chown -R bind:bind /etc/bind/zones'
    _, chown_zones_error = execute_ssh_command(chown_zones_command)
    if chown_zones_error:
        return jsonify({'error': f"Error changing ownership of zones directory: {chown_zones_error}"}), 500

    sign_command = f'cd /etc/bind/zones && dnssec-signzone -S -K {keys_directory} -o {origin} {zone_file_path}'
    output, sign_error = execute_ssh_command(sign_command)

    if sign_error:
        return jsonify({'error': f"Error occurred while signing the zone: {sign_error}"}), 500

    return jsonify({
        'success': True,
        'message': 'Zone successfully signed',
        'output': output
    }), 200


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


@app.route('/apply_changes_request', methods=['POST'])
def apply_changes_request():
    data = request.get_json()
    zone_name = data.get('zone_name')

    if not zone_name:
        return jsonify({'error': 'Zone name is required.'}), 400

    named_conf_local_path = '/etc/bind/named.conf.local'

    read_command = f'cat {named_conf_local_path}'
    named_conf_content, read_error = execute_ssh_command(read_command)

    print("named.conf.local file content:", named_conf_content)

    if read_error:
        return jsonify({'error': f"Error reading named.conf.local file: {read_error}"}), 500

    zone_start = f'zone "{zone_name}"'
    if zone_start not in named_conf_content:
        return jsonify({'error': f"Zone '{zone_name}' not found in named.conf.local"}), 404

    zone_block_start = named_conf_content.find(zone_start)

    if zone_block_start == -1:
        return jsonify({'error': f"Zone '{zone_name}' not found in named.conf.local"}), 404

    brace_count = 0
    zone_block_end = zone_block_start
    inside_zone_block = False

    for i in range(zone_block_start, len(named_conf_content)):
        char = named_conf_content[i]

        if char == '{':
            brace_count += 1
            inside_zone_block = True
        elif char == '}':
            brace_count -= 1

        if inside_zone_block and brace_count == 0:
            zone_block_end = i + 1
            break

    current_zone_block = named_conf_content[zone_block_start:zone_block_end]

    file_pattern = f'file "/etc/bind/zones/{zone_name}"'

    if file_pattern in current_zone_block:
        modified_zone_block = current_zone_block.replace(
            file_pattern,
            f'file "/etc/bind/zones/{zone_name}.signed"'
        )
    else:
        if f'file "/etc/bind/zones/{zone_name}.signed"' not in current_zone_block:
            modified_zone_block = current_zone_block.rstrip(
                '};') + f'\n    file "/etc/bind/zones/db.{zone_name}.signed";\n}}'
        else:
            modified_zone_block = current_zone_block

    key_directory_match = re.search(r'key-directory\s+"[^"]+";', modified_zone_block)

    existing_lines = re.findall(r'^\s+', modified_zone_block, re.MULTILINE)
    if existing_lines:
        indentation = existing_lines[0]
    else:
        indentation = "    "

    if key_directory_match:
        modified_zone_block = modified_zone_block
    else:
        modified_zone_block = modified_zone_block.rstrip('\n ').rstrip(
            '};') + f'{indentation}key-directory "/etc/bind/keys";\n}}'

    auto_dnssec_match = re.search(r'auto-dnssec\s+"?[^";]+"?;', modified_zone_block)

    existing_lines = re.findall(r'^\s+', modified_zone_block, re.MULTILINE)
    if existing_lines:
        indentation = existing_lines[0]
    else:
        indentation = "    "

    if auto_dnssec_match:
        modified_zone_block = re.sub(r'auto-dnssec\s+"?[^";]+"?;', f'{indentation}auto-dnssec maintain;',
                                     modified_zone_block)
    else:
        modified_zone_block = modified_zone_block.rstrip('\n ').rstrip(
            '};') + f'{indentation}auto-dnssec maintain;\n}}'

    inline_signing_match = re.search(r'inline-signing\s+"?[^";]+"?;', modified_zone_block)

    existing_lines = re.findall(r'^\s+', modified_zone_block, re.MULTILINE)
    if existing_lines:
        indentation = existing_lines[0]
    else:
        indentation = "    "

    if inline_signing_match:
        modified_zone_block = re.sub(r'inline-signing\s+"?[^";]+"?;', f'{indentation}inline-signing yes;',
                                     modified_zone_block)
    else:
        modified_zone_block = modified_zone_block.rstrip('\n ').rstrip(
            '};') + f'{indentation}inline-signing yes;\n}}'

    modified_named_conf_content = (named_conf_content[:zone_block_start] +
                                   modified_zone_block +
                                   named_conf_content[zone_block_end:])

    write_command = f'tee {named_conf_local_path} > /dev/null << EOF\n{modified_named_conf_content}\nEOF'

    _, write_error = execute_ssh_command(write_command)

    if write_error:
        return jsonify({'error': f"Error writing changes to named.conf.local file: {write_error}"}), 500

    reload_command = 'systemctl restart bind9'
    _, reload_error = execute_ssh_command(reload_command)

    if reload_error:
        return jsonify({'error': f"Error reloading BIND configuration: {reload_error}"}), 500

    return jsonify({
        'success': True,
        'message': f"Zone '{zone_name}' successfully updated and BIND reloaded."
    }), 200


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

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import paramiko
import re
from datetime import datetime, timezone

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


@app.route('/file_operations')
def file_operations():
    global ssh_client
    if ssh_client:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('file_operations.html', hostname=hostname, username=username,
                               connection_status=connection_status)
    else:
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


@app.route('/update_zone_file')
def update_zone_file():
    global ssh_client
    if ssh_client:
        hostname = session.get('hostname')
        username = session.get('username')
        connection_status = session.get('ssh_connection', False)
        return render_template('update_zone_file.html', hostname=hostname, username=username,
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

    current_time = datetime.now()
    date_str = current_time.strftime("%Y-%m-%d")
    time_str = current_time.strftime("%H-%M-%S")

    backup_file_name = f"{file_name}_{date_str}_{time_str}.backup"

    command = f'cp {zone_path}/{file_name} {backup_zone_path}/{backup_file_name}'
    output, error = execute_ssh_command(command)

    if error:
        return jsonify({'error': f"Error occurred while backing up the file: {error}"}), 500
    else:
        backup_location = f"{backup_zone_path}/{backup_file_name}"
        return jsonify({
            'success': True,
            'message': f"File successfully backed up to {backup_location}",
            'backup_location': backup_location
        }), 200


@app.route('/add_a_record', methods=['POST'])
def add_a_record():
    data = request.get_json()
    nameserver_ip = data.get('nameserver_ip')
    zone = data.get('zone_name')
    domain_name = data.get('domain_name')
    ip_address = data.get('ip')
    ttl = data.get('ttl', 3600)  # Default TTL to 3600 if not provided
    key = data.get('key')
    secret = data.get('secret')

    if not nameserver_ip or not zone or not domain_name or not ip_address or not key or not secret:
        return jsonify({'error': 'Nameserver IP, zone, domain name, key, secret and IP address are required.'}), 400

    nsupdate_command = f"echo -e 'server {nameserver_ip}\ndebug yes\nzone {zone}\nupdate add {domain_name} {ttl} A {ip_address}\nsend' | nsupdate -y {key}:{secret} -v"

    output, error = execute_ssh_command(nsupdate_command)

    # error handling removed due to the unexpected behavior
    # if error:
    #     return jsonify({'error': f"Error adding the A record: {error}"}), 500

    return jsonify({
        'success': True,
        'message': f"A record for {domain_name} successfully added with IP {ip_address} and TTL {ttl}.\nOutput: {output or error}"
    }), 200


@app.route('/update_a_record', methods=['POST'])
def update_a_record():
    data = request.get_json()
    nameserver_ip = data.get('nameserver_ip')
    zone = data.get('zone_name')
    domain_name = data.get('domain_name')
    new_ip_address = data.get('new_ip')
    ttl = data.get('ttl', 3600)  # Default TTL to 3600 if not provided
    key = data.get('key')
    secret = data.get('secret')
    a_record_to_update = data.get('a_record_to_update')

    if not nameserver_ip or not zone or not domain_name or not new_ip_address or not key or not secret or not a_record_to_update:
        return jsonify({'error': 'Nameserver IP, zone, domain name, and new IP address are required.'}), 400

    ns_command = f"echo -e 'server {nameserver_ip}\ndebug yes\nzone {zone}\nupdate delete {a_record_to_update}\nupdate add {domain_name} {ttl} A {new_ip_address}\nsend' | nsupdate -y {key}:{secret} -v"

    output, error = execute_ssh_command(ns_command)

    # error handling removed due to the unexpected behavior
    # if error:
    #     return jsonify({'error': f"Error updating the A record: {error}"}), 500

    return jsonify({
        'success': True,
        'message': f"A record for {domain_name} successfully updated to IP {new_ip_address} with TTL {ttl}.\nOutput: {output or error}"
    }), 200


@app.route('/delete_a_record', methods=['POST'])
def delete_a_record():
    data = request.get_json()
    nameserver_ip = data.get('nameserver_ip')
    zone = data.get('zone_name')
    a_record_to_delete = data.get('domain_name')
    key = data.get('key')
    secret = data.get('secret')

    if not nameserver_ip or not zone or not a_record_to_delete or not key or not secret:
        return jsonify({'error': 'Nameserver IP, zone, and domain name are required.'}), 400

    ns_command = f"echo -e 'server {nameserver_ip}\ndebug yes\nzone {zone}\nupdate delete {a_record_to_delete}\nsend' | nsupdate -y {key}:{secret} -v"

    output, error = execute_ssh_command(ns_command)

    # error handling removed due to the unexpected behavior
    # if error:
    #     return jsonify({'error': f"Error deleting the A record: {error}"}), 500

    return jsonify({
        'success': True,
        'message': f"A record for {a_record_to_delete} successfully deleted.\nOutput: {output or error}"
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

    sign_command = f'cd /etc/bind/zones && dnssec-signzone -S -K {keys_directory} -o {origin} {zone_file_path}'
    output, sign_error = execute_ssh_command(sign_command)

    if sign_error:
        return jsonify({'error': f"Error occurred while signing the zone: {sign_error}"}), 500

    return jsonify({
        'success': True,
        'message': 'Zone successfully signed',
        'output': output.replace("\n", "</br>")
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
    domain_name = data.get('domain_name')

    if not domain_name:
        return jsonify({'error': 'Domain name is required.'}), 400

    named_conf_local_path = '/etc/bind/named.conf.local'
    named_conf_options_path = '/etc/bind/named.conf.options'

    read_command = f'cat {named_conf_local_path}'
    named_conf_content, read_error = execute_ssh_command(read_command)

    if read_error:
        return jsonify({'error': f"Error reading named.conf.local file: {read_error}"}), 500

    zone_start = f'zone "{domain_name}"'
    if zone_start not in named_conf_content:
        return jsonify({'error': f"Domain name '{domain_name}' not found in named.conf.local"}), 404

    zone_block_start = named_conf_content.find(zone_start)

    if zone_block_start == -1:
        return jsonify({'error': f"Domain name '{domain_name}' not found in named.conf.local"}), 404

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

    file_pattern = f'file "/etc/bind/zones/db.{domain_name}"'

    if file_pattern in current_zone_block:
        modified_zone_block = current_zone_block.replace(
            file_pattern,
            f'file "/etc/bind/zones/db.{domain_name}.signed"'
        )
    else:
        if f'file "/etc/bind/zones/db.{domain_name}.signed"' not in current_zone_block:
            modified_zone_block = current_zone_block.rstrip(
                '};') + f'\n    file "/etc/bind/zones/db.{domain_name}.signed";\n}}'
        else:
            modified_zone_block = current_zone_block

    # modified_zone_block = current_zone_block

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

    modified_named_conf_content = (named_conf_content[:zone_block_start] +
                                   modified_zone_block +
                                   named_conf_content[zone_block_end:])

    write_command = f'tee {named_conf_local_path} > /dev/null << EOF\n{modified_named_conf_content}\nEOF'

    _, write_error = execute_ssh_command(write_command)

    if write_error:
        return jsonify({'error': f"Error writing changes to named.conf.local file: {write_error}"}), 500

    read_options_command = f'cat {named_conf_options_path}'
    named_conf_options_content, read_options_error = execute_ssh_command(read_options_command)

    if read_options_error:
        return jsonify({'error': f"Error reading named.conf.options file: {read_options_error}"}), 500

    lines = named_conf_options_content.split('\n')

    found_provide_ixfr = False
    found_dnssec_validation = False

    updated_lines = []
    inside_options_block = False

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith('options {'):
            inside_options_block = True
        elif stripped_line.startswith('};') and inside_options_block:
            if not found_provide_ixfr:
                updated_lines.append('    provide-ixfr yes;')
            if not found_dnssec_validation:
                updated_lines.append('    dnssec-validation auto;')

            inside_options_block = False

        if inside_options_block:
            if 'provide-ixfr' in stripped_line:
                updated_lines.append(re.sub(r'provide-ixfr\s+"?[^";]+"?;', 'provide-ixfr yes;', line))
                found_provide_ixfr = True
            elif 'dnssec-validation' in stripped_line:
                updated_lines.append(re.sub(r'dnssec-validation\s+"?[^";]+"?;', 'dnssec-validation auto;', line))
                found_dnssec_validation = True
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    updated_named_conf_options_content = '\n'.join(updated_lines)

    write_options_command = f'tee {named_conf_options_path} > /dev/null << EOF\n{updated_named_conf_options_content}\nEOF'
    _, write_options_error = execute_ssh_command(write_options_command)

    if write_options_error:
        return jsonify({'error': f"Error writing changes to named.conf.options file: {write_options_error}"}), 500

    reload_command = 'rndc reconfig'
    _, reload_error = execute_ssh_command(reload_command)

    if reload_error:
        return jsonify({'error': f"Error reloading BIND configuration: {reload_error}"}), 500

    rndc_command = f'rndc signing -list {domain_name}'
    rndc_output, rndc_error = execute_ssh_command(rndc_command)

    if rndc_error:
        return jsonify({'error': f"Error occurred while listing DS records: {rndc_error}"}), 500

    dsset_cat_command = f'cd /etc/bind/zones && cat dsset-{domain_name}.'
    dsset_cat_command_output, dsset_cat_command_error = execute_ssh_command(dsset_cat_command)

    if dsset_cat_command_error:
        return jsonify({'error': f"Error occurred while getting dsset: {dsset_cat_command_error}"}), 500

    return jsonify({
        'success': True,
        'message': f"Zone for '{domain_name}' successfully updated and BIND reloaded.",
        'rndc_output': rndc_output,
        'dsset_cat_command_output': dsset_cat_command_output
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


@app.route('/get_statistics', methods=['POST'])
def get_statistics():
    data = request.get_json()
    hostname = data.get('hostname')
    domain = data.get('domain')
    command_selected = data.get('command')

    if not hostname or not domain or not command_selected:
        return jsonify({'error': 'Hostname, Domain, and Command Type are required.'}), 400

    if command_selected == 'dnskey':
        command = f"dig DNSKEY {domain} @{hostname} +dnssec +multi"
    elif command_selected == 'soa':
        command = f"dig SOA {domain} @{hostname} +dnssec +multi"
    elif command_selected == 'rrsig':
        command = f"dig RRSIG {domain} @{hostname} +dnssec +multi"
    elif command_selected == 'a':
        command = f"dig A {domain} @{hostname} +dnssec +multi"
    elif command_selected == 'aaaa':
        command = f"dig AAAA {domain} @{hostname} +dnssec +multi"
    elif command_selected == 'mx':
        command = f"dig MX {domain} @{hostname} +dnssec +multi"
    elif command_selected == 'ns':
        command = f"dig NS {domain} @{hostname} +dnssec +multi"
    elif command_selected == 'ptr':
        command = f"dig PTR {domain} @{hostname} +dnssec +multi"
    elif command_selected == 'txt':
        command = f"dig TXT {domain} @{hostname} +dnssec +multi"
    else:
        return jsonify({'error': 'Invalid command selected.'}), 400

    output, error = execute_ssh_command(command)

    if error:
        return jsonify({'error': f"Error running command: {error}"}), 500

    expiration_command = f"dig +dnssec {domain} A @{hostname} | grep RRSIG | awk '{{print $9}}'"
    expiration_output, expiration_error = execute_ssh_command(expiration_command)

    if expiration_error or not expiration_output.strip():
        return jsonify({'error': 'Could not retrieve expiration date.'}), 500

    try:

        expiration_date_str = expiration_output.strip()
        expiration_date = datetime.strptime(expiration_date_str, '%Y%m%d%H%M%S')

        expiration_date = expiration_date.replace(tzinfo=timezone.utc)

        current_date = datetime.now(timezone.utc)

        days_to_expire = (expiration_date - current_date).days

    except ValueError:
        return jsonify({'error': 'Error parsing the expiration date format.'}), 500

    return jsonify({
        'success': True,
        'message': 'Successfully got statistics',
        'output': output.replace("\n", "</br>"),
        'expiration_date': expiration_date.strftime('%Y-%m-%d %H:%M:%S'),
        'days_to_expire': days_to_expire
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

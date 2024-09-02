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
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error=error)

    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if 'ssh_client' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('ssh_client', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

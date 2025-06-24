from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from utils.db import get_mysql_conn

users_bp = Blueprint('users', __name__)

# ---------------------- User Management ----------------------


@app.route('/api/users')
def api_users():
    role = request.args.get('role')
    # Use the first domain as the source of truth for users
    with open('domains.json') as f:
        domains = json.load(f)
    domain = domains[0]
    url = domain['url'].rstrip('/') + '/wp-json/wp/v2/users'
    auth = HTTPBasicAuth(domain['username'], domain['password'])
    params = {'per_page': 100}
    if role:
        params['roles'] = role
    resp = requests.get(url, auth=auth, params=params)
    if resp.status_code == 200:
        return jsonify([
            {
                'id': u['id'],
                'name': u['name'],
                'email': u.get('email', ''),
                'roles': u.get('roles', [])
            } for u in resp.json()
        ])
    return jsonify([]), resp.status_code

@app.route('/api/add-user', methods=['POST'])
def api_add_user():
    data = request.json
    # Add user to all domains
    with open('domains.json') as f:
        domains = json.load(f)
    success = False
    errors = []  # Collect errors from each domain
    for domain in domains:
        url = domain['url'].rstrip('/') + '/wp-json/wp/v2/users'
        auth = HTTPBasicAuth(domain['username'], domain['password'])
        try:
            resp = requests.post(url, auth=auth, json=data)
            resp.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            if resp.status_code in (200, 201):
                success = True
            else:
                errors.append(f"Domain: {domain['domain']}, Status Code: {resp.status_code}, Response: {resp.text}")
        except requests.exceptions.RequestException as e:
            errors.append(f"Domain: {domain['domain']}, Error: {str(e)}")

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'errors': errors}), 400

@app.route('/user-management')
def user_management():
    return render_template('user-management.html')


@app.route('/bulk-add-user', methods=['GET', 'POST'])
def bulk_add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'subscriber')

        with open('domains.json') as f:
            domains = json.load(f)
        results = []
        registered = False
        for domain in domains:
            url = domain['url'].rstrip('/') + '/wp-json/wp/v2/users'
            auth = HTTPBasicAuth(domain['username'], domain['password'])
            data = {
                'username': username,
                'email': email,
                'password': password,
                'role': role
            }   

            try:
                resp = requests.post(url, auth=auth, json=data, timeout=10)
                if resp.status_code in (200, 201):
                    results.append((domain['domain'], '✅ Success'))
                    registered = True
                else:
                    try:
                        error_msg = resp.json().get('message', 'Unknown error')
                    except:
                        error_msg = resp.text
                    results.append((domain['domain'], f"❌ Failed: {resp.status_code} - {error_msg}"))
            except Exception as e:
                results.append((domain['domain'], f"🚨 Error: {e}"))

        # Send email if registered on at least one domain
        if registered:
            msg = Message(
                subject="Welcome to Our Platform",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"Hello {username},\n\nYour account has been created on our platform. You can now log in.\n\nThanks!"
            )
            mail.send(msg)

        return render_template('bulk_add_user.html', results=results)

    return render_template('bulk_add_user.html', results=None)


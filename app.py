from flask import Flask, request, render_template, render_template_string, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a real secret key
CORS(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# In-memory storage for messages and users (replace with a database in a real application)
messages = []
users = {}

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in [user.username for user in users.values()]:
            return "Username already exists"
        user_id = str(len(users) + 1)
        users[user_id] = User(user_id, username, generate_password_hash(password))
        return redirect(url_for('login'))
    return render_template_string('''
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Register">
        </form>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = next((user for user in users.values() if user.username == username), None)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        return "Invalid username or password"
    return render_template_string('''
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Login">
        </form>
    ''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/business')
@login_required
def business_dashboard():
    return render_template_string('''
        <div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl p-4">
            <h2 class="text-xl font-bold mb-4">Business Dashboard</h2>
            <form hx-post="/send_message" hx-target="#message-status">
                <div class="mb-4">
                    <label for="message" class="block text-gray-700 text-sm font-bold mb-2">Message:</label>
                    <textarea id="message" name="message" rows="4" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required></textarea>
                </div>
                <div class="mb-4">
                    <label for="recipients" class="block text-gray-700 text-sm font-bold mb-2">Recipients (comma-separated):</label>
                    <input type="text" id="recipients" name="recipients" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required>
                </div>
                <div class="flex items-center justify-between">
                    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                        Send Message
                    </button>
                </div>
            </form>
            <div id="message-status" class="mt-4"></div>
        </div>
    ''')

@app.route('/user')
@login_required
def user_inbox():
    return render_template_string('''
        <div class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl p-4">
            <h2 class="text-xl font-bold mb-4">User Inbox</h2>
            <div id="messages" hx-get="/get_messages" hx-trigger="load">
                Loading messages...
            </div>
        </div>
    ''')

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    message = request.form.get('message')
    recipients = request.form.get('recipients').split(',')
    
    for recipient in recipients:
        messages.append({
            'id': len(messages) + 1,
            'content': message,
            'sender': current_user.username,
            'recipient': recipient.strip()
        })
    
    return f"Message sent to {len(recipients)} recipient(s)"

@app.route('/get_messages')
@login_required
def get_messages():
    user_messages = [msg for msg in messages if msg['recipient'] == current_user.username]
    return render_template_string('''
        {% if messages %}
            {% for msg in messages %}
                <div class="border-b py-2">
                    <p class="font-bold">From: {{ msg.sender }}</p>
                    <p>{{ msg.content }}</p>
                </div>
            {% endfor %}
        {% else %}
            <p>No messages found.</p>
        {% endif %}
    ''', messages=user_messages)

if __name__ == '__main__':
    app.run(debug=True)

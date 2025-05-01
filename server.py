from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import docker
import json
import os
import subprocess
from datetime import datetime, timedelta
import secrets
import psutil
import platform

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
docker_client = docker.from_env()

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# App Model
class InstalledApp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(120), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    container_id = db.Column(db.String(64))
    status = db.Column(db.String(20), default='running')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403
        user.last_login = datetime.utcnow()
        db.session.commit()
        login_user(user)
        return jsonify({'message': 'Logged in successfully', 'role': user.role})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    user = User(username=data['username'])
    user.set_password(data['password'])
    user.role = 'user'
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'})

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/apps')
@login_required
def get_apps():
    try:
        with open('repos/default.json', 'r') as f:
            apps = json.load(f)
        return jsonify(apps)
    except FileNotFoundError:
        return jsonify({'error': 'Repository not found'}), 404

@app.route('/api/apps/installed')
@login_required
def get_installed_apps():
    apps = InstalledApp.query.all()
    return jsonify([{
        'id': app.id,
        'name': app.name,
        'image': app.image,
        'port': app.port,
        'status': app.status,
        'created_at': app.created_at.isoformat(),
        'updated_at': app.updated_at.isoformat()
    } for app in apps])

@app.route('/api/apps/install', methods=['POST'])
@login_required
def install_app():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    try:
        # Create volumes if specified
        volumes = data.get('config', {}).get('volumes', [])
        for volume in volumes:
            host_path = volume.split(':')[0]
            os.makedirs(host_path, exist_ok=True)

        # Create container with all specified configurations
        container = docker_client.containers.run(
            data['image'],
            detach=True,
            ports={f"{port}/tcp": port for port in data.get('config', {}).get('ports', {}).values()},
            volumes=volumes,
            environment=data.get('config', {}).get('environment', {}),
            name=data['name']
        )

        # Save to database
        app = InstalledApp(
            name=data['name'],
            image=data['image'],
            port=data['port'],
            container_id=container.id
        )
        db.session.add(app)
        db.session.commit()

        return jsonify({'message': f'App {data["name"]} installed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apps/<int:app_id>/stop', methods=['POST'])
@login_required
def stop_app(app_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    app = InstalledApp.query.get_or_404(app_id)
    try:
        container = docker_client.containers.get(app.container_id)
        container.stop()
        app.status = 'stopped'
        db.session.commit()
        return jsonify({'message': f'App {app.name} stopped successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apps/<int:app_id>/start', methods=['POST'])
@login_required
def start_app(app_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    app = InstalledApp.query.get_or_404(app_id)
    try:
        container = docker_client.containers.get(app.container_id)
        container.start()
        app.status = 'running'
        db.session.commit()
        return jsonify({'message': f'App {app.name} started successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/apps/<int:app_id>/restart', methods=['POST'])
@login_required
def restart_app(app_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    app = InstalledApp.query.get_or_404(app_id)
    try:
        container = docker_client.containers.get(app.container_id)
        container.restart()
        app.status = 'running'
        db.session.commit()
        return jsonify({'message': f'App {app.name} restarted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users')
@login_required
def get_users():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'is_active': user.is_active
    } for user in users])

@app.route('/api/users/<int:user_id>/promote', methods=['POST'])
@login_required
def promote_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    user.role = 'admin'
    db.session.commit()
    return jsonify({'message': 'User promoted to admin'})

@app.route('/api/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'message': f'User {"enabled" if user.is_active else "disabled"} successfully'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

# System Monitoring Routes
@app.route('/api/system/stats')
@login_required
def get_system_stats():
    try:
        # CPU Stats
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        cpu_temp = None
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                cpu_temp = temps['cpu_thermal'][0].current

        # Memory Stats
        memory = psutil.virtual_memory()
        memory_used = memory.used
        memory_total = memory.total
        memory_percent = memory.percent

        # Storage Stats
        storage = psutil.disk_usage('/')
        storage_used = storage.used
        storage_total = storage.total
        storage_percent = storage.percent

        return jsonify({
            'cpu': {
                'usage': cpu_percent,
                'temperature': cpu_temp,
                'frequency': cpu_freq.current if cpu_freq else None
            },
            'memory': {
                'used': memory_used,
                'total': memory_total,
                'usage': memory_percent
            },
            'storage': {
                'used': storage_used,
                'total': storage_total,
                'usage': storage_percent
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/info')
@login_required
def get_system_info():
    try:
        # System Information
        hostname = platform.node()
        os_info = platform.platform()
        kernel = platform.release()
        uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        
        # CPU Information
        cpu_info = platform.processor()
        cpu_cores = psutil.cpu_count(logical=False)
        architecture = platform.machine()
        load_avg = os.getloadavg()

        return jsonify({
            'hostname': hostname,
            'os': os_info,
            'kernel': kernel,
            'uptime': uptime.total_seconds(),
            'cpuModel': cpu_info,
            'cpuCores': cpu_cores,
            'architecture': architecture,
            'loadAverage': f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/cpu-settings')
@login_required
def get_cpu_settings():
    try:
        # Get current CPU governor
        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'r') as f:
            governor = f.read().strip()

        # Get CPU frequency limits
        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq', 'r') as f:
            min_freq = int(f.read().strip()) // 1000  # Convert to MHz

        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq', 'r') as f:
            max_freq = int(f.read().strip()) // 1000  # Convert to MHz

        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq', 'r') as f:
            current_freq = int(f.read().strip()) // 1000  # Convert to MHz

        return jsonify({
            'governor': governor,
            'frequency': current_freq,
            'minFrequency': min_freq,
            'maxFrequency': max_freq
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/cpu-settings/governor', methods=['POST'])
@login_required
def set_cpu_governor():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        governor = data.get('governor')
        
        if governor not in ['performance', 'ondemand', 'powersave']:
            return jsonify({'error': 'Invalid governor'}), 400

        # Set CPU governor for all cores
        for cpu in range(psutil.cpu_count()):
            with open(f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor', 'w') as f:
                f.write(governor)

        return jsonify({'message': 'CPU governor updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/cpu-settings/frequency', methods=['POST'])
@login_required
def set_cpu_frequency():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        frequency = data.get('frequency')
        
        if not isinstance(frequency, int) or frequency < 0:
            return jsonify({'error': 'Invalid frequency'}), 400

        # Convert MHz to Hz
        frequency_hz = frequency * 1000

        # Set CPU frequency for all cores
        for cpu in range(psutil.cpu_count()):
            with open(f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_setspeed', 'w') as f:
                f.write(str(frequency_hz))

        return jsonify({'message': 'CPU frequency updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/memory/swappiness', methods=['POST'])
@login_required
def set_swappiness():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        value = data.get('value')
        
        if not isinstance(value, int) or value < 0 or value > 100:
            return jsonify({'error': 'Invalid swappiness value'}), 400

        # Set swappiness
        with open('/proc/sys/vm/swappiness', 'w') as f:
            f.write(str(value))

        return jsonify({'message': 'Swappiness updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/memory/cache-pressure', methods=['POST'])
@login_required
def set_cache_pressure():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        value = data.get('value')
        
        if not isinstance(value, int) or value < 0 or value > 100:
            return jsonify({'error': 'Invalid cache pressure value'}), 400

        # Set cache pressure
        with open('/proc/sys/vm/vfs_cache_pressure', 'w') as f:
            f.write(str(value))

        return jsonify({'message': 'Cache pressure updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000) 
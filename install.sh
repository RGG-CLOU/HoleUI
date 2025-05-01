#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Install Pi-hole if not already installed
if ! command -v pihole &> /dev/null; then
  echo "Installing Pi-hole..."
  curl -sSL https://install.pi-hole.net | bash
fi

# Install Docker and Docker Compose if not installed
if ! command -v docker &> /dev/null; then
  echo "Installing Docker..."
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null; then
  echo "Installing Docker Compose..."
  curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
fi

# Create HoleUI directory
mkdir -p /opt/holeui
cd /opt/holeui

# Clone HoleUI repository
git clone https://github.com/RGG-CLOU/HoleUI.git .

# Configure Pi-hole lighttpd to proxy HoleUI
cat > /etc/lighttpd/conf-available/10-holeui.conf << EOF
\$HTTP["url"] =~ "^/holeui" {
    proxy.server = ( "" => ( ( "host" => "127.0.0.1", "port" => 8080 ) ) )
    proxy.header = ( "upgrade" => "enable" )
}
EOF

# Enable the configuration
ln -sf /etc/lighttpd/conf-available/10-holeui.conf /etc/lighttpd/conf-enabled/
systemctl restart lighttpd

# Build and start HoleUI
docker-compose up -d --build

# Create initial admin user
echo "Creating initial admin user..."
docker-compose exec backend python3 -c "
from server import app, db, User
with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin')
        admin.role = 'admin'
        db.session.add(admin)
        db.session.commit()
"

echo "Installation complete!"
echo "Access HoleUI at: http://your-pi-hole-ip/holeui"
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: admin"
echo "Please change these credentials immediately!"
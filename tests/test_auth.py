def test_home_page_loads(client):
    """La página principal carga correctamente."""
    response = client.get('/')
    assert response.status_code == 200


def test_login_page_loads(client):
    """La página de login carga correctamente."""
    response = client.get('/login')
    assert response.status_code == 200


def test_register_page_loads(client):
    """La página de registro carga correctamente."""
    response = client.get('/register')
    assert response.status_code == 200


def test_login_with_wrong_credentials(client):
    """Login con credenciales incorrectas muestra error."""
    response = client.post('/login', data={
        'username': 'usuarioinexistente',
        'password': 'passwordincorrecto'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'incorrectos' in response.data.decode('utf-8').lower()


def test_register_new_user(client, db):
    """Registro de un usuario nuevo funciona correctamente."""
    response = client.post('/register', data={
        'username': 'nuevousuario',
        'email': 'nuevo@test.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'telefono': '3764111111'
    }, follow_redirects=True)
    assert response.status_code == 200
    from models import Usuario
    from app import create_app
    user = Usuario.query.filter_by(name='nuevousuario').first()
    assert user is not None


def test_register_duplicate_username(client, db):
    """Registro con username duplicado muestra error."""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'otro@test.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'telefono': '3764222222'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'uso' in response.data.decode('utf-8').lower()


def test_user_panel_requires_login(client):
    """El panel de usuario redirige si no hay sesión."""
    response = client.get('/user_panel', follow_redirects=False)
    assert response.status_code == 302


def test_admin_panel_requires_login(client):
    """El panel de admin redirige si no hay sesión."""
    response = client.get('/admin_panel', follow_redirects=False)
    assert response.status_code == 302


def test_favorites_requires_login(client):
    """Favoritos redirige si no hay sesión."""
    response = client.get('/favorites', follow_redirects=False)
    assert response.status_code == 302


def test_authenticated_user_can_access_panel(auth_client):
    """Usuario autenticado puede acceder al panel."""
    response = auth_client.get('/user_panel')
    assert response.status_code == 200


def test_listings_page_loads(client):
    """La página de listings carga correctamente."""
    response = client.get('/listings')
    assert response.status_code == 200
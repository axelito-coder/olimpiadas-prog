from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_password_no_guarda_texto_plano():
    hashed = hash_password("miclave123")
    assert hashed != "miclave123"
    assert verify_password("miclave123", hashed)
    assert not verify_password("otraclave", hashed)


def test_create_and_decode_access_token():
    token = create_access_token(subject="user@kiosco.com", rol="admin")
    payload = decode_access_token(token)
    assert payload["sub"] == "user@kiosco.com"
    assert payload["rol"] == "admin"


def test_decode_access_token_invalido():
    import pytest

    with pytest.raises(ValueError):
        decode_access_token("token-invalido")

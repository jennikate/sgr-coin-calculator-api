def test_db_uri(app):
    print(">>> DB URI in test:", app.config["SQLALCHEMY_DATABASE_URI"])
    assert "localhost:5544" in app.config["SQLALCHEMY_DATABASE_URI"]
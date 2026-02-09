class Config:
    SECRET_KEY = "90c6443319e18a59dd1849e5c6ce3132f9beda507f34807fe757cbbe398361b8"

    SQLALCHEMY_DATABASE_URI = "sqlite:///planner.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "gaurav.rayat2004@gmail.com"
    MAIL_PASSWORD = "shphtdqdgosysuhl"
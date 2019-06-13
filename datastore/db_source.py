from flask import Flask
from flask_sqlalchemy import SQLAlchemy as sql

import datastore.db_packages as pk

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datastore/dbfile.db'
db = sql(app)


class Ecosystem(db.Model):
    __tablename__ = 'ecosystem'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    packages = sql.relationship('Packages', backref='eco')


class Packages(db.Model):

    __tablename__ = 'packages'
    id = db.Column(db.Integer, primary_key=True)
    eco_id = db.Column(db.Integer, db.ForeignKey('ecosystem.id'))
    name = db.Column(db.String)
    description = db.Column(db.String)
    repo = db.Column(db.String)
    versions = sql.relationship('Versions', backref='pack')


class Versions(db.Model):
    __tablename__ = 'versions'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String)
    package = db.Column(db.String, db.ForeignKey('packages.name'))


class SqlalchemyDatabase(object):
    def __init__(self, backend):
        db.Model.metadata.create_all()
        self.session = db.create_scoped_session()

    def store(self, *args):
        session = self.session
        package_in_db = None
        for package in args:
            try:
                package_to_dict = package.to_dict()
                if 'eco' in package_to_dict:
                    exists = self.restore_from_table(package_to_dict['name'], 'packages')
                    if exists is None:
                        pass

                elif 'pack' in package_to_dict:
                    exists = self.restore_from_table(package_to_dict['version'], 'versions')
                    if exists is None:
                        pass

                elif 'name' in package_to_dict:
                    exists = self.restore_from_table(package_to_dict['name'], 'ecosystem')
                    if exists is None:
                        pass

            except Exception as e:
                print(e)
        session.commit()

    def restore_all(self, table):
        session = self.session
        item = []
        try:
            if table.title() == 'Ecosystem':
                items = Ecosystem.query.all()
                for i in items:
                    item.append(pk.Package(i.name))

            elif table.title() == 'Packages':
                items = Packages.query.all()
                for i in items:
                    item.append(pk.Description(i.name, i.description, i.repo, i.eco))

            elif table.title() == 'Versions':
                items = Versions.quary.all()
                for i in items:
                    item.append(pk.Version(i.version, i.package))

            return item

        except Exception as e:
            print(e)

    def restore_from_table(self, name, table):
        session = self.session
        try:
            if table.title() == 'Ecosystem':
                eco = Ecosystem.query.filter_by(name=name).first()
                if eco is None:
                    return None
                package = pk.Package(eco.name)

            elif table.title() == 'Packages':
                pack = Packages.query.filter_by(name=name).first()
                if pack is None:
                    return None

            elif table.title() == 'Versions':
                ver = Versions.query.filter_by(version=name).first()
                if ver is None:
                    return None
                package = pk.Version(ver.version, ver.package)

            else:
                print('Badly defined table to add to')

            return package

        except Exception as e:
            print(e)

    def restore_from_master(self, name, master_table):
        session = self.session
        packages = []

        try:
            if master_table.title() == 'Ecosystem':
                package = Ecosystem.query.filter_by(name=name).first()
                if package is None:
                    return None
                id = package.id
                packs_from_db = Packages.query.filter_by(eco_id=id).all()
                for pack in packs_from_db:
                    package = pk.Description(pack.name, pack.description, pack.repo, pack.eco)
                    packages.append(package)
            elif master_table.title() == 'Package':
                package = Packages.query.filter_by(name=name).first()
                if package is None:
                    return None
                name = package.name
                vers = Versions.query.filter_by(package=name).all()
                for ver in vers:
                    version = pk.Version(ver.version, ver.package)
                    packages.append(version)

            else:
                print('Bad master table')

            return packages

        except Exception as e:
            print(e)
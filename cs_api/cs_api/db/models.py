from cs_api.server import db


run_tecttypes = db.Table(
    'run_tecttypes',
    db.Column('run_id', db.Integer, db.ForeignKey('runs.id'), primary_key=True),
    db.Column('tecttype_id', db.Integer, db.ForeignKey('tect_types.id'), primary_key=True)
)


run_datatypes = db.Table(
    'run_data_types',
    db.Column('run_id', db.Integer, db.ForeignKey('runs.id'), primary_key=True),
    db.Column('datatype_id', db.Integer, db.ForeignKey('data_types.id'), primary_key=True)
)

run_faults = db.Table(
    'run_faults',
    db.Column('run_id', db.Integer, db.ForeignKey('runs.id'), primary_key=True),
    db.Column('fault_id', db.Integer, db.ForeignKey('faults.id'), primary_key=True)
)

fault_files = db.Table(
    'fault_files',
    db.Column('fault_id', db.Integer, db.ForeignKey('faults.id'), primary_key=True),
    db.Column('file_id', db.Integer, db.ForeignKey('files.id'), primary_key=True)
)


class Run(db.Model):
    __tablename__ = "runs"
    id = db.Column(db.Integer, primary_key=True)
    run_name = db.Column(
        db.String(100),
        unique=True,
    )

    n_faults = db.Column(db.Integer)
    region = db.Column(db.String(100))

    grid_spacing_id = db.Column(db.Integer, db.ForeignKey('grid_spacings.id'))
    grid_spacing = db.relationship('GridSpacing')
    scientific_version_id = db.Column(db.Integer, db.ForeignKey('scientific_versions.id'))
    scientific_version = db.relationship('ScientificVersion')

    tect_types = db.relationship("TectType", secondary=run_tecttypes, backref='runs')
    data_types = db.relationship("DataType", secondary=run_datatypes, backref='runs')
    faults = db.relationship("Fault", secondary=run_faults, backref='runs')


class Fault(db.Model):
    __tablename__ = "faults"
    id = db.Column(db.Integer, primary_key=True)

    fault_name = db.Column(
        db.String(100),
    )

    run_id = db.Column(db.Integer, db.ForeignKey('runs.id'))
    run = db.relationship('Run')

    files = db.relationship("File", secondary=fault_files, backref='faults')


class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)

    file_name = db.Column(
        db.String(100),
    )
    download_link = db.Column(
        db.String(255),
    )
    file_size = db.Column(
        db.Integer,
    )

    data_type_id = db.Column(db.Integer, db.ForeignKey('data_types.id'))
    data_type = db.relationship('DataType')


class TectType(db.Model):
    __tablename__ = "tect_types"
    id = db.Column(db.Integer, primary_key=True)
    tect_type = db.Column(
        db.String(100),
        unique=True
    )


class DataType(db.Model):
    __tablename__ = "data_types"
    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(
        db.String(100),
        unique=True
    )


class GridSpacing(db.Model):
    __tablename__ = "grid_spacings"
    id = db.Column(db.Integer, primary_key=True)
    grid_spacing = db.Column(
        db.String(100),
        unique=True
    )


class ScientificVersion(db.Model):
    __tablename__ = "scientific_versions"
    id = db.Column(db.Integer, primary_key=True)
    scientific_version = db.Column(
        db.String(100),
        unique=True
    )

from cs_api.server import db


class RunTectType(db.Model):
    __tablename__ = "run_tect_types"
    run_name = db.Column(
        db.String(100),
        db.ForeignKey("runs.run_name"),
        primary_key=True,
    )
    tect_type = db.Column(
        db.String(100),
        db.ForeignKey("tect_types.tect_type"),
        primary_key=True,
    )

    def __init__(self, run_name, tect_type):
        self.run_name = run_name
        self.tect_type = tect_type


class Run(db.Model):
    __tablename__ = "runs"
    run_name = db.Column(
        db.String(100),
        primary_key=True,
    )
    n_faults = db.Column(db.Integer)
    region = db.Column(db.String(100))
    grid_spacing = db.Column(db.Integer)
    scientific_version = db.Column(db.String(100))
    tect_types = db.relationship("RunTectType", back_populates="run")

    def __init__(self, run_name, n_faults, region, grid_spacing, scientific_version, tect_types):
        self.run_name = run_name
        self.n_faults = n_faults
        self.region = region
        self.grid_spacing = grid_spacing
        self.scientific_version = scientific_version
        self.tect_types = tect_types


class TectType(db.Model):
    __tablename__ = "tect_types"
    tect_type = db.Column(
        db.String(100),
        primary_key=True,
    )

    def __init__(self, tect_type):
        self.tect_type = tect_type


class DataType(db.Model):
    __tablename__ = "data_types"
    data_type = db.Column(
        db.String(100),
        primary_key=True,
    )

    def __init__(self, data_type):
        self.data_type = data_type


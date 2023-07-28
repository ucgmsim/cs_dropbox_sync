from cs_api.server import db

from cs_api import constants as const
from dropbox_rclone import dropbox_reading


run_tecttypes = db.Table(
    "run_tecttypes",
    db.Column("run_id", db.Integer, db.ForeignKey("runs.id"), primary_key=True),
    db.Column(
        "tecttype_id", db.Integer, db.ForeignKey("tect_types.id"), primary_key=True
    ),
)


run_datatypes = db.Table(
    "run_data_types",
    db.Column("run_id", db.Integer, db.ForeignKey("runs.id"), primary_key=True),
    db.Column(
        "datatype_id", db.Integer, db.ForeignKey("data_types.id"), primary_key=True
    ),
)

run_faults = db.Table(
    "run_faults",
    db.Column("run_id", db.Integer, db.ForeignKey("runs.id"), primary_key=True),
    db.Column("fault_id", db.Integer, db.ForeignKey("faults.id"), primary_key=True),
)

fault_files = db.Table(
    "fault_files",
    db.Column("fault_id", db.Integer, db.ForeignKey("faults.id"), primary_key=True),
    db.Column("file_id", db.Integer, db.ForeignKey("files.id"), primary_key=True),
)


class Run(db.Model):
    __tablename__ = "runs"
    id = db.Column(db.Integer, primary_key=True)
    run_name = db.Column(
        db.String(100),
        unique=True,
    )
    type_id = db.Column(db.Integer, db.ForeignKey("run_types.id"))
    type = db.relationship("RunType")

    n_faults = db.Column(db.Integer)
    region = db.Column(db.String(100))

    grid_spacing_id = db.Column(db.Integer, db.ForeignKey("grid_spacings.id"))
    grid_spacing = db.relationship("GridSpacing")

    tect_types = db.relationship("TectType", secondary=run_tecttypes, backref="runs")
    data_types = db.relationship("DataType", secondary=run_datatypes, backref="runs")
    faults = db.relationship("Fault", secondary=run_faults, backref="runs")

    def __init__(self, run_name, run_info):
        """
        Create a run object from a run name
        from extracting the data from dropbox

        Parameters
        ----------
        run_name : str
            Name of the run
        run_info : dict
            Dictionary of run metadata information
        """
        faults = dropbox_reading.get_run_info(run_name)
        dbx = dropbox_reading.get_dropbox_api_object()
        self.run_name = run_name
        self.n_faults = len(faults)
        self.region = run_info["region"]
        self.grid_spacing = GridSpacing.query.filter_by(
            grid_spacing=run_info["grid"]
        ).first()
        self.type = RunType.query.filter_by(
            type=str(run_info["type"])
        ).first()
        self.tect_types = [
            TectType.query.filter_by(tect_type=tect_type).first()
            for tect_type in run_info["tectonic_types"]
        ]
        # Create each fault for the run
        data_types_found = set()
        run_faults_list = []
        for fault, files in faults.items():
            fault_files_list = []
            for file_name, file_size in files.items():
                data_type_str = file_name.split(".")[0].split("_")[1]
                file_data_type = DataType.query.filter_by(
                    data_type=data_type_str
                ).first()
                data_types_found.add(file_data_type)
                file_path = dropbox_reading.get_full_dropbox_path(
                    run_name, file_name.split("/")[1]
                )
                file_obj = File(
                    file_name=file_name.split("/")[1],
                    download_link=dropbox_reading.get_download_link(file_path, dbx),
                    file_size=file_size,
                    data_type=file_data_type,
                )
                fault_files_list.append(file_obj)
                db.session.add(file_obj)
            fault_obj = Fault(
                fault_name=fault,
                run=self,
                files=fault_files_list,
            )
            run_faults_list.append(fault_obj)
            db.session.add(fault_obj)
        self.data_types = list(data_types_found)
        self.faults = run_faults_list


class Fault(db.Model):
    __tablename__ = "faults"
    id = db.Column(db.Integer, primary_key=True)

    fault_name = db.Column(
        db.String(100),
    )

    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"))
    run = db.relationship("Run")

    files = db.relationship("File", secondary=fault_files, backref="faults")


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

    data_type_id = db.Column(db.Integer, db.ForeignKey("data_types.id"))
    data_type = db.relationship("DataType")


class TectType(db.Model):
    __tablename__ = "tect_types"
    id = db.Column(db.Integer, primary_key=True)
    tect_type = db.Column(db.String(100), unique=True)


class DataType(db.Model):
    __tablename__ = "data_types"
    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String(100), unique=True)


class GridSpacing(db.Model):
    __tablename__ = "grid_spacings"
    id = db.Column(db.Integer, primary_key=True)
    grid_spacing = db.Column(db.String(100), unique=True)


class RunType(db.Model):
    __tablename__ = "run_types"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), unique=True)

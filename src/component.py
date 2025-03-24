"""
Template Component main class.

"""

import codecs
import json
import logging
import os
import zipfile
from datetime import datetime

import duckdb
from duckdb import DuckDBPyConnection
from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from client.cloud_storage_client import CloudStorageClient
from configuration import Configuration

DUCK_DB_MAX_MEMORY = "128MB"
DUCK_DB_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "duckdb")
FILES_TEMP_DIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "files")


class Component(ComponentBase):
    """
    Extends base class for general Python components. Initializes the CommonInterface
    and performs configuration validation.

    For easier debugging the data folder is picked up by default from `../data` path,
    relative to working directory.

    If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()
        self.duck = self.init_duckdb()
        self.state = self.get_state_file()
        self.params = Configuration(**self.configuration.parameters)
        self.mapping = None

    def run(self):
        date_from = self._get_date_from()
        self.state["last_run"] = datetime.now().timestamp()

        client = CloudStorageClient(self.params.gcp_service_account_key)

        logging.info(f"Downloading files from bucket {self.params.bucket_id}")

        client.download_files_from_bucket(FILES_TEMP_DIR, date_from, self.params.bucket_id)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        mapping_paths = [os.path.join(current_dir, "mapping.json"), "/code/src/mapping.json"]

        for mapping_path in mapping_paths:
            if os.path.exists(mapping_path):
                with open(mapping_path, "r") as f:
                    self.mapping = json.load(f)
                    break

        for report in self.params.reports:
            self.process_report(report)

        self.write_state_file(self.state)

    def process_report(self, report_name):
        logging.info(f"Processing report {report_name}")
        path = os.path.join(FILES_TEMP_DIR, report_name)
        report_config = self.mapping.get(report_name)

        if report_config.get("is_zipped"):
            path = self.unzip_files_in_folder(path)
            path_pattern = f"{path}/*"
        else:
            path_pattern = path

        if report_config.get("encoding"):
            path_pattern = self.convert_to_utf8(path, report_config["encoding"])

        if report_config.get("subreports"):
            reports = [
                (f"{report_name}{subreport}", f"{path_pattern}/{subreport}.csv")
                for subreport in report_config["subreports"]
            ]
        else:
            reports = [(report_name, f"{path_pattern}/*.csv")]

        for name, path in reports:
            self.export_table(name, path)

    def export_table(self, report_name, report_path, primary_key=None):
        report_name = report_name.replace("/", "_").replace("*", "")

        try:
            self.duck.execute(f"""
            CREATE TABLE '{report_name}'  AS
                    SELECT * FROM read_csv('{report_path}')
                    """).fetchall()

            out_table = self.create_out_table_definition(
                report_name,
                primary_key=primary_key,
                incremental=self.params.destination.incremental,
            )

            self.duck.execute(f"""
                COPY '{report_name}' TO '{out_table.full_path}' (HEADER, DELIMITER ',', FORCE_QUOTE *)
            """).fetchall()
            self.write_manifest(out_table)
        except duckdb.IOException as e:
            logging.warning(f"Unable to export table {report_name}: {e}")

    def _get_date_from(self) -> datetime:
        if self.params.date_from == "last_run" and not self.state.get("last_run"):
            date_from = datetime.strptime("2024-01-01", "%Y-%m-%d")
        elif self.params.date_from == "last_run":
            date_from = datetime.fromtimestamp(self.state.get("last_run"))
        else:
            date_from = datetime.strptime(self.params.date_from, "%Y-%m-%d")
        return date_from

    @staticmethod
    def init_duckdb() -> DuckDBPyConnection:
        os.makedirs(DUCK_DB_DIR, exist_ok=True)
        config = dict(temp_directory=DUCK_DB_DIR, threads="1", max_memory=DUCK_DB_MAX_MEMORY)
        conn = duckdb.connect(config=config)

        return conn

    @staticmethod
    def unzip_files_in_folder(folder_path) -> str:
        output_folder = os.path.join(folder_path, "unzipped")
        os.makedirs(output_folder, exist_ok=True)

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            if file_name.endswith(".zip") and os.path.isfile(file_path):
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    extract_path = os.path.join(output_folder, file_name[:-4])
                    os.makedirs(extract_path, exist_ok=True)
                    zip_ref.extractall(extract_path)
        return output_folder

    @staticmethod
    def convert_to_utf8(folder_path, in_encoding) -> str:
        output_folder = os.path.join(folder_path, "utf_8")
        os.makedirs(output_folder, exist_ok=True)

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".csv"):
                input_file_path = os.path.join(folder_path, filename)
                output_file_path = os.path.join(output_folder, filename)

                with codecs.open(input_file_path, "r", encoding=in_encoding) as infile:
                    content = infile.read()

                with codecs.open(output_file_path, "w", encoding="utf-8") as outfile:
                    outfile.write(content)
        return output_folder


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)

import json
import time
import urllib.error
import urllib.request

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def api_request(method, url, body=None):
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8")
    except urllib.error.URLError as err:
        return None, str(err)


class DesktopTesterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SMS API Verifier")
        self.resize(960, 760)
        self.timer_running = False
        self.start_timestamp = None
        self.elapsed_seconds = 0
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.base_url_edit = QLineEdit("http://127.0.0.1:8000/api/v1")
        layout.addWidget(QLabel("Base URL:"))
        layout.addWidget(self.base_url_edit)

        layout.addWidget(self.create_organization_group())
        layout.addWidget(self.create_project_group())
        layout.addWidget(self.create_task_group())
        layout.addWidget(self.create_time_entry_group())

        layout.addWidget(QLabel("Response Output:"))
        self.response_edit = QTextEdit()
        self.response_edit.setReadOnly(True)
        layout.addWidget(self.response_edit)

    def create_organization_group(self):
        box = QGroupBox("Organization API")
        form = QFormLayout()

        self.org_name_edit = QLineEdit("Example Org")
        self.org_status_combo = QComboBox()
        self.org_status_combo.addItems(["active", "inactive"])
        self.org_enabled_checkbox = QCheckBox("Enabled")
        self.org_enabled_checkbox.setChecked(True)

        create_org_button = QPushButton("Create Organization")
        create_org_button.clicked.connect(self.create_organization)
        refresh_org_button = QPushButton("Refresh Organizations")
        refresh_org_button.clicked.connect(self.load_organizations)

        form.addRow("Name:", self.org_name_edit)
        form.addRow("Status:", self.org_status_combo)
        form.addRow(self.org_enabled_checkbox)
        form.addRow(create_org_button, refresh_org_button)

        box.setLayout(form)
        return box

    def create_project_group(self):
        box = QGroupBox("Project API")
        form = QFormLayout()

        self.project_org_edit = QLineEdit("1")
        self.project_name_edit = QLineEdit("Example Project")
        self.project_description_edit = QLineEdit("Project for desktop verifier")
        self.project_status_combo = QComboBox()
        self.project_status_combo.addItems(["active", "inactive"])
        self.project_billable_checkbox = QCheckBox("Billable")
        self.project_billable_checkbox.setChecked(True)

        create_project_button = QPushButton("Create Project")
        create_project_button.clicked.connect(self.create_project)
        refresh_project_button = QPushButton("Refresh Projects")
        refresh_project_button.clicked.connect(self.load_projects)

        form.addRow("Organization ID:", self.project_org_edit)
        form.addRow("Name:", self.project_name_edit)
        form.addRow("Description:", self.project_description_edit)
        form.addRow("Status:", self.project_status_combo)
        form.addRow(self.project_billable_checkbox)
        form.addRow(create_project_button, refresh_project_button)

        box.setLayout(form)
        return box

    def create_task_group(self):
        box = QGroupBox("Task API")
        form = QFormLayout()

        self.task_project_edit = QLineEdit("1")
        self.task_name_edit = QLineEdit("Example Task")
        self.task_description_edit = QLineEdit("Task for desktop verifier")
        self.task_status_combo = QComboBox()
        self.task_status_combo.addItems(["open", "in_progress", "completed"])

        create_task_button = QPushButton("Create Task")
        create_task_button.clicked.connect(self.create_task)
        refresh_task_button = QPushButton("Refresh Tasks")
        refresh_task_button.clicked.connect(self.load_tasks)

        form.addRow("Project ID:", self.task_project_edit)
        form.addRow("Name:", self.task_name_edit)
        form.addRow("Description:", self.task_description_edit)
        form.addRow("Status:", self.task_status_combo)
        form.addRow(create_task_button, refresh_task_button)

        box.setLayout(form)
        return box

    def create_time_entry_group(self):
        box = QGroupBox("Time Entry Tracker")
        form = QFormLayout()

        self.user_id_edit = QLineEdit("1")
        self.time_org_edit = QLineEdit("1")
        self.time_project_edit = QLineEdit("1")
        self.time_task_edit = QLineEdit("1")
        self.time_description_edit = QLineEdit("Working on API verifier")
        self.time_billable_checkbox = QCheckBox("Billable")
        self.time_billable_checkbox.setChecked(True)
        self.time_manual_checkbox = QCheckBox("Manual Entry")
        self.time_manual_checkbox.setChecked(False)

        self.timer_state_label = QLabel("Stopped")
        self.duration_label = QLabel("00:00:00")

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        self.stop_button = QPushButton("Stop & Submit")
        self.stop_button.clicked.connect(self.stop_timer)
        self.stop_button.setEnabled(False)

        self.elapsed_timer = QTimer(self)
        self.elapsed_timer.timeout.connect(self.update_duration)

        form.addRow("User ID:", self.user_id_edit)
        form.addRow("Organization ID:", self.time_org_edit)
        form.addRow("Project ID:", self.time_project_edit)
        form.addRow("Task ID:", self.time_task_edit)
        form.addRow("Description:", self.time_description_edit)
        form.addRow(self.time_billable_checkbox, self.time_manual_checkbox)
        form.addRow("Tracker State:", self.timer_state_label)
        form.addRow("Elapsed:", self.duration_label)
        form.addRow(self.start_button, self.stop_button)

        box.setLayout(form)
        return box

    def show_response(self, title, status, body):
        self.response_edit.append(f"[{title}] Status: {status}\n{body}\n")

    def get_base_url(self):
        return self.base_url_edit.text().strip().rstrip("/")

    def load_organizations(self):
        url = f"{self.get_base_url()}/organizations"
        status, body = api_request("GET", url)
        self.show_response("Load Organizations", status, body)

    def load_projects(self):
        url = f"{self.get_base_url()}/projects"
        status, body = api_request("GET", url)
        self.show_response("Load Projects", status, body)

    def load_tasks(self):
        url = f"{self.get_base_url()}/tasks"
        status, body = api_request("GET", url)
        self.show_response("Load Tasks", status, body)

    def create_organization(self):
        url = f"{self.get_base_url()}/organizations"
        payload = {
            "name": self.org_name_edit.text().strip(),
            "status": self.org_status_combo.currentText(),
            "is_enabled": self.org_enabled_checkbox.isChecked(),
        }
        status, body = api_request("POST", url, payload)
        self.show_response("Create Organization", status, body)

    def create_project(self):
        url = f"{self.get_base_url()}/projects"
        payload = {
            "organization_id": int(self.project_org_edit.text().strip() or 0),
            "name": self.project_name_edit.text().strip(),
            "description": self.project_description_edit.text().strip(),
            "status": self.project_status_combo.currentText(),
            "is_billable": self.project_billable_checkbox.isChecked(),
        }
        status, body = api_request("POST", url, payload)
        self.show_response("Create Project", status, body)

    def create_task(self):
        url = f"{self.get_base_url()}/tasks"
        payload = {
            "project_id": int(self.task_project_edit.text().strip() or 0),
            "name": self.task_name_edit.text().strip(),
            "description": self.task_description_edit.text().strip(),
            "status": self.task_status_combo.currentText(),
        }
        status, body = api_request("POST", url, payload)
        self.show_response("Create Task", status, body)

    def start_timer(self):
        if self.timer_running:
            return
        self.start_timestamp = time.time()
        self.elapsed_seconds = 0
        self.timer_running = True
        self.timer_state_label.setText("Running")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.elapsed_timer.start(1000)
        self.update_duration()
        self.show_response("Timer", "started", "Tracking time entry")

    def update_duration(self):
        if not self.timer_running:
            return
        self.elapsed_seconds = int(time.time() - self.start_timestamp)
        hours, remainder = divmod(self.elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.duration_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def stop_timer(self):
        if not self.timer_running:
            return
        self.timer_running = False
        self.elapsed_timer.stop()
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.timer_state_label.setText("Stopped")

        start_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(self.start_timestamp))
        end_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(self.start_timestamp + self.elapsed_seconds))
        payload = {
            "organization_id": int(self.time_org_edit.text().strip() or 0),
            "user_id": int(self.user_id_edit.text().strip() or 0),
            "project_id": int(self.time_project_edit.text().strip() or 0),
            "task_id": int(self.time_task_edit.text().strip() or 0),
            "start_time": start_time,
            "end_time": end_time,
            "total_seconds": self.elapsed_seconds,
            "status": "running",
            "is_manual": self.time_manual_checkbox.isChecked(),
            "is_billable": self.time_billable_checkbox.isChecked(),
            "description": self.time_description_edit.text().strip(),
        }
        url = f"{self.get_base_url()}/time-entries"
        status, body = api_request("POST", url, payload)
        self.show_response("Stop & Submit Time Entry", status, body)
        self.duration_label.setText("00:00:00")


if __name__ == "__main__":
    app = QApplication([])
    window = DesktopTesterApp()
    window.show()
    app.exec()

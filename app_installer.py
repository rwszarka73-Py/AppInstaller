import os
import shutil
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from app_ui import Ui_MainWindow

class AppInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.center_window()

        # Connect buttons
        self.ui.exeButton.clicked.connect(self.select_executable)
        self.ui.iconButton.clicked.connect(self.select_icon)
        self.ui.installButton.clicked.connect(self.install_app)

        # Initial status
        self.update_status()

    def set_status(self, text, state=""):
        # state: "" (neutral), "ok" (green) or "error" (red) - colors come from the form's StyleSheet
        self.ui.statusLabel.setText(text)
        self.ui.statusLabel.setProperty("state", state)
        self.ui.statusLabel.style().unpolish(self.ui.statusLabel)
        self.ui.statusLabel.style().polish(self.ui.statusLabel)

    def update_status(self):
        if not self.ui.exeLineEdit.text():
            self.set_status("⚙️ Please select the executable.")
        elif not self.ui.iconLineEdit.text():
            self.set_status("🖼️ Please select an icon.")
        else:
            self.set_status("✅ Ready to install.", "ok")

    def update_icon_preview(self):
        pixmap = QPixmap(self.ui.iconLineEdit.text())
        if pixmap.isNull():
            self.ui.iconPreview.setPixmap(QPixmap())
            self.ui.iconPreview.setText("Icon")
        else:
            size = self.ui.iconPreview.size() * 0.8
            self.ui.iconPreview.setPixmap(pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def select_executable(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Executable")
        if file:
            self.ui.exeLineEdit.setText(file)
        self.update_status()

    def select_icon(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.xpm *.jpg *.svg)")
        if file:
            self.ui.iconLineEdit.setText(file)
            self.update_icon_preview()
        self.update_status()

    def install_app(self):
        exec_path = self.ui.exeLineEdit.text()
        icon_path = self.ui.iconLineEdit.text()

        if not (exec_path and icon_path):
            self.set_status("❌ Please select an executable and icon.", "error")
            return

        # The folder containing the executable
        app_folder = os.path.dirname(exec_path)
        app_name = os.path.basename(app_folder.rstrip('/'))
        install_dir = os.path.expanduser(f"~/.local/share/{app_name}")
        desktop_entry_path = os.path.expanduser(f"~/.local/share/applications/{app_name}.desktop")
        desktop_shortcut_path = os.path.expanduser(f"~/Desktop/{app_name}.desktop")
        os.makedirs(os.path.expanduser("~/.local/share/applications"), exist_ok=True)

        try:
            # Move or copy the entire folder containing the executable
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            shutil.copytree(app_folder, install_dir)

            # Copy icon into the install folder
            icon_filename = os.path.basename(icon_path)
            icon_target = os.path.join(install_dir, icon_filename)
            shutil.copy(icon_path, icon_target)

            # Path to executable after installation
            exec_filename = os.path.basename(exec_path)
            exec_target = os.path.join(install_dir, exec_filename)

            # Create .desktop file
            desktop_entry = f"""[Desktop Entry]
Name={app_name}
Exec="{exec_target}"
Icon={icon_target}
Terminal=false
Type=Application
Categories=Utility;
"""

            with open(desktop_entry_path, "w") as f:
                f.write(desktop_entry)
            os.chmod(desktop_entry_path, 0o755)

            # Copy shortcut to Desktop
            shutil.copy(desktop_entry_path, desktop_shortcut_path)
            os.chmod(desktop_shortcut_path, 0o755)

            self.set_status(f"✅ Installed '{app_name}' successfully.", "ok")
        except Exception as e:
            self.set_status(f"❌ Error: {e}", "error")
            print(e)

    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen = QApplication.primaryScreen()
        screen_center = screen.availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppInstaller()
    window.show()
    sys.exit(app.exec_())


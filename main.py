from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import numpy as np
from PIL import Image as im
from projet_ui import Ui_MainWindow
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QTableWidgetItem, QLabel, QFileDialog
from PyQt5 import QtCore
import mysql.connector
from region_growin import region_growing

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.Display_Image_From_Database.clicked.connect(self.display_images_from_database)
        self.ui.tableWidget_Image.cellClicked.connect(self.display_selected_image)
        self.ui.apply_region_growing.clicked.connect(self.apply_region_growing)
        
        self.current_pixmap = None  # Store the current displayed image pixmap

    def export_image(self, image):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)")
        if filename:
            image.save(filename, "PNG")
    
    def display_selected_image(self, row, column):
        if column == 1:
            cell_widget = self.ui.tableWidget_Image.cellWidget(row, column)
            if isinstance(cell_widget, QLabel):
                pixmap = cell_widget.pixmap()
                self.current_pixmap = pixmap
                largeur, hauteur = pixmap.width(), pixmap.height()
                max_largeur, max_hauteur = self.ui.label.width(), self.ui.label.height()
                if largeur > max_largeur or hauteur > max_hauteur:
                    pixmap = pixmap.scaled(max_largeur, max_hauteur, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.ui.label.setPixmap(pixmap)
                self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
    
    def apply_region_growing(self):
        seed_input = self.ui.seed_pixel_input.text()
        threshold_input = self.ui.threshold_input.text()
        if not self.current_pixmap:
            QMessageBox.critical(self, "Error", "No image selected!")
            return
        if not seed_input or not threshold_input:
            QMessageBox.critical(self, "Error", "Seed pixels and threshold must be provided!")
            return
        try:
            seed_x, seed_y = map(int, seed_input.split(','))
            threshold = int(threshold_input)
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid seed pixels or threshold!")
            return
        
        image = self.current_pixmap.toImage()
        width, height = image.width(), image.height()
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)
        gray_image = np.dot(arr[...,:3], [0.299, 0.587, 0.114]).astype(np.uint8)

        segmented = region_growing(gray_image, (seed_x, seed_y), threshold)
        segmented_image = QImage(segmented.data, segmented.shape[1], segmented.shape[0], segmented.strides[0], QImage.Format_Grayscale8)
        self.ui.label.setPixmap(QPixmap.fromImage(segmented_image))
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        # Appel de la méthode export_image pour exporter l'image segmentée
        self.export_image(segmented_image)

    def display_images_from_database(self):
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Min36tity!",
                database="images_traitement"
            )
            cursor = mydb.cursor()
            cursor.execute("SELECT nom, image FROM Images_to_manipulate")
            rows = cursor.fetchall()
            row_position = 0
            for row in rows:
                nom, image_blob = row
                item_nom = QTableWidgetItem(nom)
                label = QLabel()
                pixmap = QPixmap()
                pixmap.loadFromData(image_blob)
                label.setScaledContents(True)
                label.setPixmap(pixmap)
                label.setAlignment(QtCore.Qt.AlignCenter)
                self.ui.tableWidget_Image.setRowCount(row_position + 1)
                self.ui.tableWidget_Image.setRowHeight(row_position, 200)
                self.ui.tableWidget_Image.setCellWidget(row_position, 1, label)
                self.ui.tableWidget_Image.setItem(row_position, 0, item_nom)
                row_position += 1
            mydb.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while displaying images from the database.\nError: {str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.ui.tableWidget_Image.setColumnWidth(0, 340)
    window.ui.tableWidget_Image.setColumnWidth(1, 100)
    window.show()
    app.exec_()

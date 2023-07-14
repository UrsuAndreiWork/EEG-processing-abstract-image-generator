
from MainWindow import MainWindow
import pyqtgraph as pg

if __name__ == '__main__':

    app = pg.mkQApp()
    w = MainWindow()
    w.show()
    app.exec()

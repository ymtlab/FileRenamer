import sys
from pathlib import Path
from mainwindow import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore
from tableview import Model, Delegate, Data

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        
        # UI設定
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.model = Model(self)
        self.model.addColumns(['File path', 'Before name', 'After name'])
        
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.setItemDelegate(Delegate())
        self.ui.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tableView.customContextMenuRequested.connect(self.contextMenu)
        
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
    
    def dropEvent(self, event):
        event.accept()
        paths = [ Path(url.toLocalFile()) for url in event.mimeData().urls() ]
        items = [ Data({'File path':str(path), 'Before name':path.name}) for path in paths ]
        self.model.addItems(items)
        
    def contextMenu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('追加', self.addItem)
        self.menu.addAction('削除', self.delItem)
        self.menu.exec_( self.ui.tableView.mapToGlobal(point) )
        
    def addItem(self):
        self.model.addItems([ Data({'File path':'', 'Beafore name':'', 'After name':''}) ])
                
    def delItem(self):
        indexes = self.ui.tableView.selectedIndexes()
        if len(indexes) == 0:
            return
        rows = list(set( [index.row() for index in indexes] ))
        self.model.removeItems(rows)
        
    def delAllItems(self):
        self.model.removeItems( list(range( self.model.rowCount() )) )
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

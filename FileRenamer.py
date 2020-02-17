import shutil
import sys
from pathlib import Path
from mainwindow import Ui_MainWindow
from tableview import Model, Delegate, Data
from PyQt5 import QtWidgets
from PyQt5 import QtCore

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.model = Model(self)
        self.model.addColumns(['Name', 'Suffix', "Name'", "Suffix'", 'Path'])
        self.model.editableColumns = [2, 3]
        
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.setItemDelegate(Delegate())
        self.ui.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tableView.customContextMenuRequested.connect(self.contextMenu)
        self.ui.tableView.customContextMenuRequested.connect(self.contextMenu)
        self.ui.tableView.setColumnWidth(0, 150)
        self.ui.tableView.setColumnWidth(1, 40)
        self.ui.tableView.setColumnWidth(2, 150)
        self.ui.tableView.setColumnWidth(3, 40)
        self.ui.tableView.setColumnWidth(4, 300)
        
        self.model_lookup = Model(self)
        self.model_lookup.addColumns(['Reference', 'Replace'])
        self.model_lookup.editableColumns = [0, 1]
        
        self.ui.tableView_2.setModel(self.model_lookup)
        self.ui.tableView_2.setItemDelegate(Delegate())
        self.ui.tableView_2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tableView_2.customContextMenuRequested.connect(self.contextMenu)
        
        self.ui.comboBox.addItems(["Name'", "Suffix'"])
        self.ui.comboBox_2.addItems(["Name'", "Suffix'"])

        self.ui.pushButton.clicked.connect(self.rename)
        self.ui.pushButton_2.clicked.connect(self.search)
        self.ui.pushButton_3.clicked.connect(self.search_replace)
        self.ui.pushButton_4.clicked.connect(self.lookup_replace)
        
        self.setAcceptDrops(True)
        
    def lookup_replace(self):
        m = self.model_lookup
        searches = [ m.index(r, 0).data() for r in range(m.rowCount()) ]
        replaces = [ m.index(r, 1).data() for r in range(m.rowCount()) ]
        c = self.model.columns.index(self.ui.comboBox_2.currentText())
        for row in range(self.model.rowCount()):
            index = self.model.index(row, c)
            if not index.data() in searches:
                continue
            self.model.setData( index, replaces[searches.index(index.data())] )
            self.model.dataChanged.emit(index, index)

    def search(self):
        search_text = self.ui.lineEdit.text()
        m = self.model
        c = m.columns.index(self.ui.comboBox.currentText())
        indexes = [ m.index(r, c) for r in range(m.rowCount()) if search_text in m.index(r, c).data() ]
        self.ui.tableView.setCurrentIndex(indexes[0])
        self.ui.tableView.update(indexes[0])

    def search_replace(self):
        search_text = self.ui.lineEdit.text()
        replace_text = self.ui.lineEdit_2.text()
        c = self.model.columns.index(self.ui.comboBox.currentText())
        for row in range(self.model.rowCount()):
            index = self.model.index(row, c)
            replaced = index.data().replace(search_text, replace_text)
            self.model.setData(index, replaced)
            self.model.dataChanged.emit(index, index)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
    
    def dropEvent(self, event):
        def path_to_dict(path):
            _dict = {}
            _dict['Path'] = str(path)
            _dict['Name'] = str(path.stem)
            _dict['Suffix'] = str(path.suffix)
            _dict["Name'"] = str(path.stem)
            _dict["Suffix'"] = str(path.suffix)
            return _dict
        
        event.accept()
        paths = [ Path(url.toLocalFile()) for url in event.mimeData().urls() ]
        items = [ Data(path_to_dict(path)) for path in paths ]
        self.model.addItems(items)
        
    def contextMenu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('追加', self.addItem)
        self.menu.addAction('削除', self.delItem)
        self.menu.exec_( self.focusWidget().mapToGlobal(point) )
        
    def addItem(self):
        model = self.focusWidget().model()
        model.addItems([ Data({}) ])
        
    def delItem(self):
        tableView = self.focusWidget()
        indexes = tableView.selectedIndexes()
        if len(indexes) == 0:
            return
        rows = list(set( [index.row() for index in indexes] ))
        tableView.model().removeItems(rows)
        
    def delAllItems(self):
        model = self.focusWidget().model()
        model.removeItems( list(range( model.rowCount() )) )

    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            if e.key() == QtCore.Qt.Key_C:
                self.ctrlC()
            if e.key() == QtCore.Qt.Key_V:
                self.ctrlV()
            
        if e.key() == QtCore.Qt.Key_Delete:
            tableView = self.focusWidget()
            model = tableView.model()
            indexes = tableView.selectedIndexes()
            for index in indexes:
                model.setData(index, '')
                model.dataChanged.emit(index, index)
        
    def ctrlC(self):
        tableView = self.focusWidget()
        model = tableView.model()
        indexes = tableView.selectedIndexes()
        text = indexes[0].data()
        row = indexes[0].row()
        for index in indexes[1:]:
            if row == index.row():
                text = text + '\t' + index.data()
            else:
                text = text + '\n' + index.data()
            row = index.row()
        QtWidgets.QApplication.clipboard().setText(text)

    def ctrlV(self):
        text = QtWidgets.QApplication.clipboard().text().strip()
        tableView = self.focusWidget()
        model = tableView.model()
        if len(tableView.selectedIndexes()) == 0:
            index = model.index(model.rowCount(), 0)
        else:
            index = tableView.selectedIndexes()[0]
        r0 = index.row()
        c0 = index.column()

        for r, line in enumerate(text.split('\n')):
            if r0 + r >= len(model.items):
                model.addItems([Data({})])
            for c, s in enumerate(line.split('\t')):
                if c0 + c >= len(model.columns):
                    continue
                index = model.index(r0 + r, c0 + c)
                model.setData(index, s)
                model.dataChanged.emit(index, index)

    def rename(self):
        folder = Path(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        for item in self.model.items:
            before = Path(item.get('Path'))
            after = folder / (item.get("Name'") + item.get("Suffix'"))
            shutil.copy(before, after)
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

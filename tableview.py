# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore

class Data():
    def __init__(self, data=None):
        self.data = data
    
    def get(self, column):
        if column in self.data.keys():
            return self.data[column]
        return ''
    
    def setData(self, column, data):
        self.data[column] = data
    
class Model(QtCore.QAbstractItemModel):
    def __init__(self, parent_=None):
        super(Model, self).__init__(parent_)
        self.items = []
        self.columns = []
        
    def addColumns(self, columns):
        self.beginInsertColumns(QtCore.QModelIndex(), len(self.columns), len(self.columns) + len(columns) - 1)
        self.columns.extend(columns)
        self.endInsertColumns()
        
    def column(self, key):
        return self.columns[key]
    
    def addItems(self, items):
        self.beginInsertRows(QtCore.QModelIndex(), len(self.items), len(self.items) + len(items) - 1)
        self.items.extend(items)
        self.endInsertRows()
        print(len(self.items))
        
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.columns)
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            return self.items[index.row()].get( self.column(index.column()) )
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
    def headerData(self, i, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.columns[i]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return i + 1
    
    def index(self, row, column, parent):
        return self.createIndex(row, column, QtCore.QModelIndex())
    
    def parent(self, index):
        return QtCore.QModelIndex()
    
    def removeItems(self, rows):
        sec = [ [rows[0], rows[0]+1] ]
        for row in rows[1:]:
            if sec[-1][1] == row:
                sec[-1][1] = sec[-1][1] + 1
                continue
            sec.append([row, row + 1])
        print(sec)
        for s in sec[::-1]:
            self.beginRemoveRows(QtCore.QModelIndex(), s[0], s[1]-1)
            del self.items[s[0]:s[1]]
            self.endRemoveRows()
        
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)
    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            self.items[index.row()].setData( self.column(index.column()), value )
            return True
        return False

class Delegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, setModelDataEvent=None):
        super(Delegate, self).__init__(parent)
        self.setModelDataEvent = setModelDataEvent

    def createEditor(self, parent, option, index):
        return QtWidgets.QLineEdit(parent)

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText( str(value) )

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())
        if not self.setModelDataEvent is None:
            self.setModelDataEvent()
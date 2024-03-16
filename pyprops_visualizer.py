from __future__ import annotations
from pyprops import *
from pyprops_parser import *
import sys
import random
from PySide6 import QtCore, QtSvgWidgets, QtWidgets, QtGui, QtSvg
import graphviz

class MyWidget(QtWidgets.QWidget):
    svg_widget: bytes
    
    def __init__(self, svg_content: bytes):
        super().__init__()
        svg_widget = QtSvgWidgets.QSvgWidget()
        svg_widget.load(svg_content)
        self.svg_widget = svg_widget

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.svg_widget.show()

if __name__ == '__main__':
    # G = graphviz.Graph('test')
    # G.node('test')
    # G.node('sub1')
    # G.node('sub2')
    # G.edge('test', 'sub1')
    # G.edge('test', 'sub2')
    G = parse_formula('NOT(p) OR q').to_graphviz()
    svg = G.pipe(format='svg')
    app = QtWidgets.QApplication([])
    widget = MyWidget(svg)
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())

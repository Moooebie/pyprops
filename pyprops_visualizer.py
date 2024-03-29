'''PyProps Visualizer
'''
from __future__ import annotations
import sys
import random
import json
from PySide6 import QtCore, QtSvgWidgets, QtWidgets
from pyprops_parser import parse_formula, formula_expression_generator


class FormulaVisualizer(QtWidgets.QWidget):
    '''PyQT class for the visualizer window.
    
    Instance Attributes:
        - labs: dict of labels
        - tb: dict of textboxes
        - buts: dict of buttons
        - layout: the QVBox layout object of the window
        - svg_widget: the SVG renderer
    '''
    labs: dict = {}
    tb: dict = {}
    buts: dict = {}
    layout: QtSvgWidgets.QVBoxLayout
    svg_widget: QtSvgWidgets.QSvgWidget

    def __init__(self) -> None:
        super().__init__()

        # svg viewer
        self.svg_widget = QtSvgWidgets.QSvgWidget()

        # labels
        self.labs['label_formula'] = QtWidgets.QLabel('Input your formula below:')
        self.labs['label_ta'] = QtWidgets.QLabel('Input truth assignment below:')

        # textboxes
        self.tb['textbox_formula'] = QtWidgets.QTextEdit(self)
        self.tb['textbox_ta'] = QtWidgets.QTextEdit(self)

        # buttons
        self.buts['button_random_formula'] = QtWidgets.QPushButton('Generate random formula...')
        self.buts['button_formula_negation'] = QtWidgets.QPushButton('Negate')
        self.buts['button_formula_cnf'] = QtWidgets.QPushButton('Convert to CNF')
        self.buts['button_formula_dnf'] = QtWidgets.QPushButton('Convert to DNF')
        self.buts['button_formula_nnf'] = QtWidgets.QPushButton('Convert to NNF')
        self.buts['button_random_ta'] = QtWidgets.QPushButton('Generate random truth assignment...')
        self.buts['button_visualize'] = QtWidgets.QPushButton('Visualize!')

        # layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.labs['label_formula'])
        self.layout.addWidget(self.tb['textbox_formula'])
        self.layout.addWidget(self.buts['button_random_formula'])
        self.layout.addWidget(self.buts['button_formula_negation'])
        self.layout.addWidget(self.buts['button_formula_cnf'])
        self.layout.addWidget(self.buts['button_formula_dnf'])
        self.layout.addWidget(self.buts['button_formula_nnf'])
        self.layout.addWidget(self.labs['label_ta'])
        self.layout.addWidget(self.tb['textbox_ta'])
        self.layout.addWidget(self.buts['button_random_ta'])
        self.layout.addWidget(self.buts['button_visualize'])

        # click events
        self.buts['button_random_formula'].clicked.connect(self.random_formula)
        self.buts['button_formula_negation'].clicked.connect(self.formula_negate)
        self.buts['button_formula_cnf'].clicked.connect(self.to_cnf)
        self.buts['button_formula_dnf'].clicked.connect(self.to_dnf)
        self.buts['button_formula_nnf'].clicked.connect(self.to_nnf)
        self.buts['button_random_ta'].clicked.connect(self.random_truth_assginment)
        self.buts['button_visualize'].clicked.connect(self.visualize)

    @QtCore.Slot()
    def visualize(self) -> None:
        '''QPushButton Event: visualzie the graph
        '''
        f_txt = self.tb['textbox_formula'].toPlainText()
        f = parse_formula(f_txt)
        if len(self.tb['textbox_ta'].toPlainText()) == 0:
            t = None
        else:
            t = json.loads(self.tb['textbox_ta'].toPlainText())
        kwargs = {}
        if len(f_txt) > 200:
            kwargs['engine'] = 'circo'
        graph = f.to_graphviz(t, **kwargs)
        graph.attr(size='16,12!', overlap='prism', mindist='0.0')
        self.svg_widget.load(graph.pipe(format='svg'))
        self.svg_widget.show()

    @QtCore.Slot()
    def random_truth_assginment(self) -> None:
        '''QPushButton Event: generate a random truth assignment
        '''
        f = parse_formula(self.tb['textbox_formula'].toPlainText())
        truth_assignments = f.generate_truth_assignments()
        t = truth_assignments[random.randrange(len(truth_assignments))]
        self.tb['textbox_ta'].setText(json.dumps(t))

    @QtCore.Slot()
    def random_formula(self) -> None:
        '''QPushButton Event: generate a random formula
        '''
        f = formula_expression_generator(5, 5, 10)
        self.tb['textbox_formula'].setText(f)

    @QtCore.Slot()
    def formula_negate(self) -> None:
        '''QPushButton Event: Convert the formula into its negation
        '''
        f = parse_formula(self.tb['textbox_formula'].toPlainText())
        self.tb['textbox_formula'].setText(str(f.negation()))

    @QtCore.Slot()
    def to_cnf(self) -> None:
        '''QPushButton Event: Convert the formula into Conjunctive Normal Form
        '''
        f = parse_formula(self.tb['textbox_formula'].toPlainText())
        self.tb['textbox_formula'].setText(str(f.to_cnf()))

    @QtCore.Slot()
    def to_dnf(self) -> None:
        '''QPushButton Event: Convert the formula into Disjunctive Normal Form
        '''
        f = parse_formula(self.tb['textbox_formula'].toPlainText())
        self.tb['textbox_formula'].setText(str(f.to_dnf()))

    @QtCore.Slot()
    def to_nnf(self) -> None:
        '''QPushButton Event: Convert the formula into Negation Normal Form
        '''
        f = parse_formula(self.tb['textbox_formula'].toPlainText())
        self.tb['textbox_formula'].setText(str(f.to_nnf()))


def load_visualizer() -> None:
    '''Load the visualizer window.
    '''
    app = QtWidgets.QApplication([])
    # app.setStyle('Breeze')
    widget = FormulaVisualizer()
    widget.resize(500, 600)
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': [
            'pyprops', 'doctest', 'random', 'PySide6', 'json', 'sys', 'pyprops_parser'
        ],  # the names (strs) of imported modules
        'allowed-io': [],     # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
    # load_visualizer()

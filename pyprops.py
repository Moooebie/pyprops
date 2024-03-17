from __future__ import annotations
from typing import Optional
import graphviz

########## CONSTANTS ##########
# Connective types
VERSION = 1.2

VAR = 0
NOT = 1
AND = 2
OR = 3
IMPLIES = 4
IFF = 5


########## PROPOSITIONAL FORMULA CLASSES ##########
class Formula:
    '''Abstract class for propositional formulas.
    
    Instance attributes:
        - type: type of logical option, could be VAR, NOT, AND, OR, IMPLIES or IFF
        - label: optional description of the formula (will not affect logical behaviors)
    '''
    type: int
    label: Optional[str]
    
    def __init__(self, label: str = None) -> None:
        self.label = label
    
    def evaluate(self, truth_assignment: dict) -> bool:
        '''Evaluates the formula under the given truth assignment.
        '''
        raise NotImplementedError
    
    def num_connectives(self) -> int:
        '''Return number of connectives in this formula.
        '''
        raise NotImplementedError
    
    def to_text(self) -> str:
        '''Convert the propositional formula object to a human-readable formula.
        '''
        raise NotImplementedError
    
    def get_variables(self) -> set[str]:
        '''Get the names of all propositional variables within this formula.
        '''
        raise NotImplementedError
    
    def generate_truth_assignments(self) -> list[dict]:
        '''Generate all possible truth assignments for the current propositional formula.
        '''
        subs = self.get_variables()
        ret = []
        for v in subs:
            if len(ret) == 0:
                ret.append({v: True})
                ret.append({v: False})
            else:
                new_ret = []
                for i in ret:
                    i1 = i.copy()
                    i2 = i.copy()
                    i1[v] = True
                    i2[v] = False
                    new_ret.append(i1)
                    new_ret.append(i2)
                ret = new_ret
        return ret
    
    def truth_table(self) -> list[tuple]:
        '''Generate the truth table, with each possible truth assignment as the first element in
            each tuple while the result of evaluation under the truth assignment as the second.
        '''
        truth_assignments = self.generate_truth_assignments()
        ret = []
        for i in truth_assignments:
            ret.append((i, self.evaluate(i)))
        return ret

    def is_tautology(self) -> bool:
        '''Return whether the formula is a tautology (that is, return True under all
            possible truth assignments)
        '''
        return all({self.evaluate(i) for i in self.generate_truth_assignments()})
        
    def is_satisfiable(self) -> bool:
        '''Return whether the formula is satisfiable (that is, it returns True under some
            truth assignments)
        '''
        return any({self.evaluate(i) for i in self.generate_truth_assignments()})
    
    def is_fallacy(self) -> bool:
        '''Return whether the formula is a fallay (that is, it returns False under all
            possible truth assignments)
        '''
        return not self.is_satisfiable()
    
    def negation(self) -> Formula:
        '''Return the negation of this formula.
        '''
        raise NotImplementedError
    
    def to_cnf(self) -> Formula:
        '''Return a formula that is in Conjunctive Normal Form that is logically
        equivalent to this formula.
        '''
        return to_cnf(self)
    
    def to_dnf(self) -> Formula:
        '''Return a formula that is in Disjunctive Normal Form that is logically
        equivalent to this formula.
        '''
        return to_dnf(self)
    
    def to_nnf(self) -> Formula:
        '''Return a formula that is in Negation Normal Form that is logically
        equivalent to this formula.
        '''
        raise NotImplementedError
    
    def to_graphviz(
        self, truth_assignment: Optional[dict] = None, **kwargs) -> graphviz.Graph:
        '''Return a graphviz graph for visualization, optionally under a specific truth assignment
        '''
        G = graphviz.Graph(**kwargs)
        self.augment_graphviz(G, None, truth_assignment)
        return G

    def augment_graphviz(
        self, G: graphviz.Graph, parent: Optional[Formula] = None, truth_assignment: Optional[dict] = None) -> None:
        '''Augment a graphviz graph recursively
        '''
        raise NotImplementedError
    
    def trim(self) -> Formula:
        '''Return a trimmed (simplified) version of this formula.
        '''
        # TODO: we did not have enough time to implement this
        return self
    
    def __str__(self) -> str:
        '''For the builtin str() function
        '''
        return self.to_text()
    
    def __repr__(self) -> str:
        '''No much difference as __str__
        '''
        return f'''parse_formula('{str(self)}')'''
    
    def __eq__(self, other: object) -> bool:
        '''Default comparison method
        '''
        if not isinstance(other, Formula) or other.to_text() != self.to_text():
            return False
        else:
            return True
    
    def __hash__(self) -> int:
        '''Makes hashable
        '''
        return hash(self.to_text())


class PropVar(Formula):
    '''Class to represent a single propositional variable.
    
    Instance Attributes:
        - name: name of this propositional variable (used as keys in truth assignments)
    
    Representation Invariants:
        - self.name is not None
        - not self.name.isspace()
    '''
    type = VAR
    name: str
    
    def __init__(self, name: str, label: str = None) -> None:
        super().__init__(label)
        self.name = name
    
    def evaluate(self, truth_assignment: dict) -> bool:
        '''Evaluates the formula under the given truth assignment.
            Raises ValueError if self.name not in truth_assignment.
        '''
        if not self.name in truth_assignment:
            raise ValueError(f'truth assignment missing variable: {self.name}')
        elif truth_assignment[self.name]:
            return True
        else:
            return False

    def num_connectives(self) -> int:
        '''Return number of connectives in this formula.
        '''
        return 0

    def to_text(self) -> str:
        '''Convert the propositional formula object to a human-readable formula.
        '''
        return self.name
    
    def get_variables(self) -> set[str]:
        '''Get the names of all propositional variables within this formula.
        '''
        return {self.name}

    def negation(self) -> Formula:
        '''Return the negation of this formula.
        '''
        return NotFormula(self)
    
    def to_nnf(self) -> Formula:
        '''Return a formula that is in Negation Normal Form that is logically
        equivalent to this formula.
        '''
        return self
    
    def augment_graphviz(
        self, G: graphviz.Graph, parent: Optional[Formula] = None, truth_assignment: Optional[dict] = None) -> None:
        '''Augment a graph recursively
        '''
        c = '#ffffff00'
        if truth_assignment is not None:
            if self.evaluate(truth_assignment):
                c = '#ebffdcff'
            else:
                c = '#ffd2d2'
        s =  'star' if parent is None else 'ellipse'
        G.node(name=str(id(self)), label=self.name, fillcolor=c, style='filled', shape=s)
        if parent is not None:
            G.edge(str(id(self)), str(id(parent)))


class NotFormula(Formula):
    '''Class to represent a formula that is equivalent to NOT(p) for some formula p.
    
    Instance Attributes:
        - subformula: the p in NOT(p)
    '''
    type = NOT
    subformula: Formula
    
    def __init__(self, subformula: Formula, label: str = None) -> None:
        super().__init__(label)
        self.subformula = subformula
    
    def evaluate(self, truth_assignment: dict) -> bool:
        '''Evaluates the formula under the given truth assignment.
        '''
        return not self.subformula.evaluate(truth_assignment)

    def num_connectives(self) -> int:
        '''Return number of connectives in this formula.
        '''
        return self.subformula.num_connectives() + 1

    def to_text(self) -> str:
        '''Convert the propositional formula object to a human-readable formula.
        '''
        return f'NOT({self.subformula.to_text()})'
    
    def get_variables(self) -> set[str]:
        '''Get the names of all propositional variables within this formula.
        '''
        return self.subformula.get_variables()

    def negation(self) -> Formula:
        '''Return the negation of this formula.
        '''
        return self.subformula

    def _count_nots(self) -> tuple[int, Formula]:
        '''Internal function to count the number of nested NOTs.
        '''
        if self.subformula.type != NOT:
            return (1, self.subformula)
        else:
            prev = self.subformula._count_nots()
            return (prev[0] + 1, prev[1])

    def to_nnf(self) -> Formula:
        '''Return a formula that is in Negation Normal Form that is logically
        equivalent to this formula.
        '''
        res = self._count_nots()
        if res[0] % 2 == 0:
            return res[1].to_nnf()
        elif res[1].type == VAR:
            return NotFormula(res[1])
        elif res[1].type == AND:
            return OrFormula([formula.negation().to_nnf() for formula in res[1].subformulas])
        elif res[1].type == OR:
            return AndFormula([formula.negation().to_nnf() for formula in res[1].subformulas])
        else:
            return res[1].negation().to_nnf()

    def augment_graphviz(
        self, G: graphviz.Graph, parent: Optional[Formula] = None, truth_assignment: Optional[dict] = None) -> None:
        '''Augment a graph recursively
        '''
        c = '#ffffff00'
        if truth_assignment is not None:
            if self.evaluate(truth_assignment):
                c = '#ebffdcff'
            else:
                c = '#ffd2d2'
        s =  'star' if parent is None else 'triangle'
        G.node(name=str(id(self)), label='NOT', fillcolor=c, style='filled', shape=s)
        self.subformula.augment_graphviz(G, self, truth_assignment)
        if parent is not None:
            G.edge(str(id(self)), str(id(parent)))


class AndFormula(Formula):
    '''Class to represent a formula that is equivalent to (p1 AND p2 AND ... AND p_k)
        for some formulas p_i.
    
    Instance Attributes:
        - subformulas:  the formulas p_i that this formula returns True iff all
                        subformulas returns True.
    
    Representation Invariants:
        - len(self.subformula) > 1
    '''
    type = AND
    subformulas: list[Formula]
    
    def __init__(self, subformulas: list[Formula], label: str = None) -> None:
        if len(subformulas) == 0:
            raise ValueError('subformulas cannot be empty!')
        super().__init__(label)
        self.subformulas = subformulas
    
    def evaluate(self, truth_assignment: dict) -> bool:
        '''Evaluates the formula under the given truth assignment.
        '''
        return all({i.evaluate(truth_assignment) for i in self.subformulas})
    
    def num_connectives(self) -> int:
        '''Return number of connectives in this formula.
        '''
        ret = len(self.subformulas) - 1
        for formula in self.subformulas:
            ret += formula.num_connectives()
        return ret
    
    def to_text(self) -> str:
        '''Convert the propositional formula object to a human-readable formula.
        '''
        texts = []
        for formula in self.subformulas:
            if formula.type == NOT or formula.type == VAR:
                texts.append(formula.to_text())
            else:
                texts.append('(' + formula.to_text() + ')')
        return  ' AND '.join(texts)
    
    def get_variables(self) -> set[str]:
        '''Get the names of all propositional variables within this formula.
        '''
        ret = set()
        for formula in self.subformulas:
            ret = ret.union(formula.get_variables())
        return ret

    def negation(self) -> Formula:
        '''Return the negation of this formula.
        '''
        return OrFormula([formula.negation() for formula in self.subformulas])

    def to_nnf(self) -> Formula:
        '''Return a formula that is in Negation Normal Form that is logically
        equivalent to this formula.
        '''
        nnfs = [formula.to_nnf() for formula in self.subformulas]
        return AndFormula(nnfs)

    def augment_graphviz(
        self, G: graphviz.Graph, parent: Optional[Formula] = None, truth_assignment: Optional[dict] = None) -> None:
        '''Augment a graph recursively
        '''
        c = '#ffffff00'
        if truth_assignment is not None:
            if self.evaluate(truth_assignment):
                c = '#ebffdcff'
            else:
                c = '#ffd2d2'
        s =  'star' if parent is None else 'house'
        G.node(name=str(id(self)), label='AND', fillcolor=c, style='filled', shape=s)
        if parent is not None:
            G.edge(str(id(self)), str(id(parent)))
        for i in self.subformulas:
            i.augment_graphviz(G, self, truth_assignment)


class OrFormula(Formula):
    '''Class to represent a formula that is equivalent to (p1 OR p2 OR ... OR p_k)
        for some formulas p_i.
    
    Instance Attributes:
        - subformulas:  the formulas p_i that this formula returns True iff any
                        subformulas returns True.
    
    Representation Invariants:
        - len(self.subformula) > 1
    '''
    type = OR
    subformulas: set[Formula]
    
    def __init__(self, subformulas: set[Formula], label: str = None) -> None:
        if len(subformulas) == 0:
            raise ValueError('subformulas cannot be empty!')
        super().__init__(label)
        self.subformulas = subformulas
    
    def evaluate(self, truth_assignment: dict) -> bool:
        '''Evaluates the formula under the given truth assignment.
        '''
        return any({i.evaluate(truth_assignment) for i in self.subformulas})
    
    def num_connectives(self) -> int:
        '''Return number of connectives in this formula.
        '''
        ret = len(self.subformulas) - 1
        for formula in self.subformulas:
            ret += formula.num_connectives()
        return ret
    
    def to_text(self) -> str:
        '''Convert the propositional formula object to a human-readable formula.
        '''
        texts = []
        for formula in self.subformulas:
            if formula.type == NOT or formula.type == VAR:
                texts.append(formula.to_text())
            else:
                texts.append('(' + formula.to_text() + ')')
        return  ' OR '.join(texts)
    
    def get_variables(self) -> set[str]:
        '''Get the names of all propositional variables within this formula.
        '''
        ret = set()
        for formula in self.subformulas:
            ret = ret.union(formula.get_variables())
        return ret

    def negation(self) -> Formula:
        '''Return the negation of this formula.
        '''
        return AndFormula([formula.negation() for formula in self.subformulas])

    def to_nnf(self) -> Formula:
        '''Return a formula that is in Negation Normal Form that is logically
        equivalent to this formula.
        '''
        nnfs = [formula.to_nnf() for formula in self.subformulas]
        return OrFormula(nnfs)

    def augment_graphviz(
        self, G: graphviz.Graph, parent: Optional[Formula] = None, truth_assignment: Optional[dict] = None) -> None:
        '''Augment a graph recursively
        '''
        c = '#ffffff00'
        if truth_assignment is not None:
            if self.evaluate(truth_assignment):
                c = '#ebffdcff'
            else:
                c = '#ffd2d2'
        s =  'star' if parent is None else 'invhouse'
        G.node(name=str(id(self)), label='OR', fillcolor=c, style='filled', shape=s)
        if parent is not None:
            G.edge(str(id(self)), str(id(parent)))
        for i in self.subformulas:
            i.augment_graphviz(G, self, truth_assignment)


class ImpliesFormula(Formula):
    '''Class to represent a formula that is equivalent to (p IMPLIES q)
        for some formulas p and q.
    
    Instance Attributes:
        - hyp: the hypothesis, that is, the p in (P IMPLIES q)
        - concl: the conclusion, that is, the q in (p IMPLIES q)
    '''
    type = IMPLIES
    hyp: Formula
    concl: Formula
    
    def __init__(self, hypothesis: Formula, conclusion: Formula, label: str = None) -> None:
        super().__init__(label)
        self.hyp = hypothesis
        self.concl = conclusion
    
    def evaluate(self, truth_assignment: dict) -> bool:
        '''Evaluates the formula under the given truth assignment.
        '''
        return not self.hyp.evaluate(truth_assignment) or self.concl.evaluate(truth_assignment)
    
    def num_connectives(self) -> int:
        '''Return number of connectives in this formula.
        '''
        return self.hyp.num_connectives() + self.concl.num_connectives() + 1
    
    def to_text(self) -> str:
        '''Convert the propositional formula object to a human-readable formula.
        '''
        if self.hyp.type == VAR or self.hyp.type == NOT:
            t1 = self.hyp.to_text()
        else:
            t1 = '(' + self.hyp.to_text() + ')'
        if self.concl.type == VAR or self.concl.type == NOT:
            t2 = self.concl.to_text()
        else:
            t2 = '(' + self.concl.to_text() + ')'
        return t1 + ' IMPLIES ' + t2
    
    def get_variables(self) -> set[str]:
        '''Get the names of all propositional variables within this formula.
        '''
        return self.hyp.get_variables().union(self.concl.get_variables())

    def negation(self) -> Formula:
        '''Return the negation of this formula.
        '''
        return AndFormula([self.hyp, self.concl.negation()])

    def to_nnf(self) -> Formula:
        '''Return a formula that is in Negation Normal Form that is logically
        equivalent to this formula.
        '''
        return ImpliesFormula(self.hyp.to_nnf(), self.concl.to_nnf())

    def augment_graphviz(
        self, G: graphviz.Graph, parent: Optional[Formula] = None, truth_assignment: Optional[dict] = None) -> None:
        '''Augment a graph recursively
        '''
        c = '#ffffff00'
        if truth_assignment is not None:
            if self.evaluate(truth_assignment):
                c = '#ebffdcff'
            else:
                c = '#ffd2d2'
        s =  'star' if parent is None else 'rarrow'
        G.node(name=str(id(self)), label='IMPLIES', fillcolor=c, style='filled', shape=s)
        if parent is not None:
            G.edge(str(id(self)), str(id(parent)))
        self.hyp.augment_graphviz(G, self, truth_assignment)
        self.concl.augment_graphviz(G, self, truth_assignment)


class IffFormula(Formula):
    '''Class to represent a formula that is equivalent to (p IFF q)
        for some formulas p and q.
    
    Instance Attributes:
        - sub1: the hypothesis, that is, the p in (P IFF q)
        - sub2: the conclusion, that is, the q in (p IFF q)
    '''
    type = IFF
    sub1: Formula
    sub2: Formula
    
    def __init__(self, sub1: Formula, sub2: Formula, label: str = None) -> None:
        super().__init__(label)
        self.sub1 = sub1
        self.sub2 = sub2
    
    def evaluate(self, truth_assignment: dict) -> bool:
        '''Evaluates the formula under the given truth assignment.
        '''
        return self.sub1.evaluate(truth_assignment) == self.sub2.evaluate(truth_assignment)
    
    def num_connectives(self) -> int:
        '''Return number of connectives in this formula.
        '''
        return self.sub1.num_connectives() + self.sub2.num_connectives() + 1
    
    def to_text(self) -> str:
        '''Convert the propositional formula object to a human-readable formula.
        '''
        if self.sub1.type == VAR or self.sub1.type == NOT:
            t1 = self.sub1.to_text()
        else:
            t1 = '(' + self.sub1.to_text() + ')'
        if self.sub2.type == VAR or self.sub2.type == NOT:
            t2 = self.sub2.to_text()
        else:
            t2 = '(' + self.sub2.to_text() + ')'
        return t1 + ' IFF ' + t2
    
    def get_variables(self) -> set[str]:
        '''Get the names of all propositional variables within this formula.
        '''
        return self.sub1.get_variables().union(self.sub2.get_variables())

    def negation(self) -> Formula:
        '''Return the negation of this formula.
        '''
        # NOT(p IFF q) == p XOR q == (p AND NOT(q)) OR (NOT(p) AND q)
        f1 = AndFormula([self.sub1, self.sub2.negation()])
        f2 = AndFormula([self.sub1.negation(), self.sub2])
        return OrFormula([f1, f2])

    def to_nnf(self) -> Formula:
        '''Return a formula that is in Negation Normal Form that is logically
        equivalent to this formula.
        '''
        return IffFormula(self.sub1.to_nnf(), self.sub2.to_nnf())

    def augment_graphviz(
        self, G: graphviz.Graph, parent: Optional[Formula] = None, truth_assignment: Optional[dict] = None) -> None:
        '''Augment a graph recursively
        '''
        c = '#ffffff00'
        if truth_assignment is not None:
            if self.evaluate(truth_assignment):
                c = '#ebffdcff'
            else:
                c = '#ffd2d2'
        s =  'star' if parent is None else 'diamond'
        G.node(name=str(id(self)), label='IFF', fillcolor=c, style='filled', shape=s)
        if parent is not None:
            G.edge(str(id(self)), str(id(parent)))
        self.sub1.augment_graphviz(G, self, truth_assignment)
        self.sub2.augment_graphviz(G, self, truth_assignment)


########## TOOLKIT METHODS ##########
def equivalent(f1: Formula, f2: Formula) -> bool:
    '''Return wether the f1 is logically equivalent to the f2.
        Two formulas are logically equivalent if and only if they return the same
        truth under any valid truth assignment.
    '''
    return IffFormula(f1, f2).is_tautology()

def implies(f1: Formula, f2: Formula) -> bool:
    '''Return wehther the f1 logically implies the f2.
        One propositional formula logically implies another if and only if all
        truth assignments that makes it true also makes the other true.
    '''
    return ImpliesFormula(f1, f2).is_tautology()

def make_true(truth_assignment: dict) -> Formula:
    '''Helper function, generates a Formula that evaluates to True under
        the given truth assignment.
    '''
    subs = set()
    for v in truth_assignment:
        if truth_assignment[v]:
            subs.add(PropVar(v))
        else:
            subs.add(NotFormula(PropVar(v)))
    return AndFormula(subs)

def to_cnf(formula: Formula) -> Formula:
    '''Return a formula that is in Conjunctive Normal Form that is logically
    equivalent to this formula.
    '''
    falses = [i[0] for i in formula.truth_table() if not i[1]]
    formulas = []
    for j in falses:
        subs = []
        for v in j:
            if not j[v]:
                subs.append(PropVar(v))
            else:
                subs.append(NotFormula(PropVar(v)))
        formulas.append(OrFormula(subs))
    if len(formulas) == 0:
        # in case we have a tautology
        vars = formula.get_variables()
        for v in vars:
            formulas.append(OrFormula([NotFormula(PropVar(v)), PropVar(v)]))
    return AndFormula(formulas)

def to_dnf(formula: Formula) -> Formula:
    '''Return a formula that is in Disjunctive Normal Form that is logically
    equivalent to this formula.
    '''
    trues = [i[0] for i in formula.truth_table() if i[1]]
    formulas = []
    for j in trues:
        subs = []
        for v in j:
            if j[v]:
                subs.append(PropVar(v))
            else:
                subs.append(NotFormula(PropVar(v)))
        formulas.append(AndFormula(subs))
    if len(formulas) == 0:
        # in case we have a fallacy
        vars = formula.get_variables()
        for v in vars:
            formulas.append(AndFormula([NotFormula(PropVar(v)), PropVar(v)]))
    return OrFormula(formulas)

from pyprops import *
from pyprops_parser import *
from pyprops_parser import _parse_helper

if __name__ == '__main__':
    f = ImpliesFormula(PropVar('p'), PropVar('q'))
    print(f'"{f}", {type(f)}')
    # print(f.evaluate({'p': True, 'q': False}))
    # print(f.evaluate({'p': False, 'q': False}))
    # print(f.evaluate({'p': True, 'q': True}))
    # print(f.negation().to_text())
    # print(equivalent(f, OrFormula([NotFormula(PropVar('p')), PropVar('q')])))
    # f = _parse_helper('a OR b OR c'.split())
    # print(f'"{f}", {type(f)}')
    
    f = parse('c AND (d OR e) AND f AND (g OR h)')
    print(f'"{f}", {type(f)}')
    
    f = parse('c AND d AND NOT(g OR e)')
    print(f'"{f}", {type(f)}')
    
    f = parse(' (  ( r  )  AND s AND (c OR d OR (e OR f))) AND t AND p AND q')
    print(f'"{f}", {type(f)}')
    
    print()
    f = parse('(p IMPLIES q) IFF (r)')
    print(f'"{f}", {type(f)}')
    print(f.to_cnf(), equivalent(f.to_cnf(), f))
    print(f.to_dnf(), equivalent(f.to_dnf(), f))
    print(f.to_nnf(), equivalent(f.to_nnf(), f))

    print()
    f = parse('c AND d AND NOT(g OR e)')
    print(f'"{f}", {type(f)}')
    print(f.to_cnf(), equivalent(f.to_cnf(), f))
    print(f.to_nnf(), equivalent(f.to_nnf(), f))

    print()
    f = parse('c AND d AND NOT(g IFF e)')
    print(f'"{f}", {type(f)}')
    print(f.to_cnf(), equivalent(f.to_cnf(), f))
    print(f.to_nnf(), equivalent(f.to_nnf(), f))

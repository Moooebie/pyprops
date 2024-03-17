from pyprops import *
import doctest, random

def parse_formula(text: str) -> Formula:
    '''Parse a propositional formula recursively from the input text.
    
    Preconditions:
        - len(text) > 0
        - text.count('(') != text.count(')')
    
    >>> parse_formula('p IMPLIES q') == ImpliesFormula(PropVar('p'), PropVar('q'))
    True
    '''
    res = _to_nested_lists(text, [0])
    return _rec_parser(res)


def _formula_builder(subs: list[Formula], connective: str) -> Formula:
    '''Create a Formula object based on the given sub-formulas and connective.
    '''
    err = 'invalid formula expression!'
    if len(subs) == 0:
        raise ValueError
    if connective == '' and len(subs) == 1:
        return subs.pop()
    elif connective == 'AND':
        return AndFormula(subs)
    elif connective == 'OR':
        return OrFormula(subs)
    elif connective == 'IMPLIES':
        if len(subs) != 2:
            raise ValueError(err)
        else:
            return ImpliesFormula(subs[0], subs[1])
    elif connective == 'IFF':
        if len(subs) != 2:
            raise ValueError(err)
        else:
            return IffFormula(subs[0], subs[1])
    else:
        raise ValueError(err)


def _parse_helper(segments: list[str]) -> tuple[Formula, str]:
    '''Helper function for parsing text with no brackets into Formula.
    
    Preconditions:
        - len(segments) > 0
    '''
    # check for validity of the formula expression
    if 'NOT' in segments:
        raise ValueError('NOT must be used with brackets. (e.g. "NOT(p)" rather than "NOT p")')
    err = 'invalid formula expression!'
    conns = {'AND', 'OR', 'IMPLIES', 'IFF'}
    if len(segments) == 0 or segments[0] in conns or segments[-1] in conns:
        raise ValueError(err)
    # separate connectives and variables
    subs = []
    connective = ''
    prev = ''
    cur = ''
    for i in range(len(segments)):
        prev, cur = cur, segments[i]
        # if two connectives or two variables are ajacent, this is an invalid formula expression.
        if prev != '' and ((prev in conns) == (cur in conns)):
            raise ValueError(err)
        if cur in conns:
            if connective == '':
                connective = cur
            # if connectives don't match, it's invalid. e.g. "p OR q AND r IMPLIES s" is ambigious.
            elif connective != cur:
                raise ValueError(err)
        else:
            subs.append(PropVar(segments[i]))
    return _formula_builder(subs, connective), connective


def _to_nested_lists(text: str, cur_index: list[int]) -> list[str, list]:
    '''This function handles the expression in plain text into nested lists based on parenthesis.
    This function MUTATES the cur_index list to share the current index with all subroutines.
    
    >>> expected = [['p AND q AND', ['x OR y']], 'AND s']
    >>> _to_nested_lists('(p AND q AND (x OR y)) AND s', [0]) == expected
    True
    '''  
    lst = []
    c = text[cur_index[0]]
    while cur_index[0] < len(text):
        c = text[cur_index[0]]
        if c == '(':
            cur_index[0] += 1
            lst.append(_to_nested_lists(text, cur_index))
        elif c == ')':
            cur_index[0] += 1
            break
        else:
            if len(lst) == 0 or not isinstance(lst[-1], str):
                lst.append('')
            lst[-1] += c
            cur_index[0] += 1
    # cleanning up
    ret = []
    for i in lst:
        if isinstance(i, str):
            stripped = i.strip()
            if len(stripped) > 0:
                ret.append(stripped)
        else:
            ret.append(i)
    # check validty
    if any({isinstance(ret[i], str) == isinstance(ret[i - 1], str) for i in range(1, len(ret))}):
        raise ValueError('invalid formula expression!')
    else:
        return ret


def _rec_parser(lst: list[str, list]) -> Formula:
    '''Parse a nested list recursively to generate a Formula object.
    
    Preconditions:
        - lst is a valid output of _to_nested_list.
    '''
    err = 'invalid formula expression!'
    conns = {'AND', 'OR', 'IMPLIES', 'IFF'}
    # handling empty lists or and lists with a single string
    if len(lst) == 0:
        raise ValueError(err)
    elif len(lst) == 1:
        if isinstance(lst[0], str):
            return _parse_helper(lst[0].strip().split())[0]
        else:
            return _rec_parser(lst[0])
    
    # handling more complex lists
    i = 0
    connective = ''
    subs: list[Formula] = []
    valid_conn = lambda conn, curr: curr in conns and (conn == '' or conn == curr)
    # print('NEW CALL')  # NOTE: DEBUG
    while i < len(lst):
        diff = 1
        cur = lst[i]
        if isinstance(cur, list):
            subs.append(_rec_parser(cur))
            i += diff
            continue
        segments = cur.strip().split()
        # NOTE: DEBUG
        # print(lst)
        # print(cur)
        # print(segments)
        # print()
        
        # connective after
        next = None
        if i != len(lst) - 1:
            if segments[-1] == 'NOT':
                next = NotFormula(_rec_parser(lst[i + 1]))
                segments = segments[:-1]
                diff += 1
            if len(segments) == 0 and i == 0:
                if next is not None:
                    subs.append(next)
                i += diff
                continue
            if len(segments) == 0 or not valid_conn(connective, segments[-1]):
                raise ValueError(err)
            else:
                connective = segments[-1]
                if len(segments) > 1:
                    segments = segments[:-1]
        elif segments[-1] == 'NOT' or segments[-1] in conns:
            raise ValueError(err)
        # connective before
        if i > 0:
            if len(segments) == 0 or not valid_conn(connective, segments[0]):
                raise ValueError(err)
            else:
                connective = segments[0]
                segments = segments[1:]
            if len(segments) == 0 and i != len(segments) - 1:
                i += diff
                if next is not None:
                    subs.append(next)
                continue
            elif len(segments) == 0:
                raise ValueError(err)
        # processing current subformula
        if len(segments) > 0:
            sub, subconn = _parse_helper(segments)
            if connective in {'AND', 'OR'} and subconn == connective:
                subs.extend(sub.subformulas)
            else:
                subs.append(sub)
        if next is not None:
            subs.append(next)
        i += diff
    return _formula_builder(subs, connective)


def formula_expression_generator(
    num_vars: int, max_depth: int, length: int,
    _cur_vars: Optional[set] = None
    ) -> str:
    '''Randomly generate a plain-text formula expression.
    
    Parameters:
        - num_vars: number of propositional variables
        - max_depth: max depth of the formula
        - length: max length, counted by number of occurences of prop vars
        
    Preconditions:
        - min({num_vars, max_depth, length}) > 0
        - num_vars <= 26  # currently using one-letter lower cased var names only
    '''
    conns = [' AND ', ' OR ', ' IMPLIES ', ' IFF ']
    if _cur_vars is None:
        _cur_vars = set()
        while len(_cur_vars) < num_vars:
            _cur_vars.add(chr(97 + random.randrange(0, 26)))
    ret = []
    while length != 0:
        if max_depth > 1 and length > 1 and random.randrange(0, 2):
            diff = random.randrange(1, length)
            cur = formula_expression_generator(num_vars, max_depth - 1, diff, _cur_vars)
            if diff != 1:
                cur = '(' + cur + ')'
        else:
            diff = 1
            cur = list(_cur_vars)[random.randrange(len(_cur_vars))]
        if random.randrange(0, 2):
            if cur[0] != '(':
                cur = f'NOT({cur})'
            else:
                cur = 'NOT' + cur
        ret.append(cur)
        length -= diff
    if len(ret) == 1:
        return ret[0]
    elif len(ret) == 2:
        return conns[random.randrange(4)].join(ret)
    else:
        return conns[random.randrange(2)].join(ret)

def test_correctness() -> None:
    '''Test correctness of PyProps.
    NOTE: this may take quite a while to run.
    '''
    for i in range(20):
        num_vars = random.randrange(1, 15)
        max_depth = random.randrange(1, 10)
        length = random.randrange(1, 20)
        f_txt = formula_expression_generator(num_vars, max_depth, length)
        f = parse_formula(f_txt)
        try:
            assert str(f) == f_txt
            assert equivalent(f, f.negation().negation())
            assert equivalent(f, f.to_cnf())
            assert equivalent(f, f.to_dnf())
            assert equivalent(f, f.to_nnf())
        except Exception as e:
            print('FAILED FORMULA: ', f_txt)
            raise e


# NOTE: FOR DEBUG PURPOSE
if __name__ == '__main__':
    doctest.testmod()
    print(_to_nested_lists('p OR (q AND r AND (S AND T AND (Q OR P)))', [0]))
    res = parse_formula('p OR (q AND r    AND   (   S AND T AND (Q OR P)  )  )  OR K')
    print(res, type(res))
    test_correctness()
    print('tests finished successfully.')

from pyprops import *

def parse(text: str) -> Formula:
    '''Parse a propositional formula recursively from the input text.
    
    Preconditions:
        - len(text) > 0
        - text.count('(') != text.count(')')
    '''
    return rec_parse(text.strip())[0]

def _parse_helper(segments: list[str]) -> Formula:
    '''Helper function for parsing text with no brackets into Formula.
    
    Preconditions:
        - len(segments) > 0
    '''
    # check for validity of the formula expression
    if 'NOT' in segments:
        raise ValueError('NOT must be used with brackets. (e.g. "NOT(p)" rather than "NOT p")')
    err = 'invalid formula expression!'
    conns = {'AND', 'OR', 'IMPLIES', 'IFF'}
    if segments[0] in conns or segments[-1] in conns:
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
    if connective == '':
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
    else:
        if len(subs) != 2:
            raise ValueError(err)
        else:
            return IffFormula(subs[0], subs[1])

def rec_parse(text: str, index: int = 0) -> tuple[Formula, int]:
    '''Helper function: parse a propositional formula recursively from the input text.
    '''
    err = 'invalid formula expression!'
    conns = {'AND', 'OR', 'IMPLIES', 'IFF'}
    # seperates brackets with other parts
    segments = []
    while index < len(text) and text[index] != ')':
        if text[index] == '(':
            res =  rec_parse(text[index + 1:], 0)
            segments.append(res[0])
            index += res[1] + 2
        elif text[index] == ')':
            break
        else:
            if len(segments) == 0 or not isinstance(segments[-1], str):
                segments.append('')
            segments[-1] += text[index]
            index += 1
    # trim empty strings
    segments = [s for s in segments if not (isinstance(s, str) and s.isspace())]
    # NOTE: DEBUG
    # print(text, ':', segments)
    # if just one element
    if len(segments) == 1:
        # if it is a string with no bracket, parse it
        if isinstance(segments[0], str):
            return (_parse_helper(segments[0].strip().split()), index)
        # if it is a parsed Formula object, return it
        else:
            return (segments[0], index)
    # otherwise, split each string
    new_segments = []
    for i in range(len(segments)):
        if isinstance(segments[i], str):
            # print('!!!', segments[i]) # NOTE: DEBUG
            new_segments.append(segments[i].strip().split())
        else:
            new_segments.append(segments[i])
    # print(new_segments) # NOTE: DEBUG
    # parse it
    subs = []
    connective = ''
    cur = None
    prev = None
    i = 0
    while i < len(new_segments):
        # two parsed objects placed together is something like "(p AND q)(q OR p)", this is invalid.
        if isinstance(cur, Formula) and isinstance(prev, Formula):
            raise ValueError(err)
        prev, cur = cur, new_segments[i]
        # if this is a parsed Formula object, just append it
        if isinstance(cur, Formula):
            subs.append(cur)
            i += 1
            continue
        # if this is a single str
        elif len(cur) == 1:
            if cur[0] not in conns or cur[0] == 'NOT' or (connective != '' and connective != cur[0]):
                raise ValueError(err)
            else:
                connective = cur[0]
                i += 1
                continue
        b1 = i > 0 and isinstance(new_segments[i - 1], Formula)
        b2 = i < len(new_segments) - 1 and isinstance(new_segments[i + 1], Formula)
        # if after a parsed object
        if b1:
            if cur[0] not in conns or (connective != '' and connective != cur[0]):
                raise ValueError(err)
            connective = cur[0]
            # if also before a parsed object
            if b2:
                if (cur[-1] == 'NOT') and (i < len(new_segments) - 1):
                    subs.append(NotFormula(new_segments[i + 1]))
                    i += 1
                    if (len(cur) < 3) or (cur[-2] != connective):
                        raise ValueError(err)
                    else:
                        subs.append(_parse_helper(cur[1:-2]))
                elif (cur[-1] == 'NOT') or (cur[-1] != connective):
                    raise ValueError(err)
                else:
                    subs.append(_parse_helper(cur[1:-1]))
            # if just after a parsed object, not before anotjer
            else:
                subs.append(_parse_helper(cur[1:]))
        # if just before a parsed object, not after another
        elif b2:
            if cur[-1] != 'NOT' and (cur[-1] not in conns or (connective != '' and connective != cur[-1])):
                raise ValueError(err)
            elif cur[-1] == 'NOT' and i < len(new_segments) - 1:
                subs.append(NotFormula(new_segments[i + 1]))
                i += 1
                if (len(cur) < 2) or (cur[-2] not in conns) or (connective != '' and cur[-2] != connective):
                    raise ValueError(err)
                else:
                    connective = cur[-2]
                    subs.append(_parse_helper(cur[:-2]))
            elif cur[-1] != 'NOT' and ((connective == '' and cur[-1] in conns) or connective == cur[-1]):
                connective = cur[-1]
                subs.append(_parse_helper(cur[:-1]))
        i += 1
        # print('!!!', connective) # NOTE: DEBUG
    if connective == '':
        return (subs.pop(), index)
    elif connective == 'AND':
        return (AndFormula(subs), index)
    elif connective == 'OR':
        return (OrFormula(subs), index)
    elif connective == 'IMPLIES':
        if len(subs) != 2:
            raise ValueError(err)
        else:
            return (ImpliesFormula(subs[0], subs[1]), index)
    else:
        if len(subs) != 2:
            raise ValueError(err)
        else:
            return (IffFormula(subs[0], subs[1]), index)

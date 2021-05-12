OR = 'v'
AND = '^'
COND = '→'
BICOND = '↔'
XOR = '⊕'
NAND = '↑'
NOR = '↓'
NOT = '~'

OR_EXTRAS = list("∨v")
AND_EXTRAS = list("∧ᴧ^")
COND_EXTRAS = list("⟹→")
BICOND_EXTRAS = list("≡↔")
XOR_EXTRAS = list(XOR)
NAND_EXTRAS = list("|↑")
NOR_EXTRAS = list(NOR)
NOT_EXTRAS = list("∼~¬!")

stdlsymbols = [OR, AND, COND, BICOND, XOR, NAND, NOR, NOT]
lsymbols_l = [OR_EXTRAS, AND_EXTRAS, COND_EXTRAS, BICOND_EXTRAS, XOR_EXTRAS, NAND_EXTRAS, NOR_EXTRAS, NOT_EXTRAS]
lsymbols = [item for sublist in lsymbols_l for item in sublist]

def standardize(symbol):
    for i in range(len(lsymbols_l)):
        if symbol in lsymbols_l[i]:
            return stdlsymbols[i]

    return symbol # some kind of custom symbol maybe?
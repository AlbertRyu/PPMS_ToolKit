''' Define different kinds of CW law '''


def curie_weiss_law_inverse(t, c, t_c):
    '''
    Defin inversed Curie_Weiss Law
    '''
    return (t - t_c)/c


def curie_weiss_law(t, c, t_c):
    '''
    Normal Curie Weiß Law
    
    Parameters:
    -----------
    t: float
        Temperature
    c: float
        Curie constant
    t_c: float
        Curie temperature / Weiss constant / Curie-Weiß temperature   
    '''
    return c / (t - t_c)


def mod_curie_weiss_law(t, c, t_c, chi0):
    '''Define the Curie-Weiss Law with the temperature-independent term'''
    return c / (t - t_c) + chi0

# -*- coding: utf-8 -*-

from transition import *
from state import *
import os
import copy
from sp import *
from parser import *
from itertools import product
import itertools
from automateBase import AutomateBase



class Automate(AutomateBase):
        
    def succElem(self, state, lettre):
        """State x str -> list[State]
        rend la liste des états accessibles à partir d'un état
        state par l'étiquette lettre
        """
        successeurs = []
        # t: Transitions
        for t in self.getListTransitionsFrom(state):
            if t.etiquette == lettre and t.stateDest not in successeurs:
                successeurs.append(t.stateDest)
        return successeurs


    def succ (self, listStates, lettre):
        """list[State] x str -> list[State]
        rend la liste des états accessibles à partir de la liste d'états
        listStates par l'étiquette lettre
        """
        list_succ = []
        for state in listStates:
            list_succ.extend(self.succElem(state, lettre))

        return list_succ




    """ Définition d'une fonction déterminant si un mot est accepté par un automate.
    Exemple :
            a=Automate.creationAutomate("monAutomate.txt")
            if Automate.accepte(a,"abc"):
                print "L'automate accepte le mot abc"
            else:
                print "L'automate n'accepte pas le mot abc"
    """
    @staticmethod
    def accepte(auto,mot) :
        """ Automate x str -> bool
        rend True si auto accepte mot, False sinon
        """
        states = auto.getListInitialStates()

        for s in mot :
            states_suivant = []
            for e in states :
                for tr in auto.getListTransitionsFrom(e) :
                    if s == tr.etiquette:
                        states_suivant.append(tr.stateDest)

            states = states_suivant

        for a in states:
            if a in auto.getListFinalStates() :
                return True
        return False



    @staticmethod
    def estComplet(auto,alphabet) :
        """ Automate x str -> bool
         rend True si auto est complet pour alphabet, False sinon
        """
        for state in auto.listStates :
            alph = []
            for transition in auto.getListTransitionsFrom(state) :
                if transition.etiquette not in alph :
                    alph.append(transition.etiquette)
            if sorted(alph)!=sorted(alphabet) :
                return False
        return True
        
    @staticmethod
    def estDeterministe(auto) :
        """ Automate  -> bool
        rend True si auto est déterministe, False sinon
        """
        for t1 in auto.listTransitions :
            for t2 in auto.listTransitions :
                if t1.etiquette == t2.etiquette and t1.stateSrc == t2.stateSrc and not t1.stateDest == t2.stateDest :
                    return False
        return True




       
    @staticmethod
    def completeAutomate(auto,alphabet) :
        """ Automate x str -> Automate
        rend l'automate complété d'auto, par rapport à alphabet
        """
        if (Automate.estComplet(auto, alphabet)) :
            return copy.deepcopy(auto)
        else :
            # poubelle : State
            poubelle = State(404, False, False)
            # copie_auto : Automate
            copie_auto = copy.deepcopy(auto)
            copie_auto.addState(poubelle)

            for y in alphabet:
                copie_auto.addTransition(Transition(poubelle, y, poubelle))

            for x in alphabet :
                for state in auto.listStates :
                    isin = False
                    for transition in auto.getListTransitionsFrom(state) :
                        if transition.etiquette==x :
                            isin = True
                    if not isin :
                        copie_auto.addTransition(Transition(state, x, poubelle))

            return copie_auto

    @staticmethod
    def determinisation(auto) :
        """ Automate  -> Automate
        rend l'automate déterminisé d'auto
        """

        if Automate.estDeterministe(auto):
            return copy.deepcopy(auto)
        else :
            q0 = frozenset(auto.getListInitialStates())
            qn = set(auto.getListFinalStates())
            Q = set()
            Q.add(q0)
            unprocessedQ = Q.copy()
            alphabet = auto.getAlphabetFromTransitions()
            ListTransition = []
            delta ={}
            i=0
            j=0
            while (len(unprocessedQ) > 0) :
                qset = unprocessedQ.pop()
                # statesrc :State
                statesrc = State(i, qset==q0,(len(qset & qn) > 0), set(qset))

                i=i+1
                for a in alphabet :
                    nextstates=set()
                    for q in qset:
                        for tr in auto.getListTransitionsFrom(q) :
                            if tr.etiquette==a :
                                if not tr.stateDest in nextstates :
                                    if qset==q0 :
                                        print("HOHO", a,  tr.stateDest)
                                    nextstates.add(tr.stateDest)

                    nextstates = frozenset(nextstates)

                    if nextstates not in delta :
                        statedest = State(j, nextstates==q0, (len(nextstates & qn) > 0), list(nextstates))
                        j=j+1
                        if qset==q0 :
                            print("HOHO", a, nextstates)
                        delta[nextstates] = statedest
                    else :
                        statedest = delta[nextstates]
                    ListTransition.append(Transition(statesrc,a,statedest))
                    if not nextstates in Q:
                        Q.add(nextstates)
                        unprocessedQ.add(nextstates)

            return Automate(ListTransition)

        
    @staticmethod
    def complementaire(auto,alphabet):
        """ Automate -> Automate
        rend  l'automate acceptant pour langage le complémentaire du langage de a
        """
        copie_auto = copy.deepcopy(auto)
        copie_auto = Automate.completeAutomate(copie_auto, alphabet)
        copie_auto = Automate.determinisation(copie_auto)
        for state in copie_auto.listStates :
            state.fin = not state.fin
        return copie_auto

   
    @staticmethod
    def intersection (auto1, auto2):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'intersection des langages des deux automates
        """
        s1 = auto1.listStates
        s2 = auto2.listStates
        i1 = auto1.getListInitialStates()
        i2 = auto2.getListInitialStates()
        f1 = auto1.getListFinalStates()
        f2 = auto2.getListFinalStates()
        alphabet = auto.getAlphabetFromTransitions()
        transition = []
        dico = {}
        destinations = list(itertools.product(i1,i2))
        i=0
        for a in list(itertools.product(s1, s2)) :
            for b in list(itertools.product(s1, s2)) :
                a1, a2 = a          #a1 = s1    b1=s1'  a2=s2   b2=s2'
                b1, b2 = b
                for alpha in alphabet :
                    if b1 in auto1.succElem(a1, alpha) and b2 in auto2.succElem(a2, alpha) and a in destinations :
                        # making state src
                        if a in dico :
                            src = dico[a]
                        else :
                            src = State(i, a in list(itertools.product(i1,i2)), a in list(itertools.product(f1,f2)), a )
                            dico[a] = src
                            i=i+1
                        # making state src
                        if b in dico :
                            dest = dico[b]
                        else :
                            dest = State(i, b in list(itertools.product(i1,i2)), b in list(itertools.product(f1,f2)), b )
                            dico[b] = dest
                            destinations.append(b)
                            i=i+1
                        transition.append(Transition(src,alpha,dest))
        return Automate(transition)

    @staticmethod
    def union (auto1, auto2):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'union des langages des deux automates
        """
        alphabet = auto.getAlphabetFromTransitions()
        auto11 = Automate.completeAutomate(auto1, alphabet)
        auto22 = Automate.completeAutomate(auto2, alphabet)
        s1 = auto11.listStates
        s2 = auto22.listStates
        i1 = auto11.getListInitialStates()
        i2 = auto22.getListInitialStates()
        f1 = auto11.getListFinalStates()
        f2 = auto22.getListFinalStates()
        transition = []
        dico = {}
        destinations = list(itertools.product(i1, i2))
        i = 0;
        for a in list(itertools.product(s1, s2)):
            for b in list(itertools.product(s1, s2)):
                a1, a2 = a  # a1 = s1    b1=s1'  a2=s2   b2=s2'
                b1, b2 = b
                for alpha in alphabet:
                    if b1 in auto11.succElem(a1, alpha) and b2 in auto22.succElem(a2, alpha) and a in destinations:
                        # making state src
                        if a in dico:
                            src = dico[a]
                        else:
                            src = State(i, a in list(itertools.product(i1, i2)), a in list(set(itertools.product(f1, s2)) | set(itertools.product(s1, f2))),a)
                            dico[a] = src
                            i = i + 1
                        # making state dest
                        if b in dico:
                            dest = dico[b]
                        else:
                            dest = State(i, b in list(itertools.product(i1, i2)), b in list(set(itertools.product(f1, s2)) | set(itertools.product(s1, f2))),b)
                            dico[b] = dest
                            destinations.append(b)
                            i = i + 1
                        transition.append(Transition(src, alpha, dest))
        return Automate(transition)
        

   
       

    @staticmethod
    def concatenation (auto1, auto2):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage la concaténation des langages des deux automates
        """
        automate1 = copy.deepcopy(auto1)
        automate2 = copy.deepcopy(auto2)

        alphabet = auto.getAlphabetFromTransitions()
        s1 = automate1.listStates
        s2 = automate2.listStates
        i1 = automate1.getListInitialStates()
        i2 = automate2.getListInitialStates()
        f1 = automate1.getListFinalStates()
        f2 = automate2.getListFinalStates()
        t1=automate1.listTransitions
        t2=automate2.listTransitions

        transitions = t1
        for n in t2 :
            if n not in transitions : transitions.append(n)

        for i in i2 :
            for s in s1 :
                for f in f1 :
                    for alpha in alphabet :
                        if Transition(s,alpha,f) in t1 :
                            transitions.append(Transition(s,alpha,i))

        if len(list(set(i1)&set(f1))) > 0 :
            i = i1
        else :
            i = list(set(i1) | set(i2))

        for t in transitions :
            s = t.stateSrc
            d = t.stateDest
            if s in i :
                s.init = True
            else :
                s.init = False
            if d in i :
                d.init=True
            else :
                d.init= False

        for t in transitions :
            s = t.stateSrc
            d = t.stateDest
            if s in f2 :
                s.fin = True
            else :
                s.fin = False
            if d in f2 :
                d.fin=True
            else :
                d.fin= False


        return Automate(transitions)
        
       
    @staticmethod
    def etoile (auto):
        """ Automate  -> Automate
        rend l'automate acceptant pour langage l'étoile du langage de a
        """
        A = Automate.concatenation(auto,auto)
        A.listStates.append(State(len(A.listStates), True, True, "j"))
        return A



## cr´eation d’´etats
# s1 : State
s1 = State(1, True, False)
# s2 : State
s2 = State(2, False, True)
## cr´eation de transitions
# t1 : Transition
2
t1 = Transition(s1,"a",s1)
# t2 : Transition
t2 = Transition(s1,"a",s2)
# t3 : Transition
t3 = Transition(s1,"b",s2)
# t4 : Transition
t4 = Transition(s2,"a",s2)
# t5 : Transition
t5 = Transition(s2,"b",s2)
# liste : list[Transition]
liste = [t1,t2,t3,t4,t5]
## cr´eation de l’automate
# aut : Automate
aut = Automate(liste)

################ EX 2  #######################


# s0 : State
s0 = State(0, True, False)

# s1 : State
s1 = State(1, False, False)

# s2 : State
s2 = State(2, False, True)

# t1 : Transition
t1 = Transition(s0, "a", s0)

# t2 : Transition
t2 = Transition(s0, "b", s1)

# t3 : Transition
t3 = Transition(s1, "a", s2)

# t4 : Transition
t4 = Transition(s1, "b", s2)

# t5 : Transition
t5 = Transition(s2, "a", s0)

# t6 : Transition
t6 = Transition(s2, "b", s1)

# auto : Automate
auto = Automate([t1, t2, t3, t4, t5, t6])

#auto1 : Automate
auto1 = Automate([t1, t2, t3, t4, t5, t6], [s0, s1, s2])

auto2 = Automate.creationAutomate("auto.txt")
print(auto)
print(auto1)
print(auto2)
auto.addTransition(Transition(s1,"a", s1))
auto.show("2")
auto404 = Automate.etoile(auto)
auto404.show("404")
print(auto404)
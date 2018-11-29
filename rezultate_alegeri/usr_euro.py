#!/usr/bin/python
#
# Author: Catalin Drula <catalin.drula@cdep.ro>
# 
# MIT LICENSE
# Copyright (c) 2018 USR

import csv, sys

def calc_score(cand):
    return sum([a*b for a,b in zip(cand[1], cand[2])])

def cmp_results(cand_a, cand_b):
    if calc_score(cand_a) < calc_score(cand_b):
        return -1
    elif calc_score(cand_a) > calc_score(cand_b):
        return 1
    else:
        i=0
        while i < len(cand_a[1]):
            if cand_a[1][i] < cand_b[1][i]:
                #print "Spart egalitatea: %s > %s pt ca are %d fata de %d note de %d"%(cand_a[0], cand_b[0], cand_a[1][i], cand_b[1][i], cand_a[2][i])
                return -1
            elif cand_a[1][i] > cand_b[1][i]:
                #print "Spart egalitatea: %s > %s pt ca are %d fata de %d note de %d"%(cand_a[0], cand_b[0], cand_a[1][i], cand_b[1][i], cand_a[2][i])
                return 1
            i+=1
        #print "Egalitate perfecta: %s --- %s"%(cand_a[0], cand_b[0])
        return 0
                
if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print "Folosire: usr_euro.py <zeus_results.csv> [<candidati_judete.csv>]"
        print ""
        print "Daca se specifica doar un argument acesta trebuie sa fie fisierul CSV cu rezultate generat de Zeus; script-ul va face doar ordonarea si afisarea listei brute"
        print "Daca se specifica si al doilea argument acesta trebuie sa fie lista de candidati cu judet in CSV in formatul:"
        print "Mihai Popescu, Hunedoara"
        print "George Ionescu, Maramures"
        sys.exit(1)

    # citeste fisierul de tip rezultate din Zeus 
    with open(sys.argv[1], 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            # cauta linia care are doar SCORURI sau SCORES (depinde daca CSV e in Ro sau En)
            # de acolo incep in CSV numarul de note de fiecare tip primite de candidati
            if len(row) == 1 and row[0] in ["SCORES", "SCORURI"]:
                break

        # urmatoarea linie are valoarea notelor folosite in scrutin (ex. pt USR europarlamentare - 9,7,5,4,3,2,1)
        points = [int(p) for p in reader.next()[2:]]

        # incepe procesarea fiecarui candidat
        results = []
        for row in reader:
            # liniile goale sunt ignorate
            if not row:
                break
            # extrage numele candidatului
            candidate = row[0].split(":")[1].strip()
            # extrage numarul de voturi cu fiecare punctaj primit de candidati
            cand_count_points = [int(p) for p in row[2:]]
            # construieste lista procesata cu nume candidat, numar de voturi cu fiecare punctaj 
            results.append((candidate, cand_count_points, points))

    # ordoneaza candidatii dupa regula USR:
    # - dupa punctaj total
    # - in caz de egalitate, dupa numarul de note 9 primite, apoi daca e egalitate, dupa numarul de note de 7 primite, etc
    results = sorted(results, cmp=cmp_results, reverse=True)

    # construieste lista candidat, scor (ordonata)
    cand_score = []
    for cand in results:
        cand_score.append((cand[0], calc_score(cand)))

    # daca s-au dat doua argumente in linia de comanda citeste si maparea candidat - judet
    if len(sys.argv) == 3:
        cand_judet = {}
        with open(sys.argv[2], 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                cand_judet[row[0]] = row[1]

    # genereaza primii_15.csv 
    with open('primii15.csv', 'w') as f:
        csvwriter = csv.writer(f)
        for name, score in cand_score[:15]:
            csvwriter.writerow([name, score])

    # afiseaza lista bruta
    print "Lista bruta"
    for (loc, (name, score)) in enumerate(cand_score):
        if len(sys.argv) == 2:
            print "%2d. %s %d pct"%(loc+1, name, score)
        else:
            print "%2d. %s %d pct - %s"%(loc+1, name, score, cand_judet[name])

    if len(sys.argv) == 2:
        sys.exit(0)

    print ""
    print "Lista USR"
    judete_care_apar_deja = set()
    skip = list()
    lista_usr = list()
    for (index, (name, score)) in enumerate(cand_score):
        if len(lista_usr) == 43:
            break
        judet = cand_judet[name]
        if index < 15:
            # primii 15 se trec ca atare
            #print len(lista_usr), name, score, judet
            lista_usr.append((name, score, judet))
        else:
            if judet in judete_care_apar_deja:
                #print "SKIP", len(lista_usr), name, score, judet                
                skip.append((name, score, len(lista_usr), judet))
                continue
            #print len(lista_usr), name, score, judet
            lista_usr.append((name, score, judet))
        judete_care_apar_deja.add(judet)

    # daca lista e deja completa dupa prima runda, suntem gata
    if len(lista_usr) == 43:
        sys.exit(0)
        
    # altfel, reintroducere cei scosi in ordine
    reintrodusi = 0
    for (name, score, poz, judet) in skip:
        if len(lista_usr) == 43:
            break
        lista_usr.insert(poz + reintrodusi, (name, score, judet))
        reintrodusi += 1

    for loc, (name, score, judet) in enumerate(lista_usr):
        print "%2d. %s %d pct - %s"%(loc+1, name, score, judet)

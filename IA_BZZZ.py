import random
from typing import Literal
from math import sqrt
from ia import JeuDict, MoteurIA


class IAAleatoire(MoteurIA):
    nom = "IA_BZZZ"

    def __init__(
        self, joueur_id: str, ncases: int, max_tours: int, temps_ko: int
    ) -> None:
        self.joueur_id = joueur_id
        self.ncases = ncases
        self.max_tours = max_tours
        self.temps_ko = temps_ko
        self.cout_ponte = 0
        self.seuil_distance_eclaireuse = 15
        self.derniere_action = {}
        self.zones_interdites = []
        self.position_precedent = {}
        self.dernier_tour_ko = {}
        self.tour_du_joueur = 1
        self.fleurs_vides = []
        self.nectar_precedent = {}
        self.cibles_abeilles = {}

    #diagonal
    def distance(self, pos1, pos2):
        return sqrt((pos1["position"]["x"] - pos2["x"])**2 + (pos1["position"]["y"] - pos2["y"])**2)

    #pas diagonal
    def distance_manhattan(self, pos1, pos2):
        return abs(pos1["x"] - pos2["x"]) + abs(pos1["y"] - pos2["y"])
    
    def abs_distance_x(self, pos1, pos2):
        return abs(pos1["x"] - pos2["x"])
    
    def abs_distance_y(self, pos1, pos2):
        return abs(pos1["y"] - pos2["y"])
    
    def nb_types_abeilles(self, joueur):
        nb_ecl = 0
        nb_ouv = 0
        nb_bou = 0
        for abeille in joueur["abeilles"]:
            if abeille["abeille_type"] == "ECL":
                nb_ecl += 1
            elif abeille["abeille_type"] == "OUV":
                nb_ouv += 1
            else:
                nb_bou += 1
        
        return [nb_ecl, nb_ouv, nb_bou]

    def calculer_distance_fleurs(self, jeu):
        """Calcule la distance moyenne des fleurs par rapport à la ruche"""
        if not jeu["fleurs"]:
            return 0
        
        distances = []
        ruche = jeu["moi"]["position"]
        for fleur in jeu["fleurs"]:
            distance = self.distance_manhattan(ruche,fleur)
            distances.append(distance)
        return sum(distances) / len(distances)
    
    def abeille_zone(self, jeu, abeille) -> bool:  
        return self.abs_distance_x(jeu["moi"]["position"],abeille["position"]) <= 3 and self.abs_distance_y(jeu["moi"]["position"],abeille["position"]) <= 3

    def ponte(self, jeu: JeuDict, cout_ponte: int) -> Literal["OUV", "BOU", "ECL", "RIEN"]:
        moi = jeu["moi"]
        nectar = moi["nectar"]
        self.cout_ponte = cout_ponte
        nb_ecl , nb_ouv , nb_bou = self.nb_types_abeilles(moi)
        distance_moy_fleurs = self.calculer_distance_fleurs(jeu) 

        nb_abeilles = self.nb_types_abeilles(moi)
        nb_abeilles = nb_abeilles[0]+nb_abeilles[1]+nb_abeilles[2]

        
        abeilles_zone = 0
        for abeille in moi["abeilles"]:
            if self.abeille_zone(jeu,abeille):
                abeilles_zone+=1


        if nectar < cout_ponte:
            return "RIEN"
        
        #ca aussi ducoup
        '''
        elif abeilles_zone >= 12:
            return "RIEN"
        '''

        if self.tour_du_joueur == 1:
                return "OUV"
        
        if nb_bou == 0:
            return "BOU"
        if nb_ouv == 1:
            return "OUV"
        if nb_bou == 1:
            return "BOU"
        

        if distance_moy_fleurs > self.seuil_distance_eclaireuse:
            if nb_ecl < len(jeu["fleurs"]) // 8:
                return "ECL"

        if nb_ouv <= len(jeu["fleurs"]) // 6 and nb_abeilles < 10:
            return "OUV"

        return "RIEN"
    
    def fleur_vides(self, abeille, jeu: JeuDict):
        a_id = abeille["id"]
        nectar_butine = abeille["nectar"] - self.nectar_precedent[a_id]
        
        if nectar_butine == 0:
            if a_id in self.cibles_abeilles:
                self.fleurs_vides.append(self.cibles_abeilles[a_id])
                del self.cibles_abeilles[a_id]

    def choisir_meilleure_fleur(self, abeille, jeu: JeuDict):
        fleurs = jeu["fleurs"]
        if self.derniere_action[abeille["id"]] == "BUTINAGE" and self.dernier_tour_ko[abeille["id"]] == False:
            self.fleur_vides(abeille, jeu)

        distance_min = float("inf")
        for fleur in fleurs:
            if abeille["abeille_type"] == "ECL":
                distance = self.distance(abeille,fleur)
            else:
                distance = self.distance_manhattan(abeille["position"],fleur)
            
            fleur_deja_ciblee = (fleur in self.cibles_abeilles.values()) and (self.cibles_abeilles.get(abeille["id"]) != fleur)

            # Si la fleur est plus proche, puis si elle n'est pas déjà prise par une autre abeille, et enfin si cette fleur n'est pas celle déjà ciblée actuellement
            if (distance < distance_min) and (fleur not in self.fleurs_vides) and (not fleur_deja_ciblee):
                distance_min = distance
                self.cibles_abeilles[abeille["id"]] = fleur

    def butinage(self, jeu, abeille, abeilles_action):
        cible = self.cibles_abeilles.get(abeille["id"])
        if cible is None:
            cible = {"x": self.ncases // 2, "y": self.ncases // 2}
        else:
            if self.abs_distance_x(abeille["position"],cible) <= 1 and self.abs_distance_y(abeille["position"],cible) <= 1 and (not self.abeille_zone(jeu, abeille)):
                self.derniere_action[abeille["id"]] = "BUTINAGE"
                abeilles_action.append((abeille["id"],cible["x"],cible["y"],"BUTINAGE"))
                return cible, abeilles_action, True
        return cible, abeilles_action, False

    def set_abeille_vierge(self, abeille):
        if self.derniere_action.get(abeille["id"]) is None:
            self.derniere_action[abeille["id"]] = "RIEN"
        
        if self.nectar_precedent.get(abeille["id"]) is None:
            self.nectar_precedent[abeille["id"]] = 0

        if self.dernier_tour_ko.get(abeille["id"]) is None:
            self.dernier_tour_ko[abeille["id"]] = False

    def zone_joueur_proche(self, jeu, abeille):
        
        cible_x = max(jeu["moi"]["position"]["x"] - 3, min(abeille["position"]["x"], jeu["moi"]["position"]["x"] + 3))
        cible_y = max(jeu["moi"]["position"]["y"] - 3, min(abeille["position"]["y"], jeu["moi"]["position"]["y"] + 3))
        return {"x": cible_x, "y": cible_y}


    def detection_bourdon_proche(self, jeu, abeille):
        x = abeille["position"]["x"]
        y = abeille["position"]["y"]

        for joueur in jeu["autres_joueurs"]:
            for abeille_adverse in joueur["abeilles"]:
                if abeille_adverse["abeille_type"] != "BOU" or abeille_adverse["ko_temps"] != 0:
                    dx = abs(abeille_adverse["position"]["x"] - x)
                    dy = abs(abeille_adverse["position"]["y"] - y)
                    if dx <= 1 and dy <= 1:
                        return True
        return False

    def trouver_cible_ouvriere_ou_eclaireuse(self, jeu, abeille, abeilles_action):
        nectar = abeille["nectar"]
        nectar_max = abeille["max_nectar"]
        self.choisir_meilleure_fleur(abeille, jeu)
        fuir = self.detection_bourdon_proche(jeu, abeille)

        if fuir == True:
            if nectar >= self.cout_ponte * 2 + 2 or nectar >= nectar_max // 2:
                cible = self.zone_joueur_proche(jeu, abeille)
                action_effectuee = False
            else:
                cible, abeilles_action, action_effectuee = self.butinage(jeu, abeille, abeilles_action)
        else:
            if nectar >= self.cout_ponte * 2 + 2 or nectar >= nectar_max:
                cible = self.zone_joueur_proche(jeu, abeille)
                action_effectuee = False
            else:
                cible, abeilles_action, action_effectuee = self.butinage(jeu, abeille, abeilles_action)
        return cible, abeilles_action, action_effectuee

    def trouver_cible_bourdon(self, jeu, abeille):
        distance_min = float("inf")
        abeille_cible = None        
        distance_min_2 = float("inf")
        abeille_cible_2 = None

        for joueur_ennemi in jeu["autres_joueurs"]:
            for abeille_ennemie in joueur_ennemi["abeilles"]:
                if abeille_ennemie["ko_temps"] <= 0:
                    distance = self.distance_manhattan(abeille["position"],abeille_ennemie["position"])
                    if abeille_ennemie["abeille_type"] == "OUV":
                        if (distance < distance_min):
                            distance_min = distance
                            abeille_cible = abeille_ennemie["position"]
                    elif abeille_ennemie["abeille_type"] == "BOU":
                        if (distance < distance_min_2):
                            distance_min_2 = distance
                            abeille_cible_2 = abeille_ennemie["position"]

        if abeille_cible is not None:
            return abeille_cible
        elif abeille_cible_2 is not None:
            return abeille_cible_2
        else:
            return {"x": self.ncases // 2, "y": self.ncases // 2}

    def trouver_action(self, jeu, abeille, abeilles_action):
        action_effectuee = False

        if abeille["abeille_type"] == "OUV" or abeille["abeille_type"] == "ECL":
            cible, abeilles_action, action_effectuee = self.trouver_cible_ouvriere_ou_eclaireuse(jeu, abeille, abeilles_action)

        elif abeille["abeille_type"] == "BOU":
            cible = self.trouver_cible_bourdon(jeu, abeille)

        if not action_effectuee:
            abeilles_action, action_effectuee = self.deplacement(jeu, abeille, abeilles_action, cible, action_effectuee)
        
        if not action_effectuee:
            self.derniere_action[abeille["id"]] = "RIEN"

        return abeilles_action
    
    def action_abeilles(self, jeu: JeuDict) -> list[tuple[str, int, int, Literal["DEPLACEMENT", "BUTINAGE"]]]:
        moi = jeu["moi"]
        abeilles_action: list[tuple[str, int, int, Literal["DEPLACEMENT", "BUTINAGE"]]] = []

        #cherche les zones de ruches des ennemis pour les mettre dans les zones interdites
        self.zones_interdites = []
        for joueur in jeu["autres_joueurs"]:
            joueur_pos = joueur["position"]
            for x in range(-3, 4):
                for y in range(-3, 4):
                    if (0 <= joueur_pos["x"] + x < self.ncases) and (0 <= joueur_pos["y"] + y < self.ncases):
                        self.zones_interdites.append((joueur_pos["x"] + x, joueur_pos["y"] + y))

        for abeille in moi["abeilles"]:

            self.set_abeille_vierge(abeille)
            
            if abeille["ko_temps"] <= 0:
                abeilles_action = self.trouver_action(jeu, abeille, abeilles_action)
                self.nectar_precedent[abeille["id"]] = abeille["nectar"]
                self.dernier_tour_ko[abeille["id"]] = False
            else:
                self.dernier_tour_ko[abeille["id"]] = True
        self.tour_du_joueur += 1
        return abeilles_action
    
    def deplacement(self, jeu, abeille, abeilles_action, cible, action_effectuee): 
        cases_interdites = []
        x_actuel = abeille["position"]["x"]
        y_actuel = abeille["position"]["y"]

        for abeille_moi in jeu["moi"]["abeilles"]:
            if abeille_moi["id"] != abeille["id"]:
                cases_interdites.append((abeille_moi["position"]["x"], abeille_moi["position"]["y"]))
        for joueur in jeu["autres_joueurs"]:
            for abeille_ennemie in joueur["abeilles"]:
                cases_interdites.append((abeille_ennemie["position"]["x"], abeille_ennemie["position"]["y"]))

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        if abeille["abeille_type"] == "ECL":
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        cases_possibles = []

        for x, y in directions:
            deplace_x, deplace_y = x_actuel + x, y_actuel + y

            if not((deplace_x, deplace_y) in cases_interdites):
                if not((deplace_x, deplace_y) in self.zones_interdites):
                    if (0 <= deplace_x < self.ncases):
                        if(0 <= deplace_y < self.ncases):
                            if abeille["abeille_type"] == "ECL":                                
                                dist = sqrt((deplace_x - cible["x"])**2 + (deplace_y - cible["y"])**2)
                            else:
                                dist = abs(deplace_x - cible["x"]) + abs(deplace_y - cible["y"])
                            ancienne_pos = self.position_precedent.get(abeille["id"])
                            if ancienne_pos == (deplace_x,deplace_y):
                                dist+=1
                            cases_possibles.append((dist, deplace_x, deplace_y))                      

        if cases_possibles:
            case = min(cases_possibles)
        else:
            case = (0, x_actuel, y_actuel)

        abeilles_action.append((abeille["id"],case[1],case[2],"DEPLACEMENT"))
        self.derniere_action[abeille["id"]] = "DEPLACEMENT"
        self.position_precedent[abeille["id"]] = (x_actuel, y_actuel)
        return abeilles_action, True
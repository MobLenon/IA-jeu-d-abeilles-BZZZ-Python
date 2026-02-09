# IA-jeu-d-abeilles-BZZZ-Python


##Le jeu a été donné il fallait seulement créer l'IA

###mettre l'IA dans Jeu_BZZZ_IA/bzzz_moteur/ia


1. Stratégie Globale

Notre IA permet d'avoir du nectar le plus rapidement possible pour avoir une partie économique stable, puis va attaquer les autres abeilles pour les ralentir dans leurs progression.

2. Stratégie de Ponte

Il y a une logique de priorité qui prend en compte la carte et le déroulé de la partie.

Le plus vite possible, on pond une ouvrière, suivie d'un bourdon, puis une deuxième ouvrière, puis un second Bourdon pour permettre d'avoir un minimum de force dès le début de partie.

Adaptation à la carte :

Elle produit des ouvrières tant que leurs nombre ne dépasse pas 1/4 du nombre de fleurs total.

Si la distance moyenne des fleurs est supérieur au seuil de distance des éclaireuses, on va pondre des éclaireuses jusqu'à 1/8 du nombre de fleurs

Si il y n'a pas de nectar dans la ruche ou que le nombre d'abeille a atteint son nombre maximum l'IA ne pond plus pour éviter d'avoir des abeilles inutiles.

3. Stratégie de Butinage

L'IA choisit une fleur libre et la plus proche de sa position.

Il est impossible que plusieurs abeilles soient sur la même fleur.

Il y a une seule cible par abeille si une abeille reçoit une fleur qui est déjà prise elle ira en chercher une autre pour éviter tout problème.

Pour les Éclaireuses : Calcule la distance euclidienne (vol d'oiseau).

Pour les Ouvrières et Bourdons : Calcule la distance de manhattan (déplacement par cases).

Pour gérer les fleurs vides, on a tous simplement mis une liste noir pour placer les fleurs qui ont été butiné et qui ont donné 0 nectar.

Une abeille peut retourner à sa ruche si elle a atteint le maximum de nectar qu'elle peux transporter ou qu'elle a assez de nectar pour pouvoir impliquer 2 pontes.
Si une abeille a un bourdon a moins de 2 cases, elle revient à partir de la moitié du maximum de nectar ou si elle a assez de nectar pour pouvoir impliquer 2 pontes

4. Stratégie de Combat et Défense

Tout d'abord les bourdons vont scanner la carte pour trouver des ennemis. L'IA va donc prioriser les ouvrière adverse pour faire baisser l'économie de l'adversaire et si aucune ouvrière est disponible
il va prendre pour cible les bourdons ennemis.

S'il n'y a aucun ennemi, les bourdon vont se placer au centre de la carte pour avoir une zone d'occupation large et pouvoir intervenir rapidement et efficacement si un ennemi est visible.

5. Déplacements et Sécurité

L'IA va faire attention aux zones ennemies en les calculant pour éviter une élimination inutile.

Lors du calcul de déplacement, l'IA prend en compte comme obstacles les murs, les abeilles ennemies, ses abeilles alliées et les zones de joueurs.

Il y a une partie du code qui pénalise les retour sur la case précédente ce qui va permettre d'éviter de faire des mouvements d'aller-retours continus et presque tout le temps inutiles. 

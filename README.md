# Plan du projet : Détection des langues dans le code-mixing et switching

## Prétraitement du texte:

1. On commence par nettoyer les ponctuations (attention aux différentes ponctuations des différentes langues concernées), enlever les chiffres, lowercase les lettres etc.
2. **tokenization** : librairie jieba pour chinois, nltk pour anglais / français (éventuellement d'autres langues)

## Identification des lettres

1. Quand on détecte une lettre accentuée tel que "ç", on peut supposer directement qu'il s'agit de la langue française; quand il s'agit d'un token entre `\u4E00 <= token <= \u9FFF`, c'est du chinois;

## Calcul des fréquences des lettres

1. Le script compte la fréquence d'apparition de chaque lettre dans le texte. On dispose de données sur la fréquence théorique des lettres dans différentes langues (comme l'anglais, le français, l'allemand, etc.). Ces données reflètent la fréquence habituelle d'apparition des lettres dans une langue donnée.
2. Ensuite, on calcule la distance euclidienne entre les fréquences de lettres du texte et les fréquences théoriques de chaque langue. Cette étape évalue les différences entre les fréquences réelles et théoriques.
3. On identifie la langue en choisissant celle dont les données théoriques sont les plus proches des données du texte analysé, c'est-à-dire celle avec la distance minimale, potentiellment avec les possibilités des chaque langue

## Remarque

##### 04/04/2024

- Ces méthodes ont énormément de limites surtout dans le cas du code mixing et pour les textes courts, on doute qu'il soit très compliqué dans un cas où les deux langues n'ont pas de caractéristiques distinctives comme les caractères diacritiques et qu'il s'agit d'une seule phrase courte. Nous planifions de faire plus de recherches d'articles pendant les vacances pour explorer les solutions des recherches sur internet pour pouvoir avoir d'autres pistes à notre sujet.

- On dispose maintenant d'un proto-script d'un detecteur des langues pour l'anglais, chinois et français avec le nettoyage de texte. Pour l'instant qu'il ne peut que détecter des tokens contenant des diacritiques comme le français; il marche bien pour les tokens chinois, les tokens non-diacrités en français sont détectés comme anglais;

#### 02/05/2024

- modèle svm(svc): f1-socre pour lang1: 0.90, lang2: 0.91, ce qui est un résultat assez satisfaisant
- Nous planifion utiliser 2 autres méthodes pour comparer l'un avec l'autre et avoir le meilleur modèle : regression logistique et CRF

- maintenant on a implémenté et déployé notre code et modèle dans une interface en utilisant `streamlit`` pour pouvoir tester notre modèle plus rapidement et proprement, streamlit est un framework de Python opensource pour le ML et des applications de données
- le problème qu'on a remarqué est que l'outil ne peut pas détecter quand c'est du code-switching entre anglais et espagnol, quand on entre "hello amigo", il définit les 2 tokens comme anglais, mais qunad on entre seulement "amigo", il peut bien détecter que c'est de l'espagnol

#### Difficultés rencontrées
- dur au début de switcher entre deux langue, après avoir bien modifié la tokénization étape par étape pour espagnol et anglais en mettant le chinois a part, on a réussi
- quand on mélange les ponctuations avec une langue il pense que cest une langue inconnue puisqu'il le considère comme un seul token sans espace
- quand on mélange le chinois avec une autre langue(sans espace entre les langues, c'est ce qu'on a l'habitude de faire en généralement), le script la reconnaît également comme langue inconnue, donc on a utilisé une variable `buffer` qui initialise un string vide qui sert à accumuler des caractères qui appartiennet ensemble, formant soit un mot soit une ponctuation
Si le buffer n'est pas vide et ne correspond pas à un motif de ponctuation, selon la langue du premier caractère du buffer, les caractères sont traités différemments: si le premier caractère est chinois,on utilise les règles de Unicode et ensuite librairie jieba pour découper en tokens chinois; sinon, on emploie le tokénizeur de nltk pour l'espagnol et l'anglais qui sont en alphabet romain. Si le buffer correspond à un motif de ponctuation, il est ajouté directement à la liste des tokens sans découpage supplémentaire --> on appelle ce processus la tokénization intelligente, qui prend en compte à la fois les changements de scripts entre les alphabets et la ponctuation, qui assure que les tokens de différentes langues sont correctements identifiés et traités comme des éléments distincts.
"""Point d'entrée de la commande :  python -m orunmila

Quand tu tapes  python -m orunmila , Python cherche ce fichier
__main__.py et l'exécute. Il ne fait qu'une chose : lancer l'interface
terminal définie dans cli.py.
"""

from orunmila.cli import app

if __name__ == "__main__":
    app(prog_name="orunmila")

https://effbot.org/tkinterbook/canvas.html
http://tkinter.fdex.eu/doc/caw.html


Objectif :  
Le réseau de neurone doit prendre en paramètre 5 inputs : 
les 5 distances séparant la voiture de 5 directions devant elle.


TODO :  
- arrêter la voiture si elle touche le bord de la fenêtre -> DONE
- rajouter les 2 lignes en diagonale -> DONE
- détecter les points d'intersection entre le radar et le circuit -> DONE
- détecter les points d'intersection entre la voiture et le circuit -> DONE

- tracer seulement les segments entre la voiture et l'intersection de la voiture et du circuit   -> DONE
    Pour chaque point d'intersection trouvé pour une ligne de radar :
        l'enregistrer en tant que point 'le plus proche' par défaut
        si un autre point est trouvé, il faut tester lequel des 2 est le plus proche du centre de la voiture
    
- permettre d'arreter ou reset la pos de la voiture si elle sort du circuit -> DONE
- calculer la longueur des 5 segments de radar  -> DONE
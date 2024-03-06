import matplotlib.pyplot as plt
import numpy as np

def precipitations(year,month,day):                    # Cette fonction permet simplement de représenter l'évolutiond es précipitations en Ile-de-France sur une journée.
    path = 'data/'+'{:04d}/'.format(year)
    file = 'RR_IDF300x300_{:04d}{:02d}{:02d}.npy'.format(year,month,day)
    file = path + file
    RR = np.load(file)/100.0
    RR[RR < 0]=np.nan
    plt.figure()
    plt.ion()        
    for i in range (288):
        plt.imshow(RR[i,:,:], cmap='Blues')
        #plt.show(block=True)
        #cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        #cv2.imshow('image', RR[i,:,:], cmap='Blues')
        plt.pause(0.2)
        plt.clf()

def segmentation_evenements(year,month,day):        # Cette fonction permet de séparer les différents événements de précipitations.
    path = 'data/'+'{:04d}/'.format(year)
    file = 'RR_IDF300x300_{:04d}{:02d}{:02d}.npy'.format(year,month,day)
    file = path + file
    RR = np.load(file)/100.0
    RR[RR < 0]=np.nan
    RR_seg = np.zeros([288,300,300])        # RR_seg sera une carte simplifiée indiquant simplement où un événement de précpitation est en cours. C'est un tableau binaire.
    for i in range (300):
        for j in range (300):
            t = 0
            t1 = 0
            while (t<288):
                if (RR[t,i,j]>0):
                    RR_seg[t,i,j] = 1
                    t1 = 0      # Compteur du temps à partir du dernier instant de pluie. S'il atteint 6, alors l'événement de pluie est terminé.
                    t = t+1
                    t0 = t      # t0 permet de garder en mémoire le premier instant de l'acalmie.
                    while (t<288 and (RR[t,i,j]==np.nan) and t1<6):      # Deux averses au même endroit font partie du même événement pluvieux si elles adviennent à moins de 30 min d'intervalle.
                        t1 = t1+1
                        t = t+1
                    if (t<288 and t1<6):
                        for t2 in range (t0,t+1):
                            RR_seg[t2,i,j] = 1
                else :
                    t = t+1
    return RR_seg